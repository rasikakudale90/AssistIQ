from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

from backend.models.enums import MessageVisibility
from backend.schemas.auth import UserResponse


class MessageCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    body: str = Field(..., min_length=1, max_length=5000, description="Message text (max 5000 chars per SRS §7.2)")
    visibility: MessageVisibility = Field(
        MessageVisibility.REQUESTER_VISIBLE,
        description="Visibility: 'requester_visible' (all users) or 'internal_only' (staff only)",
    )


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str
    author_id: Optional[str] = None
    body: str
    visibility: MessageVisibility
    ai_generated: bool
    created_at: datetime
    author: Optional[UserResponse] = None


class AttachmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str
    storage_path: str
    file_name: str
    file_type: str
    file_size: int
    uploaded_by: Optional[str] = None
    download_url: Optional[str] = None
    created_at: datetime
    uploader: Optional[UserResponse] = None


class AttachmentListResponse(BaseModel):
    items: List[AttachmentResponse]
    total_size_bytes: int
