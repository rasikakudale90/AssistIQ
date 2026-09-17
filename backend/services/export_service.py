import csv
import io
from typing import Optional
from sqlalchemy.orm import Session, joinedload

from backend.models.enums import CaseType, CaseStatus, Priority
from backend.models.user import User
from backend.models.case import Case
from backend.repositories.case_repository import CaseRepository


class ExportService:
    @staticmethod
    def generate_cases_csv(
        db: Session,
        current_user: User,
        status: Optional[CaseStatus] = None,
        priority: Optional[Priority] = None,
        case_type: Optional[CaseType] = None,
        team_id: Optional[str] = None,
        owner_id: Optional[str] = None,
        search: Optional[str] = None,
    ) -> str:
        """
        Generates a role-scoped CSV export of cases (SRS §7.6).
        Requesters can only export their own cases; Staff sees assigned/team cases; Managers/Admins see all.
        """
        # Fetch matching cases using the RBAC-enforcing repository query
        cases, _ = CaseRepository.list_cases(
            db=db,
            current_user=current_user,
            status=status,
            priority=priority,
            case_type=case_type,
            team_id=team_id,
            owner_id=owner_id,
            search=search,
            page=1,
            page_size=10000,  # Full export limit
        )

        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

        # Header row
        writer.writerow([
            "Reference Number",
            "Type",
            "Title",
            "Status",
            "Priority",
            "Requester Email",
            "Owner Email",
            "Team Name",
            "Site",
            "Service ID",
            "Version",
            "Created At (UTC)",
            "Updated At (UTC)",
            "Resolved At (UTC)",
            "Closed At (UTC)",
            "Target Response (UTC)",
            "Target Resolve (UTC)",
            "Response Breached",
            "Resolve Breached",
            "Triage Category",
            "Triage Confidence",
        ])

        for case in cases:
            req_email = case.requester.email if case.requester else ""
            owner_email = case.owner.email if case.owner else "Unassigned"
            team_name = case.team.name if case.team else "Unassigned"

            target_resp = case.sla.target_response_at.isoformat() if case.sla else ""
            target_res = case.sla.target_resolve_at.isoformat() if case.sla else ""
            resp_breached = str(case.sla.response_breached) if case.sla else "False"
            res_breached = str(case.sla.resolve_breached) if case.sla else "False"

            triage_cat = case.triage_result.suggested_category if case.triage_result else ""
            triage_conf = case.triage_result.confidence_level.value if case.triage_result else ""

            writer.writerow([
                case.reference_number,
                case.type.value if hasattr(case.type, "value") else str(case.type),
                case.title,
                case.status.value if hasattr(case.status, "value") else str(case.status),
                case.priority.value if hasattr(case.priority, "value") else str(case.priority),
                req_email,
                owner_email,
                team_name,
                case.site or "",
                case.service_id or "",
                case.version,
                case.created_at.isoformat() if case.created_at else "",
                case.updated_at.isoformat() if case.updated_at else "",
                case.resolved_at.isoformat() if case.resolved_at else "",
                case.closed_at.isoformat() if case.closed_at else "",
                target_resp,
                target_res,
                resp_breached,
                res_breached,
                triage_cat,
                triage_conf,
            ])

        return output.getvalue()
