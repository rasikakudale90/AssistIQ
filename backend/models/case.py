import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship

from backend.db.session import Base
from backend.models.enums import CaseType, CaseStatus, Priority, CaseRelationshipType


def generate_uuid() -> str:
    return str(uuid.uuid4())


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Case(Base):
    __tablename__ = "cases"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    reference_number = Column(String(50), unique=True, nullable=False, index=True)
    type = Column(
        SQLEnum(CaseType, values_callable=lambda obj: [e.value for e in obj]),
        default=CaseType.INCIDENT,
        nullable=False,
        index=True,
    )
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)  # Immutable original description
    status = Column(
        SQLEnum(CaseStatus, values_callable=lambda obj: [e.value for e in obj]),
        default=CaseStatus.NEW,
        nullable=False,
        index=True,
    )
    priority = Column(
        SQLEnum(Priority, values_callable=lambda obj: [e.value for e in obj]),
        default=Priority.P3,
        nullable=False,
        index=True,
    )
    requester_id = Column(String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    owner_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    team_id = Column(String(36), ForeignKey("teams.id", ondelete="SET NULL"), nullable=True, index=True)
    site = Column(String(100), nullable=True, index=True)
    service_id = Column(String(100), nullable=True, index=True)

    # Optimistic concurrency locking (SRS §7.12)
    version = Column(Integer, default=1, nullable=False)

    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete

    # Relationships
    requester = relationship("User", back_populates="requested_cases", foreign_keys=[requester_id])
    owner = relationship("User", back_populates="owned_cases", foreign_keys=[owner_id])
    team = relationship("Team", back_populates="cases", foreign_keys=[team_id])

    messages = relationship("Message", back_populates="case", cascade="all, delete-orphan", order_by="Message.created_at")
    attachments = relationship("Attachment", back_populates="case", cascade="all, delete-orphan")
    sla = relationship("SLA", back_populates="case", uselist=False, cascade="all, delete-orphan")
    triage_result = relationship("AITriageResult", back_populates="case", uselist=False, cascade="all, delete-orphan")
    summary = relationship("CaseSummary", back_populates="case", uselist=False, cascade="all, delete-orphan")
    risk_assessments = relationship("CaseRiskAssessment", back_populates="case", cascade="all, delete-orphan", order_by="desc(CaseRiskAssessment.computed_at)")
    escalations = relationship("EscalationEvent", back_populates="case", cascade="all, delete-orphan", order_by="desc(EscalationEvent.created_at)")
    communication_drafts = relationship("CommunicationDraft", back_populates="case", cascade="all, delete-orphan")
    approvals = relationship("Approval", back_populates="case", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_cases_status_priority", "status", "priority"),
        Index("ix_cases_owner_status", "owner_id", "status"),
        Index("ix_cases_team_status", "team_id", "status"),
    )


class CaseRelationship(Base):
    __tablename__ = "case_relationships"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    case_id = Column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    related_case_id = Column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    relationship_type = Column(
        SQLEnum(CaseRelationshipType, values_callable=lambda obj: [e.value for e in obj]),
        default=CaseRelationshipType.RELATED_TO,
        nullable=False,
    )
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    __table_args__ = (
        Index("ix_case_rel_unique", "case_id", "related_case_id", "relationship_type", unique=True),
    )
