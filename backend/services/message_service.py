import uuid
import re
from datetime import datetime, timezone
from typing import List, Tuple
from sqlalchemy.orm import Session

from backend.core.errors import (
    NotFoundException,
    PermissionDeniedException,
    ValidationException,
)
from backend.core.file_validation import validate_file_content
from backend.models.enums import MessageVisibility, UserRole, CaseStatus
from backend.models.user import User
from backend.models.message import Message, Attachment
from backend.providers.storage import get_storage_provider
from backend.repositories.case_repository import CaseRepository
from backend.repositories.message_repository import MessageRepository
from backend.repositories.audit_repository import AuditRepository
from backend.schemas.message import (
    MessageCreate,
    MessageResponse,
    AttachmentResponse,
    AttachmentListResponse,
)
from backend.services.case_service import CaseService
from backend.services.sla_service import SLAService


class MessageService:
    @staticmethod
    def post_message(
        db: Session,
        current_user: User,
        case_id: str,
        data: MessageCreate,
    ) -> MessageResponse:
        case = CaseService.get_case(db, current_user, case_id)

        # 1. Permission check on visibility
        if current_user.role == UserRole.REQUESTER and data.visibility == MessageVisibility.INTERNAL_ONLY:
            raise PermissionDeniedException("Requesters are not permitted to author internal notes.")

        # 2. Create message
        message = MessageRepository.create_message(
            db=db,
            case_id=case.id,
            author_id=current_user.id,
            body=data.body,
            visibility=data.visibility,
            ai_generated=False,
        )

        # 3. Record SLA first response if staff sent a requester-visible message (SRS §4.3)
        if current_user.role != UserRole.REQUESTER and data.visibility == MessageVisibility.REQUESTER_VISIBLE:
            SLAService.record_first_response(db, case.id)

        # 3. Lifecycle trigger: If case was AwaitingRequester and Requester replied -> advance to Assigned (SRS §6.1)
        if (
            case.status == CaseStatus.AWAITING_REQUESTER
            and current_user.id == case.requester_id
            and data.visibility == MessageVisibility.REQUESTER_VISIBLE
        ):
            old_status = case.status
            case.status = CaseStatus.ASSIGNED
            case.version += 1
            case.updated_at = datetime.now(timezone.utc)

            AuditRepository.create_log(
                db=db,
                actor_id=current_user.id,
                action="status_change",
                target_type="case",
                target_id=case.id,
                before_value={"status": old_status.value},
                after_value={"status": CaseStatus.ASSIGNED.value, "trigger": "requester_reply"},
            )

        # 4. Audit message creation
        AuditRepository.create_log(
            db=db,
            actor_id=current_user.id,
            action="message_created",
            target_type="case",
            target_id=case.id,
            after_value={
                "message_id": message.id,
                "visibility": message.visibility.value,
            },
        )

        db.commit()
        db.refresh(message)
        return MessageResponse.model_validate(message)

    @staticmethod
    def get_messages(
        db: Session,
        current_user: User,
        case_id: str,
    ) -> List[MessageResponse]:
        CaseService.get_case(db, current_user, case_id)
        messages = MessageRepository.get_messages_for_case(db, case_id, current_user.role)
        return [MessageResponse.model_validate(m) for m in messages]

    @staticmethod
    async def upload_attachment(
        db: Session,
        current_user: User,
        case_id: str,
        file_name: str,
        file_bytes: bytes,
    ) -> AttachmentResponse:
        case = CaseService.get_case(db, current_user, case_id)

        # 1. Check current size & validate content (SRS §7.5)
        current_total = MessageRepository.get_total_attachment_size_for_case(db, case_id)
        ext, mime_type = validate_file_content(file_name, file_bytes, current_total)

        # 2. Generate secure UUID path: cases/{case_id}/{uuid}_{safe_name}
        clean_name = re.sub(r"[^a-zA-Z0-9_.-]", "_", file_name)
        storage_filename = f"{uuid.uuid4().hex}_{clean_name}"
        storage_path = f"cases/{case.id}/{storage_filename}"

        # 3. Upload to storage provider
        provider = get_storage_provider()
        await provider.upload_file(storage_path, file_bytes, mime_type)

        # 4. Save record in database
        attachment = MessageRepository.create_attachment(
            db=db,
            case_id=case.id,
            storage_path=storage_path,
            file_name=file_name,
            file_type=mime_type,
            file_size=len(file_bytes),
            uploaded_by=current_user.id,
        )

        # 5. Audit log
        AuditRepository.create_log(
            db=db,
            actor_id=current_user.id,
            action="attachment_uploaded",
            target_type="case",
            target_id=case.id,
            after_value={
                "attachment_id": attachment.id,
                "file_name": file_name,
                "file_size": len(file_bytes),
            },
        )

        db.commit()
        db.refresh(attachment)

        download_url = await provider.get_download_url(storage_path)
        resp = AttachmentResponse.model_validate(attachment)
        resp.download_url = download_url
        return resp

    @staticmethod
    async def list_attachments(
        db: Session,
        current_user: User,
        case_id: str,
    ) -> AttachmentListResponse:
        CaseService.get_case(db, current_user, case_id)
        attachments = MessageRepository.get_attachments_for_case(db, case_id)
        total_size = MessageRepository.get_total_attachment_size_for_case(db, case_id)
        provider = get_storage_provider()

        results = []
        for att in attachments:
            item = AttachmentResponse.model_validate(att)
            item.download_url = await provider.get_download_url(att.storage_path)
            results.append(item)

        return AttachmentListResponse(items=results, total_size_bytes=total_size)

    @staticmethod
    async def download_attachment_bytes(
        db: Session,
        current_user: User,
        case_id: str,
        attachment_id: str,
    ) -> Tuple[bytes, str, str]:
        case = CaseService.get_case(db, current_user, case_id)
        attachment = MessageRepository.get_attachment_by_id(db, attachment_id)

        if not attachment or attachment.case_id != case.id:
            raise NotFoundException(f"Attachment with ID '{attachment_id}' not found.")

        provider = get_storage_provider()
        file_bytes = await provider.download_file(attachment.storage_path)
        return file_bytes, attachment.file_name, attachment.file_type
