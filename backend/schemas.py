from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, ConfigDict

# Normalized Internal Document Schemas
class ExtractedStandardSchema(BaseModel):
    name: str
    edition: Optional[str] = "Demo"

class ExtractedTestSchema(BaseModel):
    test_name: str
    result: Any  # Could be float, int, or string like "PASS"
    unit: Optional[str] = None
    evidence: Optional[str] = None
    technician: Optional[str] = None

class DeviceInfoSchema(BaseModel):
    name: Optional[str] = "Unknown Medical Device"
    model: Optional[str] = "N/A"
    manufacturer: Optional[str] = "N/A"
    device_type: Optional[str] = "Blood Pressure Monitor"
    serial_number: Optional[str] = "N/A"
    test_date: Optional[str] = "N/A"

class NormalizedTRFSchema(BaseModel):
    device: DeviceInfoSchema
    standards: List[ExtractedStandardSchema] = []
    tests: List[ExtractedTestSchema] = []
    raw_notes: Optional[str] = None

# AI Structured Output Schema
class AISummarySchema(BaseModel):
    summary: str = Field(description="Executive summary of the evaluation results")
    key_findings: List[str] = Field(default_factory=list, description="Key observation bullet points")
    failed_items: List[str] = Field(default_factory=list, description="List of failed test descriptions")
    review_items: List[str] = Field(default_factory=list, description="List of items requiring expert human review")
    recommendation: str = Field(description="Actionable next step recommendation for certifier")

# DB & API Response Schemas
class DeviceTypeSchema(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class StandardSchema(BaseModel):
    id: int
    name: str
    edition: Optional[str] = None
    description: Optional[str] = None
    status: str

    model_config = ConfigDict(from_attributes=True)

class RequirementSchema(BaseModel):
    id: int
    requirement_code: str
    standard_id: int
    device_type_id: int
    title: str
    description: Optional[str] = None
    test_parameter: str
    operator: Optional[str] = None
    minimum_value: Optional[float] = None
    maximum_value: Optional[float] = None
    unit: Optional[str] = None
    expected_text: Optional[str] = None
    is_demo: bool

    model_config = ConfigDict(from_attributes=True)

class EvaluationResultSchema(BaseModel):
    id: int
    evaluation_id: int
    requirement_id: Optional[int] = None
    test_name: str
    standard_code: Optional[str] = "IEC 60601-1"
    standard_category: Optional[str] = "General"
    evidence_found: Optional[str] = "Yes"
    trf_result: Optional[str] = "PASS"
    source_location: Optional[str] = "TRF Test Results Section"
    observed_value: Optional[str] = None
    unit: Optional[str] = None
    expected_requirement: Optional[str] = None
    status: str
    reason: Optional[str] = None
    confidence: str

    model_config = ConfigDict(from_attributes=True)

class EvaluationSchema(BaseModel):
    id: int
    batch_id: str
    document_id: int
    overall_status: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    needs_review_tests: int
    not_applicable_tests: int = 0
    device_type_name: Optional[str] = None
    device_model: Optional[str] = None
    manufacturer: Optional[str] = None
    pathway: Optional[str] = "ME Equipment"
    ai_summary: Optional[str] = None
    certifier_status: str
    certifier_notes: Optional[str] = None
    created_at: datetime
    results: List[EvaluationResultSchema] = []

    model_config = ConfigDict(from_attributes=True)

class UploadedDocumentSchema(BaseModel):
    id: int
    filename: str
    file_type: str
    file_path: str
    upload_date: datetime
    processing_status: str
    extracted_data_json: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class CertifierActionRequest(BaseModel):
    action: str  # APPROVE, REQUEST_REVIEW, RETURN_TO_REVIEWER
    notes: Optional[str] = ""
