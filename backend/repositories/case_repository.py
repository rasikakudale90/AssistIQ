from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy import func, or_, desc
from sqlalchemy.orm import Session, joinedload

from backend.models.enums import CaseType, CaseStatus, Priority, UserRole
from backend.models.case import Case
from backend.models.user import User


class CaseRepository:
    @staticmethod
    def generate_reference_number(db: Session, case_type: CaseType) -> str:
        """
        Generates a sequential human-readable reference number per SRS §4.2:
        <TYPE_PREFIX>-<YEAR>-<6_DIGIT_SEQ> (e.g. INC-2026-000001 or REQ-2026-000001)
        """
        year = datetime.now(timezone.utc).year
        prefix = "INC" if case_type == CaseType.INCIDENT else "REQ"
        pattern = f"{prefix}-{year}-%"

        # Query all existing reference numbers matching this pattern to find the highest sequence
        existing_refs = (
            db.query(Case.reference_number)
            .filter(Case.reference_number.like(pattern))
            .all()
        )
        
        max_seq = 0
        for (ref,) in existing_refs:
            try:
                parts = ref.split("-")
                if len(parts) == 3:
                    seq = int(parts[2])
                    if seq > max_seq:
                        max_seq = seq
            except (ValueError, IndexError):
                continue

        next_seq = max_seq + 1
        while True:
            candidate = f"{prefix}-{year}-{next_seq:06d}"
            exists = db.query(Case.id).filter(Case.reference_number == candidate).first()
            if not exists:
                return candidate
            next_seq += 1

    @staticmethod
    def get_by_id(db: Session, case_id: str) -> Optional[Case]:
        return (
            db.query(Case)
            .options(
                joinedload(Case.requester),
                joinedload(Case.owner),
                joinedload(Case.team),
                joinedload(Case.sla),
                joinedload(Case.triage_result),
                joinedload(Case.summary),
            )
            .filter(Case.id == case_id, Case.deleted_at.is_(None))
            .first()
        )

    @staticmethod
    def get_by_reference(db: Session, ref_num: str) -> Optional[Case]:
        return (
            db.query(Case)
            .filter(Case.reference_number == ref_num, Case.deleted_at.is_(None))
            .first()
        )

    @staticmethod
    def list_cases(
        db: Session,
        current_user: User,
        status: Optional[CaseStatus] = None,
        priority: Optional[Priority] = None,
        case_type: Optional[CaseType] = None,
        team_id: Optional[str] = None,
        owner_id: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Case], int]:
        """
        Retrieves a paginated list of cases with strict server-side RBAC scoping (SRS §2.2, §3.6).
        """
        query = db.query(Case).filter(Case.deleted_at.is_(None))

        # 1. Role-based scoping
        if current_user.role == UserRole.REQUESTER:
            # Requesters can only see their own cases
            query = query.filter(Case.requester_id == current_user.id)
        elif current_user.role == UserRole.OPERATOR:
            # Operators see assigned to them, or assigned to their team, or unassigned cases
            if current_user.team_id:
                query = query.filter(
                    or_(
                        Case.owner_id == current_user.id,
                        Case.team_id == current_user.team_id,
                        Case.owner_id.is_(None),
                    )
                )
            else:
                query = query.filter(
                    or_(
                        Case.owner_id == current_user.id,
                        Case.owner_id.is_(None),
                    )
                )
        elif current_user.role == UserRole.TEAM_LEAD:
            # Team leads see their team's cases and unassigned
            if current_user.team_id:
                query = query.filter(
                    or_(
                        Case.team_id == current_user.team_id,
                        Case.owner_id.is_(None),
                    )
                )
        # Manager and Administrator have full cross-team visibility

        # 2. Filters
        if status:
            query = query.filter(Case.status == status)
        if priority:
            query = query.filter(Case.priority == priority)
        if case_type:
            query = query.filter(Case.type == case_type)
        if team_id:
            query = query.filter(Case.team_id == team_id)
        if owner_id:
            query = query.filter(Case.owner_id == owner_id)
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Case.reference_number.ilike(search_pattern),
                    Case.title.ilike(search_pattern),
                )
            )

        total = query.count()
        cases = (
            query.order_by(desc(Case.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return cases, total
