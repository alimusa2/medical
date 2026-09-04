import os
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from config import settings
from database import SessionLocal, get_db
from models import UploadedDocument
from schemas import EvaluationSchema
from services.document_processor import DocumentProcessor
from services.evaluation_engine import EvaluationEngine
from services.ai_service import AIService
from models import Evaluation, EvaluationResult
import uuid

try:
    from seed_data import demo_scenarios
except ImportError:
    from backend.seed_data import demo_scenarios

router = APIRouter(tags=["samples"])

@router.get("")
@router.get("/")
def list_sample_trfs(db: Session = Depends(get_db)):
    try:
        from seed_data import demo_scenarios
    except ImportError:
        from backend.seed_data import demo_scenarios
    samples = []
    os.makedirs(settings.SAMPLE_DIR, exist_ok=True)
    
    for idx, sc in enumerate(demo_scenarios, start=1):
        cat_key = sc["cat_key"]
        fname = f"demo_TRF_{idx:02d}_{cat_key.replace(' ', '_').replace('/', '_')}.pdf"
        dev_label = cat_key
        fpath = os.path.join(settings.SAMPLE_DIR, fname)
        size_b = os.path.getsize(fpath) if os.path.exists(fpath) else 25000

        samples.append({
            "filename": fname,
            "label": f"Demo TRF: {dev_label}",
            "size_bytes": size_b,
            "file_type": "PDF",
            "download_url": f"/api/samples/download/{fname}"
        })
    return samples

@router.get("/download/{filename}")
def download_sample_trf(filename: str, db: Session = Depends(get_db)):
    file_path = os.path.join(settings.SAMPLE_DIR, filename)
    if not os.path.exists(file_path):
        from seed_data import generate_sample_pdf_by_filename
        generate_sample_pdf_by_filename(filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Sample TRF file not found")

    media_type = "application/pdf" if filename.endswith(".pdf") else "text/csv"
    return FileResponse(file_path, media_type=media_type, filename=filename)

@router.post("/run-sample/{filename}", response_model=EvaluationSchema)
def run_sample_evaluation(filename: str, db: Session = Depends(get_db)):
    file_path = os.path.join(settings.SAMPLE_DIR, filename)
    if not os.path.exists(file_path):
        from seed_data import generate_sample_pdf_by_filename
        generate_sample_pdf_by_filename(filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Sample file not found")

    # Extract TRF
    norm = DocumentProcessor.process_file(file_path, "pdf")

    # Create document record
    doc = UploadedDocument(
        filename=filename,
        file_type="pdf",
        file_path=file_path,
        processing_status="EVALUATED",
        extracted_data_json=norm.model_dump_json()
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Evaluate
    overall_status, item_results, counts, meta = EvaluationEngine.evaluate_trf(db, norm)
    
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

    batch_id = f"BATCH-SAMPLE-{uuid.uuid4().hex[:6].upper()}"

    eval_rec = Evaluation(
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
    db.add(eval_rec)
    db.commit()
    db.refresh(eval_rec)

    for item in item_results:
        res_rec = EvaluationResult(
            evaluation_id=eval_rec.id,
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
        db.add(res_rec)

    db.commit()
    db.refresh(eval_rec)

    # Automatically generate PDF report so it is immediately listed in the Evaluation Reports section
    from routers.evaluations import _create_pdf_report
    _create_pdf_report(eval_rec, db)

    return eval_rec
