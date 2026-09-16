from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Set, Tuple
from sqlalchemy.orm import Session

from backend.core.errors import (
    NotFoundException,
    PermissionDeniedException,
    StaleVersionException,
    ValidationException,
)
from backend.models.enums import CaseType, CaseStatus, Priority, UserRole
from backend.models.case import Case
from backend.models.user import User
from backend.repositories.case_repository import CaseRepository
from backend.repositories.audit_repository import AuditRepository
from backend.schemas.case import (
    CaseCreate,
    CaseUpdate,
    CaseStatusTransition,
    CaseAssignment,
    CasePriorityOverride,
    CaseReopen,
    CaseDetailResponse,
    CaseListResponse,
    CaseSummaryResponse,
    AuditLogResponse,
)


class CaseService:
    # Permitted lifecycle state transitions per SRS §6.1 & AGENTS_AssistIQ.md §12
    VALID_TRANSITIONS: Dict[CaseStatus, Set[CaseStatus]] = {
        CaseStatus.DRAFT: {CaseStatus.NEW},
        CaseStatus.NEW: {CaseStatus.IN_ASSESSMENT, CaseStatus.CANCELLED},
        CaseStatus.IN_ASSESSMENT: {CaseStatus.ASSIGNED},
        CaseStatus.ASSIGNED: {
            CaseStatus.AWAITING_REQUESTER,
            CaseStatus.AWAITING_APPROVAL,
            CaseStatus.RESOLVED,
            CaseStatus.CANCELLED,
        },
        CaseStatus.AWAITING_REQUESTER: {CaseStatus.ASSIGNED},
        CaseStatus.AWAITING_APPROVAL: {CaseStatus.ASSIGNED},
        CaseStatus.RESOLVED: {CaseStatus.CLOSED, CaseStatus.ASSIGNED},
        CaseStatus.CLOSED: {CaseStatus.ASSIGNED},  # Reopen within 7 days
        CaseStatus.CANCELLED: set(),
    }

    @staticmethod
    def create_case(db: Session, current_user: User, data: CaseCreate) -> CaseDetailResponse:
        ref_number = CaseRepository.generate_reference_number(db, data.type)

        case = Case(
            reference_number=ref_number,
            type=data.type,
            title=data.title,
            description=data.description,
            status=CaseStatus.NEW,
            priority=data.priority or Priority.P3,
            requester_id=current_user.id,
            site=data.site or current_user.site,
            service_id=data.service_id,
            version=1,
        )
        db.add(case)
        db.flush()  # Flush to get case.id for audit log

        AuditRepository.create_log(
            db=db,
            actor_id=current_user.id,
            action="case_created",
            target_type="case",
            target_id=case.id,
            after_value={
                "reference_number": ref_number,
                "type": data.type.value,
                "title": data.title,
                "priority": case.priority.value,
            },
        )
        db.commit()
        db.refresh(case)
        return CaseDetailResponse.model_validate(case)

    @staticmethod
    def get_case(db: Session, current_user: User, case_id: str) -> Case:
        case = CaseRepository.get_by_id(db, case_id)
        if not case:
            raise NotFoundException(f"Case with ID '{case_id}' not found.")

        # Permission check
        if current_user.role == UserRole.REQUESTER and case.requester_id != current_user.id:
            raise PermissionDeniedException("You do not have permission to view this case.")

        return case

    @staticmethod
    def get_case_detail(db: Session, current_user: User, case_id: str) -> CaseDetailResponse:
        case = CaseService.get_case(db, current_user, case_id)
        return CaseDetailResponse.model_validate(case)

    @staticmethod
    def list_cases(
        db: Session,
        current_user: User,
        status: Optional[CaseStatus] = None,
        priority: Optional[Priority] = None,
        case_type: Optional[CaseType] = None,
        team_id: Optional[str] = None,
        owner_id: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> CaseListResponse:
        cases, total = CaseRepository.list_cases(
            db=db,
            current_user=current_user,
            status=status,
            priority=priority,
            case_type=case_type,
            team_id=team_id,
            owner_id=owner_id,
            search=search,
            page=page,
            page_size=page_size,
        )
        return CaseListResponse(
            items=[CaseSummaryResponse.model_validate(c) for c in cases],
            page=page,
            page_size=page_size,
            total=total,
        )

    @staticmethod
    def transition_status(
        db: Session,
        current_user: User,
        case_id: str,
        data: CaseStatusTransition,
    ) -> CaseDetailResponse:
        case = CaseService.get_case(db, current_user, case_id)

        # 1. Optimistic locking check (SRS §7.12)
        if case.version != data.version:
            raise StaleVersionException()

        old_status = case.status
        new_status = data.status

        # 2. Validate state transition
        allowed_targets = CaseService.VALID_TRANSITIONS.get(old_status, set())
        if new_status not in allowed_targets:
            raise ValidationException(
                f"Invalid lifecycle transition from '{old_status.value}' to '{new_status.value}'."
            )

        # 3. RBAC checks for specific transitions
        if current_user.role == UserRole.REQUESTER:
            # Requesters can only cancel their own case or confirm/reject resolution
            if new_status == CaseStatus.CANCELLED and old_status in [CaseStatus.NEW, CaseStatus.ASSIGNED]:
                pass
            elif old_status == CaseStatus.RESOLVED and new_status in [CaseStatus.CLOSED, CaseStatus.ASSIGNED]:
                pass
            else:
                raise PermissionDeniedException(
                    f"Requesters cannot transition cases from '{old_status.value}' to '{new_status.value}'."
                )

        # 4. Apply transition
        case.status = new_status
        now = datetime.now(timezone.utc)
        if new_status == CaseStatus.RESOLVED:
            case.resolved_at = now
        elif new_status == CaseStatus.CLOSED:
            case.closed_at = now
        elif new_status == CaseStatus.ASSIGNED and old_status == CaseStatus.RESOLVED:
            # Requester rejected the fix
            case.resolved_at = None

        case.version += 1
        case.updated_at = now

        # 5. Audit Log
        AuditRepository.create_log(
            db=db,
            actor_id=current_user.id,
            action="status_change",
            target_type="case",
            target_id=case.id,
            before_value={"status": old_status.value},
            after_value={"status": new_status.value, "reason": data.reason},
        )

        db.commit()
        db.refresh(case)
        return CaseDetailResponse.model_validate(case)

    @staticmethod
    def assign_case(
        db: Session,
        current_user: User,
        case_id: str,
        data: CaseAssignment,
    ) -> CaseDetailResponse:
        case = CaseService.get_case(db, current_user, case_id)

        # 1. Staff check
        if current_user.role not in [UserRole.OPERATOR, UserRole.TEAM_LEAD, UserRole.MANAGER, UserRole.ADMINISTRATOR]:
            raise PermissionDeniedException("Only staff members can assign cases.")

        # 2. TeamLead scope check: Leads cannot assign outside their team unless Manager/Admin
        if current_user.role == UserRole.TEAM_LEAD and data.team_id and data.team_id != current_user.team_id:
            raise PermissionDeniedException("Team Leads cannot assign cases to other teams.")

        # 3. Optimistic locking check
        if case.version != data.version:
            raise StaleVersionException()

        before_val = {"owner_id": case.owner_id, "team_id": case.team_id}

        if data.owner_id is not None:
            case.owner_id = data.owner_id
        if data.team_id is not None:
            case.team_id = data.team_id

        # Auto-advance InAssessment -> Assigned if owner or team is now set
        if case.status in [CaseStatus.NEW, CaseStatus.IN_ASSESSMENT] and (case.owner_id or case.team_id):
            case.status = CaseStatus.ASSIGNED

        case.version += 1
        case.updated_at = datetime.now(timezone.utc)

        AuditRepository.create_log(
            db=db,
            actor_id=current_user.id,
            action="assignment",
            target_type="case",
            target_id=case.id,
            before_value=before_val,
            after_value={"owner_id": case.owner_id, "team_id": case.team_id, "status": case.status.value},
        )

        db.commit()
        db.refresh(case)
        return CaseDetailResponse.model_validate(case)

    @staticmethod
    def override_priority(
        db: Session,
        current_user: User,
        case_id: str,
        data: CasePriorityOverride,
    ) -> CaseDetailResponse:
        case = CaseService.get_case(db, current_user, case_id)

        # Manager and Admin only (SRS §2.2)
        if current_user.role not in [UserRole.MANAGER, UserRole.ADMINISTRATOR]:
            raise PermissionDeniedException("Only Managers and Administrators can override case priority.")

        if case.version != data.version:
            raise StaleVersionException()

        old_priority = case.priority
        case.priority = data.priority
        case.version += 1
        case.updated_at = datetime.now(timezone.utc)

        AuditRepository.create_log(
            db=db,
            actor_id=current_user.id,
            action="priority_override",
            target_type="case",
            target_id=case.id,
            before_value={"priority": old_priority.value},
            after_value={"priority": data.priority.value, "reason": data.reason},
        )

        db.commit()
        db.refresh(case)
        return CaseDetailResponse.model_validate(case)

    @staticmethod
    def reopen_case(
        db: Session,
        current_user: User,
        case_id: str,
        data: CaseReopen,
    ) -> CaseDetailResponse:
        case = CaseService.get_case(db, current_user, case_id)

        if case.status != CaseStatus.CLOSED:
            raise ValidationException(f"Only closed cases can be reopened. Current status is '{case.status.value}'.")

        # 7-day reopen window rule (SRS §6)
        if case.closed_at:
            closed_at = case.closed_at
            if closed_at.tzinfo is None:
                closed_at = closed_at.replace(tzinfo=timezone.utc)
            cutoff = datetime.now(timezone.utc) - timedelta(days=7)
            if closed_at < cutoff:
                raise ValidationException(
                    "This case was closed more than 7 days ago and cannot be reopened. Please submit a new case."
                )

        # Check permissions: original requester or any staff
        if current_user.role == UserRole.REQUESTER and case.requester_id != current_user.id:
            raise PermissionDeniedException("Only the original requester or IT staff can reopen this case.")

        if case.version != data.version:
            raise StaleVersionException()

        case.status = CaseStatus.ASSIGNED
        case.resolved_at = None
        case.closed_at = None
        case.version += 1
        case.updated_at = datetime.now(timezone.utc)

        AuditRepository.create_log(
            db=db,
            actor_id=current_user.id,
            action="reopened",
            target_type="case",
            target_id=case.id,
            before_value={"status": CaseStatus.CLOSED.value},
            after_value={"status": CaseStatus.ASSIGNED.value, "reason": data.reason},
        )

        db.commit()
        db.refresh(case)
        return CaseDetailResponse.model_validate(case)

    @staticmethod
    def get_timeline(db: Session, current_user: User, case_id: str) -> List[AuditLogResponse]:
        # Verifies read permissions on the case
        CaseService.get_case(db, current_user, case_id)
        logs = AuditRepository.get_timeline_for_target(db, target_type="case", target_id=case_id)
        return [AuditLogResponse.model_validate(log) for log in logs]
