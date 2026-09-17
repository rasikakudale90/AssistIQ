import os
from typing import Optional
from backend.core.config import settings
from backend.providers.ai.base import AIProvider, TriageResultDTO
from backend.providers.ai.gemini import GeminiAIProvider
from backend.providers.ai.mock import MockAIProvider

_ai_provider_instance: Optional[AIProvider] = None


def get_ai_provider() -> AIProvider:
    global _ai_provider_instance
    if _ai_provider_instance is not None:
        return _ai_provider_instance

    # If in test mode or no Gemini API key provided, use MockAIProvider
    if os.getenv("TESTING", "").lower() in ["1", "true"] or not settings.GEMINI_API_KEY:
        _ai_provider_instance = MockAIProvider()
    else:
        _ai_provider_instance = GeminiAIProvider()

    return _ai_provider_instance


def set_ai_provider(provider: Optional[AIProvider]) -> None:
    global _ai_provider_instance
    _ai_provider_instance = provider


__all__ = [
    "AIProvider",
    "TriageResultDTO",
    "GeminiAIProvider",
    "MockAIProvider",
    "get_ai_provider",
    "set_ai_provider",
]
