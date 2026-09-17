from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from backend.models.enums import Priority


class SLAResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str
    priority: Priority
    target_response_at: datetime
    target_resolve_at: datetime
    response_breached: bool
    resolve_breached: bool
    responded_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    paused_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    # Computed fields for human-friendly countdown display (SRS §4.3)
    response_time_remaining_seconds: Optional[int] = None
    resolve_time_remaining_seconds: Optional[int] = None
    is_response_approaching: bool = False
    is_resolve_approaching: bool = False
