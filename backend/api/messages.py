from typing import List, Optional
from fastapi import (
    APIRouter,
    Depends,
    File,
    Header,
    Response,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from backend.core.dependencies import require_verified_user
from backend.core.idempotency import get_cached_idempotent_response, store_idempotent_response
from backend.db.session import get_db
from backend.models.user import User
from backend.schemas.message import (
    MessageCreate,
    MessageResponse,
    AttachmentResponse,
    AttachmentListResponse,
)
from backend.services.message_service import MessageService

router = APIRouter(prefix="/cases/{case_id}", tags=["Messages & Attachments"])


@router.post(
    "/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Post a message or internal staff note to a case",
)
def post_message(
    case_id: str,
    data: MessageCreate,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    current_user: User = Depends(require_verified_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    # 1. Idempotency check (SRS §3.6)
    cached = get_cached_idempotent_response(idempotency_key)
    if cached:
        return MessageResponse.model_validate(cached)

    result = MessageService.post_message(db, current_user, case_id, data)
    store_idempotent_response(idempotency_key, result.model_dump())
    return result


@router.get(
    "/messages",
    response_model=List[MessageResponse],
    summary="Get all messages for a case (internal notes filtered for requesters)",
)
def get_messages(
    case_id: str,
    current_user: User = Depends(require_verified_user),
    db: Session = Depends(get_db),
) -> List[MessageResponse]:
    return MessageService.get_messages(db, current_user, case_id)


@router.post(
    "/attachments",
    response_model=AttachmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a file attachment (10MB limit per file, validated format)",
)
async def upload_attachment(
    case_id: str,
    file: UploadFile = File(...),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    current_user: User = Depends(require_verified_user),
    db: Session = Depends(get_db),
) -> AttachmentResponse:
    cached = get_cached_idempotent_response(idempotency_key)
    if cached:
        return AttachmentResponse.model_validate(cached)

    file_bytes = await file.read()
    result = await MessageService.upload_attachment(
        db=db,
        current_user=current_user,
        case_id=case_id,
        file_name=file.filename or "attachment.bin",
        file_bytes=file_bytes,
    )
    store_idempotent_response(idempotency_key, result.model_dump())
    return result


@router.get(
    "/attachments",
    response_model=AttachmentListResponse,
    summary="List all attachments for a case",
)
async def list_attachments(
    case_id: str,
    current_user: User = Depends(require_verified_user),
    db: Session = Depends(get_db),
) -> AttachmentListResponse:
    return await MessageService.list_attachments(db, current_user, case_id)


@router.get(
    "/attachments/{attachment_id}/download",
    summary="Download an attachment file",
)
async def download_attachment(
    case_id: str,
    attachment_id: str,
    current_user: User = Depends(require_verified_user),
    db: Session = Depends(get_db),
):
    file_bytes, filename, content_type = await MessageService.download_attachment_bytes(
        db, current_user, case_id, attachment_id
    )
    return Response(
        content=file_bytes,
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
