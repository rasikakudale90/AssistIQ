import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from backend.core.errors import (
    NotFoundException,
    PermissionDeniedException,
    ValidationException,
)
from backend.models.enums import (
    ConfidenceLevel,
    DraftStatus,
    DraftType,
    MessageVisibility,
    UserRole,
    AvailabilityStatus,
    CaseStatus,
)
from backend.models.ai import AITriageResult, CaseSummary, CommunicationDraft
from backend.models.case import Case
from backend.models.message import Message
from backend.models.user import User, Team
from backend.providers.ai import get_ai_provider
from backend.repositories.audit_repository import AuditRepository
from backend.repositories.case_repository import CaseRepository
from backend.repositories.message_repository import MessageRepository
from backend.schemas.ai import (
    AITriageResultResponse,
    CaseSummaryResponse,
    CommunicationDraftResponse,
    SendCommunicationDraftRequest,
    AssignmentRecommendationResponse,
    CandidateOperatorRecommendation,
)
from backend.services.search_service import SearchService

logger = logging.getLogger("assistiq.services.ai")


class AIService:
    @staticmethod
    def _score_to_confidence_level(score: Optional[float]) -> ConfidenceLevel:
        """
        Maps confidence score to ConfidenceLevel enum per SRS §5.13:
        Low: 0.00 – 0.49
        Moderate: 0.50 – 0.79
        High: 0.80 – 1.00
        """
        if score is None:
            return ConfidenceLevel.MODERATE
        if score < 0.50:
            return ConfidenceLevel.LOW
        elif score < 0.80:
            return ConfidenceLevel.MODERATE
        else:
            return ConfidenceLevel.HIGH

    @staticmethod
    async def run_triage_analysis(
        db: Session,
        case_id: str,
        current_user: Optional[User] = None,
        force_refresh: bool = False,
    ) -> Optional[AITriageResultResponse]:
        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            raise NotFoundException(f"Case with ID '{case_id}' not found.")

        existing = db.query(AITriageResult).filter(AITriageResult.case_id == case.id).first()
        if existing and not force_refresh:
            return AITriageResultResponse.model_validate(existing)

        # 1. Candidate duplicate/similar cases search (SRS §5.5)
        similar_result = SearchService.detect_similar_cases(
            db=db,
            current_user=current_user or case.requester,
            title=case.title,
            description=case.description,
            service_id=case.service_id,
            exclude_case_id=case.id,
        )
        related_ids = [cand.case_id for cand in similar_result.candidates]

        # 2. Call AI Provider for triage suggestions
        provider = get_ai_provider()
        dto = await provider.analyze_triage(
            title=case.title,
            description=case.description,
            case_type=case.type.value if hasattr(case.type, "value") else str(case.type),
            site=case.site,
            service_id=case.service_id,
        )

        if not dto:
            logger.warning(f"AI triage unavailable for case {case.reference_number}. Gracefully skipping.")
            return None

        conf_level = AIService._score_to_confidence_level(dto.confidence_score)

        if not existing:
            triage_rec = AITriageResult(
                case_id=case.id,
                suggested_category=dto.suggested_category,
                suggested_severity=dto.suggested_severity,
                suggested_priority=dto.suggested_priority,
                confidence_level=conf_level,
                confidence_score=dto.confidence_score,
                supporting_factors=dto.supporting_factors,
                missing_info=dto.missing_info,
                suggested_team=dto.suggested_team,
                recommended_next_action=dto.recommended_next_action,
                related_case_ids=related_ids,
            )
            db.add(triage_rec)
        else:
            existing.suggested_category = dto.suggested_category
            existing.suggested_severity = dto.suggested_severity
            existing.suggested_priority = dto.suggested_priority
            existing.confidence_level = conf_level
            existing.confidence_score = dto.confidence_score
            existing.supporting_factors = dto.supporting_factors
            existing.missing_info = dto.missing_info
            existing.suggested_team = dto.suggested_team
            existing.recommended_next_action = dto.recommended_next_action
            existing.related_case_ids = related_ids
            triage_rec = existing

        # 3. Audit Log entry (SRS §5.11)
        actor_id = current_user.id if current_user else case.requester_id
        AuditRepository.create_log(
            db=db,
            actor_id=actor_id,
            action="ai_triage_generated",
            target_type="case",
            target_id=case.id,
            after_value={
                "suggested_category": dto.suggested_category,
                "suggested_priority": dto.suggested_priority,
                "confidence_level": conf_level.value,
                "confidence_score": dto.confidence_score,
            },
        )

        db.commit()
        db.refresh(triage_rec)
        return AITriageResultResponse.model_validate(triage_rec)

    @staticmethod
    async def recompute_case_summary(
        db: Session,
        case_id: str,
        last_message_id: Optional[str] = None,
    ) -> Optional[CaseSummaryResponse]:
        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            return None

        # Fetch recent message history
        messages = (
            db.query(Message)
            .filter(Message.case_id == case.id)
            .order_by(Message.created_at.asc())
            .all()
        )

        msg_history = [
            {
                "visibility": m.visibility.value,
                "author_role": m.author.role.value if m.author else "User",
                "body": m.body,
            }
            for m in messages
        ]

        provider = get_ai_provider()
        summary_text = await provider.generate_summary(
            case_title=case.title,
            case_description=case.description,
            case_status=case.status.value,
            messages_history=msg_history,
        )

        if not summary_text:
            logger.warning(f"AI summary unavailable for case {case.reference_number}.")
            return None

        summary = db.query(CaseSummary).filter(CaseSummary.case_id == case.id).first()
        now = datetime.now(timezone.utc)
        if not summary:
            summary = CaseSummary(
                case_id=case.id,
                summary_text=summary_text,
                last_source_message_id=last_message_id,
                updated_at=now,
            )
            db.add(summary)
        else:
            summary.summary_text = summary_text
            summary.last_source_message_id = last_message_id
            summary.updated_at = now

        AuditRepository.create_log(
            db=db,
            actor_id="system",
            action="ai_summary_updated",
            target_type="case",
            target_id=case.id,
            after_value={"last_source_message_id": last_message_id},
        )

        db.commit()
        db.refresh(summary)
        return CaseSummaryResponse.model_validate(summary)

    @staticmethod
    def get_assignment_recommendations(
        db: Session,
        case_id: str,
        current_user: User,
    ) -> AssignmentRecommendationResponse:
        """
        Smart Assignment Recommendation (SRS §5.6 - Level 1):
        Combines suggested team from triage, candidate operator active workloads,
        availability status, site matching, and requester history.
        """
        case = CaseRepository.get_by_id(db, case_id)
        if not case:
            raise NotFoundException(f"Case with ID '{case_id}' not found.")

        triage = db.query(AITriageResult).filter(AITriageResult.case_id == case.id).first()
        suggested_team_name = triage.suggested_team if triage else None

        # Look up matching team
        matching_team = None
        if suggested_team_name:
            matching_team = db.query(Team).filter(Team.name.ilike(f"%{suggested_team_name}%")).first()

        # Find candidate operators and team leads
        staff_query = db.query(User).filter(
            User.role.in_([UserRole.OPERATOR, UserRole.TEAM_LEAD]),
            User.deleted_at.is_(None),
        )

        if matching_team:
            staff_query = staff_query.filter(User.team_id == matching_team.id)

        staff_members = staff_query.all()
        if not staff_members:
            # Fallback to all active operators across teams
            staff_members = (
                db.query(User)
                .filter(User.role.in_([UserRole.OPERATOR, UserRole.TEAM_LEAD]), User.deleted_at.is_(None))
                .all()
            )

        # Count active open cases per candidate operator
        active_counts_query = (
            db.query(Case.owner_id, func.count(Case.id))
            .filter(
                Case.owner_id.isnot(None),
                Case.status.in_([CaseStatus.NEW, CaseStatus.IN_ASSESSMENT, CaseStatus.ASSIGNED, CaseStatus.AWAITING_REQUESTER]),
            )
            .group_by(Case.owner_id)
            .all()
        )
        workload_map = {row[0]: row[1] for row in active_counts_query}

        candidates: List[CandidateOperatorRecommendation] = []
        for staff in staff_members:
            score = 100.0
            reasons = []

            # Workload scoring (lower active cases -> higher score)
            active_cases = workload_map.get(staff.id, 0)
            workload_penalty = active_cases * 10.0
            score -= workload_penalty
            reasons.append(f"Current active caseload: {active_cases} case(s)")

            # Availability scoring
            if staff.availability_status == AvailabilityStatus.AVAILABLE:
                score += 20.0
                reasons.append("Staff availability is 'Available'")
            elif staff.availability_status == AvailabilityStatus.AWAY:
                score -= 30.0
                reasons.append("Staff is currently 'Away'")
            else:
                score -= 60.0
                reasons.append("Staff is currently 'Offline'")

            # Site matching
            if case.site and staff.site and case.site.lower() == staff.site.lower():
                score += 25.0
                reasons.append(f"Site match: '{staff.site}'")

            # Team match
            team_name = staff.team.name if staff.team else None
            if matching_team and staff.team_id == matching_team.id:
                score += 30.0
                reasons.append(f"Member of suggested team '{matching_team.name}'")

            candidates.append(
                CandidateOperatorRecommendation(
                    user_id=staff.id,
                    email=staff.email,
                    role=staff.role,
                    team_id=staff.team_id,
                    team_name=team_name,
                    availability_status=staff.availability_status,
                    active_case_count=active_cases,
                    site=staff.site,
                    score=round(max(0.0, score), 1),
                    match_reasons=reasons,
                )
            )

        # Sort candidates by score descending
        candidates.sort(key=lambda c: c.score, reverse=True)

        rationale = [
            f"Suggested team based on initial triage: {suggested_team_name or 'General IT Service Desk'}.",
            "Scored candidates by active workload capacity, availability status, and site alignment.",
        ]

        return AssignmentRecommendationResponse(
            case_id=case.id,
            suggested_team=suggested_team_name,
            suggested_team_id=matching_team.id if matching_team else None,
            candidate_operators=candidates[:5],  # Top 5
            rationale=rationale,
        )

    @staticmethod
    async def generate_communication_draft(
        db: Session,
        case_id: str,
        draft_type: DraftType,
        current_user: User,
        custom_instructions: Optional[str] = None,
    ) -> CommunicationDraftResponse:
        """
        AI Communication Draft Generation (SRS §5.9 - Level 1):
        Generates a draft for human review. Never auto-sends.
        """
        case = CaseRepository.get_by_id(db, case_id)
        if not case:
            raise NotFoundException(f"Case with ID '{case_id}' not found.")

        # Requesters cannot generate staff communication drafts
        if current_user.role == UserRole.REQUESTER:
            raise PermissionDeniedException("Requesters are not permitted to generate communication drafts.")

        messages = (
            db.query(Message)
            .filter(Message.case_id == case.id)
            .order_by(Message.created_at.desc())
            .limit(5)
            .all()
        )
        msg_history = [
            {
                "visibility": m.visibility.value,
                "author_role": m.author.role.value if m.author else "User",
                "body": m.body,
            }
            for m in reversed(messages)
        ]

        provider = get_ai_provider()
        draft_body = await provider.generate_communication_draft(
            draft_type=draft_type.value,
            case_title=case.title,
            case_description=case.description,
            messages_history=msg_history,
            custom_instructions=custom_instructions,
        )

        if not draft_body:
            raise ValidationException("AI service is currently unavailable. Please author the message manually.")

        draft = CommunicationDraft(
            case_id=case.id,
            draft_type=draft_type,
            body=draft_body,
            status=DraftStatus.DRAFT,
            reviewed_by=None,
        )
        db.add(draft)

        AuditRepository.create_log(
            db=db,
            actor_id=current_user.id,
            action="ai_draft_generated",
            target_type="case",
            target_id=case.id,
            after_value={"draft_type": draft_type.value},
        )

        db.commit()
        db.refresh(draft)
        return CommunicationDraftResponse.model_validate(draft)

    @staticmethod
    def send_communication_draft(
        db: Session,
        draft_id: str,
        current_user: User,
        data: SendCommunicationDraftRequest,
    ) -> Message:
        """
        Sends an approved/edited communication draft. Creates a Message with ai_generated=True.
        """
        draft = db.query(CommunicationDraft).filter(CommunicationDraft.id == draft_id).first()
        if not draft:
            raise NotFoundException(f"Draft with ID '{draft_id}' not found.")

        if draft.status != DraftStatus.DRAFT:
            raise ValidationException(f"Draft is already in '{draft.status.value}' state.")

        case = CaseRepository.get_by_id(db, draft.case_id)
        if not case:
            raise NotFoundException("Associated case not found.")

        # Requesters cannot post internal notes
        if current_user.role == UserRole.REQUESTER and data.visibility == MessageVisibility.INTERNAL_ONLY:
            raise PermissionDeniedException("Requesters cannot author internal notes.")

        # Create message with ai_generated = True per SRS §5.9
        message = MessageRepository.create_message(
            db=db,
            case_id=case.id,
            author_id=current_user.id,
            body=data.body,
            visibility=data.visibility,
            ai_generated=True,
        )

        draft.status = DraftStatus.SENT
        draft.body = data.body
        draft.reviewed_by = current_user.id
        draft.sent_message_id = message.id

        AuditRepository.create_log(
            db=db,
            actor_id=current_user.id,
            action="ai_draft_sent",
            target_type="case",
            target_id=case.id,
            after_value={
                "draft_id": draft.id,
                "message_id": message.id,
                "visibility": data.visibility.value,
            },
        )

        db.commit()
        db.refresh(message)
        return message
