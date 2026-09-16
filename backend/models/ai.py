import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Text,
    Float,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    JSON,
)
from sqlalchemy.orm import relationship

from backend.db.session import Base
from backend.models.enums import (
    ConfidenceLevel,
    RiskLevel,
    EscalationReason,
    EscalationStatus,
    DraftType,
    DraftStatus,
)


def generate_uuid() -> str:
    return str(uuid.uuid4())


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


class AITriageResult(Base):
    __tablename__ = "ai_triage_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    case_id = Column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    suggested_category = Column(String(100), nullable=True)
    suggested_severity = Column(String(50), nullable=True)
    suggested_priority = Column(String(10), nullable=True)
    confidence_level = Column(
        SQLEnum(ConfidenceLevel, values_callable=lambda obj: [e.value for e in obj]),
        default=ConfidenceLevel.MODERATE,
        nullable=False,
    )
    confidence_score = Column(Float, nullable=True)  # Internal use only (SRS §4)
    supporting_factors = Column(JSON, default=list, nullable=False)
    missing_info = Column(JSON, default=list, nullable=False)
    suggested_team = Column(String(100), nullable=True)
    recommended_next_action = Column(Text, nullable=True)
    related_case_ids = Column(JSON, default=list, nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    # Relationships
    case = relationship("Case", back_populates="triage_result")


class CaseSummary(Base):
    __tablename__ = "case_summaries"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    case_id = Column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    summary_text = Column(Text, nullable=False)
    last_source_message_id = Column(String(36), nullable=True)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)

    # Relationships
    case = relationship("Case", back_populates="summary")


class CaseRiskAssessment(Base):
    __tablename__ = "case_risk_assessments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    case_id = Column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    risk_level = Column(
        SQLEnum(RiskLevel, values_callable=lambda obj: [e.value for e in obj]),
        default=RiskLevel.LOW,
        nullable=False,
        index=True,
    )
    # JSON containing: inactivity_hours, follow_up_count, reassignment_count, missing_info_flag, hours_to_deadline, reopen_count
    signals = Column(JSON, default=dict, nullable=False)
    computed_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False, index=True)

    # Relationships
    case = relationship("Case", back_populates="risk_assessments")

    __table_args__ = (
        Index("ix_risk_case_computed", "case_id", "computed_at"),
    )


class EscalationEvent(Base):
    __tablename__ = "escalation_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    case_id = Column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    trigger_reason = Column(
        SQLEnum(EscalationReason, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        index=True,
    )
    escalated_to = Column(String(36), nullable=True)  # user_id or role
    escalated_by = Column(String(36), default="system", nullable=False)  # "system" or user_id
    status = Column(
        SQLEnum(EscalationStatus, values_callable=lambda obj: [e.value for e in obj]),
        default=EscalationStatus.OPEN,
        nullable=False,
        index=True,
    )
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False, index=True)

    # Relationships
    case = relationship("Case", back_populates="escalations")


class CommunicationDraft(Base):
    __tablename__ = "communication_drafts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    case_id = Column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    draft_type = Column(
        SQLEnum(DraftType, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        index=True,
    )
    body = Column(Text, nullable=False)
    status = Column(
        SQLEnum(DraftStatus, values_callable=lambda obj: [e.value for e in obj]),
        default=DraftStatus.DRAFT,
        nullable=False,
        index=True,
    )
    reviewed_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    sent_message_id = Column(String(36), ForeignKey("messages.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    # Relationships
    case = relationship("Case", back_populates="communication_drafts")
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    sent_message = relationship("Message", foreign_keys=[sent_message_id])
