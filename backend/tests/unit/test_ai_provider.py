import pytest
from backend.models.enums import ConfidenceLevel
from backend.providers.ai.mock import MockAIProvider
from backend.services.ai_service import AIService
from backend.ai.triage_prompt import format_triage_user_prompt
from backend.ai.summary_prompt import format_summary_user_prompt
from backend.ai.draft_prompt import format_draft_user_prompt


def test_confidence_score_mapping():
    assert AIService._score_to_confidence_level(0.2) == ConfidenceLevel.LOW
    assert AIService._score_to_confidence_level(0.49) == ConfidenceLevel.LOW
    assert AIService._score_to_confidence_level(0.50) == ConfidenceLevel.MODERATE
    assert AIService._score_to_confidence_level(0.79) == ConfidenceLevel.MODERATE
    assert AIService._score_to_confidence_level(0.80) == ConfidenceLevel.HIGH
    assert AIService._score_to_confidence_level(1.0) == ConfidenceLevel.HIGH
    assert AIService._score_to_confidence_level(None) == ConfidenceLevel.MODERATE


@pytest.mark.asyncio
async def test_mock_ai_provider_triage():
    provider = MockAIProvider()
    dto = await provider.analyze_triage(
        title="VPN Connection failure and wifi drops",
        description="Cannot connect to corporate network from home",
        case_type="Incident",
    )
    assert dto is not None
    assert dto.suggested_category == "Network"
    assert dto.suggested_team == "Network Engineering"
    assert dto.confidence_score >= 0.8


@pytest.mark.asyncio
async def test_mock_ai_provider_summary_and_draft():
    provider = MockAIProvider()
    summary = await provider.generate_summary(
        case_title="Password Reset Request",
        case_description="Locked out of SAP",
        case_status="Assigned",
        messages_history=[{"visibility": "requester_visible", "body": "Please reset my account", "author_role": "Requester"}],
    )
    assert summary is not None
    assert "What was reported" in summary

    draft = await provider.generate_communication_draft(
        draft_type="info_request",
        case_title="Monitor flickering",
        case_description="Dell monitor flickers when connected via HDMI",
        messages_history=[],
    )
    assert draft is not None
    assert "Monitor flickering" in draft


@pytest.mark.asyncio
async def test_mock_ai_provider_failure_mode():
    provider = MockAIProvider(should_fail=True)
    assert await provider.analyze_triage("Title", "Desc", "Incident") is None
    assert await provider.generate_summary("Title", "Desc", "New", []) is None
    assert await provider.generate_communication_draft("info_request", "Title", "Desc", []) is None


def test_prompt_formatting():
    triage_prompt = format_triage_user_prompt("Printer jammed", "Tray 2 jammed", "Incident", "NYC HQ")
    assert "UNTRUSTED USER INPUT START" in triage_prompt
    assert "Printer jammed" in triage_prompt

    summary_prompt = format_summary_user_prompt("Issue", "Desc", "New", [])
    assert "TIMELINE OF MESSAGES" in summary_prompt

    draft_prompt = format_draft_user_prompt("resolution", "Issue", "Desc", [])
    assert "Draft Type: resolution" in draft_prompt
