from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.core.dependencies import (
    get_current_user,
    require_verified_user,
    require_staff,
    require_manager,
)
from backend.db.session import get_db
from backend.models.enums import CaseType, CaseStatus, Priority
from backend.models.user import User
from backend.schemas.case import (
    CaseCreate,
    CaseStatusTransition,
    CaseAssignment,
    CasePriorityOverride,
    CaseReopen,
    CaseDetailResponse,
    CaseListResponse,
    AuditLogResponse,
)
from backend.services.case_service import CaseService

router = APIRouter(prefix="/cases", tags=["Cases"])


@router.post(
    "",
    response_model=CaseDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Incident or Service Request",
)
def create_case(
    data: CaseCreate,
    current_user: User = Depends(require_verified_user),
    db: Session = Depends(get_db),
) -> CaseDetailResponse:
    return CaseService.create_case(db, current_user, data)


@router.get(
    "",
    response_model=CaseListResponse,
    summary="List cases with role-scoped visibility and filters",
)
def list_cases(
    status: Optional[CaseStatus] = Query(None, description="Filter by status"),
    priority: Optional[Priority] = Query(None, description="Filter by priority"),
    case_type: Optional[CaseType] = Query(None, alias="type", description="Filter by case type"),
    team_id: Optional[str] = Query(None, description="Filter by assigned team"),
    owner_id: Optional[str] = Query(None, description="Filter by assigned owner"),
    search: Optional[str] = Query(None, description="Search reference number or title"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(require_verified_user),
    db: Session = Depends(get_db),
) -> CaseListResponse:
    return CaseService.list_cases(
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


@router.get(
    "/{case_id}",
    response_model=CaseDetailResponse,
    summary="Get case details by ID",
)
def get_case(
    case_id: str,
    current_user: User = Depends(require_verified_user),
    db: Session = Depends(get_db),
) -> CaseDetailResponse:
    return CaseService.get_case_detail(db, current_user, case_id)


@router.patch(
    "/{case_id}/status",
    response_model=CaseDetailResponse,
    summary="Transition case lifecycle status",
)
def transition_case_status(
    case_id: str,
    data: CaseStatusTransition,
    current_user: User = Depends(require_verified_user),
    db: Session = Depends(get_db),
) -> CaseDetailResponse:
    return CaseService.transition_status(db, current_user, case_id, data)


@router.patch(
    "/{case_id}/assign",
    response_model=CaseDetailResponse,
    summary="Assign case to an operator and/or team",
)
def assign_case(
    case_id: str,
    data: CaseAssignment,
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db),
) -> CaseDetailResponse:
    return CaseService.assign_case(db, current_user, case_id, data)


@router.patch(
    "/{case_id}/priority",
    response_model=CaseDetailResponse,
    summary="Override case priority (Manager/Admin only)",
)
def override_priority(
    case_id: str,
    data: CasePriorityOverride,
    current_user: User = Depends(require_manager),
    db: Session = Depends(get_db),
) -> CaseDetailResponse:
    return CaseService.override_priority(db, current_user, case_id, data)


@router.post(
    "/{case_id}/reopen",
    response_model=CaseDetailResponse,
    summary="Reopen a closed case within the 7-day window",
)
def reopen_case(
    case_id: str,
    data: CaseReopen,
    current_user: User = Depends(require_verified_user),
    db: Session = Depends(get_db),
) -> CaseDetailResponse:
    return CaseService.reopen_case(db, current_user, case_id, data)


@router.get(
    "/{case_id}/timeline",
    response_model=List[AuditLogResponse],
    summary="Get full audit timeline of case events and changes",
)
def get_case_timeline(
    case_id: str,
    current_user: User = Depends(require_verified_user),
    db: Session = Depends(get_db),
) -> List[AuditLogResponse]:
    return CaseService.get_timeline(db, current_user, case_id)
