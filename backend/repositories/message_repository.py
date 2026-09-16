from typing import List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from backend.models.enums import MessageVisibility, UserRole
from backend.models.message import Message, Attachment


class MessageRepository:
    @staticmethod
    def create_message(
        db: Session,
        case_id: str,
        author_id: Optional[str],
        body: str,
        visibility: MessageVisibility,
        ai_generated: bool = False,
    ) -> Message:
        message = Message(
            case_id=case_id,
            author_id=author_id,
            body=body,
            visibility=visibility,
            ai_generated=ai_generated,
        )
        db.add(message)
        db.flush()
        return message

    @staticmethod
    def get_messages_for_case(
        db: Session,
        case_id: str,
        user_role: UserRole,
    ) -> List[Message]:
        """
        Retrieves messages for a case.
        Strict security rule: Requesters never see 'internal_only' messages (PRD §4, SRS §4).
        """
        query = (
            db.query(Message)
            .options(joinedload(Message.author))
            .filter(Message.case_id == case_id)
        )
        if user_role == UserRole.REQUESTER:
            query = query.filter(Message.visibility == MessageVisibility.REQUESTER_VISIBLE)

        return query.order_by(Message.created_at.asc()).all()

    @staticmethod
    def create_attachment(
        db: Session,
        case_id: str,
        storage_path: str,
        file_name: str,
        file_type: str,
        file_size: int,
        uploaded_by: Optional[str],
    ) -> Attachment:
        attachment = Attachment(
            case_id=case_id,
            storage_path=storage_path,
            file_name=file_name,
            file_type=file_type,
            file_size=file_size,
            uploaded_by=uploaded_by,
        )
        db.add(attachment)
        db.flush()
        return attachment

    @staticmethod
    def get_attachments_for_case(db: Session, case_id: str) -> List[Attachment]:
        return (
            db.query(Attachment)
            .options(joinedload(Attachment.uploader))
            .filter(Attachment.case_id == case_id)
            .order_by(Attachment.created_at.asc())
            .all()
        )

    @staticmethod
    def get_total_attachment_size_for_case(db: Session, case_id: str) -> int:
        total = (
            db.query(func.sum(Attachment.file_size))
            .filter(Attachment.case_id == case_id)
            .scalar()
        )
        return total or 0

    @staticmethod
    def get_attachment_by_id(db: Session, attachment_id: str) -> Optional[Attachment]:
        return (
            db.query(Attachment)
            .options(joinedload(Attachment.uploader), joinedload(Attachment.case))
            .filter(Attachment.id == attachment_id)
            .first()
        )
