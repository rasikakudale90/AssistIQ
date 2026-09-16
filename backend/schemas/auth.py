from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

from backend.models.enums import UserRole, AuthProvider, AvailabilityStatus


class UserSignup(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str = Field(..., min_length=12, description="Minimum password length 12 characters per SRS §7.4")
    site: Optional[str] = Field(None, max_length=100)
    role: Optional[UserRole] = Field(UserRole.REQUESTER, description="Initial role assignment")


class UserLogin(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str


class GoogleAuthRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id_token: Optional[str] = None
    code: Optional[str] = None
    redirect_uri: Optional[str] = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    role: UserRole
    auth_provider: AuthProvider
    team_id: Optional[str] = None
    site: Optional[str] = None
    availability_status: AvailabilityStatus
    email_verified: bool
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    refresh_token: str


class PasswordResetRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str
    new_password: str = Field(..., min_length=12)


class MessageResponse(BaseModel):
    message: str
    success: bool = True
