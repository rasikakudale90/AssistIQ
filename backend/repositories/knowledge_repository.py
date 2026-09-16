from typing import List, Optional, Tuple
from sqlalchemy import desc, func, or_
from sqlalchemy.orm import Session, joinedload

from backend.models.enums import KnowledgeState, UserRole
from backend.models.governance import KnowledgeArticle


class KnowledgeRepository:
    @staticmethod
    def create_article(
        db: Session,
        title: str,
        body: str,
        category: str,
        owner_id: str,
        state: KnowledgeState = KnowledgeState.PUBLISHED,
        source_case_id: Optional[str] = None,
    ) -> KnowledgeArticle:
        article = KnowledgeArticle(
            title=title,
            body=body,
            category=category,
            owner_id=owner_id,
            state=state,
            source_case_id=source_case_id,
        )
        db.add(article)
        db.flush()
        return article

    @staticmethod
    def get_by_id(db: Session, article_id: str, user_role: UserRole) -> Optional[KnowledgeArticle]:
        query = (
            db.query(KnowledgeArticle)
            .options(joinedload(KnowledgeArticle.owner))
            .filter(KnowledgeArticle.id == article_id)
        )
        # Requesters can only access published articles
        if user_role == UserRole.REQUESTER:
            query = query.filter(KnowledgeArticle.state == KnowledgeState.PUBLISHED)

        return query.first()

    @staticmethod
    def list_articles(
        db: Session,
        user_role: UserRole,
        category: Optional[str] = None,
        state: Optional[KnowledgeState] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[KnowledgeArticle], int]:
        query = db.query(KnowledgeArticle).options(joinedload(KnowledgeArticle.owner))

        # Requesters strictly restricted to published articles (SRS §7.6)
        if user_role == UserRole.REQUESTER:
            query = query.filter(KnowledgeArticle.state == KnowledgeState.PUBLISHED)
        elif state:
            query = query.filter(KnowledgeArticle.state == state)

        if category:
            query = query.filter(KnowledgeArticle.category == category)

        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    KnowledgeArticle.title.ilike(search_pattern),
                    KnowledgeArticle.body.ilike(search_pattern),
                    KnowledgeArticle.category.ilike(search_pattern),
                )
            )

        total = query.count()
        articles = (
            query.order_by(desc(KnowledgeArticle.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return articles, total

    @staticmethod
    def get_categories(db: Session) -> List[str]:
        rows = (
            db.query(KnowledgeArticle.category)
            .filter(KnowledgeArticle.state == KnowledgeState.PUBLISHED)
            .distinct()
            .all()
        )
        return [r[0] for r in rows if r[0]]
