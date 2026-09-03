from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class DeviceType(Base):
    __tablename__ = "device_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)

    requirements = relationship("Requirement", back_populates="device_type")


class Standard(Base):
    __tablename__ = "standards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    edition = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="ACTIVE")

    requirements = relationship("Requirement", back_populates="standard")


class Requirement(Base):
    __tablename__ = "requirements"

    id = Column(Integer, primary_key=True, index=True)
    requirement_code = Column(String(50), nullable=False, unique=True, index=True)
    standard_id = Column(Integer, ForeignKey("standards.id"), nullable=False)
    device_type_id = Column(Integer, ForeignKey("device_types.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    test_parameter = Column(String(100), nullable=False, index=True)
    operator = Column(String(10), nullable=True) # <=, >=, range, ==
    minimum_value = Column(Float, nullable=True)
    maximum_value = Column(Float, nullable=True)
    unit = Column(String(50), nullable=True)
    expected_text = Column(String(100), nullable=True)
    is_demo = Column(Boolean, default=True)

    standard = relationship("Standard", back_populates="requirements")
    device_type = relationship("DeviceType", back_populates="requirements")
    evaluation_results = relationship("EvaluationResult", back_populates="requirement")


class UploadedDocument(Base):
    __tablename__ = "uploaded_documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False)
    file_path = Column(String(500), nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    processing_status = Column(String(50), default="PENDING") # PENDING, EXTRACTED, EVALUATED, ERROR
    extracted_data_json = Column(Text, nullable=True)

    evaluations = relationship("Evaluation", back_populates="document")


class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(String(100), nullable=False, index=True)
    document_id = Column(Integer, ForeignKey("uploaded_documents.id"), nullable=False)
    overall_status = Column(String(50), nullable=False) # PASS, FAIL, NEEDS REVIEW
    total_tests = Column(Integer, default=0)
    passed_tests = Column(Integer, default=0)
    failed_tests = Column(Integer, default=0)
    needs_review_tests = Column(Integer, default=0)
    not_applicable_tests = Column(Integer, default=0)
    device_type_name = Column(String(100), nullable=True)
    device_model = Column(String(100), nullable=True)
    manufacturer = Column(String(100), nullable=True)
    pathway = Column(String(100), default="ME Equipment")
    ai_summary = Column(Text, nullable=True)
    certifier_status = Column(String(50), default="PENDING_REVIEW") # PENDING_REVIEW, APPROVED, REJECTED, NEEDS_MORE_INFO
    certifier_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("UploadedDocument", back_populates="evaluations")
    results = relationship("EvaluationResult", back_populates="evaluation", cascade="all, delete-orphan")


class EvaluationResult(Base):
    __tablename__ = "evaluation_results"

    id = Column(Integer, primary_key=True, index=True)
    evaluation_id = Column(Integer, ForeignKey("evaluations.id"), nullable=False)
    requirement_id = Column(Integer, ForeignKey("requirements.id"), nullable=True)
    test_name = Column(String(150), nullable=False)
    standard_code = Column(String(100), nullable=True, default="IEC 60601-1")
    standard_category = Column(String(50), nullable=True, default="General")
    evidence_found = Column(String(50), nullable=True, default="Yes")
    trf_result = Column(String(50), nullable=True, default="PASS")
    source_location = Column(String(255), nullable=True, default="TRF Test Results Section")
    observed_value = Column(String(100), nullable=True)
    unit = Column(String(50), nullable=True)
    expected_requirement = Column(String(255), nullable=True)
    status = Column(String(50), nullable=False) # PASS, FAIL, NEEDS REVIEW, NOT APPLICABLE
    reason = Column(Text, nullable=True)
    confidence = Column(String(20), default="HIGH") # HIGH, MEDIUM, LOW

    evaluation = relationship("Evaluation", back_populates="results")
    requirement = relationship("Requirement", back_populates="evaluation_results")

