from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.core.dependencies import get_current_user, require_roles
from backend.db.session import get_db
from backend.models.enums import UserRole
from backend.models.user import User
from backend.schemas.ai import (
    EscalationEventResponse,
    EscalationCreateRequest,
    EscalationAcknowledgeRequest,
)
from backend.services.escalation_service import EscalationService

router = APIRouter(tags=["Escalations"])


@router.post(
    "/cases/{case_id}/escalate",
    response_model=EscalationEventResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(UserRole.OPERATOR, UserRole.TEAM_LEAD, UserRole.MANAGER, UserRole.ADMINISTRATOR))],
)
def escalate_case(
    case_id: str,
    data: EscalationCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Operator explicit request for managerial help (SRS §5.8 - Level 2 human action).
    """
    return EscalationService.escalate_case(
        db=db,
        case_id=case_id,
        current_user=current_user,
        reason=data.reason,
        notes=data.notes,
    )


@router.get("/cases/{case_id}/escalations", response_model=List[EscalationEventResponse])
def list_case_escalations(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lists escalation events for a given case.
    """
    return EscalationService.list_escalations_for_case(
        db=db,
        case_id=case_id,
        current_user=current_user,
    )


@router.post(
    "/escalations/{escalation_id}/acknowledge",
    response_model=EscalationEventResponse,
    dependencies=[Depends(require_roles(UserRole.TEAM_LEAD, UserRole.MANAGER, UserRole.ADMINISTRATOR))],
)
def acknowledge_escalation(
    escalation_id: str,
    data: EscalationAcknowledgeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Team Lead, Manager, or Admin acknowledges an active escalation event.
    """
    return EscalationService.acknowledge_escalation(
        db=db,
        escalation_id=escalation_id,
        current_user=current_user,
        new_status=data.status,
    )
