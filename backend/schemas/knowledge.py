from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

from backend.models.enums import KnowledgeState
from backend.schemas.auth import UserResponse


class KnowledgeArticleCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=3, max_length=255, description="Article title")
    body: str = Field(..., min_length=10, description="Markdown/Plaintext article body")
    category: str = Field(..., min_length=2, max_length=100, description="Category (e.g. Network, Hardware, Access)")
    state: Optional[KnowledgeState] = Field(KnowledgeState.PUBLISHED, description="Article publication status")
    source_case_id: Optional[str] = Field(None, description="Optional case ID this article originated from")


class KnowledgeArticleUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = Field(None, min_length=3, max_length=255)
    body: Optional[str] = Field(None, min_length=10)
    category: Optional[str] = Field(None, min_length=2, max_length=100)
    state: Optional[KnowledgeState] = None


class KnowledgeArticleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    body: str
    category: str
    owner_id: str
    state: KnowledgeState
    review_date: Optional[datetime] = None
    source_case_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    owner: Optional[UserResponse] = None


class KnowledgeArticleListResponse(BaseModel):
    items: List[KnowledgeArticleResponse]
    page: int
    page_size: int
    total: int
