import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    Boolean,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship

from backend.db.session import Base
from backend.models.enums import MessageVisibility


def generate_uuid() -> str:
    return str(uuid.uuid4())


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    case_id = Column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    author_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    body = Column(Text, nullable=False)
    visibility = Column(
        SQLEnum(MessageVisibility, values_callable=lambda obj: [e.value for e in obj]),
        default=MessageVisibility.REQUESTER_VISIBLE,
        nullable=False,
        index=True,
    )
    ai_generated = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False, index=True)

    # Relationships
    case = relationship("Case", back_populates="messages")
    author = relationship("User", back_populates="messages")

    __table_args__ = (
        Index("ix_messages_case_visibility", "case_id", "visibility"),
    )


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    case_id = Column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    storage_path = Column(String(500), nullable=False)  # Path in Supabase Storage
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(100), nullable=False)     # MIME type
    file_size = Column(Integer, nullable=False)         # Bytes (max 10MB per SRS §7.5)
    uploaded_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    # Relationships
    case = relationship("Case", back_populates="attachments")
    uploader = relationship("User", back_populates="uploaded_attachments")
