from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.core.security import create_access_token
from backend.models import User, UserRole, Team, Case, CaseStatus, Priority, CaseType


def create_test_user(db: Session, email: str, role: UserRole, team_id: str = None) -> User:
    user = User(
        email=email,
        role=role,
        team_id=team_id,
        email_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def auth_header(user: User) -> dict:
    token = create_access_token(user.id, user.role.value)
    return {"Authorization": f"Bearer {token}"}


def test_case_creation_and_reference_generation(client: TestClient, db_session: Session):
    requester = create_test_user(db_session, "user1@test.com", UserRole.REQUESTER)
    headers = auth_header(requester)

    # 1. Create Incident
    inc_payload = {
        "type": "Incident",
        "title": "Email server not responding",
        "description": "Outlook returns error 503 when connecting to Exchange server.",
        "priority": "P2",
        "site": "New York",
    }
    resp1 = client.post("/api/v1/cases", json=inc_payload, headers=headers)
    assert resp1.status_code == 201
    inc_data = resp1.json()
    assert inc_data["reference_number"].startswith("INC-")
    assert inc_data["status"] == "New"
    assert inc_data["version"] == 1

    # 2. Create Service Request
    req_payload = {
        "type": "Service Request",
        "title": "Request developer laptop setup",
        "description": "New hire joining engineering team needs standard MacBook Pro setup.",
        "priority": "P3",
    }
    resp2 = client.post("/api/v1/cases", json=req_payload, headers=headers)
    assert resp2.status_code == 201
    req_data = resp2.json()
    assert req_data["reference_number"].startswith("REQ-")


def test_case_lifecycle_and_optimistic_locking(client: TestClient, db_session: Session):
    requester = create_test_user(db_session, "user2@test.com", UserRole.REQUESTER)
    operator = create_test_user(db_session, "op_lifecycle@test.com", UserRole.OPERATOR)

    # 1. Create case as Requester
    create_resp = client.post(
        "/api/v1/cases",
        json={
            "type": "Incident",
            "title": "Broken printer in Building B",
            "description": "Paper jam and flashing red light.",
        },
        headers=auth_header(requester),
    )
    case_data = create_resp.json()
    case_id = case_data["id"]
    version = case_data["version"]

    # 2. Transition New -> InAssessment (by Operator)
    t1_resp = client.patch(
        f"/api/v1/cases/{case_id}/status",
        json={"status": "InAssessment", "version": version, "reason": "Triage started"},
        headers=auth_header(operator),
    )
    assert t1_resp.status_code == 200
    case_data = t1_resp.json()
    assert case_data["status"] == "InAssessment"
    assert case_data["version"] == version + 1
    version = case_data["version"]

    # 3. Assign to Operator -> moves to Assigned
    assign_resp = client.patch(
        f"/api/v1/cases/{case_id}/assign",
        json={"owner_id": operator.id, "version": version},
        headers=auth_header(operator),
    )
    assert assign_resp.status_code == 200
    case_data = assign_resp.json()
    assert case_data["status"] == "Assigned"
    assert case_data["owner_id"] == operator.id
    version = case_data["version"]

    # 4. Optimistic locking check: try with STALE version
    stale_resp = client.patch(
        f"/api/v1/cases/{case_id}/status",
        json={"status": "Resolved", "version": version - 1},
        headers=auth_header(operator),
    )
    assert stale_resp.status_code == 409
    assert stale_resp.json()["error"]["code"] == "STALE_VERSION"

    # 5. Resolve case
    resolve_resp = client.patch(
        f"/api/v1/cases/{case_id}/status",
        json={"status": "Resolved", "version": version, "reason": "Replaced roller"},
        headers=auth_header(operator),
    )
    assert resolve_resp.status_code == 200
    case_data = resolve_resp.json()
    assert case_data["status"] == "Resolved"
    assert case_data["resolved_at"] is not None
    version = case_data["version"]

    # 6. Close case (Requester confirms outcome)
    close_resp = client.patch(
        f"/api/v1/cases/{case_id}/status",
        json={"status": "Closed", "version": version, "reason": "Printer working now"},
        headers=auth_header(requester),
    )
    assert close_resp.status_code == 200
    case_data = close_resp.json()
    assert case_data["status"] == "Closed"
    assert case_data["closed_at"] is not None
    version = case_data["version"]

    # 7. Reopen case within 7 days
    reopen_resp = client.post(
        f"/api/v1/cases/{case_id}/reopen",
        json={"reason": "Printer started jamming again today", "version": version},
        headers=auth_header(requester),
    )
    assert reopen_resp.status_code == 200
    case_data = reopen_resp.json()
    assert case_data["status"] == "Assigned"


def test_priority_override_rbac(client: TestClient, db_session: Session):
    requester = create_test_user(db_session, "user3@test.com", UserRole.REQUESTER)
    operator = create_test_user(db_session, "op3@test.com", UserRole.OPERATOR)
    manager = create_test_user(db_session, "mgr@test.com", UserRole.MANAGER)

    create_resp = client.post(
        "/api/v1/cases",
        json={
            "type": "Incident",
            "title": "Slow internet in finance wing",
            "description": "Speeds dropped below 1 Mbps.",
            "priority": "P3",
        },
        headers=auth_header(requester),
    )
    case_data = create_resp.json()
    case_id = case_data["id"]
    version = case_data["version"]

    # Operator cannot override priority -> 403
    op_override = client.patch(
        f"/api/v1/cases/{case_id}/priority",
        json={"priority": "P1", "reason": "Urgent quarter close", "version": version},
        headers=auth_header(operator),
    )
    assert op_override.status_code == 403

    # Manager can override priority -> 200
    mgr_override = client.patch(
        f"/api/v1/cases/{case_id}/priority",
        json={"priority": "P1", "reason": "Urgent quarter close", "version": version},
        headers=auth_header(manager),
    )
    assert mgr_override.status_code == 200
    assert mgr_override.json()["priority"] == "P1"


def test_role_scoped_case_isolation(client: TestClient, db_session: Session):
    alice = create_test_user(db_session, "alice@test.com", UserRole.REQUESTER)
    bob = create_test_user(db_session, "bob@test.com", UserRole.REQUESTER)

    # Alice creates a case
    alice_case = client.post(
        "/api/v1/cases",
        json={"type": "Incident", "title": "Alice's secret issue", "description": "Details here."},
        headers=auth_header(alice),
    ).json()

    # Bob attempts to view Alice's case -> 403
    bob_view = client.get(f"/api/v1/cases/{alice_case['id']}", headers=auth_header(bob))
    assert bob_view.status_code == 403

    # Bob lists cases -> should not see Alice's case
    bob_list = client.get("/api/v1/cases", headers=auth_header(bob)).json()
    assert bob_list["total"] == 0


def test_case_audit_timeline(client: TestClient, db_session: Session):
    requester = create_test_user(db_session, "user_audit@test.com", UserRole.REQUESTER)
    create_resp = client.post(
        "/api/v1/cases",
        json={"type": "Incident", "title": "Audit test case", "description": "Description."},
        headers=auth_header(requester),
    )
    case_id = create_resp.json()["id"]

    timeline_resp = client.get(f"/api/v1/cases/{case_id}/timeline", headers=auth_header(requester))
    assert timeline_resp.status_code == 200
    timeline = timeline_resp.json()
    assert len(timeline) >= 1
    assert timeline[0]["action"] == "case_created"
