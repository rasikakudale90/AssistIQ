import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    JSON,
)
from sqlalchemy.orm import relationship

from backend.db.session import Base
from backend.models.enums import ApprovalDecision, KnowledgeState


def generate_uuid() -> str:
    return str(uuid.uuid4())


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    actor_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)  # Null for system/sweep actions
    action = Column(String(100), nullable=False, index=True)  # e.g. "status_change", "assignment", "priority_override", "escalation", "reopened"
    target_type = Column(String(50), nullable=False, index=True)  # "case", "user", "team", "article"
    target_id = Column(String(36), nullable=False, index=True)
    before_value = Column(JSON, nullable=True)
    after_value = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False, index=True)

    # Relationships
    actor = relationship("User", foreign_keys=[actor_id])

    __table_args__ = (
        Index("ix_audit_target", "target_type", "target_id", "created_at"),
    )


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    case_id = Column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    approver_id = Column(String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    decision = Column(
        SQLEnum(ApprovalDecision, values_callable=lambda obj: [e.value for e in obj]),
        default=ApprovalDecision.PENDING,
        nullable=False,
        index=True,
    )
    reason = Column(Text, nullable=True)
    decided_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    # Relationships
    case = relationship("Case", back_populates="approvals")
    approver = relationship("User", foreign_keys=[approver_id])


class KnowledgeArticle(Base):
    __tablename__ = "knowledge_articles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False, index=True)
    body = Column(Text, nullable=False)
    category = Column(String(100), nullable=False, index=True)
    owner_id = Column(String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    state = Column(
        SQLEnum(KnowledgeState, values_callable=lambda obj: [e.value for e in obj]),
        default=KnowledgeState.PUBLISHED,
        nullable=False,
        index=True,
    )
    review_date = Column(DateTime(timezone=True), nullable=True)
    source_case_id = Column(String(36), ForeignKey("cases.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)

    # Relationships
    owner = relationship("User", foreign_keys=[owner_id])
    source_case = relationship("Case", foreign_keys=[source_case_id])
