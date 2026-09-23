from typing import Callable, List, Optional
from fastapi import Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.core.errors import (
    UnauthorizedException,
    PermissionDeniedException,
    NotFoundException,
)
from backend.core.security import decode_token
from backend.db.session import get_db
from backend.models.enums import UserRole
from backend.models.user import User

security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Extracts and validates JWT Bearer token, retrieving the authenticated user from the database.
    Raises 401 Unauthorized if missing, expired, or invalid.
    """
    if not credentials or not credentials.credentials:
        raise UnauthorizedException("Authentication token required", headers={"WWW-Authenticate": "Bearer"})

    token = credentials.credentials
    payload = decode_token(token)

    if payload.get("type") != "access":
        raise UnauthorizedException("Invalid token type. Expected access token.")

    user_id: Optional[str] = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Token payload missing subject identifier")

    user = db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()
    if not user:
        raise UnauthorizedException("User associated with this token no longer exists")

    return user


def require_verified_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Ensures the authenticated user is active and eligible to access services.
    Permits instant self-service case creation for all registered roles.
    """
    if not current_user.email_verified and settings.ENVIRONMENT in ["staging", "production"] and getattr(settings, "REQUIRE_EMAIL_VERIFICATION", False) and settings.BREVO_API_KEY:
        raise PermissionDeniedException("Email verification required before accessing this service.")
    return current_user


def require_roles(*allowed_roles: UserRole) -> Callable[[User], User]:
    """
    Role-Based Access Control (RBAC) dependency factory.
    Verifies that the authenticated user possesses one of the allowed roles.
    """
    def role_checker(current_user: User = Depends(require_verified_user)) -> User:
        if current_user.role not in allowed_roles:
            raise PermissionDeniedException(
                f"Access forbidden: User role '{current_user.role.value}' does not have permission for this resource."
            )
        return current_user

    return role_checker


# Role helper dependencies
require_admin = require_roles(UserRole.ADMINISTRATOR)
require_manager = require_roles(UserRole.MANAGER, UserRole.ADMINISTRATOR)
require_team_lead = require_roles(UserRole.TEAM_LEAD, UserRole.MANAGER, UserRole.ADMINISTRATOR)
require_operator = require_roles(UserRole.OPERATOR, UserRole.TEAM_LEAD, UserRole.MANAGER, UserRole.ADMINISTRATOR)
require_staff = require_roles(UserRole.OPERATOR, UserRole.TEAM_LEAD, UserRole.MANAGER, UserRole.ADMINISTRATOR)
require_requester = require_roles(UserRole.REQUESTER, UserRole.OPERATOR, UserRole.TEAM_LEAD, UserRole.MANAGER, UserRole.ADMINISTRATOR)
