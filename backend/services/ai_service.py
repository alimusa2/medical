import json
import logging
from typing import Dict, Any, List
from groq import Groq
from config import settings
from schemas import AISummarySchema

logger = logging.getLogger(__name__)

class AIService:
    @staticmethod
    def _get_client() -> Groq:
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY environment variable is not configured.")
        return Groq(api_key=settings.GROQ_API_KEY, max_retries=0, timeout=5.0)

    @staticmethod
    def verify_groq_status() -> Dict[str, Any]:
        """Verify Groq API key and test connection to configured model."""
        if not settings.GROQ_API_KEY:
            return {
                "status": "error",
                "message": "GROQ_API_KEY is missing from environment variables.",
                "configured_model": settings.GROQ_MODEL,
                "is_available": False
            }

        try:
            client = AIService._get_client()
            models_res = client.models.list()
            available_model_ids = [m.id for m in models_res.data]
            
            target_model = settings.GROQ_MODEL
            is_present = target_model in available_model_ids
            
            return {
                "status": "ok" if is_present or len(available_model_ids) > 0 else "warning",
                "message": f"Connected to Groq API. Configured model: '{target_model}'",
                "configured_model": target_model,
                "is_available": True,
                "available_models": available_model_ids[:10]
            }
        except Exception as e:
            logger.warning(f"Groq API connection test failed: {e}")
            return {
                "status": "error",
                "message": f"Groq API connection failed: {str(e)}",
                "configured_model": settings.GROQ_MODEL,
                "is_available": False
            }

    @staticmethod
    def generate_evaluation_summary(
        device_name: str,
        model_name: str,
        standards_str: str,
        results_list: List[Dict[str, Any]],
        overall_status: str
    ) -> AISummarySchema:
        """
        Generates a professional evaluation summary using Groq LLM.
        Strictly relies on provided results and falls back cleanly on error.
        """
        failed_items = [r["test_name"] for r in results_list if r.get("status") == "FAIL"]
        review_items = [r["test_name"] for r in results_list if r.get("status") == "NEEDS REVIEW"]
        passed_items_count = len(results_list) - len(failed_items) - len(review_items)

        fallback_res = AISummarySchema(
            summary=f"The {device_name} (Model: {model_name}) evaluation completed with preliminary status: {overall_status}. "
                    f"A total of {len(results_list)} standard requirement areas were evaluated across applicable standards ({standards_str}).",
            key_findings=[
                f"Device: {device_name} (Model: {model_name})",
                f"Standards Pathway: {standards_str}",
                f"Passed Evaluation Areas: {passed_items_count}",
                f"Failed Parameters: {len(failed_items)}",
                f"Items Requiring Technical Review: {len(review_items)}"
            ],
            failed_items=failed_items,
            review_items=review_items,
            recommendation="Technical reviewer / certifier inspection required prior to final regulatory determination."
        )

        if not settings.GROQ_API_KEY:
            return fallback_res

        system_prompt = (
            "You are an evaluation-report drafting assistant for a medical device testing laboratory.\n"
            "CRITICAL CONSTRAINTS:\n"
            "1. You must ONLY use the supplied extracted test results and evaluation engine results.\n"
            "2. Do NOT invent standards or acceptance criteria.\n"
            "3. Do NOT change PASS/FAIL/NEEDS REVIEW results.\n"
            "4. You MUST return ONLY valid JSON matching this schema:\n"
            "{\n"
            '  "summary": "Executive summary paragraph",\n'
            '  "key_findings": ["finding 1", "finding 2"],\n'
            '  "failed_items": ["failed test 1"],\n'
            '  "review_items": ["review item 1"],\n'
            '  "recommendation": "Certifier recommendation"\n'
            "}"
        )

        user_prompt = (
            f"Device: {device_name}\n"
            f"Model: {model_name}\n"
            f"Standards: {standards_str}\n"
            f"Overall Status: {overall_status}\n"
            f"Evaluated Test Results:\n{json.dumps(results_list, indent=2)}\n\n"
            "Please generate the structured evaluation summary JSON."
        )

        try:
            client = AIService._get_client()
            response = client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            data = json.loads(content)
            return AISummarySchema(**data)

        except Exception as e:
            logger.warning(f"Groq LLM call failed: {e}. Falling back to deterministic summary.")
            return fallback_res
