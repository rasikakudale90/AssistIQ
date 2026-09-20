from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.core.dependencies import get_current_user, require_roles
from backend.core.errors import NotFoundException, PermissionDeniedException
from backend.db.session import get_db
from backend.models.enums import UserRole
from backend.models.user import User
from backend.models.ai import AITriageResult, CaseSummary, CaseRiskAssessment, CommunicationDraft
from backend.schemas.ai import (
    AITriageResultResponse,
    CaseSummaryResponse,
    CaseRiskAssessmentResponse,
    AssignmentRecommendationResponse,
    CommunicationDraftCreate,
    CommunicationDraftResponse,
    SendCommunicationDraftRequest,
)
from backend.schemas.message import MessageResponse
from backend.services.ai_service import AIService
from backend.services.case_service import CaseService

router = APIRouter(tags=["AI Capabilities"])


@router.get("/cases/{case_id}/triage", response_model=Optional[AITriageResultResponse])
async def get_or_run_triage(
    case_id: str,
    refresh: bool = Query(False, description="Force re-running the AI triage analysis"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieves or triggers the synchronous AI triage analysis for a case (SRS §5.2).
    """
    case = CaseService.get_case(db, current_user, case_id)
    return await AIService.run_triage_analysis(
        db=db,
        case_id=case.id,
        current_user=current_user,
        force_refresh=refresh,
    )


@router.get("/cases/{case_id}/summary", response_model=Optional[CaseSummaryResponse])
async def get_case_summary(
    case_id: str,
    refresh: bool = Query(False, description="Force recomputing the AI summary"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieves the latest continuous AI summary for a case (SRS §5.3).
    Automatically computes if not yet generated or refreshed.
    """
    case = CaseService.get_case(db, current_user, case_id)
    summary = db.query(CaseSummary).filter(CaseSummary.case_id == case.id).first()
    if not summary or refresh:
        return await AIService.recompute_case_summary(db=db, case_id=case.id)
    return CaseSummaryResponse.model_validate(summary)


@router.get(
    "/cases/{case_id}/risk",
    response_model=Optional[CaseRiskAssessmentResponse],
    dependencies=[Depends(require_roles(UserRole.OPERATOR, UserRole.TEAM_LEAD, UserRole.MANAGER, UserRole.ADMINISTRATOR))],
)
def get_case_risk_assessment(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieves the latest risk assessment score computed by the Sweep (SRS §5.7).
    Staff only — never exposed to Requesters.
    """
    case = CaseService.get_case(db, current_user, case_id)
    risk = (
        db.query(CaseRiskAssessment)
        .filter(CaseRiskAssessment.case_id == case.id)
        .order_by(CaseRiskAssessment.computed_at.desc())
        .first()
    )
    if not risk:
        return None
    return CaseRiskAssessmentResponse.model_validate(risk)


@router.get(
    "/cases/{case_id}/assignment-recommendations",
    response_model=AssignmentRecommendationResponse,
    dependencies=[Depends(require_roles(UserRole.OPERATOR, UserRole.TEAM_LEAD, UserRole.MANAGER, UserRole.ADMINISTRATOR))],
)
def get_assignment_recommendations(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Smart assignment recommendations based on team triage, active operator workloads,
    availability, and site alignment (SRS §5.6).
    """
    return AIService.get_assignment_recommendations(
        db=db,
        case_id=case_id,
        current_user=current_user,
    )


@router.post(
    "/cases/{case_id}/drafts",
    response_model=CommunicationDraftResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(UserRole.OPERATOR, UserRole.TEAM_LEAD, UserRole.MANAGER, UserRole.ADMINISTRATOR))],
)
async def generate_communication_draft(
    case_id: str,
    data: CommunicationDraftCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generates an AI communication draft for operator review (SRS §5.9).
    Never auto-sent.
    """
    return await AIService.generate_communication_draft(
        db=db,
        case_id=case_id,
        draft_type=data.draft_type,
        current_user=current_user,
        custom_instructions=data.custom_instructions,
    )


@router.get(
    "/cases/{case_id}/drafts",
    response_model=List[CommunicationDraftResponse],
    dependencies=[Depends(require_roles(UserRole.OPERATOR, UserRole.TEAM_LEAD, UserRole.MANAGER, UserRole.ADMINISTRATOR))],
)
def list_case_drafts(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lists communication drafts for a case. Staff only.
    """
    case = CaseService.get_case(db, current_user, case_id)
    drafts = (
        db.query(CommunicationDraft)
        .filter(CommunicationDraft.case_id == case.id)
        .order_by(CommunicationDraft.created_at.desc())
        .all()
    )
    return [CommunicationDraftResponse.model_validate(d) for d in drafts]


@router.post(
    "/drafts/{draft_id}/send",
    response_model=MessageResponse,
    dependencies=[Depends(require_roles(UserRole.OPERATOR, UserRole.TEAM_LEAD, UserRole.MANAGER, UserRole.ADMINISTRATOR))],
)
def send_communication_draft(
    draft_id: str,
    data: SendCommunicationDraftRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Operator reviews, approves, and sends a communication draft (SRS §5.9).
    Publishes a Message with `ai_generated = true`.
    """
    message = AIService.send_communication_draft(
        db=db,
        draft_id=draft_id,
        current_user=current_user,
        data=data,
    )
    return MessageResponse.model_validate(message)
