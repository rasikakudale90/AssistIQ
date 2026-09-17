import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from backend.models.enums import UserRole, CaseType, CaseStatus, Priority
from backend.models.user import User, Team
from backend.models.case import Case
from backend.models.sla import SLA
from backend.models.ai import AITriageResult
from backend.services.insights_service import InsightsService
from backend.services.export_service import ExportService


@pytest.mark.asyncio
async def test_insights_aggregations(db_session: Session):
    # Create Team & Users
    team = Team(name="Hardware Support")
    db_session.add(team)
    db_session.flush()

    requester = User(email="insights_req@test.com", role=UserRole.REQUESTER, email_verified=True)
    operator = User(email="insights_op@test.com", role=UserRole.OPERATOR, team_id=team.id, email_verified=True)
    db_session.add_all([requester, operator])
    db_session.flush()

    # Create cases
    now = datetime.now(timezone.utc)
    c1 = Case(
        reference_number="INC-2026-000101",
        type=CaseType.INCIDENT,
        title="Laptop issue",
        description="Hardware problem",
        status=CaseStatus.RESOLVED,
        priority=Priority.P3,
        requester_id=requester.id,
        owner_id=operator.id,
        team_id=team.id,
        site="NYC",
        created_at=now - timedelta(days=2),
        resolved_at=now - timedelta(days=1),
        version=1,
    )
    c2 = Case(
        reference_number="REQ-2026-000102",
        type=CaseType.SERVICE_REQUEST,
        title="Monitor request",
        description="Hardware monitor",
        status=CaseStatus.NEW,
        priority=Priority.P4,
        requester_id=requester.id,
        site="London",
        created_at=now - timedelta(days=1),
        version=1,
    )
    db_session.add_all([c1, c2])
    db_session.flush()

    # SLA for c1
    sla1 = SLA(
        case_id=c1.id,
        priority=Priority.P3,
        target_response_at=now - timedelta(days=2) + timedelta(hours=4),
        target_resolve_at=now - timedelta(days=2) + timedelta(hours=72),
        responded_at=now - timedelta(days=2) + timedelta(hours=1),
        resolved_at=c1.resolved_at,
        response_breached=False,
        resolve_breached=False,
    )
    db_session.add(sla1)
    db_session.commit()

    # Compute insights for 7d window
    insights = await InsightsService.get_operational_insights(db_session, window="7d", narrate=False)

    assert insights.total_cases >= 2
    assert insights.resolved_cases >= 1
    assert "Incident" in insights.cases_by_type
    assert "Service Request" in insights.cases_by_type
    assert "P3" in insights.cases_by_priority
    assert insights.sla_metrics.compliance_rate_percent >= 0.0


def test_csv_export_formatting(db_session: Session):
    manager = User(email="manager_csv@test.com", role=UserRole.MANAGER, email_verified=True)
    db_session.add(manager)
    db_session.commit()

    csv_data = ExportService.generate_cases_csv(db_session, manager)
    assert "Reference Number" in csv_data
    assert "Requester Email" in csv_data
    assert "SLA" in csv_data or "Target Response" in csv_data
