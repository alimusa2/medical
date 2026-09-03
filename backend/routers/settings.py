from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from config import settings
from services.ai_service import AIService
from seed_data import seed_database

router = APIRouter(prefix="/api/settings", tags=["settings"])

@router.get("/status")
def get_system_status(db: Session = Depends(get_db)):
    groq_diag = AIService.verify_groq_status()
    
    return {
        "ai_model": settings.GROQ_MODEL,
        "groq_status": groq_diag,
        "database_status": "Connected (SQLite)",
        "supported_file_types": ["PDF", "CSV", "XLSX", "DOCX"],
        "upload_dir": settings.UPLOAD_DIR,
        "report_dir": settings.REPORT_DIR,
        "sample_dir": settings.SAMPLE_DIR
    }

@router.get("/verify-groq")
def verify_groq():
    return AIService.verify_groq_status()

@router.post("/reseed-db")
def reseed_db(db: Session = Depends(get_db)):
    seed_database(db)
    return {"message": "Database and synthetic TRFs successfully reseeded!"}
