from typing import List, Optional
from sqlalchemy.orm import Session

from backend.core.errors import NotFoundException, PermissionDeniedException
from backend.models.enums import KnowledgeState, UserRole
from backend.models.user import User
from backend.models.governance import KnowledgeArticle
from backend.repositories.knowledge_repository import KnowledgeRepository
from backend.repositories.audit_repository import AuditRepository
from backend.schemas.knowledge import (
    KnowledgeArticleCreate,
    KnowledgeArticleUpdate,
    KnowledgeArticleResponse,
    KnowledgeArticleListResponse,
)


class KnowledgeService:
    @staticmethod
    def create_article(
        db: Session,
        current_user: User,
        data: KnowledgeArticleCreate,
    ) -> KnowledgeArticleResponse:
        if current_user.role not in [UserRole.OPERATOR, UserRole.TEAM_LEAD, UserRole.MANAGER, UserRole.ADMINISTRATOR]:
            raise PermissionDeniedException("Only IT staff members can author knowledge base articles.")

        article = KnowledgeRepository.create_article(
            db=db,
            title=data.title,
            body=data.body,
            category=data.category,
            owner_id=current_user.id,
            state=data.state or KnowledgeState.PUBLISHED,
            source_case_id=data.source_case_id,
        )

        AuditRepository.create_log(
            db=db,
            actor_id=current_user.id,
            action="article_created",
            target_type="article",
            target_id=article.id,
            after_value={"title": article.title, "category": article.category, "state": article.state.value},
        )
        db.commit()
        db.refresh(article)
        return KnowledgeArticleResponse.model_validate(article)

    @staticmethod
    def get_article(
        db: Session,
        current_user: User,
        article_id: str,
    ) -> KnowledgeArticleResponse:
        article = KnowledgeRepository.get_by_id(db, article_id, current_user.role)
        if not article:
            raise NotFoundException(f"Knowledge article with ID '{article_id}' not found.")
        return KnowledgeArticleResponse.model_validate(article)

    @staticmethod
    def list_articles(
        db: Session,
        current_user: User,
        category: Optional[str] = None,
        state: Optional[KnowledgeState] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> KnowledgeArticleListResponse:
        articles, total = KnowledgeRepository.list_articles(
            db=db,
            user_role=current_user.role,
            category=category,
            state=state,
            search=search,
            page=page,
            page_size=page_size,
        )
        return KnowledgeArticleListResponse(
            items=[KnowledgeArticleResponse.model_validate(a) for a in articles],
            page=page,
            page_size=page_size,
            total=total,
        )

    @staticmethod
    def update_article(
        db: Session,
        current_user: User,
        article_id: str,
        data: KnowledgeArticleUpdate,
    ) -> KnowledgeArticleResponse:
        if current_user.role not in [UserRole.OPERATOR, UserRole.TEAM_LEAD, UserRole.MANAGER, UserRole.ADMINISTRATOR]:
            raise PermissionDeniedException("Only IT staff members can edit knowledge base articles.")

        article = db.query(KnowledgeArticle).filter(KnowledgeArticle.id == article_id).first()
        if not article:
            raise NotFoundException(f"Knowledge article with ID '{article_id}' not found.")

        before_val = {"title": article.title, "body": article.body, "category": article.category, "state": article.state.value}

        if data.title is not None:
            article.title = data.title
        if data.body is not None:
            article.body = data.body
        if data.category is not None:
            article.category = data.category
        if data.state is not None:
            article.state = data.state

        AuditRepository.create_log(
            db=db,
            actor_id=current_user.id,
            action="article_updated",
            target_type="article",
            target_id=article.id,
            before_value=before_val,
            after_value={"title": article.title, "category": article.category, "state": article.state.value},
        )
        db.commit()
        db.refresh(article)
        return KnowledgeArticleResponse.model_validate(article)

    @staticmethod
    def archive_article(
        db: Session,
        current_user: User,
        article_id: str,
    ) -> None:
        if current_user.role not in [UserRole.OPERATOR, UserRole.TEAM_LEAD, UserRole.MANAGER, UserRole.ADMINISTRATOR]:
            raise PermissionDeniedException("Only IT staff members can archive knowledge base articles.")

        article = db.query(KnowledgeArticle).filter(KnowledgeArticle.id == article_id).first()
        if not article:
            raise NotFoundException(f"Knowledge article with ID '{article_id}' not found.")

        article.state = KnowledgeState.ARCHIVED
        AuditRepository.create_log(
            db=db,
            actor_id=current_user.id,
            action="article_archived",
            target_type="article",
            target_id=article.id,
            after_value={"state": KnowledgeState.ARCHIVED.value},
        )
        db.commit()
