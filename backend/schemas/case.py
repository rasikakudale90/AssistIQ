from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict

from backend.models.enums import CaseType, CaseStatus, Priority
from backend.schemas.auth import UserResponse


class CaseCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: CaseType = Field(CaseType.INCIDENT, description="Case type: Incident or Service Request")
    title: str = Field(..., min_length=3, max_length=200, description="Short summary of issue or request")
    description: str = Field(..., min_length=5, max_length=10000, description="Detailed problem description")
    priority: Optional[Priority] = Field(Priority.P3, description="Initial priority (defaults to P3)")
    site: Optional[str] = Field(None, max_length=100, description="User's site or office location")
    service_id: Optional[str] = Field(None, max_length=100, description="Associated IT service catalog ID")


class CaseUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = Field(None, min_length=3, max_length=200)
    site: Optional[str] = Field(None, max_length=100)
    service_id: Optional[str] = Field(None, max_length=100)
    version: int = Field(..., description="Current version integer for optimistic concurrency control")


class CaseStatusTransition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: CaseStatus = Field(..., description="Target lifecycle status")
    reason: Optional[str] = Field(None, max_length=1000, description="Reason for transition")
    version: int = Field(..., description="Current version integer for optimistic concurrency control")


class CaseAssignment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    owner_id: Optional[str] = Field(None, description="Assign to specific operator user ID")
    team_id: Optional[str] = Field(None, description="Assign to specific team ID")
    version: int = Field(..., description="Current version integer for optimistic concurrency control")


class CasePriorityOverride(BaseModel):
    model_config = ConfigDict(extra="forbid")

    priority: Priority = Field(..., description="New priority level (P1-P4)")
    reason: str = Field(..., min_length=3, max_length=500, description="Justification for priority override")
    version: int = Field(..., description="Current version integer for optimistic concurrency control")


class CaseReopen(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reason: str = Field(..., min_length=5, max_length=1000, description="Explanation why issue is unresolved")
    version: int = Field(..., description="Current version integer for optimistic concurrency control")


class CaseSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    reference_number: str
    type: CaseType
    title: str
    status: CaseStatus
    priority: Priority
    requester_id: str
    owner_id: Optional[str] = None
    team_id: Optional[str] = None
    site: Optional[str] = None
    service_id: Optional[str] = None
    version: int
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None


class TeamSimpleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str


class CaseDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    reference_number: str
    type: CaseType
    title: str
    description: str
    status: CaseStatus
    priority: Priority
    requester_id: str
    owner_id: Optional[str] = None
    team_id: Optional[str] = None
    site: Optional[str] = None
    service_id: Optional[str] = None
    version: int
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    requester: Optional[UserResponse] = None
    owner: Optional[UserResponse] = None
    team: Optional[TeamSimpleResponse] = None


class CaseListResponse(BaseModel):
    items: List[CaseSummaryResponse]
    page: int
    page_size: int
    total: int


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    actor_id: Optional[str] = None
    action: str
    target_type: str
    target_id: str
    before_value: Optional[Dict[str, Any]] = None
    after_value: Optional[Dict[str, Any]] = None
    created_at: datetime
