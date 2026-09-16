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
from sqlalchemy.orm import relationship

from backend.db.session import Base
from backend.models.enums import Priority


def generate_uuid() -> str:
    return str(uuid.uuid4())


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


class SLA(Base):
    __tablename__ = "slas"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    case_id = Column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    priority = Column(
        SQLEnum(Priority, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )
    # 24/7 elapsed wall-clock time deadlines (SRS §4.3)
    target_response_at = Column(DateTime(timezone=True), nullable=False, index=True)
    target_resolve_at = Column(DateTime(timezone=True), nullable=False, index=True)

    response_breached = Column(Boolean, default=False, nullable=False, index=True)
    resolve_breached = Column(Boolean, default=False, nullable=False, index=True)

    responded_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    paused_reason = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)

    # Relationships
    case = relationship("Case", back_populates="sla")

    __table_args__ = (
        Index("ix_sla_breach_monitoring", "resolve_breached", "target_resolve_at"),
    )
