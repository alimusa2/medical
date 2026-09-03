"""
Medical Device IEC Standards Knowledge Base & Device Category Evaluation Mapping Rules.
Provides prototype evaluation rules, standard hierarchies, and requirement areas
for 15 medical device categories without downloading or reproducing copyrighted standards.
"""

from typing import Dict, Any, List, Optional

# Structured Internal Knowledge Base for IEC & ISO Standards
STANDARDS_KNOWLEDGE_BASE: Dict[str, Dict[str, Any]] = {
    "IEC 60601-1": {
        "code": "IEC 60601-1",
        "title": "Medical electrical equipment - General requirements for basic safety and essential performance",
        "category": "General",
        "applies_to_pathway": "ME Equipment",
        "description": "General baseline standard for all medical electrical equipment.",
        "evaluation_areas": [
            {"area": "Electrical Safety", "param": "Leakage Current", "op": "<=", "max_val": 0.50, "unit": "mA", "desc": "Earth leakage current in normal condition"},
            {"area": "Insulation", "param": "Insulation Resistance", "op": ">=", "min_val": 50.0, "unit": "MΩ", "desc": "Mains supply insulation resistance"},
            {"area": "Dielectric Strength", "param": "Dielectric Strength", "op": ">=", "min_val": 1500.0, "unit": "V", "desc": "High voltage insulation breakdown test"},
            {"area": "Temperature", "param": "Temperature", "op": "<=", "max_val": 41.0, "unit": "°C", "desc": "Maximum enclosure surface temperature under steady state"},
            {"area": "Marking & Labeling", "param": "Label Verification", "op": "==", "exp_text": "COMPLETE", "desc": "Verification of safety warning labels, ratings plate, and symbols"},
            {"area": "Documentation", "param": "Accompanying Documents", "op": "==", "exp_text": "COMPLETE", "desc": "Review of instructions for use and technical description"}
        ]
    },
    "IEC 60601-1-2": {
        "code": "IEC 60601-1-2",
        "title": "Electromagnetic disturbances - Requirements and tests",
        "category": "Collateral",
        "applies_to_pathway": "ME Equipment",
        "description": "Collateral standard for electromagnetic compatibility (EMC emissions & immunity).",
        "evaluation_areas": [
            {"area": "EMC Emissions", "param": "EMC Emissions", "op": "==", "exp_text": "PASS", "desc": "Conducted and radiated radio-frequency emissions (CISPR 11 Class B)"},
            {"area": "Radiated Immunity", "param": "Radiated Immunity", "op": "==", "exp_text": "PASS", "desc": "RF electromagnetic field immunity check (80 MHz - 2.7 GHz)"},
            {"area": "Conducted Immunity", "param": "Conducted Immunity", "op": "==", "exp_text": "PASS", "desc": "Immunity to conducted disturbances induced by RF fields"},
            {"area": "Electrostatic Discharge", "param": "ESD Immunity", "op": "==", "exp_text": "PASS", "desc": "Electrostatic discharge immunity (±8kV contact / ±15kV air)"}
        ]
    },
    "IEC 60601-1-6": {
        "code": "IEC 60601-1-6",
        "title": "Usability - General requirements for basic safety and essential performance",
        "category": "Collateral",
        "applies_to_pathway": "ME Equipment",
        "description": "Collateral standard evaluating usability engineering process.",
        "evaluation_areas": [
            {"area": "Usability Engineering Process", "param": "Usability Evaluation", "op": "==", "exp_text": "COMPLETE", "desc": "Verification of usability engineering file and user interface specification"}
        ]
    },
    "IEC 60601-1-8": {
        "code": "IEC 60601-1-8",
        "title": "Alarm systems - General requirements, tests and guidance in medical electrical equipment",
        "category": "Collateral",
        "applies_to_pathway": "ME Equipment (Alarm Capable)",
        "description": "Collateral standard covering alarm priorities, visual indications, and auditory alarm signals.",
        "evaluation_areas": [
            {"area": "Alarm Priority & Indication", "param": "Alarm Priority", "op": "==", "exp_text": "PASS", "desc": "High/medium/low priority alarm categorization and visual indicator check"},
            {"area": "Alarm Signal Sound Pressure", "param": "Alarm Sound Level", "op": "range", "min_val": 45.0, "max_val": 85.0, "unit": "dBA", "desc": "Auditory alarm signal sound pressure level check"},
            {"area": "Alarm Delay & Silence", "param": "Alarm Silence Control", "op": "==", "exp_text": "PASS", "desc": "Temporary alarm mute and reset control mechanism"}
        ]
    },
    "IEC 60601-1-3": {
        "code": "IEC 60601-1-3",
        "title": "Radiation protection in diagnostic X-ray equipment",
        "category": "Collateral",
        "applies_to_pathway": "Radiology Equipment",
        "description": "Collateral standard for radiation protection and shielding in X-ray systems.",
        "evaluation_areas": [
            {"area": "Beam Limitation", "param": "Radiation Collimation", "op": "==", "exp_text": "PASS", "desc": "X-ray beam alignment and automatic collimation check"},
            {"area": "Stray Radiation Shielding", "param": "Leakage Radiation", "op": "<=", "max_val": 1.0, "unit": "mGy/h", "desc": "Stray leakage radiation measurement at 1 meter distance"}
        ]
    },
    "IEC 61010-1": {
        "code": "IEC 61010-1",
        "title": "Safety requirements for electrical equipment for measurement, control, and laboratory use",
        "category": "General",
        "applies_to_pathway": "IVD / Laboratory Equipment",
        "description": "General baseline safety standard for laboratory diagnostic electrical equipment (Non-ME Scope).",
        "evaluation_areas": [
            {"area": "Mains Insulation", "param": "Lab Mains Insulation", "op": ">=", "min_val": 20.0, "unit": "MΩ", "desc": "Mains electrical insulation for laboratory equipment"},
            {"area": "Enclosure Protection", "param": "Enclosure Safety", "op": "==", "exp_text": "PASS", "desc": "Mechanical impact and finger probe enclosure test"},
            {"area": "Over-temperature Protection", "param": "Thermal Cutoff", "op": "<=", "max_val": 55.0, "unit": "°C", "desc": "Maximum internal component temperature limit"}
        ]
    },
    "IEC 61010-2-101": {
        "code": "IEC 61010-2-101",
        "title": "Particular requirements for in vitro diagnostic (IVD) medical equipment",
        "category": "Particular",
        "applies_to_pathway": "IVD / Laboratory Equipment",
        "description": "Particular standard for IVD laboratory analyzers.",
        "evaluation_areas": [
            {"area": "Biohazard Containment", "param": "Sample Spill Isolation", "op": "==", "exp_text": "PASS", "desc": "Biological specimen containment and fluid splash guard verification"},
            {"area": "Reagent Rotor Temperature", "param": "Reagent Storage Temp", "op": "range", "min_val": 2.0, "max_val": 8.0, "unit": "°C", "desc": "Reagent carousel temperature control verification"}
        ]
    },
    "ISO 14971": {
        "code": "ISO 14971",
        "title": "Medical devices - Application of risk management to medical devices",
        "category": "Related",
        "applies_to_pathway": "All Medical Devices",
        "description": "Risk management process standard. TRF provides partial risk mitigation evidence.",
        "evaluation_areas": [
            {"area": "Risk Management File", "param": "Risk Analysis Report", "op": "==", "exp_text": "COMPLETE", "desc": "Verification of risk hazard analysis and risk control implementation"}
        ]
    },
    "IEC 62366-1": {
        "code": "IEC 62366-1",
        "title": "Medical devices - Application of usability engineering to medical devices",
        "category": "Related",
        "applies_to_pathway": "All Medical Devices",
        "description": "Usability engineering process standard.",
        "evaluation_areas": [
            {"area": "Usability Engineering", "param": "Usability Validation", "op": "==", "exp_text": "PASS", "desc": "Validation of use errors and user interface safety"}
        ]
    },
    "IEC 62304": {
        "code": "IEC 62304",
        "title": "Medical device software - Software life cycle processes",
        "category": "Related",
        "applies_to_pathway": "Software Devices",
        "description": "Software lifecycle standard for devices containing firmware/software.",
        "evaluation_areas": [
            {"area": "Software Lifecycle", "param": "Software Verification", "op": "==", "exp_text": "PASS", "desc": "Software architecture documentation and unit test coverage"}
        ]
    }
}

