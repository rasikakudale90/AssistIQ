from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.core.security import create_access_token
from backend.models import User, UserRole, Case, CaseType, Priority, CaseStatus


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


def test_operational_insights_rbac_and_data(client: TestClient, db_session: Session):
    requester = create_user(db_session, "ins_req@test.com", UserRole.REQUESTER)
    operator = create_user(db_session, "ins_op@test.com", UserRole.OPERATOR)
    manager = create_user(db_session, "ins_mgr@test.com", UserRole.MANAGER)
    admin = create_user(db_session, "ins_adm@test.com", UserRole.ADMINISTRATOR)

    # Requesters and Operators cannot access Operational Insights (403)
    resp_req = client.get("/api/v1/insights", headers=auth_header(requester))
    assert resp_req.status_code == 403

    resp_op = client.get("/api/v1/insights", headers=auth_header(operator))
    assert resp_op.status_code == 403

    # Managers and Admins can access Operational Insights (200)
    resp_mgr = client.get("/api/v1/insights?window=30d", headers=auth_header(manager))
    assert resp_mgr.status_code == 200
    mgr_data = resp_mgr.json()
    assert "total_cases" in mgr_data
    assert "cases_by_status" in mgr_data
    assert "sla_metrics" in mgr_data

    resp_adm = client.get("/api/v1/insights?window=all", headers=auth_header(admin))
    assert resp_adm.status_code == 200


def test_quick_dashboard_stats_endpoint(client: TestClient, db_session: Session):
    operator = create_user(db_session, "dash_op@test.com", UserRole.OPERATOR)

    resp = client.get("/api/v1/insights/dashboard", headers=auth_header(operator))
    assert resp.status_code == 200
    stats = resp.json()
    assert "total_open_cases" in stats
    assert "unassigned_cases" in stats
    assert "active_sla_breaches" in stats


def test_csv_export_endpoint_and_scoping(client: TestClient, db_session: Session):
    requester = create_user(db_session, "csv_req@test.com", UserRole.REQUESTER)
    manager = create_user(db_session, "csv_mgr@test.com", UserRole.MANAGER)

    # 1. Requester exports CSV
    resp_req = client.get("/api/v1/reports/export/cases.csv", headers=auth_header(requester))
    assert resp_req.status_code == 200
    assert resp_req.headers["content-type"].startswith("text/csv")
    assert "assistiq_cases_export.csv" in resp_req.headers.get("content-disposition", "")
    content_req = resp_req.text
    assert "Reference Number,Type,Title,Status" in content_req

    # 2. Manager exports CSV
    resp_mgr = client.get("/api/v1/reports/export/cases.csv", headers=auth_header(manager))
    assert resp_mgr.status_code == 200
    content_mgr = resp_mgr.text
    assert "Reference Number,Type,Title,Status" in content_mgr
