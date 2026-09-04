import sys
import os

# Ensure backend directory is in sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base
from models import DeviceType, Standard, Requirement
from schemas import NormalizedTRFSchema, DeviceInfoSchema, ExtractedTestSchema, ExtractedStandardSchema
from services.evaluation_engine import EvaluationEngine

TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

def test_1_valid_passing_value(db_session):
    """Test 1: Valid passing value (0.22 mA <= 0.50 mA) -> PASS"""
    trf = NormalizedTRFSchema(
        device=DeviceInfoSchema(device_type="Blood Pressure Monitor"),
        standards=[ExtractedStandardSchema(name="IEC 60601-1")],
        tests=[ExtractedTestSchema(test_name="Leakage Current", result=0.22, unit="mA")]
    )
    overall, items, counts, meta = EvaluationEngine.evaluate_trf(db_session, trf)
    assert meta["device_category"] == "Blood Pressure Monitor"
    
    elec_item = next((i for i in items if "Electrical Safety" in i["test_name"]), None)
    assert elec_item is not None
    assert elec_item["status"] == "PASS"

def test_2_value_above_maximum(db_session):
    """Test 2: Value above maximum (0.72 mA > 0.50 mA) -> FAIL"""
    trf = NormalizedTRFSchema(
        device=DeviceInfoSchema(device_type="Blood Pressure Monitor"),
        standards=[ExtractedStandardSchema(name="IEC 60601-1")],
        tests=[ExtractedTestSchema(test_name="Leakage Current", result=0.72, unit="mA")]
    )
    overall, items, counts, meta = EvaluationEngine.evaluate_trf(db_session, trf)
    assert overall == "FAIL"
    elec_item = next((i for i in items if "Electrical Safety" in i["test_name"]), None)
    assert elec_item is not None
    assert elec_item["status"] == "FAIL"
    assert counts["failed_tests"] >= 1

def test_3_missing_value(db_session):
    """Test 3: Missing value -> NEEDS REVIEW"""
    trf = NormalizedTRFSchema(
        device=DeviceInfoSchema(device_type="Blood Pressure Monitor"),
        standards=[ExtractedStandardSchema(name="IEC 60601-1")],
        tests=[ExtractedTestSchema(test_name="Leakage Current", result=None, unit="mA")]
    )
    overall, items, counts, meta = EvaluationEngine.evaluate_trf(db_session, trf)
    assert overall == "NEEDS REVIEW"
    elec_item = next((i for i in items if "Electrical Safety" in i["test_name"]), None)
    assert elec_item is not None
    assert elec_item["status"] == "NEEDS REVIEW"

def test_4_ivd_pathway_demonstration(db_session):
    """Test 4: Laboratory Analyzer device -> Demonstrates IEC 61010 pathway (IEC 60601-1 NOT APPLICABLE)"""
    trf = NormalizedTRFSchema(
        device=DeviceInfoSchema(device_type="Medical Laboratory / Diagnostic Electrical Equipment"),
        standards=[ExtractedStandardSchema(name="IEC 61010-1")],
        tests=[ExtractedTestSchema(test_name="Lab Mains Insulation", result=45.0, unit="MΩ")]
    )
    overall, items, counts, meta = EvaluationEngine.evaluate_trf(db_session, trf)
    assert meta["pathway"] == "IVD / Laboratory Equipment"
    na_item = next((i for i in items if "IEC 60601-1" in i["test_name"]), None)
    assert na_item is not None
    assert na_item["status"] == "NOT APPLICABLE"