# 15 Medical Device Category Mappings with Standard Hierarchy & Selection Reasoning
DEVICE_CATEGORIES_MAPPING: Dict[str, Dict[str, Any]] = {
    "Blood Pressure Monitor": {
        "name": "Non-invasive Blood Pressure Monitor",
        "example_model": "BP-100",
        "pathway": "ME Equipment",
        "has_alarms": False,
        "is_radiology": False,
        "has_software": True,
        "particular_standard": "IEC 60601-2-30",
        "particular_title": "Particular requirements for basic safety and essential performance of automated non-invasive sphygmomanometers",
        "particular_selection_reason": "Device identified as an automated non-invasive blood pressure monitor.",
        "particular_eval_areas": [
            {"area": "BP Accuracy Test", "param": "BP Measurement Bias", "op": "<=", "max_val": 3.0, "unit": "mmHg", "desc": "Overall blood pressure measurement accuracy deviation against reference cuff"},
            {"area": "Overpressure Cutoff", "param": "Overpressure Safety Cutoff", "op": "<=", "max_val": 300.0, "unit": "mmHg", "desc": "Maximum pneumatic pressure relief safety cutoff mechanism"},
            {"area": "Inflation Deflation Cycle", "param": "Functional Test", "op": "==", "exp_text": "PASS", "desc": "Cuff automatic inflation and controlled deflation rate verification"}
        ]
    },
    "ECG / Electrocardiograph": {
        "name": "12-lead ECG Machine",
        "example_model": "ECG-1200",
        "pathway": "ME Equipment",
        "has_alarms": False,
        "is_radiology": False,
        "has_software": True,
        "particular_standard": "IEC 60601-2-25",
        "particular_title": "Particular requirements for the basic safety and essential performance of electrocardiographs",
        "particular_selection_reason": "Device identified as a diagnostic 12-lead electrocardiograph (ECG).",
        "particular_eval_areas": [
            {"area": "Patient Lead Auxiliary Current", "param": "Patient Leakage Current", "op": "<=", "max_val": 0.05, "unit": "mA", "desc": "Direct current through applied ECG leads to patient"},
            {"area": "Defibrillation Protection", "param": "Defibrillator Discharge Test", "op": "==", "exp_text": "PASS", "desc": "Recovery and insulation protection after 5kV defibrillator discharge pulse"},
            {"area": "Frequency Response", "param": "ECG Frequency Bandwidth", "op": ">=", "min_val": 150.0, "unit": "Hz", "desc": "Frequency response bandwidth for diagnostic ECG waveform accuracy"}
        ]
    },
    "Patient Monitor": {
        "name": "Multiparameter Patient Monitor",
        "example_model": "PM-800",
        "pathway": "ME Equipment",
        "has_alarms": True,
        "is_radiology": False,
        "has_software": True,
        "particular_standard": "IEC 60601-2-49",
        "particular_title": "Particular requirements for basic safety and essential performance of multifunction patient monitoring equipment",
        "particular_selection_reason": "Device identified as a multiparameter vital signs monitor.",
        "particular_eval_areas": [
            {"area": "Multi-parameter Isolation", "param": "Channel Isolation", "op": ">=", "min_val": 4000.0, "unit": "V", "desc": "Electrical isolation between ECG, NIBP, and SpO2 applied channels"},
            {"area": "Display Refresh Rate", "param": "Waveform Display Latency", "op": "<=", "max_val": 100.0, "unit": "ms", "desc": "Real-time waveform sweep delay on monitor screen"}
        ]
    },
    "Infusion Pump": {
        "name": "Infusion Pump",
        "example_model": "IP-500",
        "pathway": "ME Equipment",
        "has_alarms": True,
        "is_radiology": False,
        "has_software": True,
        "particular_standard": "IEC 60601-2-24",
        "particular_title": "Particular requirements for basic safety and essential performance of infusion pumps and controllers",
        "particular_selection_reason": "Device identified as a volumetric infusion pump.",
        "particular_eval_areas": [
            {"area": "Flow Rate Accuracy", "param": "Flow Delivery Accuracy", "op": "<=", "max_val": 5.0, "unit": "%", "desc": "Percentage error of volumetric fluid infusion rate"},
            {"area": "Occlusion Pressure Alarm", "param": "Occlusion Pressure Limit", "op": "<=", "max_val": 100.0, "unit": "kPa", "desc": "Maximum downstream fluid occlusion pressure before alarm activation"},
            {"area": "Air-in-line Sensor", "param": "Air Bubble Detection", "op": "<=", "max_val": 50.0, "unit": "µL", "desc": "Minimum ultrasonic air bubble size trigger limit"}
        ]
    },
    "Infusion Syringe Pump": {
        "name": "Syringe Pump",
        "example_model": "SP-200",
        "pathway": "ME Equipment",
        "has_alarms": True,
        "is_radiology": False,
        "has_software": True,
        "particular_standard": "IEC 60601-2-24",
        "particular_title": "Particular requirements for basic safety and essential performance of infusion pumps (Syringe subtype)",
        "particular_selection_reason": "Device identified as a syringe driver infusion pump.",
        "particular_eval_areas": [
            {"area": "Syringe Barrel Size Detection", "param": "Syringe Barrel Fit Test", "op": "==", "exp_text": "PASS", "desc": "Automatic optical or mechanical syringe size recognition check"},
            {"area": "Bolus Delivery Accuracy", "param": "Bolus Volume Error", "op": "<=", "max_val": 3.0, "unit": "%", "desc": "Accuracy of high-rate bolus volume administration"}
        ]
    },
    "Ventilator": {
        "name": "Critical Care Ventilator",
        "example_model": "V-900",
        "pathway": "ME Equipment",
        "has_alarms": True,
        "is_radiology": False,
        "has_software": True,
        "particular_standard": "IEC 60601-2-12",
        "particular_title": "Particular requirements for basic safety and essential performance of critical care ventilators",
        "particular_selection_reason": "Device identified as a critical care respiratory ventilator.",
        "particular_eval_areas": [
            {"area": "Tidal Volume Delivery", "param": "Tidal Volume Accuracy", "op": "<=", "max_val": 7.5, "unit": "%", "desc": "Target volume delivery tolerance during mandatory ventilation"},
            {"area": "Maximum Airway Pressure Cutoff", "param": "Max Airway Pressure", "op": "<=", "max_val": 60.0, "unit": "cmH2O", "desc": "High airway pressure mechanical relief valve limit"},
            {"area": "Battery Backup Duration", "param": "Battery Backup Operating Time", "op": ">=", "min_val": 60.0, "unit": "min", "desc": "Internal emergency battery operating time under standard load"}
        ]
    },
    "Defibrillator": {
        "name": "External Defibrillator",
        "example_model": "DEF-700",
        "pathway": "ME Equipment",
        "has_alarms": True,
        "is_radiology": False,
        "has_software": True,
        "particular_standard": "IEC 60601-2-4",
        "particular_title": "Particular requirements for basic safety and essential performance of cardiac defibrillators",
        "particular_selection_reason": "Device identified as an external cardiac defibrillator / AED.",
        "particular_eval_areas": [
            {"area": "Delivered Energy Accuracy", "param": "Defibrillation Energy Accuracy", "op": "<=", "max_val": 15.0, "unit": "%", "desc": "Energy output error across 50 ohm test load at 360 Joules"},
            {"area": "Capacitor Charge Time", "param": "Maximum Charge Time", "op": "<=", "max_val": 10.0, "unit": "s", "desc": "Time taken to charge high-voltage storage capacitor to maximum energy"},
            {"area": "Internal Safety Discharge", "param": "Internal Auto-discharge", "op": "<=", "max_val": 2.0, "unit": "s", "desc": "Automatic internal discharge of stored energy when disarmed"}
        ]
    },
    "Pulse Oximeter": {
        "name": "Pulse Oximeter",
        "example_model": "PO-50",
        "pathway": "ME Equipment",
        "has_alarms": False,
        "is_radiology": False,
        "has_software": True,
        "particular_standard": "ISO 80601-2-61",
        "particular_title": "Particular requirements for basic safety and essential performance of pulse oximeter equipment",
        "particular_selection_reason": "Device identified as a pulse oximeter for SpO2 monitoring.",
        "particular_eval_areas": [
            {"area": "SpO2 Accuracy Arms", "param": "SpO2 Measurement Accuracy", "op": "<=", "max_val": 2.0, "unit": "%", "desc": "Root mean square error of oxygen saturation (SpO2 70%-100%)"},
            {"area": "Probe Thermal Safety", "param": "Probe Surface Temperature", "op": "<=", "max_val": 41.0, "unit": "°C", "desc": "Maximum contact surface temperature of optical SpO2 sensor probe"}
        ]
    },
    "Electrosurgical Unit": {
        "name": "Electrosurgical Generator",
        "example_model": "ESU-400",
        "pathway": "ME Equipment",
        "has_alarms": False,
        "is_radiology": False,
        "has_software": True,
        "particular_standard": "IEC 60601-2-2",
        "particular_title": "Particular requirements for basic safety and essential performance of high frequency surgical equipment and high frequency surgical accessories",
        "particular_selection_reason": "Device identified as a high-frequency electrosurgical generator (ESU).",
        "particular_eval_areas": [
            {"area": "HF Leakage Current", "param": "High Frequency Leakage Current", "op": "<=", "max_val": 150.0, "unit": "mA", "desc": "RF leakage current from active electrode to earth at 500 kHz"},
            {"area": "Neutral Electrode Monitor", "param": "CQM Neutral Plate Interlock", "op": "==", "exp_text": "PASS", "desc": "Contact quality monitoring interlock for split return plate"},
            {"area": "Max Power Output Test", "param": "RF Output Power Limit", "op": "<=", "max_val": 400.0, "unit": "W", "desc": "Maximum continuous RF power output across nominal load"}
        ]
    },
    "X-Ray Diagnostic Equipment": {
        "name": "Diagnostic X-Ray System",
        "example_model": "XR-500",
        "pathway": "ME Equipment",
        "has_alarms": False,
        "is_radiology": True,
        "has_software": True,
        "particular_standard": "IEC 60601-2-54",
        "particular_title": "Particular requirements for basic safety and essential performance of X-ray equipment for radiography and radioscopy",
        "particular_selection_reason": "Device identified as a diagnostic radiography X-ray system.",
        "particular_eval_areas": [
            {"area": "Tube Peak Voltage (kVp)", "param": "Tube Voltage Accuracy", "op": "<=", "max_val": 5.0, "unit": "%", "desc": "Accuracy of generated X-ray tube high voltage (kVp)"},
            {"area": "Exposure Timer Reproducibility", "param": "Exposure Time Error", "op": "<=", "max_val": 2.0, "unit": "%", "desc": "Timer exposure reproducibility across repeated exposures"}
        ]
    },
    "Ultrasound Diagnostic Equipment": {
        "name": "Diagnostic Ultrasound System",
        "example_model": "US-300",
        "pathway": "ME Equipment",
        "has_alarms": False,
        "is_radiology": False,
        "has_software": True,
        "particular_standard": "IEC 60601-2-37",
        "particular_title": "Particular requirements for basic safety and essential performance of ultrasonic medical diagnostic and monitoring equipment",
        "particular_selection_reason": "Device identified as a diagnostic ultrasound imaging system.",
        "particular_eval_areas": [
            {"area": "Mechanical Index (MI)", "param": "Acoustic Mechanical Index", "op": "<=", "max_val": 1.9, "unit": "-", "desc": "Peak acoustic pressure mechanical index limit for cavitation safety"},
            {"area": "Thermal Index (TI)", "param": "Acoustic Thermal Index", "op": "<=", "max_val": 6.0, "unit": "-", "desc": "Tissue thermal heating index limit during Doppler mode"}
        ]
    },
    "Surgical Operating Table": {
        "name": "Electrically Operated Operating Table",
        "example_model": "OT-700",
        "pathway": "ME Equipment",
        "has_alarms": False,
        "is_radiology": False,
        "has_software": False,
        "particular_standard": "IEC 60601-2-46",
        "particular_title": "Particular requirements for basic safety and essential performance of operating tables",
        "particular_selection_reason": "Device identified as an electrically powered operating table.",
        "particular_eval_areas": [
            {"area": "Safe Working Load", "param": "Safe Working Load Capacity", "op": ">=", "min_val": 250.0, "unit": "kg", "desc": "Static load test on extended table section"},
            {"area": "Emergency Mechanical Braking", "param": "Emergency Brake Release", "op": "==", "exp_text": "PASS", "desc": "Manual hydraulic or mechanical override release check"}
        ]
    },
    "Medical Examination / Treatment Light": {
        "name": "Surgical / Examination Light",
        "example_model": "SL-100",
        "pathway": "ME Equipment",
        "has_alarms": False,
        "is_radiology": False,
        "has_software": False,
        "particular_standard": "IEC 60601-2-41",
        "particular_title": "Particular requirements for basic safety and essential performance of surgical luminaires and luminaires for diagnosis",
        "particular_selection_reason": "Device identified as a surgical or diagnostic luminaire.",
        "particular_eval_areas": [
            {"area": "Central Illuminance", "param": "Central Illuminance Lux", "op": "range", "min_val": 40000.0, "max_val": 160000.0, "unit": "Lux", "desc": "Light intensity at 1 meter focal distance"},
            {"area": "Total Irradiance Limit", "param": "Total Light Irradiance", "op": "<=", "max_val": 1000.0, "unit": "W/m²", "desc": "Infrared thermal radiation limit on surgical field"}
        ]
    },
    "Medical Laboratory / Diagnostic Electrical Equipment": {
        "name": "Laboratory Diagnostic Analyzer",
        "example_model": "LA-500",
        "pathway": "IVD / Laboratory Equipment",
        "has_alarms": False,
        "is_radiology": False,
        "has_software": True,
        "particular_standard": "IEC 61010-2-101",
        "particular_title": "Particular requirements for in vitro diagnostic (IVD) medical equipment",
        "particular_selection_reason": "Device identified as an In-Vitro Diagnostic (IVD) laboratory analyzer. Evaluated under IEC 61010 laboratory equipment safety pathway.",
        "particular_eval_areas": [
            {"area": "Sample Pipette Accuracy", "param": "Pipette Aspiration Volume", "op": "<=", "max_val": 1.5, "unit": "%", "desc": "Precision of micro-volume reagent aspirator"},
            {"area": "Incubation Block Stability", "param": "Incubator Temperature Stability", "op": "range", "min_val": 36.5, "max_val": 37.5, "unit": "°C", "desc": "Reaction chamber temperature control"}
        ]
    },
    "Medical Electrical Therapy Equipment": {
        "name": "Physiotherapy / Therapeutic Electrical Equipment",
        "example_model": "TH-300",
        "pathway": "ME Equipment",
        "has_alarms": False,
        "is_radiology": False,
        "has_software": True,
        "particular_standard": "IEC 60601-2-10",
        "particular_title": "Particular requirements for basic safety and essential performance of nerve and muscle stimulators",
        "particular_selection_reason": "Device identified as a therapeutic nerve and muscle electrical stimulator.",
        "particular_eval_areas": [
            {"area": "Maximum Current Output", "param": "Stimulus Current Amplitude", "op": "<=", "max_val": 80.0, "unit": "mA", "desc": "Maximum output pulse current into 500 ohm load"},
            {"area": "DC Component Limit", "param": "DC Current Offset", "op": "<=", "max_val": 0.1, "unit": "mA", "desc": "Direct current offset limit to prevent skin tissue electrolysis"}
        ]
    }
}


