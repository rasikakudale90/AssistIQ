from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict

from backend.models.enums import (
    ConfidenceLevel,
    RiskLevel,
    EscalationReason,
    EscalationStatus,
    DraftType,
    DraftStatus,
    MessageVisibility,
    UserRole,
    AvailabilityStatus,
)


class AITriageResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str
    suggested_category: Optional[str] = None
    suggested_severity: Optional[str] = None
    suggested_priority: Optional[str] = None
    confidence_level: ConfidenceLevel
    confidence_score: Optional[float] = None
    supporting_factors: List[str] = Field(default_factory=list)
    missing_info: List[str] = Field(default_factory=list)
    suggested_team: Optional[str] = None
    recommended_next_action: Optional[str] = None
    related_case_ids: List[str] = Field(default_factory=list)
    created_at: datetime


class CaseSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str
    summary_text: str
    last_source_message_id: Optional[str] = None
    updated_at: datetime


class CaseRiskAssessmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str
    risk_level: RiskLevel
    signals: Dict[str, Any] = Field(default_factory=dict)
    computed_at: datetime


class EscalationEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str
    trigger_reason: EscalationReason
    escalated_to: Optional[str] = None
    escalated_by: str
    status: EscalationStatus
    created_at: datetime


class EscalationCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reason: EscalationReason = Field(
        default=EscalationReason.OPERATOR_REQUESTED,
        description="Reason for escalation (defaults to operator_requested)",
    )
    notes: Optional[str] = Field(None, max_length=1000, description="Notes for the Team Lead/Manager")


class EscalationAcknowledgeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: EscalationStatus = Field(
        default=EscalationStatus.ACKNOWLEDGED,
        description="Updated escalation status (acknowledged or resolved)",
    )


class CommunicationDraftCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    draft_type: DraftType = Field(..., description="Type of draft to generate")
    custom_instructions: Optional[str] = Field(
        None, max_length=1000, description="Optional custom prompts or guidance for the AI"
    )


class CommunicationDraftUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    body: str = Field(..., min_length=1, max_length=5000, description="Updated draft body")


class SendCommunicationDraftRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    body: str = Field(..., min_length=1, max_length=5000, description="Final reviewed message body")
    visibility: MessageVisibility = Field(
        default=MessageVisibility.REQUESTER_VISIBLE,
        description="Message visibility (requester_visible or internal_only)",
    )


class CommunicationDraftResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str
    draft_type: DraftType
    body: str
    status: DraftStatus
    reviewed_by: Optional[str] = None
    sent_message_id: Optional[str] = None
    created_at: datetime


class CandidateOperatorRecommendation(BaseModel):
    user_id: str
    email: str
    role: UserRole
    team_id: Optional[str] = None
    team_name: Optional[str] = None
    availability_status: AvailabilityStatus
    active_case_count: int
    site: Optional[str] = None
    score: float
    match_reasons: List[str] = Field(default_factory=list)


class AssignmentRecommendationResponse(BaseModel):
    case_id: str
    suggested_team: Optional[str] = None
    suggested_team_id: Optional[str] = None
    candidate_operators: List[CandidateOperatorRecommendation] = Field(default_factory=list)
    rationale: List[str] = Field(default_factory=list)
