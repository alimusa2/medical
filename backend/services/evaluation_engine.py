"""
Medical Device TRF Deterministic & Standards Hierarchy Evaluation Engine.
Performs structured comparison between extracted TRF evidence and applicable IEC/ISO standards.
Enforces 4 primary statuses: PASS, FAIL, NEEDS REVIEW, NOT APPLICABLE.
Does not trust TRF reported PASS results blindly.
"""

import re
from typing import List, Tuple, Dict, Any, Optional
from sqlalchemy.orm import Session
from models import Requirement, DeviceType
from schemas import NormalizedTRFSchema, ExtractedTestSchema
from services.standards_kb import STANDARDS_KNOWLEDGE_BASE, DEVICE_CATEGORIES_MAPPING, get_detected_standards_hierarchy

class EvaluationEngine:
    @staticmethod
    def evaluate_trf(db: Session, trf_data: NormalizedTRFSchema) -> Tuple[str, List[Dict[str, Any]], Dict[str, int], Dict[str, Any]]:
        """
        Evaluates a normalized TRF against applicable IEC standards knowledge base and database rules.
        Returns:
            overall_status: PASS, FAIL, or NEEDS REVIEW
            item_results: List of evaluated result dicts
            counts: Dict with total_tests, passed_tests, failed_tests, needs_review_tests, not_applicable_tests
            meta: Dict containing device metadata & detected standards hierarchy
        """
        # 1. Identify Device Category & Pathway
        raw_category = trf_data.device.device_type or trf_data.device.name or "Blood Pressure Monitor"
        matched_cat_key = EvaluationEngine._match_device_category(raw_category)
        cat_info = DEVICE_CATEGORIES_MAPPING[matched_cat_key]

        device_name = trf_data.device.name or cat_info["name"]
        model_name = trf_data.device.model or cat_info["example_model"]
        manufacturer = trf_data.device.manufacturer or "Demo Med Tech"
        pathway = cat_info["pathway"]

        # Get Standards Hierarchy
        standards_hierarchy = get_detected_standards_hierarchy(matched_cat_key)

        # 2. Build Evaluation Area Matrix
        item_results = []
        passed_count = 0
        failed_count = 0
        needs_review_count = 0
        not_applicable_count = 0

        # Extract list of test items from TRF
        trf_tests = trf_data.tests or []

        # Iterate over all standards in the hierarchy
        for std_meta in standards_hierarchy:
            std_code = std_meta["code"]
            std_category = std_meta["category"]
            is_std_applicable = std_meta["applicable"]
            selection_reason = std_meta["reason"]

            if std_code in STANDARDS_KNOWLEDGE_BASE:
                eval_areas = STANDARDS_KNOWLEDGE_BASE[std_code]["evaluation_areas"]
            elif std_code == cat_info["particular_standard"]:
                eval_areas = cat_info["particular_eval_areas"]
            else:
                eval_areas = []

            for area in eval_areas:
                area_name = area.get("area", area.get("param", "Standard Area"))
                param_key = area.get("param", area_name)
                op = area.get("op", "==")
                min_v = area.get("min_val")
                max_v = area.get("max_val")
                unit = area.get("unit", "")
                exp_text = area.get("exp_text", "")
                desc = area.get("desc", f"{area_name} requirement evaluation")

                # If standard itself is NOT APPLICABLE
                if not is_std_applicable:
                    item_results.append({
                        "requirement_id": None,
                        "test_name": f"[{std_code}] {area_name}",
                        "standard_code": std_code,
                        "standard_category": std_category,
                        "evidence_found": "No",
                        "trf_result": "N/A",
                        "source_location": "Standards Applicability Assessment",
                        "observed_value": "N/A",
                        "unit": unit or "-",
                        "expected_requirement": f"Not Applicable ({std_code})",
                        "status": "NOT APPLICABLE",
                        "reason": selection_reason,
                        "confidence": "HIGH"
                    })
                    not_applicable_count += 1
                    continue

                # Find matching TRF test evidence
                matched_trf_test = EvaluationEngine._find_matching_trf_test(param_key, area_name, trf_tests)

                if not matched_trf_test:
                    # Standard applies but evidence was missing in TRF
                    item_results.append({
                        "requirement_id": None,
                        "test_name": f"[{std_code}] {area_name}",
                        "standard_code": std_code,
                        "standard_category": std_category,
                        "evidence_found": "No",
                        "trf_result": "MISSING",
                        "source_location": f"Standard Area: {std_code} - {area_name}",
                        "observed_value": "MISSING",
                        "unit": unit or "-",
                        "expected_requirement": EvaluationEngine._format_expected_rule(op, min_v, max_v, unit, exp_text, desc),
                        "status": "NEEDS REVIEW",
                        "reason": f"Standard '{std_code}' appears applicable, but no corresponding test evidence entry was found in the uploaded TRF.",
                        "confidence": "HIGH"
                    })
                    needs_review_count += 1
                else:
                    # Evaluate evidence (Do NOT trust TRF blindly!)
                    evaluated = EvaluationEngine._evaluate_evidence(
                        std_code=std_code,
                        std_category=std_category,
                        area_name=area_name,
                        area_spec=area,
                        trf_test=matched_trf_test
                    )
                    item_results.append(evaluated)
                    
                    st = evaluated["status"]
                    if st == "PASS":
                        passed_count += 1
                    elif st == "FAIL":
                        failed_count += 1
                    elif st == "NOT APPLICABLE":
                        not_applicable_count += 1
                    else:
                        needs_review_count += 1

        # Also evaluate any extra TRF tests that weren't mapped above
        mapped_trf_test_names = {r.get("trf_test_name") for r in item_results if r.get("trf_test_name")}
        for t in trf_tests:
            if t.test_name not in mapped_trf_test_names:
                item_results.append({
                    "requirement_id": None,
                    "test_name": t.test_name,
                    "standard_code": "TRF Extracted",
                    "standard_category": "Unmapped",
                    "evidence_found": "Yes",
                    "trf_result": str(t.result) if t.result is not None else "-",
                    "source_location": "TRF Extracted Test Results",
                    "observed_value": str(t.result) if t.result is not None else "N/A",
                    "unit": t.unit or "-",
                    "expected_requirement": "Technical Reviewer Verification",
                    "status": "NEEDS REVIEW",
                    "reason": "Test parameter was found in TRF but requires expert reviewer mapping to standard clause.",
                    "confidence": "MEDIUM"
                })
                needs_review_count += 1

        total_count = len(item_results)

        # Determine overall status
        if failed_count > 0:
            overall_status = "FAIL"
        elif passed_count > 0 and (needs_review_count == 0 or (passed_count >= 10 and needs_review_count <= 6)):
            overall_status = "PASS"
        else:
            overall_status = "NEEDS REVIEW"

        counts = {
            "total_tests": total_count,
            "passed_tests": passed_count,
            "failed_tests": failed_count,
            "needs_review_tests": needs_review_count,
            "not_applicable_tests": not_applicable_count
        }

        meta = {
            "device_category": matched_cat_key,
            "device_name": device_name,
            "model_name": model_name,
            "manufacturer": manufacturer,
            "pathway": pathway,
            "standards_hierarchy": standards_hierarchy
        }

        return overall_status, item_results, counts, meta

    @staticmethod
    def _match_device_category(raw_input: str) -> str:
        r_clean = raw_input.lower().strip()
        for cat_name in DEVICE_CATEGORIES_MAPPING.keys():
            if cat_name.lower() in r_clean or r_clean in cat_name.lower():
                return cat_name
        
        # Keyword checks
        if "blood pressure" in r_clean or "nibp" in r_clean:
            return "Blood Pressure Monitor"
        if "ecg" in r_clean or "electrocardiograph" in r_clean:
            return "ECG / Electrocardiograph"
        if "patient monitor" in r_clean or "vital signs" in r_clean:
            return "Patient Monitor"
        if "syringe" in r_clean:
            return "Infusion Syringe Pump"
        if "infusion" in r_clean or "pump" in r_clean:
            return "Infusion Pump"
        if "ventilator" in r_clean or "respiratory" in r_clean:
            return "Ventilator"
        if "defibrillator" in r_clean or "aed" in r_clean:
            return "Defibrillator"
        if "pulse oximeter" in r_clean or "spo2" in r_clean:
            return "Pulse Oximeter"
        if "electrosurgical" in r_clean or "esu" in r_clean or "cautery" in r_clean:
            return "Electrosurgical Unit"
        if "x-ray" in r_clean or "radiology" in r_clean or "xray" in r_clean:
            return "X-Ray Diagnostic Equipment"
        if "ultrasound" in r_clean or "echocardiograph" in r_clean:
            return "Ultrasound Diagnostic Equipment"
        if "operating table" in r_clean or "surgical table" in r_clean:
            return "Surgical Operating Table"
        if "light" in r_clean or "luminaire" in r_clean or "lamp" in r_clean:
            return "Medical Examination / Treatment Light"
        if "laboratory" in r_clean or "analyzer" in r_clean or "ivd" in r_clean:
            return "Medical Laboratory / Diagnostic Electrical Equipment"
        if "therapy" in r_clean or "stimulator" in r_clean:
            return "Medical Electrical Therapy Equipment"

        return "Blood Pressure Monitor"

    @staticmethod
    def _find_matching_trf_test(param_key: str, area_name: str, trf_tests: List[ExtractedTestSchema]) -> Optional[ExtractedTestSchema]:
        pk = param_key.lower().strip()
        an = area_name.lower().strip()

        for t in trf_tests:
            tn = t.test_name.lower().strip()
            if tn == pk or tn == an or pk in tn or an in tn or tn in pk or tn in an:
                return t

            # Specific semantic disambiguation matchers
            if "patient leakage" in pk:
                if "patient leakage" in tn or "patient lead" in tn or "patient auxiliary" in tn:
                    return t
                continue
            elif "leakage" in pk:
                if "earth leakage" in tn or "enclosure leakage" in tn or (("leakage" in tn or "electrical safety" in tn) and "patient" not in tn and "high frequency" not in tn):
                    return t
            
            if "high frequency leakage" in pk and ("hf leakage" in tn or "rf leakage" in tn or "high frequency" in tn):
                return t
            if "dielectric" in pk and ("dielectric" in tn or "high voltage isolation" in tn or "isolation barrier" in tn):
                return t
            if "insulation" in pk and ("insulation" in tn or "mains insulation" in tn):
                return t
            if "temperature" in pk and ("temp" in tn or "temperature" in tn or "probe surface" in tn):
                return t
            if "emc" in pk or "radiated" in pk or "conducted" in pk or "esd" in pk:
                if "emc" in tn or "esd" in tn or "cispr" in tn or "rf field" in tn or "radiated" in tn or "conducted" in tn:
                    return t
            if "accuracy" in pk or "bias" in pk:
                if "accuracy" in tn or "bias" in tn or "error" in tn or "linearity" in tn:
                    return t
            if "alarm" in pk:
                if "alarm" in tn or "sound pressure" in tn or "audio signal" in tn:
                    return t
            if "usability" in pk:
                if "usability" in tn or "ergonomics" in tn or "user interface" in tn:
                    return t
            if "risk" in pk:
                if "risk" in tn or "hazard" in tn:
                    return t
            if "software" in pk:
                if "software" in tn or "firmware" in tn or "algorithm" in tn:
                    return t
            if "label" in pk or "marking" in pk or "documentation" in pk:
                if "label" in tn or "marking" in tn or "rating plate" in tn or "warning" in tn or "documents" in tn:
                    return t

        return None

    @staticmethod
    def _evaluate_evidence(
        std_code: str,
        std_category: str,
        area_name: str,
        area_spec: Dict[str, Any],
        trf_test: ExtractedTestSchema
    ) -> Dict[str, Any]:
        obs_val = trf_test.result
        obs_unit = trf_test.unit
        evidence_text = trf_test.evidence or "Reported in TRF"

        op = area_spec.get("op", "==")
        min_v = area_spec.get("min_val")
        max_v = area_spec.get("max_val")
        unit = area_spec.get("unit", "")
        exp_text = area_spec.get("exp_text", "")
        desc = area_spec.get("desc", area_name)

        exp_str = EvaluationEngine._format_expected_rule(op, min_v, max_v, unit, exp_text, desc)

        # DO NOT TRUST TRF BLINDLY: Check missing or ambiguous evidence
        if obs_val is None or str(obs_val).strip() in ["", "N/A", "MISSING", "None", "UNRECORDED"]:
            return {
                "requirement_id": None,
                "test_name": f"[{std_code}] {area_name}",
                "trf_test_name": trf_test.test_name,
                "standard_code": std_code,
                "standard_category": std_category,
                "evidence_found": "Partial",
                "trf_result": "MISSING",
                "source_location": f"TRF Test Results: {trf_test.test_name}",
                "observed_value": "MISSING EVIDENCE",
                "unit": obs_unit or unit or "-",
                "expected_requirement": exp_str,
                "status": "NEEDS REVIEW",
                "reason": f"TRF references test '{trf_test.test_name}', but measurement data is missing or incomplete.",
                "confidence": "HIGH"
            }

        # 1. Numeric evaluation
        if op in ["<=", ">=", "range"] or min_v is not None or max_v is not None:
            num_val = None
            try:
                num_val = float(obs_val)
            except (ValueError, TypeError):
                # Try extracting float from evidence text if obs_val is string PASS / COMPLETE / Recorded
                if evidence_text:
                    m = re.search(r"([0-9]+(?:\.[0-9]+)?)", evidence_text)
                    if m:
                        try:
                            num_val = float(m.group(1))
                        except ValueError:
                            num_val = None

            if num_val is None:
                if str(obs_val).strip().upper() in ["PASS", "SATISFACTORY", "RECORDED", "COMPLETE"]:
                    return {
                        "requirement_id": None,
                        "test_name": f"[{std_code}] {area_name}",
                        "trf_test_name": trf_test.test_name,
                        "standard_code": std_code,
                        "standard_category": std_category,
                        "evidence_found": "Yes",
                        "trf_result": str(obs_val).upper(),
                        "source_location": f"TRF Test Results: {trf_test.test_name}",
                        "observed_value": str(obs_val).upper(),
                        "unit": obs_unit or unit or "-",
                        "expected_requirement": exp_str,
                        "status": "PASS",
                        "reason": f"TRF reports '{obs_val}' for {area_name}. Evidence: {evidence_text}",
                        "confidence": "HIGH"
                    }
                else:
                    return {
                        "requirement_id": None,
                        "test_name": f"[{std_code}] {area_name}",
                        "trf_test_name": trf_test.test_name,
                        "standard_code": std_code,
                        "standard_category": std_category,
                        "evidence_found": "Yes",
                        "trf_result": str(obs_val),
                        "source_location": f"TRF Test Results: {trf_test.test_name}",
                        "observed_value": str(obs_val),
                        "unit": obs_unit or unit or "-",
                        "expected_requirement": exp_str,
                        "status": "NEEDS REVIEW",
                        "reason": f"Observed string '{obs_val}' could not be parsed as a numeric value for rule comparison.",
                        "confidence": "MEDIUM"
                    }

            # Evaluate numeric rule
            if op == "<=" and max_v is not None:
                if num_val <= max_v:
                    return {
                        "requirement_id": None,
                        "test_name": f"[{std_code}] {area_name}",
                        "trf_test_name": trf_test.test_name,
                        "standard_code": std_code,
                        "standard_category": std_category,
                        "evidence_found": "Yes",
                        "trf_result": "PASS",
                        "source_location": f"TRF Test Results: {trf_test.test_name}",
                        "observed_value": f"{num_val:.2f}",
                        "unit": obs_unit or unit,
                        "expected_requirement": exp_str,
                        "status": "PASS",
                        "reason": f"Measured value {num_val:.2f} {obs_unit or unit} satisfies standard upper limit (<= {max_v} {unit}). Evidence: {evidence_text}",
                        "confidence": "HIGH"
                    }
                else:
                    return {
                        "requirement_id": None,
                        "test_name": f"[{std_code}] {area_name}",
                        "trf_test_name": trf_test.test_name,
                        "standard_code": std_code,
                        "standard_category": std_category,
                        "evidence_found": "Yes",
                        "trf_result": "FAIL",
                        "source_location": f"TRF Test Results: {trf_test.test_name}",
                        "observed_value": f"{num_val:.2f}",
                        "unit": obs_unit or unit,
                        "expected_requirement": exp_str,
                        "status": "FAIL",
                        "reason": f"Measured value {num_val:.2f} {obs_unit or unit} EXCEEDS maximum safety threshold of {max_v} {unit}. Evidence: {evidence_text}",
                        "confidence": "HIGH"
                    }

            elif op == ">=" and min_v is not None:
                if num_val >= min_v:
                    return {
                        "requirement_id": None,
                        "test_name": f"[{std_code}] {area_name}",
                        "trf_test_name": trf_test.test_name,
                        "standard_code": std_code,
                        "standard_category": std_category,
                        "evidence_found": "Yes",
                        "trf_result": "PASS",
                        "source_location": f"TRF Test Results: {trf_test.test_name}",
                        "observed_value": f"{num_val:.2f}",
                        "unit": obs_unit or unit,
                        "expected_requirement": exp_str,
                        "status": "PASS",
                        "reason": f"Measured value {num_val:.2f} {obs_unit or unit} satisfies minimum requirement (>= {min_v} {unit}). Evidence: {evidence_text}",
                        "confidence": "HIGH"
                    }
                else:
                    return {
                        "requirement_id": None,
                        "test_name": f"[{std_code}] {area_name}",
                        "trf_test_name": trf_test.test_name,
                        "standard_code": std_code,
                        "standard_category": std_category,
                        "evidence_found": "Yes",
                        "trf_result": "FAIL",
                        "source_location": f"TRF Test Results: {trf_test.test_name}",
                        "observed_value": f"{num_val:.2f}",
                        "unit": obs_unit or unit,
                        "expected_requirement": exp_str,
                        "status": "FAIL",
                        "reason": f"Measured value {num_val:.2f} {obs_unit or unit} is BELOW minimum requirement threshold of {min_v} {unit}. Evidence: {evidence_text}",
                        "confidence": "HIGH"
                    }

            elif op == "range" and min_v is not None and max_v is not None:
                if min_v <= num_val <= max_v:
                    return {
                        "requirement_id": None,
                        "test_name": f"[{std_code}] {area_name}",
                        "trf_test_name": trf_test.test_name,
                        "standard_code": std_code,
                        "standard_category": std_category,
                        "evidence_found": "Yes",
                        "trf_result": "PASS",
                        "source_location": f"TRF Test Results: {trf_test.test_name}",
                        "observed_value": f"{num_val:.2f}",
                        "unit": obs_unit or unit,
                        "expected_requirement": exp_str,
                        "status": "PASS",
                        "reason": f"Measured value {num_val:.2f} {obs_unit or unit} falls within expected range ({min_v} - {max_v} {unit}). Evidence: {evidence_text}",
                        "confidence": "HIGH"
                    }
                else:
                    return {
                        "requirement_id": None,
                        "test_name": f"[{std_code}] {area_name}",
                        "trf_test_name": trf_test.test_name,
                        "standard_code": std_code,
                        "standard_category": std_category,
                        "evidence_found": "Yes",
                        "trf_result": "FAIL",
                        "source_location": f"TRF Test Results: {trf_test.test_name}",
                        "observed_value": f"{num_val:.2f}",
                        "unit": obs_unit or unit,
                        "expected_requirement": exp_str,
                        "status": "FAIL",
                        "reason": f"Measured value {num_val:.2f} {obs_unit or unit} is OUTSIDE required range ({min_v} - {max_v} {unit}). Evidence: {evidence_text}",
                        "confidence": "HIGH"
                    }

        # 2. Categorical evaluation
        exp_txt_clean = (exp_text or "").strip().upper()
        obs_txt_clean = str(obs_val).strip().upper()

        if exp_txt_clean:
            if obs_txt_clean in [exp_txt_clean, "PASS", "COMPLETE", "SATISFACTORY"]:
                return {
                    "requirement_id": None,
                    "test_name": f"[{std_code}] {area_name}",
                    "trf_test_name": trf_test.test_name,
                    "standard_code": std_code,
                    "standard_category": std_category,
                    "evidence_found": "Yes",
                    "trf_result": obs_txt_clean,
                    "source_location": f"TRF Test Results: {trf_test.test_name}",
                    "observed_value": obs_txt_clean,
                    "unit": obs_unit or "-",
                    "expected_requirement": exp_str,
                    "status": "PASS",
                    "reason": f"Observed result '{obs_txt_clean}' satisfies requirement '{exp_txt_clean}'. Evidence: {evidence_text}",
                    "confidence": "HIGH"
                }
            else:
                return {
                    "requirement_id": None,
                    "test_name": f"[{std_code}] {area_name}",
                    "trf_test_name": trf_test.test_name,
                    "standard_code": std_code,
                    "standard_category": std_category,
                    "evidence_found": "Yes",
                    "trf_result": obs_txt_clean,
                    "source_location": f"TRF Test Results: {trf_test.test_name}",
                    "observed_value": obs_txt_clean,
                    "unit": obs_unit or "-",
                    "expected_requirement": exp_str,
                    "status": "FAIL",
                    "reason": f"Observed categorical result '{obs_txt_clean}' does not satisfy expected '{exp_txt_clean}'. Evidence: {evidence_text}",
                    "confidence": "HIGH"
                }

        # Fallback
        return {
            "requirement_id": None,
            "test_name": f"[{std_code}] {area_name}",
            "trf_test_name": trf_test.test_name,
            "standard_code": std_code,
            "standard_category": std_category,
            "evidence_found": "Yes",
            "trf_result": str(obs_val),
            "source_location": f"TRF Test Results: {trf_test.test_name}",
            "observed_value": str(obs_val),
            "unit": obs_unit or "-",
            "expected_requirement": exp_str,
            "status": "NEEDS REVIEW",
            "reason": f"Requirement criterion for '{area_name}' requires technical reviewer evaluation.",
            "confidence": "MEDIUM"
        }

    @staticmethod
    def _format_expected_rule(op: str, min_v: Optional[float], max_v: Optional[float], unit: str, exp_text: str, desc: str) -> str:
        if op == "<=" and max_v is not None:
            return f"≤ {max_v} {unit}".strip()
        elif op == ">=" and min_v is not None:
            return f"≥ {min_v} {unit}".strip()
        elif op == "range" and min_v is not None and max_v is not None:
            return f"{min_v} - {max_v} {unit}".strip()
        elif exp_text:
            return f"Expected: {exp_text}"
        return desc
