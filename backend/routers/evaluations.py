import json
import os
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import UploadedDocument, Evaluation, EvaluationResult
from schemas import EvaluationSchema, NormalizedTRFSchema
from services.evaluation_engine import EvaluationEngine
from services.ai_service import AIService
from services.report_generator import PDFReportGenerator

router = APIRouter(tags=["evaluations"])

@router.get("", response_model=List[EvaluationSchema])
def list_evaluations(db: Session = Depends(get_db)):
    return db.query(Evaluation).order_by(Evaluation.created_at.desc()).all()

@router.get("/{eval_id}", response_model=EvaluationSchema)
def get_evaluation(eval_id: int, db: Session = Depends(get_db)):
    ev = db.query(Evaluation).filter(Evaluation.id == eval_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Evaluation record not found")
    return ev

@router.post("/document/{doc_id}/run", response_model=EvaluationSchema)
def run_evaluation(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(UploadedDocument).filter(UploadedDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Uploaded document not found")

    if not doc.extracted_data_json:
        # Try extracting if not done yet
        from services.document_processor import DocumentProcessor
        norm = DocumentProcessor.process_file(doc.file_path, doc.file_type)
        doc.extracted_data_json = norm.model_dump_json()
        doc.processing_status = "EXTRACTED"
        db.commit()
    else:
        norm = NormalizedTRFSchema.model_validate_json(doc.extracted_data_json)

    # 1. Deterministic Evaluation Engine
    overall_status, item_results, counts, meta = EvaluationEngine.evaluate_trf(db, norm)

    # 2. AI Summary Generation
    device_name = meta.get("device_name", norm.device.name or "Medical Device")
    model_name = meta.get("model_name", norm.device.model or "N/A")
    standards_str = ", ".join([h["code"] for h in meta.get("standards_hierarchy", []) if h.get("applicable")]) or "IEC 60601-1"

    ai_schema = AIService.generate_evaluation_summary(
        device_name=device_name,
        model_name=model_name,
        standards_str=standards_str,
        results_list=item_results,
        overall_status=overall_status
    )

    batch_id = f"BATCH-{uuid.uuid4().hex[:8].upper()}"

    # Create Evaluation DB record
    eval_record = Evaluation(
        batch_id=batch_id,
        document_id=doc.id,
        overall_status=overall_status,
        total_tests=counts.get("total_tests", 0),
        passed_tests=counts.get("passed_tests", 0),
        failed_tests=counts.get("failed_tests", 0),
        needs_review_tests=counts.get("needs_review_tests", 0),
        not_applicable_tests=counts.get("not_applicable_tests", 0),
        device_type_name=meta.get("device_category"),
        device_model=model_name,
        manufacturer=meta.get("manufacturer"),
        pathway=meta.get("pathway", "ME Equipment"),
        ai_summary=ai_schema.model_dump_json(),
        certifier_status="PENDING_REVIEW"
    )
    db.add(eval_record)
    db.commit()
    db.refresh(eval_record)

    # Create EvaluationResult DB records
    for item in item_results:
        res_record = EvaluationResult(
            evaluation_id=eval_record.id,
            requirement_id=item.get("requirement_id"),
            test_name=item["test_name"],
            standard_code=item.get("standard_code", "IEC 60601-1"),
            standard_category=item.get("standard_category", "General"),
            evidence_found=item.get("evidence_found", "Yes"),
            trf_result=item.get("trf_result", "PASS"),
            source_location=item.get("source_location", "TRF Test Results Section"),
            observed_value=item.get("observed_value"),
            unit=item.get("unit"),
            expected_requirement=item.get("expected_requirement"),
            status=item["status"],
            reason=item.get("reason"),
            confidence=item.get("confidence", "HIGH")
        )
        db.add(res_record)

    doc.processing_status = "EVALUATED"
    db.commit()
    db.refresh(eval_record)

    # Automatically generate PDF report so it is immediately listed in the Evaluation Reports section
    _create_pdf_report(eval_record, db)

    return eval_record

def _create_pdf_report(ev: Evaluation, db: Session) -> str:
    doc = db.query(UploadedDocument).filter(UploadedDocument.id == ev.document_id).first()
    norm = None
    if doc and doc.extracted_data_json:
        try:
            norm = NormalizedTRFSchema.model_validate_json(doc.extracted_data_json)
        except Exception:
            norm = None

    eval_dict = {
        "overall_status": ev.overall_status,
        "batch_id": ev.batch_id,
        "counts": {
            "total_tests": ev.total_tests,
            "passed_tests": ev.passed_tests,
            "failed_tests": ev.failed_tests,
            "needs_review_tests": ev.needs_review_tests,
            "not_applicable_tests": ev.not_applicable_tests
        },
        "device_info": norm.device.model_dump() if (norm and norm.device) else {},
        "document_info": {"filename": doc.filename if doc else "N/A", "upload_date": str(doc.upload_date) if doc else "N/A"},
        "standards_str": ", ".join([s.name for s in norm.standards]) if (norm and norm.standards) else "IEC 60601-1 (Demo)",
        "results": [
            {
                "test_name": r.test_name,
                "standard_code": r.standard_code,
                "standard_category": r.standard_category,
                "observed_value": r.observed_value,
                "unit": r.unit,
                "expected_requirement": r.expected_requirement,
                "status": r.status,
                "reason": r.reason
            }
            for r in ev.results
        ],
        "ai_summary": ev.ai_summary
    }

    try:
        report_path = PDFReportGenerator.generate_evaluation_pdf(ev.id, eval_dict)
        return report_path
    except Exception as e:
        print(f"Warning: PDF report generation failed: {e}")
        return ""

@router.post("/{eval_id}/generate-report")
def generate_report(eval_id: int, db: Session = Depends(get_db)):
    ev = db.query(Evaluation).filter(Evaluation.id == eval_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Evaluation record not found")

    report_path = _create_pdf_report(ev, db)
    if report_path and os.path.exists(report_path):
        filename = os.path.basename(report_path)
        return {"message": "Report generated successfully", "report_path": report_path, "filename": filename}
    else:
        raise HTTPException(status_code=500, detail="Report generation failed.")
