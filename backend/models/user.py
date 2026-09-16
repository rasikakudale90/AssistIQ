import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.db.session import Base
from backend.models.enums import UserRole, AuthProvider, AvailabilityStatus


def generate_uuid() -> str:
    return str(uuid.uuid4())


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Team(Base):
    __tablename__ = "teams"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)
    lead_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL", use_alter=True, name="fk_teams_lead_id_users"),
        nullable=True,
    )
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    # Relationships
    members = relationship("User", back_populates="team", foreign_keys="User.team_id")
    lead = relationship("User", foreign_keys=[lead_id], post_update=True)
    cases = relationship("Case", back_populates="team", foreign_keys="Case.team_id")


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)  # Nullable for OAuth-only signups
    auth_provider = Column(
        SQLEnum(AuthProvider, values_callable=lambda obj: [e.value for e in obj]),
        default=AuthProvider.PASSWORD,
        nullable=False,
    )
    oauth_subject_id = Column(String(255), unique=True, nullable=True, index=True)
    role = Column(
        SQLEnum(UserRole, values_callable=lambda obj: [e.value for e in obj]),
        default=UserRole.REQUESTER,
        nullable=False,
        index=True,
    )
    team_id = Column(String(36), ForeignKey("teams.id", ondelete="SET NULL"), nullable=True, index=True)
    site = Column(String(100), nullable=True)  # Feeds smart assignment (location matching)
    availability_status = Column(
        SQLEnum(AvailabilityStatus, values_callable=lambda obj: [e.value for e in obj]),
        default=AvailabilityStatus.AVAILABLE,
        nullable=False,
    )
    email_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete

    # Relationships
    team = relationship("Team", back_populates="members", foreign_keys=[team_id])
    requested_cases = relationship("Case", back_populates="requester", foreign_keys="Case.requester_id")
    owned_cases = relationship("Case", back_populates="owner", foreign_keys="Case.owner_id")
    messages = relationship("Message", back_populates="author", foreign_keys="Message.author_id")
    uploaded_attachments = relationship("Attachment", back_populates="uploader", foreign_keys="Attachment.uploaded_by")

    __table_args__ = (
        Index("ix_users_role_availability", "role", "availability_status"),
        Index("ix_users_team_role", "team_id", "role"),
    )
