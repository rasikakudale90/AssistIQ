import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.core.security import create_access_token
from backend.models import User, UserRole, Case, CaseType, Priority, CaseStatus
from backend.providers.ai import set_ai_provider
from backend.providers.ai.mock import MockAIProvider


def create_user(db: Session, email: str, role: UserRole, site: str = "NYC") -> User:
    user = User(
        email=email,
        role=role,
        email_verified=True,
        site=site,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def auth_header(user: User) -> dict:
    token = create_access_token(user.id, user.role.value)
    return {"Authorization": f"Bearer {token}"}


def test_ai_triage_and_summary_api(client: TestClient, db_session: Session):
    set_ai_provider(MockAIProvider())

    requester = create_user(db_session, "ai_req@test.com", UserRole.REQUESTER)
    operator = create_user(db_session, "ai_op@test.com", UserRole.OPERATOR)

    # 1. Create Case
    case_payload = {
        "type": "Incident",
        "title": "VPN connection drops constantly on corporate wifi",
        "description": "Whenever I connect to the office wifi, Cisco AnyConnect disconnects with error 402.",
        "priority": "P2",
        "site": "NYC",
    }
    create_resp = client.post("/api/v1/cases", json=case_payload, headers=auth_header(requester))
    assert create_resp.status_code == 201
    case_id = create_resp.json()["id"]

    # 2. Get AI Triage
    triage_resp = client.get(f"/api/v1/cases/{case_id}/triage", headers=auth_header(operator))
    assert triage_resp.status_code == 200
    triage_data = triage_resp.json()
    assert triage_data["suggested_category"] == "Network"
    assert triage_data["suggested_team"] == "Network Engineering"
    assert triage_data["confidence_level"] == "High"

    # 3. Post a message and get summary
    msg_payload = {
        "body": "Rebooted router, issue still persists.",
        "visibility": "requester_visible",
    }
    client.post(f"/api/v1/cases/{case_id}/messages", json=msg_payload, headers=auth_header(requester))

    # Trigger summary recomputation
    from backend.services.ai_service import AIService
    import asyncio
    asyncio.run(AIService.recompute_case_summary(db_session, case_id))

    summary_resp = client.get(f"/api/v1/cases/{case_id}/summary", headers=auth_header(operator))
    assert summary_resp.status_code == 200
    summary_data = summary_resp.json()
    assert summary_data is not None
    assert "What was reported" in summary_data["summary_text"]


def test_ai_draft_lifecycle_and_send(client: TestClient, db_session: Session):
    set_ai_provider(MockAIProvider())

    requester = create_user(db_session, "draft_req@test.com", UserRole.REQUESTER)
    operator = create_user(db_session, "draft_op@test.com", UserRole.OPERATOR)

    # Create Case
    case = Case(
        reference_number="INC-2026-000888",
        type=CaseType.INCIDENT,
        title="Laptop keyboard not responding",
        description="Keys Q, W, E not working after water spill",
        priority=Priority.P3,
        status=CaseStatus.ASSIGNED,
        requester_id=requester.id,
        owner_id=operator.id,
        version=1,
    )
    db_session.add(case)
    db_session.commit()

    # Requesters cannot generate drafts (403)
    draft_req = {"draft_type": "info_request", "custom_instructions": "Ask for asset tag"}
    resp_req = client.post(f"/api/v1/cases/{case.id}/drafts", json=draft_req, headers=auth_header(requester))
    assert resp_req.status_code == 403

    # Operator generates draft
    resp_op = client.post(f"/api/v1/cases/{case.id}/drafts", json=draft_req, headers=auth_header(operator))
    assert resp_op.status_code == 201
    draft_data = resp_op.json()
    draft_id = draft_data["id"]
    assert draft_data["status"] == "draft"
    assert "Laptop keyboard not responding" in draft_data["body"]

    # List drafts
    list_resp = client.get(f"/api/v1/cases/{case.id}/drafts", headers=auth_header(operator))
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    # Operator reviews, edits, and sends draft
    send_payload = {
        "body": "Hello, could you please provide your laptop asset tag number and serial number?",
        "visibility": "requester_visible",
    }
    send_resp = client.post(f"/api/v1/drafts/{draft_id}/send", json=send_payload, headers=auth_header(operator))
    assert send_resp.status_code == 200
    msg_data = send_resp.json()
    assert msg_data["ai_generated"] is True
    assert msg_data["body"] == send_payload["body"]

    # Verify draft is now marked sent
    list_after = client.get(f"/api/v1/cases/{case.id}/drafts", headers=auth_header(operator))
    assert list_after.json()[0]["status"] == "sent"


def test_assignment_recommendation_and_risk_rbac(client: TestClient, db_session: Session):
    requester = create_user(db_session, "assign_req@test.com", UserRole.REQUESTER)
    operator = create_user(db_session, "assign_op@test.com", UserRole.OPERATOR)

    case = Case(
        reference_number="INC-2026-000777",
        type=CaseType.INCIDENT,
        title="Printer paper jam",
        description="Printer on 3rd floor jammed",
        priority=Priority.P4,
        status=CaseStatus.NEW,
        requester_id=requester.id,
        site="NYC",
        version=1,
    )
    db_session.add(case)
    db_session.commit()

    # Requesters cannot view assignment recommendations or risk (403)
    rec_req = client.get(f"/api/v1/cases/{case.id}/assignment-recommendations", headers=auth_header(requester))
    assert rec_req.status_code == 403

    risk_req = client.get(f"/api/v1/cases/{case.id}/risk", headers=auth_header(requester))
    assert risk_req.status_code == 403

    # Operator can view assignment recommendations
    rec_op = client.get(f"/api/v1/cases/{case.id}/assignment-recommendations", headers=auth_header(operator))
    assert rec_op.status_code == 200
    rec_data = rec_op.json()
    assert "candidate_operators" in rec_data
    assert len(rec_data["candidate_operators"]) >= 1
