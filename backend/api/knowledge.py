from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.core.dependencies import require_verified_user, require_staff
from backend.db.session import get_db
from backend.models.enums import KnowledgeState
from backend.models.user import User
from backend.schemas.knowledge import (
    KnowledgeArticleCreate,
    KnowledgeArticleUpdate,
    KnowledgeArticleResponse,
    KnowledgeArticleListResponse,
)
from backend.schemas.auth import MessageResponse
from backend.services.knowledge_service import KnowledgeService

router = APIRouter(prefix="/knowledge", tags=["Knowledge Base"])


@router.get(
    "",
    response_model=KnowledgeArticleListResponse,
    summary="List knowledge base articles",
)
def list_articles(
    category: Optional[str] = Query(None, description="Filter by category"),
    state: Optional[KnowledgeState] = Query(None, description="Filter by state (staff only)"),
    search: Optional[str] = Query(None, description="Search term in title, body, or category"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_verified_user),
    db: Session = Depends(get_db),
) -> KnowledgeArticleListResponse:
    return KnowledgeService.list_articles(
        db=db,
        current_user=current_user,
        category=category,
        state=state,
        search=search,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{article_id}",
    response_model=KnowledgeArticleResponse,
    summary="Get knowledge article details",
)
def get_article(
    article_id: str,
    current_user: User = Depends(require_verified_user),
    db: Session = Depends(get_db),
) -> KnowledgeArticleResponse:
    return KnowledgeService.get_article(db, current_user, article_id)


@router.post(
    "",
    response_model=KnowledgeArticleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new knowledge base article (Staff only)",
)
def create_article(
    data: KnowledgeArticleCreate,
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db),
) -> KnowledgeArticleResponse:
    return KnowledgeService.create_article(db, current_user, data)


@router.put(
    "/{article_id}",
    response_model=KnowledgeArticleResponse,
    summary="Update a knowledge base article (Staff only)",
)
def update_article(
    article_id: str,
    data: KnowledgeArticleUpdate,
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db),
) -> KnowledgeArticleResponse:
    return KnowledgeService.update_article(db, current_user, article_id, data)


@router.delete(
    "/{article_id}",
    response_model=MessageResponse,
    summary="Archive a knowledge base article (Staff only)",
)
def archive_article(
    article_id: str,
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db),
) -> MessageResponse:
    KnowledgeService.archive_article(db, current_user, article_id)
    return MessageResponse(message="Knowledge article archived successfully.")
