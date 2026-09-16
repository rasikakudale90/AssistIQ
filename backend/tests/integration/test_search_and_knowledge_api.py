from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.core.security import create_access_token
from backend.models import User, UserRole, Case, KnowledgeArticle, KnowledgeState


def create_user_and_headers(db: Session, email: str, role: UserRole) -> tuple[User, dict]:
    user = User(email=email, role=role, email_verified=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(user.id, user.role.value)
    return user, {"Authorization": f"Bearer {token}"}


def test_knowledge_article_lifecycle_and_rbac(client: TestClient, db_session: Session):
    operator, op_headers = create_user_and_headers(db_session, "kb_op@test.com", UserRole.OPERATOR)
    requester, req_headers = create_user_and_headers(db_session, "kb_req@test.com", UserRole.REQUESTER)

    # 1. Requester cannot create an article -> 403
    req_create = client.post(
        "/api/v1/knowledge",
        json={"title": "Hacker Guide", "body": "How to bypass filters", "category": "Security"},
        headers=req_headers,
    )
    assert req_create.status_code == 403

    # 2. Operator creates a draft article
    draft_resp = client.post(
        "/api/v1/knowledge",
        json={
            "title": "Wi-Fi Configuration Steps",
            "body": "Detailed steps to connect to Corporate-Secure WPA3 Enterprise Wi-Fi.",
            "category": "Network",
            "state": "draft",
        },
        headers=op_headers,
    )
    assert draft_resp.status_code == 201
    draft_id = draft_resp.json()["id"]

    # 3. Requester tries to view draft article -> 404 Not Found
    req_view_draft = client.get(f"/api/v1/knowledge/{draft_id}", headers=req_headers)
    assert req_view_draft.status_code == 404

    # 4. Operator publishes the article
    pub_resp = client.put(
        f"/api/v1/knowledge/{draft_id}",
        json={"state": "published"},
        headers=op_headers,
    )
    assert pub_resp.status_code == 200
    assert pub_resp.json()["state"] == "published"

    # 5. Requester can now view the published article -> 200 OK
    req_view_pub = client.get(f"/api/v1/knowledge/{draft_id}", headers=req_headers)
    assert req_view_pub.status_code == 200
    assert req_view_pub.json()["title"] == "Wi-Fi Configuration Steps"

    # 6. Operator archives the article
    arch_resp = client.delete(f"/api/v1/knowledge/{draft_id}", headers=op_headers)
    assert arch_resp.status_code == 200


def test_similar_case_candidate_detection(client: TestClient, db_session: Session):
    requester, req_headers = create_user_and_headers(db_session, "sim_req@test.com", UserRole.REQUESTER)

    # 1. Create an existing case
    client.post(
        "/api/v1/cases",
        json={
            "type": "Incident",
            "title": "Outlook crash on Windows 11 startup",
            "description": "Outlook throws an application error 0x80040154 when launching on Windows 11.",
        },
        headers=req_headers,
    )

    # 2. Detect similar cases with a slightly different wording
    detect_resp = client.post(
        "/api/v1/cases/detect-similar",
        json={
            "title": "Outlook crashing when starting computer",
            "description": "Application crash 0x80040154 on Windows 11 boot up.",
        },
        headers=req_headers,
    )
    assert detect_resp.status_code == 200
    data = detect_resp.json()
    assert data["total"] >= 1
    top_candidate = data["candidates"][0]
    assert "Outlook" in top_candidate["title"]
    assert top_candidate["similarity_score"] > 0.25


def test_unified_search(client: TestClient, db_session: Session):
    operator, op_headers = create_user_and_headers(db_session, "search_op@test.com", UserRole.OPERATOR)

    # 1. Create a case
    client.post(
        "/api/v1/cases",
        json={
            "type": "Incident",
            "title": "VPN connection error 800",
            "description": "Cannot connect to Cisco AnyConnect VPN gateway.",
        },
        headers=op_headers,
    )

    # 2. Create a published knowledge article
    client.post(
        "/api/v1/knowledge",
        json={
            "title": "VPN Gateway Troubleshooting Guide",
            "body": "Steps to resolve VPN error 800 and certificate issues.",
            "category": "Network",
            "state": "published",
        },
        headers=op_headers,
    )

    # 3. Perform unified search for "VPN"
    search_resp = client.get("/api/v1/search?q=VPN", headers=op_headers)
    assert search_resp.status_code == 200
    results = search_resp.json()["results"]
    assert len(results) >= 2

    types = {r["type"] for r in results}
    assert "case" in types
    assert "knowledge" in types
