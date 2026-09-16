from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class SimilarDetectionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=5, max_length=10000)
    service_id: Optional[str] = Field(None, max_length=100)


class SimilarCaseCandidate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    case_id: str
    reference_number: str
    title: str
    status: str
    similarity_score: float = Field(..., ge=0.0, le=1.0)
    created_at: datetime


class SimilarCaseCandidatesResponse(BaseModel):
    candidates: List[SimilarCaseCandidate]
    total: int


class UnifiedSearchItem(BaseModel):
    type: str = Field(..., description="'case' or 'knowledge'")
    id: str
    title: str
    snippet: str
    reference_number: Optional[str] = None
    category_or_status: Optional[str] = None
    score: float


class UnifiedSearchResponse(BaseModel):
    results: List[UnifiedSearchItem]
    total: int
