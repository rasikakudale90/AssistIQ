from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TriageResultDTO(BaseModel):
    suggested_category: Optional[str] = None
    suggested_severity: Optional[str] = None
    suggested_priority: Optional[str] = None
    confidence_score: float = Field(default=0.5, ge=0.0, le=1.0)
    supporting_factors: List[str] = Field(default_factory=list)
    missing_info: List[str] = Field(default_factory=list)
    suggested_team: Optional[str] = None
    recommended_next_action: Optional[str] = None


class AIProvider(ABC):
    """
    Abstract base class for AI providers (e.g. Gemini, Mock for testing).
    Follows SRS §5 and AGENTS_AssistIQ.md §13-§16 (AI is an assistant, not an authority).
    """

    @abstractmethod
    async def analyze_triage(
        self,
        title: str,
        description: str,
        case_type: str,
        site: Optional[str] = None,
        service_id: Optional[str] = None,
    ) -> Optional[TriageResultDTO]:
        """
        Synchronous case triage returning suggested category, severity, priority,
        confidence score, missing information questions, suggested team, and recommended next action.
        Returns None if AI is unavailable (graceful fallback).
        """
        pass

    @abstractmethod
    async def generate_summary(
        self,
        case_title: str,
        case_description: str,
        case_status: str,
        messages_history: List[Dict[str, str]],
    ) -> Optional[str]:
        """
        Recomputes case summary covering:
        1. What was reported
        2. What happened since
        3. What's confirmed
        4. What remains unresolved
        Returns None if AI is unavailable.
        """
        pass

    @abstractmethod
    async def generate_communication_draft(
        self,
        draft_type: str,
        case_title: str,
        case_description: str,
        messages_history: List[Dict[str, str]],
        custom_instructions: Optional[str] = None,
    ) -> Optional[str]:
        """
        Generates an AI communication draft (info request, progress update, resolution, escalation summary).
        Returns None if AI is unavailable.
        """
        pass
