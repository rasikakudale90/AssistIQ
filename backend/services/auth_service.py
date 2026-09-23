import logging
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
import httpx

from backend.core.config import settings
from backend.core.errors import (
    UnauthorizedException,
    ConflictException,
    NotFoundException,
    ValidationException,
)
from backend.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    create_email_verification_token,
    create_password_reset_token,
    decode_token,
)
from backend.models.enums import UserRole, AuthProvider, AvailabilityStatus
from backend.models.user import User
from backend.providers.notifications import get_notification_provider
from backend.schemas.auth import (
    UserSignup,
    UserLogin,
    GoogleAuthRequest,
    TokenResponse,
    UserResponse,
)

logger = logging.getLogger("assistiq.auth_service")


class AuthService:
    @staticmethod
    async def signup(db: Session, data: UserSignup) -> UserResponse:
        # Check if email is already taken
        existing_user = db.query(User).filter(User.email == data.email.lower()).first()
        if existing_user:
            raise ConflictException(
                message="An account with this email address already exists.",
                code="EMAIL_ALREADY_EXISTS",
            )

        # Auto-verify users upon registration for immediate self-service access
        is_verified = True if (settings.ENVIRONMENT == "local" or not settings.BREVO_API_KEY or not getattr(settings, "REQUIRE_EMAIL_VERIFICATION", False)) else True

        user = User(
            email=data.email.lower(),
            password_hash=hash_password(data.password),
            auth_provider=AuthProvider.PASSWORD,
            role=data.role or UserRole.REQUESTER,
            site=data.site,
            availability_status=AvailabilityStatus.AVAILABLE,
            email_verified=is_verified,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Send verification email if not verified
        if not is_verified and settings.BREVO_API_KEY:
            verification_token = create_email_verification_token(user.email)
            verify_url = f"http://{settings.HOST}:{settings.PORT}/api/v1/auth/verify-email?token={verification_token}"
            html_body = f"""
            <h2>Welcome to AssistIQ!</h2>
            <p>Please verify your email address by clicking the link below:</p>
            <p><a href="{verify_url}">Verify Email Address</a></p>
            <p>If you did not request this, please ignore this email.</p>
            """
            provider = get_notification_provider()
            await provider.send_email(
                to_email=user.email,
                subject="Verify your AssistIQ Account",
                html_body=html_body,
                text_body=f"Verify your email here: {verify_url}",
            )

        return UserResponse.model_validate(user)

    @staticmethod
    def login(db: Session, data: UserLogin) -> TokenResponse:
        user = db.query(User).filter(User.email == data.email.lower(), User.deleted_at.is_(None)).first()
        if not user or not user.password_hash or not verify_password(data.password, user.password_hash):
            raise UnauthorizedException("Invalid email or password")

        # In production, require email verification only if strict verification is configured
        if settings.ENVIRONMENT in ["staging", "production"] and getattr(settings, "REQUIRE_EMAIL_VERIFICATION", False) and settings.BREVO_API_KEY and not user.email_verified:
            raise UnauthorizedException("Please verify your email address before logging in.")

        access_token = create_access_token(subject=user.id, role=user.role.value)
        refresh_token = create_refresh_token(subject=user.id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserResponse.model_validate(user),
        )

    @staticmethod
    async def authenticate_google(db: Session, data: GoogleAuthRequest) -> TokenResponse:
        """
        Exchanges Google OAuth token/code for user profile and returns JWT tokens (SRS §3.3a, §7.4).
        """
        google_user_info: Dict[str, Any] = {}

        if data.id_token:
            # Verify ID token via Google TokenInfo API
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={data.id_token}")
                if resp.status_code != 200:
                    raise UnauthorizedException("Invalid Google ID token")
                google_user_info = resp.json()
        elif data.code:
            # Exchange authorization code for tokens
            async with httpx.AsyncClient(timeout=10.0) as client:
                token_url = "https://oauth2.googleapis.com/token"
                payload = {
                    "code": data.code,
                    "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
                    "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
                    "redirect_uri": data.redirect_uri or "http://localhost:8000/api/v1/auth/google/callback",
                    "grant_type": "authorization_code",
                }
                token_resp = await client.post(token_url, data=payload)
                if token_resp.status_code != 200:
                    raise UnauthorizedException("Failed to exchange Google authorization code")
                
                access_token = token_resp.json().get("access_token")
                userinfo_resp = await client.get(
                    "https://www.googleapis.com/oauth2/v3/userinfo",
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                if userinfo_resp.status_code != 200:
                    raise UnauthorizedException("Failed to fetch Google user profile")
                google_user_info = userinfo_resp.json()
        else:
            raise ValidationException("Either 'id_token' or 'code' must be provided for Google authentication")

        email = google_user_info.get("email", "").lower()
        sub = google_user_info.get("sub")

        if not email or not sub:
            raise UnauthorizedException("Google response did not contain valid email or subject ID")

        # 1. Lookup by oauth_subject_id
        user = db.query(User).filter(User.oauth_subject_id == sub, User.deleted_at.is_(None)).first()

        if not user:
            # 2. Check if a password-based user exists with the same email
            existing_user = db.query(User).filter(User.email == email, User.deleted_at.is_(None)).first()
            if existing_user and existing_user.auth_provider == AuthProvider.PASSWORD:
                # Per SRS §7.4: No silent account merging — raise 409 Conflict
                raise ConflictException(
                    message="An account with this email already exists using password authentication. Please sign in with your password.",
                    code="ACCOUNT_COLLISION_CONFLICT",
                )

            # 3. Create new Google OAuth user (auto-verified per SRS §3.3a)
            user = User(
                email=email,
                auth_provider=AuthProvider.GOOGLE,
                oauth_subject_id=sub,
                role=UserRole.REQUESTER,
                email_verified=True,
                availability_status=AvailabilityStatus.AVAILABLE,
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        access_token = create_access_token(subject=user.id, role=user.role.value)
        refresh_token = create_refresh_token(subject=user.id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserResponse.model_validate(user),
        )

    @staticmethod
    def refresh_token(db: Session, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid token type. Expected refresh token.")

        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()
        if not user:
            raise UnauthorizedException("User associated with this token not found")

        new_access_token = create_access_token(subject=user.id, role=user.role.value)
        new_refresh_token = create_refresh_token(subject=user.id)

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            user=UserResponse.model_validate(user),
        )

    @staticmethod
    def verify_email(db: Session, token: str) -> bool:
        payload = decode_token(token)
        if payload.get("type") != "email_verification":
            raise UnauthorizedException("Invalid verification token")

        email = payload.get("sub")
        user = db.query(User).filter(User.email == email, User.deleted_at.is_(None)).first()
        if not user:
            raise NotFoundException("User not found")

        user.email_verified = True
        db.commit()
        return True

    @staticmethod
    async def request_password_reset(db: Session, email: str) -> bool:
        user = db.query(User).filter(User.email == email.lower(), User.deleted_at.is_(None)).first()
        if not user or not user.password_hash:
            # Silently return True to prevent user enumeration
            return True

        reset_token = create_password_reset_token(user.email)
        reset_url = f"http://{settings.HOST}:{settings.PORT}/reset-password?token={reset_token}"
        html_body = f"""
        <h2>Password Reset Request</h2>
        <p>Click the link below to reset your password:</p>
        <p><a href="{reset_url}">Reset Password</a></p>
        <p>If you did not request this, please ignore this email.</p>
        """
        provider = get_notification_provider()
        await provider.send_email(
            to_email=user.email,
            subject="Reset your AssistIQ Password",
            html_body=html_body,
            text_body=f"Reset your password here: {reset_url}",
        )
        return True

    @staticmethod
    def confirm_password_reset(db: Session, token: str, new_password: str) -> bool:
        payload = decode_token(token)
        if payload.get("type") != "password_reset":
            raise UnauthorizedException("Invalid password reset token")

        email = payload.get("sub")
        user = db.query(User).filter(User.email == email, User.deleted_at.is_(None)).first()
        if not user:
            raise NotFoundException("User not found")

        user.password_hash = hash_password(new_password)
        db.commit()
        return True
