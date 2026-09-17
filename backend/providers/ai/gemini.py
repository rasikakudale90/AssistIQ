import asyncio
import json
import logging
import re
import httpx

try:
    from google import genai
    from google.genai import types
    from google.genai.errors import APIError
    HAS_GENAI_SDK = True
except ImportError:
    genai = None
    types = None
    APIError = Exception
    HAS_GENAI_SDK = False

from backend.core.config import settings
from backend.providers.ai.base import AIProvider, TriageResultDTO
from backend.ai.triage_prompt import TRIAGE_SYSTEM_PROMPT, format_triage_user_prompt
from backend.ai.summary_prompt import SUMMARY_SYSTEM_PROMPT, format_summary_user_prompt
from backend.ai.draft_prompt import DRAFT_SYSTEM_PROMPT, format_draft_user_prompt

logger = logging.getLogger("assistiq.ai.gemini")


class GeminiAIProvider(AIProvider):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL
        self._client = None
        if self.api_key and HAS_GENAI_SDK and genai is not None:
            try:
                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Gemini SDK client: {e}")

    def _clean_json_text(self, text: str) -> str:
        """Strips markdown code fences if returned by model."""
        text = text.strip()
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if match:
            return match.group(1).strip()
        return text

    async def _call_gemini_with_retry(
        self,
        system_instruction: str,
        user_prompt: str,
        response_mime_type: Optional[str] = None,
    ) -> Optional[str]:
        """
        Executes a Gemini API call with 1 exponential backoff retry (base 1s) per SRS §7.14.
        Returns None if call fails or Gemini is unavailable (SRS §9 fallback).
        """
        if not self.api_key:
            logger.warning("Gemini AI API key not configured. Falling back to AI-unavailable state.")
            return None

        for attempt in range(2):  # Max 1 retry (2 attempts total)
            try:
                if self._client and types is not None:
                    config = types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.2,
                    )
                    if response_mime_type:
                        config.response_mime_type = response_mime_type

                    response = await asyncio.to_thread(
                        self._client.models.generate_content,
                        model=self.model,
                        contents=user_prompt,
                        config=config,
                    )
                    if response and response.text:
                        return response.text
                else:
                    # Direct REST API fallback via httpx
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
                    payload = {
                        "system_instruction": {"parts": [{"text": system_instruction}]},
                        "contents": [{"parts": [{"text": user_prompt}]}],
                        "generationConfig": {"temperature": 0.2},
                    }
                    if response_mime_type:
                        payload["generationConfig"]["response_mime_type"] = response_mime_type

                    async with httpx.AsyncClient(timeout=15.0) as http_client:
                        resp = await http_client.post(url, json=payload)
                        if resp.status_code == 200:
                            data = resp.json()
                            candidates = data.get("candidates", [])
                            if candidates and "content" in candidates[0]:
                                parts = candidates[0]["content"].get("parts", [])
                                if parts and "text" in parts[0]:
                                    return parts[0]["text"]
                        else:
                            logger.warning(f"Gemini REST API returned status {resp.status_code}: {resp.text[:200]}")
                return None
            except Exception as exc:
                logger.warning(f"Gemini API attempt {attempt + 1} failed: {exc}")
                if attempt == 0:
                    await asyncio.sleep(1.0)  # Exponential backoff 1s
                else:
                    logger.error(f"Gemini API call failed after 1 retry: {exc}. Gracefully returning None.")
                    return None
        return None

    async def analyze_triage(
        self,
        title: str,
        description: str,
        case_type: str,
        site: Optional[str] = None,
        service_id: Optional[str] = None,
    ) -> Optional[TriageResultDTO]:
        user_prompt = format_triage_user_prompt(
            title=title,
            description=description,
            case_type=case_type,
            site=site,
            service_id=service_id,
        )
        raw_output = await self._call_gemini_with_retry(
            system_instruction=TRIAGE_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_mime_type="application/json",
        )
        if not raw_output:
            return None

        try:
            cleaned = self._clean_json_text(raw_output)
            data = json.loads(cleaned)
            score = float(data.get("confidence_score", 0.5))
            score = max(0.0, min(1.0, score))

            return TriageResultDTO(
                suggested_category=data.get("suggested_category"),
                suggested_severity=data.get("suggested_severity"),
                suggested_priority=data.get("suggested_priority"),
                confidence_score=score,
                supporting_factors=data.get("supporting_factors", []),
                missing_info=data.get("missing_info", []),
                suggested_team=data.get("suggested_team"),
                recommended_next_action=data.get("recommended_next_action"),
            )
        except Exception as e:
            logger.error(f"Failed to parse Gemini triage JSON output: {e}. Raw: {raw_output[:200]}")
            return None

    async def generate_summary(
        self,
        case_title: str,
        case_description: str,
        case_status: str,
        messages_history: List[Dict[str, str]],
    ) -> Optional[str]:
        user_prompt = format_summary_user_prompt(
            case_title=case_title,
            case_description=case_description,
            case_status=case_status,
            messages_history=messages_history,
        )
        summary = await self._call_gemini_with_retry(
            system_instruction=SUMMARY_SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )
        return summary.strip() if summary else None

    async def generate_communication_draft(
        self,
        draft_type: str,
        case_title: str,
        case_description: str,
        messages_history: List[Dict[str, str]],
        custom_instructions: Optional[str] = None,
    ) -> Optional[str]:
        user_prompt = format_draft_user_prompt(
            draft_type=draft_type,
            case_title=case_title,
            case_description=case_description,
            messages_history=messages_history,
            custom_instructions=custom_instructions,
        )
        draft = await self._call_gemini_with_retry(
            system_instruction=DRAFT_SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )
        return draft.strip() if draft else None
