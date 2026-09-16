import re
from typing import List, Optional, Set
from sqlalchemy import or_, desc
from sqlalchemy.orm import Session

from backend.models.enums import UserRole, KnowledgeState
from backend.models.user import User
from backend.models.case import Case
from backend.models.governance import KnowledgeArticle
from backend.repositories.case_repository import CaseRepository
from backend.schemas.search import (
    SimilarCaseCandidate,
    SimilarCaseCandidatesResponse,
    UnifiedSearchItem,
    UnifiedSearchResponse,
)


def compute_text_similarity(text1: str, text2: str) -> float:
    """
    Computes a normalized word-level and trigram Jaccard similarity score (0.0 to 1.0)
    providing reliable cross-database text matching (PostgreSQL & SQLite).
    """
    if not text1 or not text2:
        return 0.0

    # Tokenize words
    words1 = set(re.findall(r"\w+", text1.lower()))
    words2 = set(re.findall(r"\w+", text2.lower()))

    if not words1 or not words2:
        return 0.0

    word_overlap = len(words1 & words2)
    word_union = len(words1 | words2)
    word_score = word_overlap / word_union if word_union > 0 else 0.0

    # Character trigrams for typo tolerance
    def get_trigrams(t: str) -> Set[str]:
        t_clean = f"  {t.lower()}  "
        return {t_clean[i:i+3] for i in range(len(t_clean) - 2)}

    tri1 = get_trigrams(text1)
    tri2 = get_trigrams(text2)
    tri_overlap = len(tri1 & tri2)
    tri_union = len(tri1 | tri2)
    tri_score = tri_overlap / tri_union if tri_union > 0 else 0.0

    # Weighted combination: 60% word overlap, 40% trigram similarity
    return round(0.6 * word_score + 0.4 * tri_score, 2)


class SearchService:
    @staticmethod
    def detect_similar_cases(
        db: Session,
        current_user: User,
        title: str,
        description: str,
        service_id: Optional[str] = None,
        exclude_case_id: Optional[str] = None,
    ) -> SimilarCaseCandidatesResponse:
        """
        Detects candidate duplicate or similar cases for human review (SRS §5.5, §5.14).
        Never auto-merges or auto-links cases.
        """
        query = db.query(Case).filter(Case.deleted_at.is_(None))

        if exclude_case_id:
            query = query.filter(Case.id != exclude_case_id)
        if service_id:
            query = query.filter(Case.service_id == service_id)

        # Requesters can only check similarity against their own cases; staff can check against all cases
        if current_user.role == UserRole.REQUESTER:
            query = query.filter(Case.requester_id == current_user.id)

        candidate_pool = query.order_by(desc(Case.created_at)).limit(50).all()
        incoming_text = f"{title} {description}"

        scored_candidates: List[SimilarCaseCandidate] = []
        for case in candidate_pool:
            target_text = f"{case.title} {case.description}"
            score = compute_text_similarity(incoming_text, target_text)

            # Only include candidates above minimal similarity threshold (0.15)
            if score >= 0.15:
                scored_candidates.append(
                    SimilarCaseCandidate(
                        case_id=case.id,
                        reference_number=case.reference_number,
                        title=case.title,
                        status=case.status.value,
                        similarity_score=score,
                        created_at=case.created_at,
                    )
                )

        # Sort descending by similarity score
        scored_candidates.sort(key=lambda c: c.similarity_score, reverse=True)
        top_candidates = scored_candidates[:5]

        return SimilarCaseCandidatesResponse(
            candidates=top_candidates,
            total=len(top_candidates),
        )

    @staticmethod
    def unified_search(
        db: Session,
        current_user: User,
        query: str,
        limit: int = 20,
    ) -> UnifiedSearchResponse:
        """
        Unified search across permitted cases and published knowledge articles (SRS §5.14, PRD §7.2).
        """
        clean_q = query.strip()
        if not clean_q:
            return UnifiedSearchResponse(results=[], total=0)

        results: List[UnifiedSearchItem] = []
        search_pattern = f"%{clean_q}%"

        # 1. Search Cases (with RBAC enforcement)
        cases_query = db.query(Case).filter(Case.deleted_at.is_(None))
        if current_user.role == UserRole.REQUESTER:
            cases_query = cases_query.filter(Case.requester_id == current_user.id)

        matching_cases = (
            cases_query.filter(
                or_(
                    Case.reference_number.ilike(search_pattern),
                    Case.title.ilike(search_pattern),
                    Case.description.ilike(search_pattern),
                )
            )
            .limit(limit)
            .all()
        )

        for c in matching_cases:
            snippet = c.description[:150] + ("..." if len(c.description) > 150 else "")
            score = 1.0 if clean_q.lower() in c.reference_number.lower() else compute_text_similarity(clean_q, c.title)
            results.append(
                UnifiedSearchItem(
                    type="case",
                    id=c.id,
                    title=c.title,
                    snippet=snippet,
                    reference_number=c.reference_number,
                    category_or_status=c.status.value,
                    score=score,
                )
            )

        # 2. Search Published Knowledge Articles
        matching_articles = (
            db.query(KnowledgeArticle)
            .filter(
                KnowledgeArticle.state == KnowledgeState.PUBLISHED,
                or_(
                    KnowledgeArticle.title.ilike(search_pattern),
                    KnowledgeArticle.body.ilike(search_pattern),
                    KnowledgeArticle.category.ilike(search_pattern),
                ),
            )
            .limit(limit)
            .all()
        )

        for a in matching_articles:
            snippet = a.body[:150] + ("..." if len(a.body) > 150 else "")
            score = compute_text_similarity(clean_q, a.title)
            results.append(
                UnifiedSearchItem(
                    type="knowledge",
                    id=a.id,
                    title=a.title,
                    snippet=snippet,
                    category_or_status=a.category,
                    score=score,
                )
            )

        # Sort by relevance score
        results.sort(key=lambda r: r.score, reverse=True)
        return UnifiedSearchResponse(results=results[:limit], total=len(results[:limit]))
