from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session

from backend.core.errors import (
    NotFoundException,
    PermissionDeniedException,
    ValidationException,
)
from backend.models.enums import (
    EscalationReason,
    EscalationStatus,
    UserRole,
)
from backend.models.ai import EscalationEvent
from backend.models.case import Case
from backend.models.user import User
from backend.repositories.audit_repository import AuditRepository
from backend.repositories.case_repository import CaseRepository
from backend.schemas.ai import EscalationEventResponse


class EscalationService:
    @staticmethod
    def escalate_case(
        db: Session,
        case_id: str,
        current_user: User,
        reason: EscalationReason = EscalationReason.OPERATOR_REQUESTED,
        notes: Optional[str] = None,
    ) -> EscalationEventResponse:
        """
        Human-triggered or operator-requested escalation (SRS §5.8 - Level 2).
        """
        case = CaseRepository.get_by_id(db, case_id)
        if not case:
            raise NotFoundException(f"Case with ID '{case_id}' not found.")

        # Requesters cannot trigger managerial escalation
        if current_user.role == UserRole.REQUESTER:
            raise PermissionDeniedException("Requesters cannot escalate cases directly to managers.")

        # Determine target: Team Lead first, then Manager
        escalated_to_role = "TeamLead" if case.team_id else "Manager"

        event = EscalationEvent(
            case_id=case.id,
            trigger_reason=reason,
            escalated_to=escalated_to_role,
            escalated_by=current_user.id,
            status=EscalationStatus.OPEN,
        )
        db.add(event)

        AuditRepository.create_log(
            db=db,
            actor_id=current_user.id,
            action="case_escalated",
            target_type="case",
            target_id=case.id,
            after_value={
                "reason": reason.value,
                "escalated_to": escalated_to_role,
                "notes": notes,
            },
        )

        db.commit()
        db.refresh(event)
        return EscalationEventResponse.model_validate(event)

    @staticmethod
    def list_escalations_for_case(
        db: Session,
        case_id: str,
        current_user: User,
    ) -> List[EscalationEventResponse]:
        case = CaseRepository.get_by_id(db, case_id)
        if not case:
            raise NotFoundException(f"Case with ID '{case_id}' not found.")

        if current_user.role == UserRole.REQUESTER and case.requester_id != current_user.id:
            raise PermissionDeniedException("You do not have permission to view escalations for this case.")

        events = (
            db.query(EscalationEvent)
            .filter(EscalationEvent.case_id == case.id)
            .order_by(EscalationEvent.created_at.desc())
            .all()
        )
        return [EscalationEventResponse.model_validate(e) for e in events]

    @staticmethod
    def acknowledge_escalation(
        db: Session,
        escalation_id: str,
        current_user: User,
        new_status: EscalationStatus = EscalationStatus.ACKNOWLEDGED,
    ) -> EscalationEventResponse:
        event = db.query(EscalationEvent).filter(EscalationEvent.id == escalation_id).first()
        if not event:
            raise NotFoundException(f"Escalation event '{escalation_id}' not found.")

        if current_user.role not in [UserRole.TEAM_LEAD, UserRole.MANAGER, UserRole.ADMINISTRATOR]:
            raise PermissionDeniedException("Only Team Leads, Managers, and Admins can acknowledge escalations.")

        old_status = event.status
        event.status = new_status

        AuditRepository.create_log(
            db=db,
            actor_id=current_user.id,
            action="escalation_status_update",
            target_type="case",
            target_id=event.case_id,
            before_value={"status": old_status.value},
            after_value={"status": new_status.value},
        )

        db.commit()
        db.refresh(event)
        return EscalationEventResponse.model_validate(event)
