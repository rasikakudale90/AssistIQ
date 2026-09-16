from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.core.dependencies import get_current_user
from backend.db.session import get_db
from backend.models.user import User
from backend.schemas.auth import (
    UserSignup,
    UserLogin,
    GoogleAuthRequest,
    TokenResponse,
    UserResponse,
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    MessageResponse,
)
from backend.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new password-based user",
)
async def signup(data: UserSignup, db: Session = Depends(get_db)) -> UserResponse:
    return await AuthService.signup(db, data)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate with email and password",
)
def login(data: UserLogin, db: Session = Depends(get_db)) -> TokenResponse:
    return AuthService.login(db, data)


@router.post(
    "/google",
    response_model=TokenResponse,
    summary="Authenticate or register with Google OAuth 2.0 / OIDC",
)
async def google_auth(data: GoogleAuthRequest, db: Session = Depends(get_db)) -> TokenResponse:
    return await AuthService.authenticate_google(db, data)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Rotate refresh token and issue new access token",
)
def refresh_token(data: RefreshTokenRequest, db: Session = Depends(get_db)) -> TokenResponse:
    return AuthService.refresh_token(db, data.refresh_token)


@router.get(
    "/verify-email",
    response_model=MessageResponse,
    summary="Verify email address with signed link token",
)
def verify_email(token: str = Query(..., description="Email verification JWT token"), db: Session = Depends(get_db)) -> MessageResponse:
    AuthService.verify_email(db, token)
    return MessageResponse(message="Email verified successfully. You may now sign in and use AssistIQ.")


@router.post(
    "/password-reset/request",
    response_model=MessageResponse,
    summary="Request a password reset link",
)
async def request_password_reset(data: PasswordResetRequest, db: Session = Depends(get_db)) -> MessageResponse:
    await AuthService.request_password_reset(db, data.email)
    return MessageResponse(message="If an account exists with this email, password reset instructions have been sent.")


@router.post(
    "/password-reset/confirm",
    response_model=MessageResponse,
    summary="Confirm password reset with signed token",
)
def confirm_password_reset(data: PasswordResetConfirm, db: Session = Depends(get_db)) -> MessageResponse:
    AuthService.confirm_password_reset(db, data.token, data.new_password)
    return MessageResponse(message="Password reset successfully. You can now login with your new password.")


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user profile",
)
def get_profile(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)
