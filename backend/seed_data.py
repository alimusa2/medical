import os
import uuid
from sqlalchemy.orm import Session

from database import engine, SessionLocal, Base
from models import DeviceType, Standard, Requirement, UploadedDocument, Evaluation, EvaluationResult
from config import settings
from services.standards_kb import DEVICE_CATEGORIES_MAPPING
from schemas import NormalizedTRFSchema, DeviceInfoSchema, ExtractedStandardSchema, ExtractedTestSchema, AISummarySchema
from services.evaluation_engine import EvaluationEngine
from services.ai_service import AIService


def seed_database(db: Session):
    # Re-create database schema cleanly
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # 1. Device Types Seed
    for cat_key, cat_data in DEVICE_CATEGORIES_MAPPING.items():
        existing = db.query(DeviceType).filter_by(name=cat_key).first()
        if not existing:
            db.add(DeviceType(name=cat_key, description=cat_data["particular_title"]))
    db.commit()

    # 2. Standards Seed
    default_stds = [
        ("IEC 60601-1", "3.2 Edition", "General safety for medical electrical equipment"),
        ("IEC 60601-1-2", "4.1 Edition", "Electromagnetic disturbances - EMC"),
        ("IEC 60601-1-6", "3.2 Edition", "Usability engineering"),
        ("IEC 60601-1-8", "2.2 Edition", "Alarm systems in medical electrical equipment"),
        ("IEC 60601-1-3", "2.1 Edition", "Radiation protection in diagnostic X-ray"),
        ("IEC 61010-1", "3.1 Edition", "Safety requirements for laboratory electrical equipment"),
        ("IEC 61010-2-101", "3.0 Edition", "Particular requirements for IVD medical equipment"),
        ("ISO 14971", "2019 Edition", "Application of risk management to medical devices"),
        ("IEC 62366-1", "2020 Edition", "Usability engineering process"),
        ("IEC 62304", "2015 Edition", "Medical device software lifecycle processes")
    ]
    for s_name, s_ed, s_desc in default_stds:
        existing = db.query(Standard).filter_by(name=s_name).first()
        if not existing:
            db.add(Standard(name=s_name, edition=s_ed, description=s_desc))
    db.commit()

    # 2.5 Seed Requirements Table from Knowledge Base
    from services.standards_kb import STANDARDS_KNOWLEDGE_BASE
    dev_type_obj = db.query(DeviceType).first()
    dev_type_id = dev_type_obj.id if dev_type_obj else 1
    for std_name, std_info in STANDARDS_KNOWLEDGE_BASE.items():
        std_obj = db.query(Standard).filter_by(name=std_name).first()
        if not std_obj:
            continue
        for area in std_info.get("evaluation_areas", []):
            req_code = f"REQ-{std_name.replace(' ', '-').replace('/', '-')}-{area['param'].replace(' ', '-')}"
            existing = db.query(Requirement).filter_by(requirement_code=req_code).first()
            if not existing:
                db.add(Requirement(
                    requirement_code=req_code,
                    standard_id=std_obj.id,
                    device_type_id=dev_type_id,
                    title=area["area"],
                    test_parameter=area["param"],
                    operator=area.get("op", "=="),
                    minimum_value=area.get("min_val"),
                    maximum_value=area.get("max_val"),
                    expected_text=area.get("exp_text"),
                    unit=area.get("unit")
                ))
    db.commit()

    # 3. Generate 15 Synthetic Sample TRFs & Seed Database Evaluations
    seed_all_15_demo_evaluations(db)


