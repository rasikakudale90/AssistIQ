from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.models import User, UserRole, AuthProvider


def test_auth_signup_and_login_flow(client: TestClient):
    # 1. Signup
    signup_payload = {
        "email": "janedoe@example.com",
        "password": "Password123456!",
        "site": "Headquarters",
        "role": "Requester",
    }
    signup_resp = client.post("/api/v1/auth/signup", json=signup_payload)
    assert signup_resp.status_code == 201
    user_data = signup_resp.json()
    assert user_data["email"] == "janedoe@example.com"
    assert user_data["role"] == "Requester"

    # 2. Duplicate Signup -> 409 Conflict
    dup_resp = client.post("/api/v1/auth/signup", json=signup_payload)
    assert dup_resp.status_code == 409
    assert dup_resp.json()["error"]["code"] == "EMAIL_ALREADY_EXISTS"

    # 3. Login with correct password
    login_payload = {
        "email": "janedoe@example.com",
        "password": "Password123456!",
    }
    login_resp = client.post("/api/v1/auth/login", json=login_payload)
    assert login_resp.status_code == 200
    token_data = login_resp.json()
    assert "access_token" in token_data
    assert "refresh_token" in token_data
    assert token_data["token_type"] == "bearer"

    access_token = token_data["access_token"]
    refresh_token = token_data["refresh_token"]

    # 4. Get Current User Profile via /api/v1/auth/me
    me_resp = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "janedoe@example.com"

    # 5. Refresh Token
    refresh_resp = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_resp.status_code == 200
    new_token_data = refresh_resp.json()
    assert "access_token" in new_token_data

    # 6. Login with wrong password -> 401
    bad_login = client.post(
        "/api/v1/auth/login",
        json={"email": "janedoe@example.com", "password": "WrongPassword123!"},
    )
    assert bad_login.status_code == 401


def test_auth_me_unauthorized(client: TestClient):
    # Missing token -> 401
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "UNAUTHORIZED"

    # Invalid token -> 401
    resp_invalid = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid.fake.token"},
    )
    assert resp_invalid.status_code == 401


def test_google_oauth_collision_with_password_account(client: TestClient):
    # 1. Create a password account
    client.post(
        "/api/v1/auth/signup",
        json={"email": "alice@example.com", "password": "Password123456!"},
    )

    # 2. Attempt Google OAuth signup with same email without linking -> 409 Conflict per SRS §7.4
    from unittest.mock import patch, AsyncMock, MagicMock
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "email": "alice@example.com",
        "sub": "google-sub-987654",
        "email_verified": True,
    }

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        resp = client.post(
            "/api/v1/auth/google",
            json={"id_token": "valid-mocked-google-id-token"},
        )
        assert resp.status_code == 409
        assert resp.json()["error"]["code"] == "ACCOUNT_COLLISION_CONFLICT"


def test_google_oauth_new_user_success(client: TestClient):
    from unittest.mock import patch, AsyncMock, MagicMock
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "email": "brandnew.google@example.com",
        "sub": "google-sub-112233",
        "email_verified": True,
    }

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        resp = client.post(
            "/api/v1/auth/google",
            json={"id_token": "valid-new-google-id-token"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["user"]["email"] == "brandnew.google@example.com"
        assert data["user"]["auth_provider"] == "google"
        assert data["user"]["email_verified"] is True


def test_email_verification_flow(client: TestClient):
    from backend.core.security import create_email_verification_token

    # Create unverified user
    client.post(
        "/api/v1/auth/signup",
        json={"email": "unverified@example.com", "password": "Password123456!"},
    )

    # Verify with token
    token = create_email_verification_token("unverified@example.com")
    verify_resp = client.get(f"/api/v1/auth/verify-email?token={token}")
    assert verify_resp.status_code == 200
    assert verify_resp.json()["success"] is True