def get_detected_standards_hierarchy(device_type: str) -> List[Dict[str, Any]]:
    """
    Constructs the detected standard hierarchy for a given device type,
    showing Level 1 (General), Level 2 (Collateral), Level 3 (Particular), and Level 4 (Related)
    with explicit applicability selection rationale.
    """
    info = DEVICE_CATEGORIES_MAPPING.get(device_type)
    if not info:
        # Fallback to Blood Pressure Monitor
        info = DEVICE_CATEGORIES_MAPPING["Blood Pressure Monitor"]

    hierarchy = []

    # 1. Level 1: General Standard
    if info["pathway"] == "IVD / Laboratory Equipment":
        gen_std = STANDARDS_KNOWLEDGE_BASE["IEC 61010-1"]
        hierarchy.append({
            "code": gen_std["code"],
            "title": gen_std["title"],
            "category": "General",
            "level": 1,
            "applicable": True,
            "reason": "General baseline safety standard for laboratory diagnostic electrical equipment (IVD Pathway)."
        })
        # Mark IEC 60601-1 as NOT APPLICABLE
        gen_60601 = STANDARDS_KNOWLEDGE_BASE["IEC 60601-1"]
        hierarchy.append({
            "code": gen_60601["code"],
            "title": gen_60601["title"],
            "category": "General",
            "level": 1,
            "applicable": False,
            "reason": "Not Applicable: Device is classified as IVD laboratory equipment and falls under the IEC 61010 scope."
        })
    else:
        gen_std = STANDARDS_KNOWLEDGE_BASE["IEC 60601-1"]
        hierarchy.append({
            "code": gen_std["code"],
            "title": gen_std["title"],
            "category": "General",
            "level": 1,
            "applicable": True,
            "reason": "General baseline standard for basic safety and essential performance of medical electrical equipment."
        })

    # 2. Level 2: Collateral Standards
    if info["pathway"] == "ME Equipment":
        # EMC
        emc_std = STANDARDS_KNOWLEDGE_BASE["IEC 60601-1-2"]
        hierarchy.append({
            "code": emc_std["code"],
            "title": emc_std["title"],
            "category": "Collateral",
            "level": 2,
            "applicable": True,
            "reason": "Electrical medical equipment contains electronic circuits subject to EMC evaluation."
        })
        # Usability
        usa_std = STANDARDS_KNOWLEDGE_BASE["IEC 60601-1-6"]
        hierarchy.append({
            "code": usa_std["code"],
            "title": usa_std["title"],
            "category": "Collateral",
            "level": 2,
            "applicable": True,
            "reason": "Device features operator interface requiring usability engineering evaluation."
        })
        # Alarm Systems
        alarm_std = STANDARDS_KNOWLEDGE_BASE["IEC 60601-1-8"]
        if info["has_alarms"]:
            hierarchy.append({
                "code": alarm_std["code"],
                "title": alarm_std["title"],
                "category": "Collateral",
                "level": 2,
                "applicable": True,
                "reason": f"Device identified as {info['name']} with integrated alarm functionality."
            })
        else:
            hierarchy.append({
                "code": alarm_std["code"],
                "title": alarm_std["title"],
                "category": "Collateral",
                "level": 2,
                "applicable": False,
                "reason": "Not Applicable: No relevant patient alarm functionality detected for this equipment type."
            })
        # Radiation Protection
        rad_std = STANDARDS_KNOWLEDGE_BASE["IEC 60601-1-3"]
        if info["is_radiology"]:
            hierarchy.append({
                "code": rad_std["code"],
                "title": rad_std["title"],
                "category": "Collateral",
                "level": 2,
                "applicable": True,
                "reason": "Diagnostic X-ray radiology equipment producing ionizing radiation."
            })

    # 3. Level 3: Particular Standards
    part_code = info["particular_standard"]
    part_title = info["particular_title"]
    hierarchy.append({
        "code": part_code,
        "title": part_title,
        "category": "Particular",
        "level": 3,
        "applicable": True,
        "reason": info["particular_selection_reason"]
    })

    # 4. Level 4: Related Standards (ISO 14971, IEC 62366-1, IEC 62304)
    iso_risk = STANDARDS_KNOWLEDGE_BASE["ISO 14971"]
    hierarchy.append({
        "code": iso_risk["code"],
        "title": iso_risk["title"],
        "category": "Related",
        "level": 4,
        "applicable": True,
        "reason": "Related standard for medical device risk management file evaluation."
    })

    iec_usa_proc = STANDARDS_KNOWLEDGE_BASE["IEC 62366-1"]
    hierarchy.append({
        "code": iec_usa_proc["code"],
        "title": iec_usa_proc["title"],
        "category": "Related",
        "level": 4,
        "applicable": True,
        "reason": "Related standard for usability engineering process."
    })

    if info["has_software"]:
        iec_sw = STANDARDS_KNOWLEDGE_BASE["IEC 62304"]
        hierarchy.append({
            "code": iec_sw["code"],
            "title": iec_sw["title"],
            "category": "Related",
            "level": 4,
            "applicable": True,
            "reason": "Potentially applicable related standard for software / firmware lifecycle processes."
        })

    return hierarchy