def seed_all_15_demo_evaluations(db: Session):
    sample_dir = settings.SAMPLE_DIR
    upload_dir = settings.UPLOAD_DIR
    os.makedirs(sample_dir, exist_ok=True)
    os.makedirs(upload_dir, exist_ok=True)

    # 15 Specific Demonstration Devices & Comprehensive Real-World IEC Test Scenarios
    demo_scenarios = [
        {
            "cat_key": "Blood Pressure Monitor",
            "model": "BP-100",
            "mfr": "CardioTech Medical Systems",
            "serial": "SN-BP-1001",
            "report_num": "TRF-2026-BP01",
            "expected_outcome": "PASS",
            "tests": [
                {"test_name": "Leakage Current", "result": 0.22, "unit": "mA", "evidence": "Earth leakage 0.22 mA recorded under 230V normal condition (limit <= 0.5 mA)"},
                {"test_name": "Insulation Resistance", "result": 100.0, "unit": "MΩ", "evidence": "500V DC applied, 100 MΩ measured (limit >= 20 MΩ)"},
                {"test_name": "Dielectric Strength", "result": "PASS", "unit": "-", "evidence": "1500V AC 50Hz applied for 60s without breakdown"},
                {"test_name": "Temperature", "result": 37.5, "unit": "°C", "evidence": "Maximum enclosure surface thermal probe reading (limit <= 41.0 °C)"},
                {"test_name": "Patient Leakage Current", "result": 0.02, "unit": "mA", "evidence": "Direct patient cuff leakage 0.02 mA (limit <= 0.05 mA)"},
                {"test_name": "BP Measurement Accuracy", "result": 1.5, "unit": "mmHg", "evidence": "Static pressure calibration bias 1.5 mmHg (limit <= 3.0 mmHg)"},
                {"test_name": "Overpressure Safety Cutoff", "result": 285.0, "unit": "mmHg", "evidence": "Automatic pressure relief valve activated at 285 mmHg (limit <= 300 mmHg)"},
                {"test_name": "Cuff Pressure Transducer Accuracy", "result": 1.0, "unit": "mmHg", "evidence": "Pressure linearity error 1.0 mmHg"},
                {"test_name": "EMC Immunity", "result": "PASS", "unit": "-", "evidence": "8kV air / 6kV contact ESD immunity satisfied per IEC 60601-1-2"},
                {"test_name": "Alarm Priority", "result": "PASS", "evidence": "Auditory alarm sound pressure 70 dBA measured per IEC 60601-1-8"},
                {"test_name": "Usability Engineering", "result": "PASS", "evidence": "Summative usability evaluation complete per IEC 62366-1"},
                {"test_name": "Risk Management", "result": "PASS", "evidence": "ISO 14971 risk management file audit verified"},
                {"test_name": "Software Lifecycle", "result": "PASS", "evidence": "IEC 62304 Class B firmware verification & validation passed"},
                {"test_name": "Label Verification", "result": "COMPLETE", "evidence": "Rating plate & CE mark verified"}
            ]
        },
        {
            "cat_key": "ECG / Electrocardiograph",
            "model": "ECG-1200",
            "mfr": "BioSignal Instruments",
            "serial": "SN-ECG-992",
            "report_num": "TRF-2026-ECG02",
            "expected_outcome": "FAIL",
            "tests": [
                {"test_name": "Leakage Current", "result": 0.18, "unit": "mA", "evidence": "Earth leakage current normal condition"},
                {"test_name": "Insulation Resistance", "result": 85.0, "unit": "MΩ", "evidence": "Mains supply insulation OK"},
                {"test_name": "Dielectric Strength", "result": "PASS", "unit": "-", "evidence": "4000V high voltage insulation test satisfied"},
                {"test_name": "Temperature", "result": 36.2, "unit": "°C", "evidence": "Enclosure surface temp 36.2 °C"},
                {"test_name": "Patient Leakage Current", "result": 0.08, "unit": "mA", "evidence": "Direct patient lead auxiliary current 0.08 mA - EXCEEDS LIMIT (<= 0.05 mA)"},
                {"test_name": "Defibrillator Discharge Test", "result": "PASS", "evidence": "Post 5kV energy recovery verified per IEC 60601-2-25"},
                {"test_name": "ECG Frequency Bandwidth", "result": 160.0, "unit": "Hz", "evidence": "3dB frequency bandwidth 0.05 - 160 Hz"},
                {"test_name": "Pacemaker Pulse Suppression", "result": "PASS", "evidence": "Rejection of 2mV pacemaker pulse confirmed"},
                {"test_name": "EMC Immunity", "result": "PASS", "evidence": "Radiated RF field immunity 10 V/m satisfied"},
                {"test_name": "Alarm Priority", "result": "PASS", "evidence": "Lead-off visual & auditory alarm 74 dBA"},
                {"test_name": "Usability Engineering", "result": "PASS", "evidence": "Lead color coding usability verified"},
                {"test_name": "Risk Management", "result": "PASS", "evidence": "ISO 14971 risk management file verified"},
                {"test_name": "Software Lifecycle", "result": "PASS", "evidence": "ECG rhythm analysis algorithm verified per IEC 62304"},
                {"test_name": "Label Verification", "result": "COMPLETE", "evidence": "Defibrillator proof warning label present"}
            ]
        },
        {
            "cat_key": "Patient Monitor",
            "model": "PM-800",
            "mfr": "OmniCare Diagnostics",
            "serial": "SN-PM-8840",
            "report_num": "TRF-2026-PM03",
            "expected_outcome": "NEEDS REVIEW",
            "tests": [
                {"test_name": "Leakage Current", "result": 0.29, "unit": "mA", "evidence": "Normal condition earth leakage"},
                {"test_name": "Insulation Resistance", "result": 120.0, "unit": "MΩ", "evidence": "Primary isolation 120 MΩ"},
                {"test_name": "Dielectric Strength", "result": "PASS", "unit": "-", "evidence": "4500V dielectric breakdown check satisfied"},
                {"test_name": "Temperature", "result": 38.1, "unit": "°C", "evidence": "Enclosure surface temp 38.1 °C"},
                {"test_name": "Patient Leakage Current", "result": 0.03, "unit": "mA", "evidence": "Patient auxiliary leakage 0.03 mA"},
                {"test_name": "Channel Isolation", "result": 4000.0, "unit": "V", "evidence": "High voltage channel isolation verified"},
                {"test_name": "Waveform Display Latency", "result": 65.0, "unit": "ms", "evidence": "Real-time sweep rendering latency 65 ms"},
                {"test_name": "EMC Immunity", "result": "PASS", "evidence": "10 V/m RF field immunity satisfied"},
                {"test_name": "Alarm Priority", "result": "UNRECORDED", "evidence": "Auditory alarm sound pressure level missing in test records section 3"},
                {"test_name": "Usability Engineering", "result": "PASS", "evidence": "Display layout & touch screen usability validated"},
                {"test_name": "Risk Management", "result": "PASS", "evidence": "ISO 14971 risk management file verified"},
                {"test_name": "Software Lifecycle", "result": "PASS", "evidence": "Multi-parameter software verification complete"},
                {"test_name": "Label Verification", "result": "COMPLETE", "evidence": "Rating plate & CE markings present"}
            ]
        },
        {
            "cat_key": "Infusion Pump",
            "model": "IP-500",
            "mfr": "FluidCare Medical Equipment",
            "serial": "SN-IP-5011",
            "report_num": "TRF-2026-IP04",
            "expected_outcome": "FAIL",
            "tests": [
                {"test_name": "Leakage Current", "result": 0.31, "unit": "mA", "evidence": "Standard enclosure leakage test"},
                {"test_name": "Insulation Resistance", "result": 110.0, "unit": "MΩ", "evidence": "Mains supply insulation 110 MΩ"},
                {"test_name": "Dielectric Strength", "result": "PASS", "unit": "-", "evidence": "3000V high voltage isolation check"},
                {"test_name": "Temperature", "result": 39.2, "unit": "°C", "evidence": "Motor housing surface temp 39.2 °C"},
                {"test_name": "Patient Leakage Current", "result": 0.02, "unit": "mA", "evidence": "Patient lead leakage 0.02 mA"},
                {"test_name": "Flow Delivery Accuracy", "result": 2.1, "unit": "%", "evidence": "Volumetric delivery rate error 2.1% (limit <= 5.0%)"},
                {"test_name": "Occlusion Pressure Limit", "result": 135.0, "unit": "kPa", "evidence": "Downstream occlusion pressure 135 kPa - EXCEEDS SAFETY LIMIT (<= 100 kPa)"},
                {"test_name": "Air Bubble Detection", "result": 35.0, "unit": "µL", "evidence": "Ultrasonic air sensor trigger 35 µL"},
                {"test_name": "EMC Immunity", "result": "PASS", "evidence": "Conducted disturbances immunity satisfied"},
                {"test_name": "Alarm Priority", "result": "PASS", "evidence": "Red high priority occlusion alarm 78 dBA"},
                {"test_name": "Usability Engineering", "result": "PASS", "evidence": "Dosing unit input usability validated"},
                {"test_name": "Risk Management", "result": "PASS", "evidence": "Infusion risk hazard analysis verified"},
                {"test_name": "Software Lifecycle", "result": "PASS", "evidence": "Pump motor control software Class C verified"},
                {"test_name": "Label Verification", "result": "COMPLETE", "evidence": "Flow direction markings present"}
            ]
        },
        {
            "cat_key": "Infusion Syringe Pump",
            "model": "SP-200",
            "mfr": "FluidCare Medical Equipment",
            "serial": "SN-SP-2004",
            "report_num": "TRF-2026-SP05",
            "expected_outcome": "PASS",
            "tests": [
                {"test_name": "Leakage Current", "result": 0.25, "unit": "mA", "evidence": "Enclosure leakage test 0.25 mA"},
                {"test_name": "Insulation Resistance", "result": 95.0, "unit": "MΩ", "evidence": "Mains insulation test 95 MΩ"},
                {"test_name": "Dielectric Strength", "result": "PASS", "unit": "-", "evidence": "3000V high voltage isolation satisfied"},
                {"test_name": "Temperature", "result": 36.8, "unit": "°C", "evidence": "Enclosure surface temp 36.8 °C"},
                {"test_name": "Patient Leakage Current", "result": 0.01, "unit": "mA", "evidence": "Patient lead leakage 0.01 mA"},
                {"test_name": "Syringe Barrel Fit Test", "result": "PASS", "evidence": "Optical sensor syringe size check"},
                {"test_name": "Flow Delivery Accuracy", "result": 1.8, "unit": "%", "evidence": "Volumetric delivery accuracy 1.8%"},
                {"test_name": "Occlusion Pressure Limit", "result": 85.0, "unit": "kPa", "evidence": "Occlusion pressure relief 85 kPa (limit <= 100 kPa)"},
                {"test_name": "EMC Immunity", "result": "PASS", "evidence": "8kV ESD immunity satisfied"},
                {"test_name": "Alarm Priority", "result": "PASS", "evidence": "Syringe empty auditory alarm 72 dBA"},
                {"test_name": "Usability Engineering", "result": "PASS", "evidence": "Syringe loading ergonomics file verified"},
                {"test_name": "Risk Management", "result": "PASS", "evidence": "ISO 14971 risk management file complete"},
                {"test_name": "Software Lifecycle", "result": "PASS", "evidence": "Syringe drive firmware verification complete"},
                {"test_name": "Label Verification", "result": "COMPLETE", "evidence": "Syringe size compatibility plate present"}
            ]
        },
        {
            "cat_key": "Ventilator",
            "model": "V-900",
            "mfr": "RespiTech Care Systems",
            "serial": "SN-VENT-901",
            "report_num": "TRF-2026-VENT06",
            "expected_outcome": "FAIL",
            "tests": [
                {"test_name": "Leakage Current", "result": 0.45, "unit": "mA", "evidence": "Earth leakage 0.45 mA"},
                {"test_name": "Insulation Resistance", "result": 75.0, "unit": "MΩ", "evidence": "Primary insulation 75 MΩ"},
                {"test_name": "Dielectric Strength", "result": "PASS", "unit": "-", "evidence": "4000V high voltage check satisfied"},
                {"test_name": "Temperature", "result": 42.1, "unit": "°C", "evidence": "Blower motor temp 42.1 °C"},
                {"test_name": "Patient Leakage Current", "result": 0.03, "unit": "mA", "evidence": "Patient circuit leakage 0.03 mA"},
                {"test_name": "Tidal Volume Accuracy", "result": 4.2, "unit": "%", "evidence": "Volume delivery tolerance 4.2%"},
                {"test_name": "Max Airway Pressure", "result": 68.0, "unit": "cmH2O", "evidence": "Airway pressure cutoff 68 cmH2O - EXCEEDS LIMIT (<= 60 cmH2O)"},
                {"test_name": "Battery Backup Operating Time", "result": 22.0, "unit": "min", "evidence": "Internal battery operating time 22 mins - BELOW MINIMUM (>= 60 min)"},
                {"test_name": "EMC Immunity", "result": "PASS", "evidence": "10 V/m RF field immunity satisfied"},
                {"test_name": "Alarm Priority", "result": "PASS", "evidence": "High urgency apnea alarm 82 dBA"},
                {"test_name": "Usability Engineering", "result": "PASS", "evidence": "ICU clinical user evaluation complete"},
                {"test_name": "Risk Management", "result": "PASS", "evidence": "Ventilator hazard mitigation file verified"},
                {"test_name": "Software Lifecycle", "result": "PASS", "evidence": "Critical software architecture Class C verified"},
                {"test_name": "Label Verification", "result": "COMPLETE", "evidence": "Oxygen supply inlet markings present"}
            ]
        },
        {
            "cat_key": "Defibrillator",
            "model": "DEF-700",
            "mfr": "LifePulse Resuscitation Tech",
            "serial": "SN-DEF-7002",
            "report_num": "TRF-2026-DEF07",
            "expected_outcome": "PASS",
            "tests": [
                {"test_name": "Leakage Current", "result": 0.20, "unit": "mA", "evidence": "Earth leakage test 0.20 mA"},
                {"test_name": "Insulation Resistance", "result": 150.0, "unit": "MΩ", "evidence": "Mains insulation 150 MΩ"},
                {"test_name": "Dielectric Strength", "result": "PASS", "unit": "-", "evidence": "5000V paddle isolation barrier satisfied"},
                {"test_name": "Temperature", "result": 38.9, "unit": "°C", "evidence": "Internal capacitor temp 38.9 °C"},
                {"test_name": "Patient Leakage Current", "result": 0.02, "unit": "mA", "evidence": "Patient auxiliary leakage 0.02 mA"},
                {"test_name": "Defibrillation Energy Accuracy", "result": 3.5, "unit": "%", "evidence": "Output energy error 3.5% at 360J"},
                {"test_name": "Maximum Charge Time", "result": 6.2, "unit": "s", "evidence": "Capacitor charge time to max energy 6.2s (limit <= 15.0s)"},
                {"test_name": "Internal Auto-discharge", "result": 1.1, "unit": "s", "evidence": "Safety discharge time 1.1s (limit <= 2.0s)"},
                {"test_name": "EMC Immunity", "result": "PASS", "evidence": "Surge immunity test satisfied"},
                {"test_name": "Alarm Priority", "result": "PASS", "evidence": "Ready for shock audio indicator 75 dBA"},
                {"test_name": "Usability Engineering", "result": "PASS", "evidence": "AED rescue user flow usability complete"},
                {"test_name": "Risk Management", "result": "PASS", "evidence": "High energy discharge hazard file verified"},
                {"test_name": "Software Lifecycle", "result": "PASS", "evidence": "Shock delivery firmware verification complete"},
                {"test_name": "Label Verification", "result": "COMPLETE", "evidence": "Paddle energy rating & CE mark verified"}
            ]
        },
        {
            "cat_key": "Pulse Oximeter",
            "model": "PO-50",
            "mfr": "OptiPulse Healthcare",
            "serial": "SN-PO-501",
            "report_num": "TRF-2026-PO08",
            "expected_outcome": "PASS",
            "tests": [
                {"test_name": "Leakage Current", "result": 0.15, "unit": "mA", "evidence": "Normal condition leakage 0.15 mA"},
                {"test_name": "Insulation Resistance", "result": 110.0, "unit": "MΩ", "evidence": "Primary insulation 110 MΩ"},
                {"test_name": "Dielectric Strength", "result": "PASS", "unit": "-", "evidence": "2500V isolation barrier check satisfied"},
                {"test_name": "Temperature", "result": 39.1, "unit": "°C", "evidence": "Optical probe surface temp 39.1 °C (limit <= 41.0 °C)"},
                {"test_name": "Patient Leakage Current", "result": 0.01, "unit": "mA", "evidence": "Patient probe leakage 0.01 mA"},
                {"test_name": "SpO2 Measurement Accuracy", "result": 1.2, "unit": "%", "evidence": "RMS SpO2 accuracy deviation 1.2% per ISO 80601-2-61"},
                {"test_name": "Pulse Rate Measurement Accuracy", "result": 1.5, "unit": "bpm", "evidence": "Pulse rate accuracy 1.5 bpm"},
                {"test_name": "EMC Immunity", "result": "PASS", "evidence": "8kV ESD air discharge satisfied"},
                {"test_name": "Alarm Priority", "result": "PASS", "evidence": "Desaturation alarm signal 70 dBA"},
                {"test_name": "Usability Engineering", "result": "PASS", "evidence": "Probe attachment usability file complete"},
                {"test_name": "Risk Management", "result": "PASS", "evidence": "ISO 14971 risk management file verified"},
                {"test_name": "Software Lifecycle", "result": "PASS", "evidence": "Oximetry signal processing software verified"},
                {"test_name": "Label Verification", "result": "COMPLETE", "evidence": "Optical probe rating label present"}
            ]
        },
        {
            "cat_key": "Electrosurgical Unit",
            "model": "ESU-400",
            "mfr": "SurgeTech Electrosurgery",
            "serial": "SN-ESU-4089",
            "report_num": "TRF-2026-ESU09",
            "expected_outcome": "FAIL",
            "tests": [
                {"test_name": "Leakage Current", "result": 0.35, "unit": "mA", "evidence": "Low frequency mains leakage 0.35 mA"},
                {"test_name": "Insulation Resistance", "result": 60.0, "unit": "MΩ", "evidence": "Primary insulation 60 MΩ"},
                {"test_name": "Dielectric Strength", "result": "PASS", "unit": "-", "evidence": "3500V generator high voltage check satisfied"},
                {"test_name": "Temperature", "result": 44.0, "unit": "°C", "evidence": "Heatsink surface temp 44.0 °C"},
                {"test_name": "High Frequency Leakage Current", "result": 195.0, "unit": "mA", "evidence": "RF leakage at active electrode 195 mA - EXCEEDS LIMIT (<= 150 mA)"},
                {"test_name": "CQM Neutral Plate Interlock", "result": "PASS", "evidence": "Split return plate alarm interlock verified per IEC 60601-2-2"},
                {"test_name": "RF Output Power Limit", "result": 380.0, "unit": "W", "evidence": "Maximum RF output power 380 W at 500 ohms"},
                {"test_name": "EMC Immunity", "result": "PASS", "evidence": "Class A RF radiated emissions satisfied"},
                {"test_name": "Alarm Priority", "result": "PASS", "evidence": "Neutral electrode fault alarm 80 dBA"},
                {"test_name": "Usability Engineering", "result": "PASS", "evidence": "Surgical foot pedal ergonomics file verified"},
                {"test_name": "Risk Management", "result": "PASS", "evidence": "High frequency burn hazard file verified"},
                {"test_name": "Software Lifecycle", "result": "PASS", "evidence": "Generator control software verified"},
                {"test_name": "Label Verification", "result": "COMPLETE", "evidence": "High frequency warning plate present"}
            ]
        },
        {
            "cat_key": "X-Ray Diagnostic Equipment",
            "model": "XR-500",
            "mfr": "Radiance Imaging Corp",
            "serial": "SN-XR-5001",
            "report_num": "TRF-2026-XR10",
            "expected_outcome": "NEEDS REVIEW",
            "tests": [
                {"test_name": "Leakage Current", "result": 0.38, "unit": "mA", "evidence": "Generator cabinet earth leakage 0.38 mA"},
                {"test_name": "Insulation Resistance", "result": 140.0, "unit": "MΩ", "evidence": "Generator insulation 140 MΩ"},
                {"test_name": "Dielectric Strength", "result": "PASS", "unit": "-", "evidence": "100kV high voltage generator tank check satisfied"},
                {"test_name": "Temperature", "result": 48.0, "unit": "°C", "evidence": "Anode thermal capacity temp 48.0 °C"},
                {"test_name": "Radiation Collimation", "result": "PASS", "evidence": "Automatic light beam diaphragm collimation checked per IEC 60601-1-3"},
                {"test_name": "Tube Voltage Accuracy", "result": 2.4, "unit": "%", "evidence": "kVp output accuracy 2.4% across 80-120 kV range"},
                {"test_name": "Exposure Time Error", "result": 1.1, "unit": "%", "evidence": "Exposure timer reproducibility check 1.1%"},
                {"test_name": "Leakage Radiation", "result": "UNRECORDED", "evidence": "Stray radiation measurement data missing in section 4"},
                {"test_name": "EMC Immunity", "result": "PASS", "evidence": "Class A electromagnetic compatibility satisfied"},
                {"test_name": "Alarm Priority", "result": "PASS", "evidence": "X-Ray exposure active audible warning 78 dBA"},
                {"test_name": "Usability Engineering", "result": "PASS", "evidence": "Operator console ergonomics complete"},
                {"test_name": "Risk Management", "result": "PASS", "evidence": "Diagnostic radiation risk index complete"},
                {"test_name": "Software Lifecycle", "result": "PASS", "evidence": "Exposure control system verification complete"},
                {"test_name": "Label Verification", "result": "COMPLETE", "evidence": "Ionizing radiation warning sign present"}
            ]
        },
        {
            "cat_key": "Ultrasound Diagnostic Equipment",
            "model": "US-300",
            "mfr": "SonoVision Systems",
            "serial": "SN-US-3009",
            "report_num": "TRF-2026-US11",
            "expected_outcome": "PASS",
            "tests": [
                {"test_name": "Leakage Current", "result": 0.18, "unit": "mA", "evidence": "Console leakage current 0.18 mA"},
                {"test_name": "Insulation Resistance", "result": 180.0, "unit": "MΩ", "evidence": "Console insulation 180 MΩ"},
                {"test_name": "Dielectric Strength", "result": "PASS", "unit": "-", "evidence": "3000V transducer isolation barrier check"},
                {"test_name": "Temperature", "result": 38.5, "unit": "°C", "evidence": "Transducer face temperature steady state 38.5 °C"},
                {"test_name": "Patient Leakage Current", "result": 0.01, "unit": "mA", "evidence": "Patient probe leakage 0.01 mA"},
                {"test_name": "Acoustic Mechanical Index", "result": 1.2, "unit": "-", "evidence": "Peak acoustic MI 1.2 (limit <= 1.9) per IEC 60601-2-37"},
                {"test_name": "Acoustic Thermal Index", "result": 2.1, "unit": "-", "evidence": "Doppler mode TI 2.1 (limit <= 6.0)"},
                {"test_name": "High Voltage Pulse Stability", "result": 1.5, "unit": "%", "evidence": "Transducer drive voltage stability 1.5%"},
                {"test_name": "EMC Immunity", "result": "PASS", "evidence": "8kV ESD & RF susceptibility satisfied"},
                {"test_name": "Alarm Priority", "result": "PASS", "evidence": "Thermal index limit audio warning 72 dBA"},
                {"test_name": "Usability Engineering", "result": "PASS", "evidence": "Sonographer console usability file verified"},
                {"test_name": "Risk Management", "result": "PASS", "evidence": "Acoustic output risk management file complete"},
                {"test_name": "Software Lifecycle", "result": "PASS", "evidence": "Ultrasound image processing firmware verified"},
                {"test_name": "Label Verification", "result": "COMPLETE", "evidence": "Acoustic rating plate & CE label present"}
            ]
        },
        {
            "cat_key": "Surgical Operating Table",
            "model": "OT-700",
            "mfr": "SurgeTech Operating Systems",
            "serial": "SN-OT-7005",
            "report_num": "TRF-2026-OT12",
            "expected_outcome": "PASS",
            "tests": [
                {"test_name": "Leakage Current", "result": 0.28, "unit": "mA", "evidence": "Hydraulic pump motor leakage 0.28 mA"},
                {"test_name": "Insulation Resistance", "result": 150.0, "unit": "MΩ", "evidence": "Power supply insulation resistance 150 MΩ"},
                {"test_name": "Dielectric Strength", "result": "PASS", "unit": "-", "evidence": "2000V high voltage motor insulation check"},
                {"test_name": "Temperature", "result": 41.0, "unit": "°C", "evidence": "Hydraulic oil reservoir temp 41.0 °C"},
                {"test_name": "Safe Working Load Capacity", "result": 300.0, "unit": "kg", "evidence": "Static load test 300 kg satisfied per IEC 60601-2-46 (limit >= 220 kg)"},
                {"test_name": "Emergency Brake Release", "result": "PASS", "evidence": "Manual emergency foot lever verified"},
                {"test_name": "Table Articulation Locking", "result": "PASS", "evidence": "100% mechanical lock under full load"},
                {"test_name": "Anti-Tip Stability Margin", "result": 15.0, "unit": "deg", "evidence": "Anti-tip static margin 15.0 deg incline"},
                {"test_name": "EMC Immunity", "result": "PASS", "evidence": "Motor drive EMC immunity satisfied"},
                {"test_name": "Alarm Priority", "result": "PASS", "evidence": "Battery disconnect warning signal active"},
                {"test_name": "Usability Engineering", "result": "PASS", "evidence": "Surgical team positioning usability file verified"},
                {"test_name": "Risk Management", "result": "PASS", "evidence": "Patient fall risk analysis verified"},
                {"test_name": "Software Lifecycle", "result": "PASS", "evidence": "Articulation motor control software verified"},
                {"test_name": "Label Verification", "result": "COMPLETE", "evidence": "Rating plate & CE/FDA markings present"}
            ]
        },
        {
            "cat_key": "Medical Examination / Treatment Light",
            "model": "SL-100",
            "mfr": "LumiMed Lighting Tech",
            "serial": "SN-SL-1002",
            "report_num": "TRF-2026-SL13",
            "expected_outcome": "PASS",
            "tests": [
                {"test_name": "Leakage Current", "result": 0.12, "unit": "mA", "evidence": "Luminaire head leakage 0.12 mA"},
                {"test_name": "Insulation Resistance", "result": 200.0, "unit": "MΩ", "evidence": "Transformer insulation test 200 MΩ"},
                {"test_name": "Dielectric Strength", "result": "PASS", "unit": "-", "evidence": "2500V arm mechanism wire insulation check"},
                {"test_name": "Temperature", "result": 42.0, "unit": "°C", "evidence": "Lamp enclosure surface temp 42.0 °C"},
                {"test_name": "Central Illuminance Lux", "result": 120000.0, "unit": "Lux", "evidence": "Measured at 1m focal distance 120000 Lux per IEC 60601-2-41 (40000 - 160000 Lux)"},
                {"test_name": "Total Light Irradiance", "result": 450.0, "unit": "W/m²", "evidence": "Infrared heat radiation 450 W/m² (limit <= 1000 W/m²)"},
                {"test_name": "Color Rendering Index Ra", "result": 96.0, "unit": "-", "evidence": "Color rendering index Ra 96 (limit >= 85)"},
                {"test_name": "EMC Immunity", "result": "PASS", "evidence": "LED driver EMC emissions Class B satisfied"},
                {"test_name": "Usability Engineering", "result": "PASS", "evidence": "Surgical field light positioning usability complete"},
                {"test_name": "Risk Management", "result": "PASS", "evidence": "Photobiological hazard analysis verified"},
                {"test_name": "Software Lifecycle", "result": "PASS", "evidence": "Dimming controller firmware verification complete"},
                {"test_name": "Label Verification", "result": "COMPLETE", "evidence": "Safety warning label & CE mark verified"}
            ]
        },
        {
            "cat_key": "Medical Laboratory / Diagnostic Electrical Equipment",
            "model": "LA-500",
            "mfr": "BioLab Analyzer Systems",
            "serial": "SN-LA-5001",
            "report_num": "TRF-2026-LA14",
            "expected_outcome": "PASS",
            "tests": [
                {"test_name": "Lab Mains Insulation", "result": 45.0, "unit": "MΩ", "evidence": "IEC 61010 laboratory insulation test 45 MΩ (limit >= 20 MΩ)"},
                {"test_name": "Enclosure Safety", "result": "PASS", "evidence": "Finger probe mechanical safety checked per IEC 61010-1"},
                {"test_name": "Thermal Cutoff", "result": 42.0, "unit": "°C", "evidence": "Maximum component temp 42.0 °C (limit <= 55 °C)"},
                {"test_name": "Sample Splash Guard", "result": "PASS", "evidence": "IVD specimen biological containment verified per IEC 61010-2-101"},
                {"test_name": "Reagent Storage Temp", "result": 4.5, "unit": "°C", "evidence": "Reagent carousel temp 4.5 °C (range 2.0 - 8.0 °C)"},
                {"test_name": "Sample Pipetting Volume Accuracy", "result": 0.8, "unit": "%", "evidence": "Pipetting volume accuracy 0.8% (limit <= 2.0%)"},
                {"test_name": "EMC Immunity", "result": "PASS", "evidence": "Lab analyzer EMC immunity satisfied per IEC 61326-2-6"},
                {"test_name": "Alarm Priority", "result": "PASS", "evidence": "Reagent low & error audio tone 70 dBA"},
                {"test_name": "Usability Engineering", "result": "PASS", "evidence": "Lab technician user workflow validated"},
                {"test_name": "Risk Management", "result": "PASS", "evidence": "Biohazard risk management file complete"},
                {"test_name": "Software Lifecycle", "result": "PASS", "evidence": "Analyzer processing software Class B verified"},
                {"test_name": "Label Verification", "result": "COMPLETE", "evidence": "Biological hazard label & rating plate present"}
            ]
        },
        {
            "cat_key": "Medical Electrical Therapy Equipment",
            "model": "TH-300",
            "mfr": "NeuroPulse Therapy Inc",
            "serial": "SN-TH-3004",
            "report_num": "TRF-2026-TH15",
            "expected_outcome": "FAIL",
            "tests": [
                {"test_name": "Leakage Current", "result": 0.22, "unit": "mA", "evidence": "Earth leakage test 0.22 mA"},
                {"test_name": "Insulation Resistance", "result": 90.0, "unit": "MΩ", "evidence": "Primary insulation 90 MΩ"},
                {"test_name": "Dielectric Strength", "result": "PASS", "unit": "-", "evidence": "3000V output isolation check satisfied"},
                {"test_name": "Temperature", "result": 38.0, "unit": "°C", "evidence": "Electrode pad surface temp 38.0 °C"},
                {"test_name": "Patient Leakage Current", "result": 0.02, "unit": "mA", "evidence": "Patient auxiliary leakage 0.02 mA"},
                {"test_name": "Stimulus Current Amplitude", "result": 65.0, "unit": "mA", "evidence": "Pulse amplitude 65 mA per IEC 60601-2-10 (limit <= 80 mA)"},
                {"test_name": "DC Current Offset", "result": 0.45, "unit": "mA", "evidence": "Direct current offset 0.45 mA - EXCEEDS SAFETY LIMIT (<= 0.10 mA)"},
                {"test_name": "Pulse Duration Accuracy", "result": 2.0, "unit": "%", "evidence": "Pulse duration accuracy 2.0%"},
                {"test_name": "EMC Immunity", "result": "PASS", "evidence": "8kV ESD air discharge satisfied"},
                {"test_name": "Alarm Priority", "result": "PASS", "evidence": "Electrode disconnect audio warning 72 dBA"},
                {"test_name": "Usability Engineering", "result": "PASS", "evidence": "Patient electrode placement usability verified"},
                {"test_name": "Risk Management", "result": "PASS", "evidence": "Tissue burn & direct current risk file verified"},
                {"test_name": "Software Lifecycle", "result": "PASS", "evidence": "Stimulation pulse control firmware verified"},
                {"test_name": "Label Verification", "result": "COMPLETE", "evidence": "High voltage output warning plate present"}
            ]
        }
    ]

    # Delete existing sample evaluations to avoid duplicates
    db.query(EvaluationResult).delete()
    db.query(Evaluation).delete()
    db.query(UploadedDocument).delete()
    db.commit()

    for idx, sc in enumerate(demo_scenarios, start=1):
        cat_key = sc["cat_key"]
        cat_info = DEVICE_CATEGORIES_MAPPING[cat_key]
        model = sc["model"]
        mfr = sc["mfr"]
        serial = sc["serial"]
        report_num = sc["report_num"]
        tests_data = sc["tests"]

        filename = f"demo_TRF_{idx:02d}_{cat_key.replace(' ', '_').replace('/', '_')}.pdf"
        file_path = os.path.join(sample_dir, filename)
        upload_path = os.path.join(upload_dir, filename)

        # Construct Normalized TRF Schema
        tests_schemas = []
        for t in tests_data:
            tests_schemas.append(ExtractedTestSchema(
                test_name=t["test_name"],
                result=t["result"],
                unit=t.get("unit"),
                evidence=t.get("evidence")
            ))

        norm_trf = NormalizedTRFSchema(
            device=DeviceInfoSchema(
                name=cat_info['name'],
                model=model,
                manufacturer=mfr,
                device_type=cat_key,
                serial_number=serial,
                test_date="2026-08-28"
            ),
            standards=[ExtractedStandardSchema(name=cat_info['particular_standard'], edition="Demo")],
            tests=tests_schemas,
            raw_notes=f"Synthetic TRF report {report_num} for {cat_info['name']}"
        )

        # Create UploadedDocument DB Record
        up_doc = UploadedDocument(
            filename=filename,
            file_type="pdf",
            file_path=upload_path,
            processing_status="EVALUATED",
            extracted_data_json=norm_trf.model_dump_json()
        )
        db.add(up_doc)
        db.commit()
        db.refresh(up_doc)

        # Run Evaluation Engine
        overall_status, item_results, counts, meta = EvaluationEngine.evaluate_trf(db, norm_trf)

        # Generate Instant Fast AI Summary Schema for Seeding
        failed_items = [t["test_name"] for t in tests_data if t.get("result") == "FAIL" or "EXCEEDS" in str(t.get("evidence", ""))]
        review_items = [t["test_name"] for t in tests_data if t.get("result") == "UNRECORDED" or "MISSING" in str(t.get("evidence", ""))]
        passed_count = len(tests_data) - len(failed_items) - len(review_items)
        
        ai_summary_obj = AISummarySchema(
            summary=f"The {cat_info['name']} (Model: {model}) evaluation completed with status: {overall_status}. "
                    f"A total of {len(tests_data)} test parameters were evaluated against standard {cat_info['particular_standard']}.",
            key_findings=[
                f"Device: {cat_info['name']} (Model: {model})",
                f"Applicable Standard: {cat_info['particular_standard']}",
                f"Passed Tests: {passed_count}",
                f"Failed Parameters: {len(failed_items)}",
                f"Items Requiring Technical Review: {len(review_items)}"
            ],
            failed_items=failed_items,
            review_items=review_items,
            recommendation="Technical reviewer / certifier inspection required prior to final regulatory determination."
        )

        batch_id = f"BATCH-DEMO-{idx:02d}"

        # Assign realistic demonstration certifier statuses
        if idx in [1, 3, 5, 7, 11]:
            c_status = "APPROVED"
            c_notes = "Evaluation certified & signed off for compliance filing by Senior Certifier."
        elif idx in [8, 14]:
            c_status = "NEEDS_MORE_INFO"
            c_notes = "Certifier requested additional laboratory oscilloscope waveforms and environmental calibration records."
        elif idx in [12]:
            c_status = "REJECTED"
            c_notes = "Returned to technical reviewer due to unaddressed safety limit violation in section 3."
        else:
            c_status = "PENDING_REVIEW"
            c_notes = "Awaiting final certifier review and sign-off."

        # Insert Evaluation Record
        eval_rec = Evaluation(
            batch_id=batch_id,
            document_id=up_doc.id,
            overall_status=overall_status,
            total_tests=counts.get("total_tests", 0),
            passed_tests=counts.get("passed_tests", 0),
            failed_tests=counts.get("failed_tests", 0),
            needs_review_tests=counts.get("needs_review_tests", 0),
            not_applicable_tests=counts.get("not_applicable_tests", 0),
            device_type_name=cat_key,
            device_model=model,
            manufacturer=mfr,
            pathway=cat_info["pathway"],
            ai_summary=ai_summary_obj.model_dump_json(),
            certifier_status=c_status,
            certifier_notes=c_notes
        )
        db.add(eval_rec)
        db.commit()
        db.refresh(eval_rec)

        # Insert EvaluationResult Records
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

    print("Successfully seeded 15 synthetic medical device TRFs and evaluations into SQLite database.")


