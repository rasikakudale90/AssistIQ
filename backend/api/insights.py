from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.core.dependencies import get_current_user, require_roles
from backend.db.session import get_db
from backend.models.enums import UserRole
from backend.models.user import User
from backend.schemas.insights import (
    OperationalInsightsResponse,
    QuickDashboardStats,
    TimeWindow,
)
from backend.services.insights_service import InsightsService

router = APIRouter(tags=["Operational Insights & Analytics"])


@router.get(
    "/insights",
    response_model=OperationalInsightsResponse,
    dependencies=[Depends(require_roles(UserRole.MANAGER, UserRole.ADMINISTRATOR))],
)
async def get_operational_insights(
    window: TimeWindow = Query("30d", description="Time window for aggregation: 7d, 30d, 90d, all"),
    narrate: bool = Query(False, description="Generate an executive AI plain-language summary narrative"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieves aggregated operational metrics, category/team/site volume trends,
    reopen rates, SLA compliance, and optional AI summary narration (SRS §5.12).
    Restricted to Manager and Administrator.
    """
    return await InsightsService.get_operational_insights(
        db=db,
        window=window,
        narrate=narrate,
    )


@router.get("/insights/dashboard", response_model=QuickDashboardStats)
def get_dashboard_summary_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieves quick badge summary statistics for dashboards.
    """
    return InsightsService.get_quick_dashboard_stats(
        db=db,
        current_user=current_user,
    )
