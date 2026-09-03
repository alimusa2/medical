import os
import json
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session

from database import get_db
from models import UploadedDocument, Evaluation
from schemas import UploadedDocumentSchema
from services.document_processor import DocumentProcessor
from config import settings

router = APIRouter(prefix="/api/documents", tags=["documents"])

@router.post("/upload", response_model=UploadedDocumentSchema)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Validate file extension
    ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    allowed_exts = ["pdf", "csv", "xlsx", "xls", "docx", "doc"]
    if ext not in allowed_exts:
        raise HTTPException(status_code=400, detail=f"Unsupported file extension '.{ext}'. Supported: {', '.join(allowed_exts)}")

    # Generate unique stored filename
    stored_filename = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, stored_filename)

    # Write file
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Create UploadedDocument DB record
    doc_record = UploadedDocument(
        filename=file.filename,
        file_type=ext,
        file_path=file_path,
        processing_status="PENDING"
    )
    db.add(doc_record)
    db.commit()
    db.refresh(doc_record)

    # Synchronously run extraction for fast user response
    try:
        norm_data = DocumentProcessor.process_file(file_path, ext)
        doc_record.extracted_data_json = norm_data.model_dump_json()
        doc_record.processing_status = "EXTRACTED"
        db.commit()
        db.refresh(doc_record)
    except Exception as e:
        doc_record.processing_status = "ERROR"
        db.commit()

    return doc_record

@router.get("", response_model=List[UploadedDocumentSchema])
def list_documents(db: Session = Depends(get_db)):
    return db.query(UploadedDocument).order_by(UploadedDocument.upload_date.desc()).all()

@router.get("/{doc_id}", response_model=UploadedDocumentSchema)
def get_document(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(UploadedDocument).filter(UploadedDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.post("/{doc_id}/process", response_model=UploadedDocumentSchema)
def process_document(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(UploadedDocument).filter(UploadedDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        norm_data = DocumentProcessor.process_file(doc.file_path, doc.file_type)
        doc.extracted_data_json = norm_data.model_dump_json()
        doc.processing_status = "EXTRACTED"
        db.commit()
        db.refresh(doc)
        return doc
    except Exception as e:
        doc.processing_status = "ERROR"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")