def generate_sample_pdf_by_filename(filename: str) -> str:
    sample_dir = settings.SAMPLE_DIR
    os.makedirs(sample_dir, exist_ok=True)
    file_path = os.path.join(sample_dir, filename)
    
    # Check matching scenario from demo_scenarios
    sc = None
    for idx, s in enumerate(demo_scenarios, start=1):
        cat_k = s["cat_key"]
        expected_fn = f"demo_TRF_{idx:02d}_{cat_k.replace(' ', '_').replace('/', '_')}.pdf"
        if expected_fn == filename or filename.replace(".pdf", "") in expected_fn:
            sc = s
            break

    if not sc:
        sc = demo_scenarios[0]

    cat_key = sc["cat_key"]
    cat_info = DEVICE_CATEGORIES_MAPPING[cat_key]
    model = sc["model"]
    mfr = sc["mfr"]
    serial = sc["serial"]
    report_num = sc["report_num"]
    tests_data = sc["tests"]

    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'DocTitle', parent=styles['Heading1'], fontSize=18, leading=22, textColor=colors.HexColor("#0f172a"), spaceAfter=4
        )
        subtitle_style = ParagraphStyle(
            'DocSubtitle', parent=styles['Normal'], fontSize=9, leading=13, textColor=colors.HexColor("#0284c7"), spaceAfter=10
        )
        disclaimer_style = ParagraphStyle(
            'Disclaimer', parent=styles['Normal'], fontSize=8, leading=11, textColor=colors.HexColor("#b91c1c"), spaceBefore=6, spaceAfter=8
        )
        section_heading = ParagraphStyle(
            'SectionHeading', parent=styles['Heading2'], fontSize=11, leading=15, textColor=colors.HexColor("#0f172a"), spaceBefore=10, spaceAfter=6
        )

        doc = SimpleDocTemplate(file_path, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        story = []

        story.append(Paragraph(f"TEST REPORT FORM (TRF) — {cat_info['name'].upper()}", title_style))
        story.append(Paragraph(f"Report No: {report_num}  |  Pathway: {cat_info['pathway']}  |  Standard: {cat_info['particular_standard']}", subtitle_style))
        story.append(Paragraph("⚠️ DEMONSTRATION DOCUMENT — SYNTHETIC DATA — NOT FOR CERTIFICATION USE", disclaimer_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=10))

        story.append(Paragraph("1. Device & Test Laboratory Specifications", section_heading))
        meta_rows = [
            ["Device Name:", cat_info['name'], "Model Number:", model],
            ["Manufacturer:", mfr, "Serial Number:", serial],
            ["Device Category:", cat_key, "Report Number:", report_num],
            ["Safety Pathway:", cat_info['pathway'], "Test Date:", "2026-08-28"]
        ]
        t_meta = Table(meta_rows, colWidths=[110, 160, 110, 160])
        t_meta.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 8.5),
            ('TEXTCOLOR', (0,0), (0,-1), colors.HexColor("#475569")),
            ('TEXTCOLOR', (2,0), (2,-1), colors.HexColor("#475569")),
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))
        story.append(t_meta)
        story.append(Spacer(1, 10))

        story.append(Paragraph("2. Laboratory Test Results & Evidence", section_heading))
        t_rows = [["Test Parameter", "Measured Result", "Unit", "Technician Observation / Evidence"]]
        for t in tests_data:
            t_rows.append([
                t["test_name"],
                str(t["result"]),
                t.get("unit", "-"),
                t.get("evidence", "Recorded")
            ])
        
        t_tests = Table(t_rows, colWidths=[140, 95, 55, 250])
        t_tests.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f5f9")),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8.5),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ('PADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(t_tests)
        doc.build(story)
    except Exception as e:
        print(f"Error generating sample PDF {filename}: {e}")

    return file_path


if __name__ == "__main__":
    db = SessionLocal()
    seed_database(db)

