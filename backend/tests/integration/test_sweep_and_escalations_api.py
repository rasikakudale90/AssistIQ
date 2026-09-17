import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.core.security import create_access_token
from backend.models import (
    User,
    UserRole,
    Case,
    CaseType,
    Priority,
    CaseStatus,
    SLA,
    EscalationStatus,
    EscalationReason,
)
from backend.scheduler.sweep import run_the_sweep


def create_user(db: Session, email: str, role: UserRole) -> User:
    user = User(
        email=email,
        role=role,
        email_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def auth_header(user: User) -> dict:
    token = create_access_token(user.id, user.role.value)
    return {"Authorization": f"Bearer {token}"}


def test_sla_api_endpoint(client: TestClient, db_session: Session):
    requester = create_user(db_session, "sla_endpoint_req@test.com", UserRole.REQUESTER)

    case_payload = {
        "type": "Incident",
        "title": "Email server offline",
        "description": "Entire exchange server offline",
        "priority": "P1",
    }
    create_resp = client.post("/api/v1/cases", json=case_payload, headers=auth_header(requester))
    assert create_resp.status_code == 201
    case_id = create_resp.json()["id"]

    sla_resp = client.get(f"/api/v1/cases/{case_id}/sla", headers=auth_header(requester))
    assert sla_resp.status_code == 200
    sla_data = sla_resp.json()
    assert sla_data["priority"] == "P1"
    assert sla_data["response_breached"] is False
    assert sla_data["resolve_breached"] is False
    assert sla_data["response_time_remaining_seconds"] is not None


def test_operator_manual_escalation_flow(client: TestClient, db_session: Session):
    requester = create_user(db_session, "esc_req@test.com", UserRole.REQUESTER)
    operator = create_user(db_session, "esc_op@test.com", UserRole.OPERATOR)
    team_lead = create_user(db_session, "esc_lead@test.com", UserRole.TEAM_LEAD)

    case = Case(
        reference_number="INC-2026-000555",
        type=CaseType.INCIDENT,
        title="Complex database corruption",
        description="Corrupted tables in customer database",
        priority=Priority.P2,
        status=CaseStatus.ASSIGNED,
        requester_id=requester.id,
        owner_id=operator.id,
        version=1,
    )
    db_session.add(case)
    db_session.commit()

    # Requesters cannot trigger escalation (403)
    esc_payload = {"reason": "operator_requested", "notes": "Requires Tier-3 DBA intervention"}
    resp_req = client.post(f"/api/v1/cases/{case.id}/escalate", json=esc_payload, headers=auth_header(requester))
    assert resp_req.status_code == 403

    # Operator triggers escalation
    resp_op = client.post(f"/api/v1/cases/{case.id}/escalate", json=esc_payload, headers=auth_header(operator))
    assert resp_op.status_code == 201
    esc_data = resp_op.json()
    esc_id = esc_data["id"]
    assert esc_data["trigger_reason"] == "operator_requested"
    assert esc_data["status"] == "open"

    # List escalations
    list_resp = client.get(f"/api/v1/cases/{case.id}/escalations", headers=auth_header(operator))
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    # Team Lead acknowledges escalation
    ack_payload = {"status": "acknowledged"}
    ack_resp = client.post(f"/api/v1/escalations/{esc_id}/acknowledge", json=ack_payload, headers=auth_header(team_lead))
    assert ack_resp.status_code == 200
    assert ack_resp.json()["status"] == "acknowledged"


@pytest.mark.asyncio
async def test_the_sweep_execution(db_session: Session):
    requester = create_user(db_session, "sweep_req@test.com", UserRole.REQUESTER)

    # Create a breached open case
    past_time = datetime.now(timezone.utc) - timedelta(hours=10)
    case = Case(
        reference_number="INC-2026-000444",
        type=CaseType.INCIDENT,
        title="Payroll service unreachable",
        description="Critical payroll downtime",
        priority=Priority.P1,
        status=CaseStatus.ASSIGNED,
        requester_id=requester.id,
        created_at=past_time,
        updated_at=past_time,
        version=1,
    )
    db_session.add(case)
    db_session.flush()

    sla = SLA(
        case_id=case.id,
        priority=Priority.P1,
        target_response_at=past_time + timedelta(minutes=15),
        target_resolve_at=past_time + timedelta(hours=4),
        response_breached=False,
        resolve_breached=False,
    )
    db_session.add(sla)
    db_session.commit()

    # Run the Sweep
    stats = await run_the_sweep(db_session)
    assert stats["cases_evaluated"] >= 1
    assert stats["sla_breaches_detected"] >= 1
    assert stats["risk_assessments_written"] >= 1
    assert stats["escalations_raised"] >= 1
