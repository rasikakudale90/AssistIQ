from typing import Optional
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from backend.core.dependencies import get_current_user
from backend.db.session import get_db
from backend.models.enums import CaseType, CaseStatus, Priority
from backend.models.user import User
from backend.services.export_service import ExportService

router = APIRouter(tags=["Reports & Exports"])


@router.get("/reports/export/cases.csv")
def export_cases_csv(
    status: Optional[CaseStatus] = Query(None, description="Filter by case status"),
    priority: Optional[Priority] = Query(None, description="Filter by priority"),
    case_type: Optional[CaseType] = Query(None, description="Filter by type (Incident / Service Request)"),
    team_id: Optional[str] = Query(None, description="Filter by team ID"),
    owner_id: Optional[str] = Query(None, description="Filter by owner user ID"),
    search: Optional[str] = Query(None, description="Search keyword filter"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Exports a CSV file of cases matching the requested filters and strictly scoped by the user's role (SRS §7.6).
    """
    csv_data = ExportService.generate_cases_csv(
        db=db,
        current_user=current_user,
        status=status,
        priority=priority,
        case_type=case_type,
        team_id=team_id,
        owner_id=owner_id,
        search=search,
    )

    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=assistiq_cases_export.csv",
            "Cache-Control": "no-cache",
        },
    )
