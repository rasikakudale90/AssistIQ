from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.core.dependencies import require_verified_user
from backend.db.session import get_db
from backend.models.user import User
from backend.schemas.search import (
    SimilarDetectionRequest,
    SimilarCaseCandidatesResponse,
    UnifiedSearchResponse,
)
from backend.services.case_service import CaseService
from backend.services.search_service import SearchService

router = APIRouter(tags=["Search & Similarity"])


@router.get(
    "/search",
    response_model=UnifiedSearchResponse,
    summary="Unified full-text search across permitted cases and knowledge articles",
)
def unified_search(
    q: str = Query(..., min_length=1, description="Search query string"),
    limit: int = Query(20, ge=1, le=50, description="Max results"),
    current_user: User = Depends(require_verified_user),
    db: Session = Depends(get_db),
) -> UnifiedSearchResponse:
    return SearchService.unified_search(db, current_user, query=q, limit=limit)


@router.post(
    "/cases/detect-similar",
    response_model=SimilarCaseCandidatesResponse,
    summary="Detect candidate duplicate/similar cases before submission",
)
def detect_similar_cases(
    data: SimilarDetectionRequest,
    current_user: User = Depends(require_verified_user),
    db: Session = Depends(get_db),
) -> SimilarCaseCandidatesResponse:
    return SearchService.detect_similar_cases(
        db=db,
        current_user=current_user,
        title=data.title,
        description=data.description,
        service_id=data.service_id,
    )


@router.get(
    "/cases/{case_id}/similar",
    response_model=SimilarCaseCandidatesResponse,
    summary="Get candidate similar cases for an existing case",
)
def get_similar_cases_for_case(
    case_id: str,
    current_user: User = Depends(require_verified_user),
    db: Session = Depends(get_db),
) -> SimilarCaseCandidatesResponse:
    case = CaseService.get_case(db, current_user, case_id)
    return SearchService.detect_similar_cases(
        db=db,
        current_user=current_user,
        title=case.title,
        description=case.description,
        service_id=case.service_id,
        exclude_case_id=case.id,
    )
