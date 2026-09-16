import pytest
from datetime import timedelta
from backend.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    create_email_verification_token,
    create_password_reset_token,
    decode_token,
)
from backend.core.errors import UnauthorizedException


def test_password_hashing():
    pw = "SuperSecretPassword123!"
    hashed = hash_password(pw)
    assert hashed != pw
    assert verify_password(pw, hashed) is True
    assert verify_password("WrongPassword", hashed) is False
    assert verify_password(pw, "") is False


def test_jwt_access_and_refresh_tokens():
    sub = "user-uuid-1234"
    role = "Operator"
    
    access_token = create_access_token(sub, role)
    payload = decode_token(access_token)
    assert payload["sub"] == sub
    assert payload["role"] == role
    assert payload["type"] == "access"

    refresh_token = create_refresh_token(sub)
    r_payload = decode_token(refresh_token)
    assert r_payload["sub"] == sub
    assert r_payload["type"] == "refresh"


def test_token_expiration():
    sub = "user-uuid-expired"
    # Token expired 1 minute ago
    expired_token = create_access_token(sub, "Requester", expires_delta=timedelta(minutes=-1))
    
    with pytest.raises(UnauthorizedException) as exc_info:
        decode_token(expired_token)
    assert "expired" in str(exc_info.value.message).lower()


def test_email_verification_and_password_reset_tokens():
    email = "test.user@example.com"
    v_token = create_email_verification_token(email)
    v_payload = decode_token(v_token)
    assert v_payload["sub"] == email
    assert v_payload["type"] == "email_verification"

    r_token = create_password_reset_token(email)
    r_payload = decode_token(r_token)
    assert r_payload["sub"] == email
    assert r_payload["type"] == "password_reset"
