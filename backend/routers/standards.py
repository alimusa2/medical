from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Standard, Requirement, DeviceType
from schemas import StandardSchema, RequirementSchema, DeviceTypeSchema

router = APIRouter(tags=["standards"])

@router.get("", response_model=List[StandardSchema])
def list_standards(db: Session = Depends(get_db)):
    return db.query(Standard).all()

@router.get("/device-types", response_model=List[DeviceTypeSchema])
def list_device_types(db: Session = Depends(get_db)):
    return db.query(DeviceType).all()

@router.get("/requirements", response_model=List[RequirementSchema])
def list_requirements(db: Session = Depends(get_db)):
    return db.query(Requirement).all()
