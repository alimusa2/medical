from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models import Evaluation
from schemas import EvaluationSchema, CertifierActionRequest

router = APIRouter(tags=["certifier"])

@router.get("/pending", response_model=List[EvaluationSchema])
def get_pending_certifications(db: Session = Depends(get_db)):
    return db.query(Evaluation).filter(Evaluation.certifier_status == "PENDING_REVIEW").order_by(Evaluation.created_at.desc()).all()

@router.get("/all", response_model=List[EvaluationSchema])
def get_all_certifications(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Evaluation)
    if status and status.upper() != "ALL":
        query = query.filter(Evaluation.certifier_status == status.upper())
    return query.order_by(Evaluation.created_at.desc()).all()

@router.get("/history")
def get_certifier_history(db: Session = Depends(get_db)):
    evals = db.query(Evaluation).order_by(Evaluation.created_at.desc()).all()
    history = []
    for ev in evals:
        history.append({
            "id": ev.id,
            "batch_id": ev.batch_id,
            "device_name": ev.device_name or "Medical Device",
            "device_model": ev.device_model or "N/A",
            "overall_status": ev.overall_status,
            "certifier_status": ev.certifier_status or "PENDING_REVIEW",
            "certifier_notes": ev.certifier_notes or "No notes recorded.",
            "created_at": ev.created_at.isoformat() if ev.created_at else None,
            "passed_tests": ev.passed_tests,
            "failed_tests": ev.failed_tests,
            "needs_review_tests": ev.needs_review_tests
        })
    return history

@router.post("/{evaluation_id}/approve", response_model=EvaluationSchema)
def approve_evaluation(evaluation_id: int, req: CertifierActionRequest = CertifierActionRequest(action="APPROVE"), db: Session = Depends(get_db)):
    ev = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Evaluation record not found")

    ev.certifier_status = "APPROVED"
    ev.certifier_notes = req.notes or "Evaluation approved by certifier."
    db.commit()
    db.refresh(ev)
    return ev

@router.post("/{evaluation_id}/request-review", response_model=EvaluationSchema)
def request_review(evaluation_id: int, req: CertifierActionRequest = CertifierActionRequest(action="REQUEST_REVIEW"), db: Session = Depends(get_db)):
    ev = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Evaluation record not found")

    ev.certifier_status = "NEEDS_MORE_INFO"
    ev.certifier_notes = req.notes or "Further technical reviewer investigation requested."
    db.commit()
    db.refresh(ev)
    return ev

@router.post("/{evaluation_id}/return-to-reviewer", response_model=EvaluationSchema)
def return_to_reviewer(evaluation_id: int, req: CertifierActionRequest = CertifierActionRequest(action="RETURN_TO_REVIEWER"), db: Session = Depends(get_db)):
    ev = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Evaluation record not found")

    ev.certifier_status = "REJECTED"
    ev.certifier_notes = req.notes or "Returned to technical reviewer for clarification."
    db.commit()
    db.refresh(ev)
    return ev
