import io
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.core.security import create_access_token
from backend.models import User, UserRole, Case, CaseStatus, Message, MessageVisibility


def create_user_and_headers(db: Session, email: str, role: UserRole) -> tuple[User, dict]:
    user = User(email=email, role=role, email_verified=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(user.id, user.role.value)
    return user, {"Authorization": f"Bearer {token}"}


def test_message_visibility_isolation(client: TestClient, db_session: Session):
    requester, req_headers = create_user_and_headers(db_session, "msg_req@test.com", UserRole.REQUESTER)
    operator, op_headers = create_user_and_headers(db_session, "msg_op@test.com", UserRole.OPERATOR)

    # 1. Create a case
    case_resp = client.post(
        "/api/v1/cases",
        json={"type": "Incident", "title": "Monitor flickering", "description": "HDMI loose."},
        headers=req_headers,
    )
    case_id = case_resp.json()["id"]

    # 2. Operator posts a public message
    client.post(
        f"/api/v1/cases/{case_id}/messages",
        json={"body": "We have ordered a new HDMI cable for you.", "visibility": "requester_visible"},
        headers=op_headers,
    )

    # 3. Operator posts an internal staff note
    client.post(
        f"/api/v1/cases/{case_id}/messages",
        json={"body": "Internal Note: Checked stock in room 402.", "visibility": "internal_only"},
        headers=op_headers,
    )

    # 4. Requester views messages -> MUST ONLY see 1 message (requester_visible)
    req_view = client.get(f"/api/v1/cases/{case_id}/messages", headers=req_headers)
    assert req_view.status_code == 200
    req_messages = req_view.json()
    assert len(req_messages) == 1
    assert req_messages[0]["visibility"] == "requester_visible"

    # 5. Operator views messages -> MUST see both messages (2)
    op_view = client.get(f"/api/v1/cases/{case_id}/messages", headers=op_headers)
    assert op_view.status_code == 200
    assert len(op_view.json()) == 2


def test_requester_cannot_post_internal_note(client: TestClient, db_session: Session):
    requester, req_headers = create_user_and_headers(db_session, "hack_req@test.com", UserRole.REQUESTER)

    case_resp = client.post(
        "/api/v1/cases",
        json={"type": "Incident", "title": "Test case", "description": "Test description."},
        headers=req_headers,
    )
    case_id = case_resp.json()["id"]

    # Requester tries to post internal note -> 403 Forbidden
    resp = client.post(
        f"/api/v1/cases/{case_id}/messages",
        json={"body": "Secret note", "visibility": "internal_only"},
        headers=req_headers,
    )
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "PERMISSION_DENIED"


def test_requester_reply_auto_advances_awaiting_requester(client: TestClient, db_session: Session):
    requester, req_headers = create_user_and_headers(db_session, "reply_req@test.com", UserRole.REQUESTER)
    operator, op_headers = create_user_and_headers(db_session, "reply_op@test.com", UserRole.OPERATOR)

    case_resp = client.post(
        "/api/v1/cases",
        json={"type": "Incident", "title": "Software error", "description": "App crashes."},
        headers=req_headers,
    )
    case_id = case_resp.json()["id"]
    version = case_resp.json()["version"]

    # Move to InAssessment -> Assigned -> AwaitingRequester
    client.patch(f"/api/v1/cases/{case_id}/status", json={"status": "InAssessment", "version": version}, headers=op_headers)
    client.patch(f"/api/v1/cases/{case_id}/status", json={"status": "Assigned", "version": version + 1}, headers=op_headers)
    client.patch(f"/api/v1/cases/{case_id}/status", json={"status": "AwaitingRequester", "version": version + 2}, headers=op_headers)

    # Requester posts a reply
    client.post(
        f"/api/v1/cases/{case_id}/messages",
        json={"body": "Here is the error code: ERR_502", "visibility": "requester_visible"},
        headers=req_headers,
    )

    # Verify case status automatically advanced to Assigned (SRS §6.1)
    case_check = client.get(f"/api/v1/cases/{case_id}", headers=req_headers).json()
    assert case_check["status"] == "Assigned"


def test_attachment_upload_and_download(client: TestClient, db_session: Session):
    requester, req_headers = create_user_and_headers(db_session, "att_req@test.com", UserRole.REQUESTER)

    case_resp = client.post(
        "/api/v1/cases",
        json={"type": "Incident", "title": "Screenshot issue", "description": "Attached screenshot."},
        headers=req_headers,
    )
    case_id = case_resp.json()["id"]

    # 1. Upload valid PNG image (starts with PNG magic bytes)
    png_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4"
    files = {"file": ("error_screenshot.png", io.BytesIO(png_bytes), "image/png")}

    upload_resp = client.post(
        f"/api/v1/cases/{case_id}/attachments",
        files=files,
        headers=req_headers,
    )
    assert upload_resp.status_code == 201
    att_data = upload_resp.json()
    assert att_data["file_name"] == "error_screenshot.png"
    attachment_id = att_data["id"]

    # 2. List attachments
    list_resp = client.get(f"/api/v1/cases/{case_id}/attachments", headers=req_headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()["items"]) == 1

    # 3. Download attachment
    download_resp = client.get(
        f"/api/v1/cases/{case_id}/attachments/{attachment_id}/download",
        headers=req_headers,
    )
    assert download_resp.status_code == 200
    assert download_resp.content == png_bytes


def test_attachment_magic_byte_rejection(client: TestClient, db_session: Session):
    requester, req_headers = create_user_and_headers(db_session, "spoof_req@test.com", UserRole.REQUESTER)

    case_resp = client.post(
        "/api/v1/cases",
        json={"type": "Incident", "title": "Spoof test", "description": "Test spoofing."},
        headers=req_headers,
    )
    case_id = case_resp.json()["id"]

    # Upload malicious executable bytes disguised as .png
    fake_png = b"MZ\x90\x00\x03\x00\x00\x00WindowsExecutablePayload"
    files = {"file": ("virus.png", io.BytesIO(fake_png), "image/png")}

    upload_resp = client.post(
        f"/api/v1/cases/{case_id}/attachments",
        files=files,
        headers=req_headers,
    )
    assert upload_resp.status_code == 422
    assert "magic byte mismatch" in upload_resp.json()["error"]["message"].lower()


def test_idempotency_key_caching(client: TestClient, db_session: Session):
    requester, req_headers = create_user_and_headers(db_session, "idem_req@test.com", UserRole.REQUESTER)

    case_resp = client.post(
        "/api/v1/cases",
        json={"type": "Incident", "title": "Idempotent test", "description": "Test idempotency."},
        headers=req_headers,
    )
    case_id = case_resp.json()["id"]

    headers_with_key = {**req_headers, "Idempotency-Key": "unique-uuid-key-9999"}

    # 1. First post
    resp1 = client.post(
        f"/api/v1/cases/{case_id}/messages",
        json={"body": "Idempotent message content", "visibility": "requester_visible"},
        headers=headers_with_key,
    )
    assert resp1.status_code == 201
    msg1_id = resp1.json()["id"]

    # 2. Second post with exact same key -> should return cached response without duplicate row
    resp2 = client.post(
        f"/api/v1/cases/{case_id}/messages",
        json={"body": "Idempotent message content", "visibility": "requester_visible"},
        headers=headers_with_key,
    )
    assert resp2.status_code == 201
    assert resp2.json()["id"] == msg1_id

    # 3. Check DB messages count is exactly 1
    messages_list = client.get(f"/api/v1/cases/{case_id}/messages", headers=req_headers).json()
    assert len(messages_list) == 1
