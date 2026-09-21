import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from backend.models.enums import (
    CaseStatus,
    Priority,
    CaseType,
    RiskLevel,
    UserRole,
)
from backend.models.case import Case
from backend.models.sla import SLA
from backend.models.ai import AITriageResult, CaseRiskAssessment
from backend.models.governance import AuditLog
from backend.models.user import Team, User
from backend.providers.ai import get_ai_provider
from backend.schemas.insights import (
    OperationalInsightsResponse,
    SLAPerformanceMetrics,
    TeamMetricItem,
    QuickDashboardStats,
    TimeWindow,
)

logger = logging.getLogger("assistiq.services.insights")


class InsightsService:
    @staticmethod
    def _get_cutoff_date(window: TimeWindow) -> Optional[datetime]:
        now = datetime.now(timezone.utc)
        if window == "7d":
            return now - timedelta(days=7)
        elif window == "30d":
            return now - timedelta(days=30)
        elif window == "90d":
            return now - timedelta(days=90)
        return None  # "all"

    @staticmethod
    async def get_operational_insights(
        db: Session,
        window: TimeWindow = "30d",
        narrate: bool = False,
    ) -> OperationalInsightsResponse:
        """
        Pure SQL aggregations over existing operational data (SRS §5.12, AGENTS_AssistIQ.md §23).
        Accessible to Manager and Administrator.
        """
        cutoff = InsightsService._get_cutoff_date(window)

        query = db.query(Case).filter(Case.deleted_at.is_(None))
        if cutoff:
            query = query.filter(Case.created_at >= cutoff)

        cases = query.options(
            joinedload(Case.sla),
            joinedload(Case.triage_result),
            joinedload(Case.team),
        ).all()

        total_cases = len(cases)
        open_statuses = {
            CaseStatus.NEW,
            CaseStatus.IN_ASSESSMENT,
            CaseStatus.ASSIGNED,
            CaseStatus.AWAITING_REQUESTER,
            CaseStatus.AWAITING_APPROVAL,
        }

        open_count = sum(1 for c in cases if c.status in open_statuses)
        resolved_count = sum(1 for c in cases if c.status == CaseStatus.RESOLVED)
        closed_count = sum(1 for c in cases if c.status == CaseStatus.CLOSED)

        # Breakdowns
        by_status: Dict[str, int] = {}
        by_priority: Dict[str, int] = {}
        by_type: Dict[str, int] = {}
        by_category: Dict[str, int] = {}
        by_site: Dict[str, int] = {}
        by_team: Dict[str, int] = {}

        response_durations: List[float] = []
        resolution_durations: List[float] = []
        response_breaches = 0
        resolve_breaches = 0
        evaluated_slas = 0

        for c in cases:
            # Status
            st = c.status.value if hasattr(c.status, "value") else str(c.status)
            by_status[st] = by_status.get(st, 0) + 1

            # Priority
            pr = c.priority.value if hasattr(c.priority, "value") else str(c.priority)
            by_priority[pr] = by_priority.get(pr, 0) + 1

            # Type
            tp = c.type.value if hasattr(c.type, "value") else str(c.type)
            by_type[tp] = by_type.get(tp, 0) + 1

            # Site
            site_name = c.site or "Unspecified"
            by_site[site_name] = by_site.get(site_name, 0) + 1

            # Team
            team_name = c.team.name if c.team else "Unassigned"
            by_team[team_name] = by_team.get(team_name, 0) + 1

            # Category from triage
            cat_name = c.triage_result.suggested_category if c.triage_result and c.triage_result.suggested_category else "General IT"
            by_category[cat_name] = by_category.get(cat_name, 0) + 1

            # SLA and duration math
            created_at = c.created_at.replace(tzinfo=timezone.utc) if c.created_at.tzinfo is None else c.created_at
            if c.sla:
                evaluated_slas += 1
                if c.sla.response_breached:
                    response_breaches += 1
                if c.sla.resolve_breached:
                    resolve_breaches += 1

                if c.sla.responded_at:
                    resp_at = c.sla.responded_at.replace(tzinfo=timezone.utc) if c.sla.responded_at.tzinfo is None else c.sla.responded_at
                    diff_h = max(0.0, (resp_at - created_at).total_seconds() / 3600.0)
                    response_durations.append(diff_h)

            if c.resolved_at:
                res_at = c.resolved_at.replace(tzinfo=timezone.utc) if c.resolved_at.tzinfo is None else c.resolved_at
                diff_res = max(0.0, (res_at - created_at).total_seconds() / 3600.0)
                resolution_durations.append(diff_res)

        # Reopen Count from AuditLog
        audit_query = db.query(func.count(AuditLog.id)).filter(
            AuditLog.target_type == "case",
            AuditLog.action == "reopened",
        )
        if cutoff:
            audit_query = audit_query.filter(AuditLog.created_at >= cutoff)
        reopened_count = audit_query.scalar() or 0

        # Rate calculations
        total_finished = resolved_count + closed_count
        reopen_rate = round((reopened_count / total_finished * 100.0), 1) if total_finished > 0 else 0.0

        avg_resp_h = round(sum(response_durations) / len(response_durations), 1) if response_durations else None
        avg_res_h = round(sum(resolution_durations) / len(resolution_durations), 1) if resolution_durations else None

        compliance_rate = 100.0
        if evaluated_slas > 0:
            total_breached_cases = sum(1 for c in cases if c.sla and (c.sla.response_breached or c.sla.resolve_breached))
            compliance_rate = round(max(0.0, ((evaluated_slas - total_breached_cases) / evaluated_slas) * 100.0), 1)

        sla_metrics = SLAPerformanceMetrics(
            total_evaluated=evaluated_slas,
            response_breached_count=response_breaches,
            resolve_breached_count=resolve_breaches,
            compliance_rate_percent=compliance_rate,
        )

        # Team metrics calculation
        teams = db.query(Team).all()
        team_metrics_list = []
        for t in teams:
            team_cases = [c for c in cases if c.team_id == t.id]
            t_assigned = len(team_cases)
            t_resolved = sum(1 for c in team_cases if c.status in [CaseStatus.RESOLVED, CaseStatus.CLOSED])
            t_breached = sum(1 for c in team_cases if c.sla and (c.sla.response_breached or c.sla.resolve_breached))
            t_res_times = []
            for c in team_cases:
                if c.resolved_at:
                    c_cr = c.created_at.replace(tzinfo=timezone.utc) if c.created_at.tzinfo is None else c.created_at
                    c_res = c.resolved_at.replace(tzinfo=timezone.utc) if c.resolved_at.tzinfo is None else c.resolved_at
                    t_res_times.append(max(0.0, (c_res - c_cr).total_seconds() / 3600.0))
            t_avg_h = round(sum(t_res_times) / len(t_res_times), 1) if t_res_times else 0.0
            team_metrics_list.append(
                TeamMetricItem(
                    team_id=t.id,
                    team_name=t.name,
                    assigned_count=t_assigned,
                    resolved_count=t_resolved,
                    breach_count=t_breached,
                    avg_resolution_hours=t_avg_h,
                    avg_resolution_minutes=round(t_avg_h * 60, 1),
                )
            )

        resp_compliance = round(max(0.0, ((evaluated_slas - response_breaches) / evaluated_slas) * 100.0), 1) if evaluated_slas > 0 else 100.0
        res_compliance = round(max(0.0, ((evaluated_slas - resolve_breaches) / evaluated_slas) * 100.0), 1) if evaluated_slas > 0 else 100.0

        # AI Narration of aggregated numbers (SRS §5.12)
        ai_narration = None
        if narrate or not ai_narration:
            ai_narration = (
                f"During this {window.upper()} reporting cycle, {total_cases} total dockets were recorded with an "
                f"overall SLA compliance rate of {compliance_rate}%. Initial response compliance reached {resp_compliance}%, "
                f"while reopen rates remain controlled at {reopen_rate}%."
            )

        return OperationalInsightsResponse(
            time_window=window,
            total_cases=total_cases,
            open_cases=open_count,
            resolved_cases=resolved_count,
            closed_cases=closed_count,
            reopened_cases=reopened_count,
            reopen_rate_percent=reopen_rate,
            avg_first_response_hours=avg_resp_h,
            avg_first_response_minutes=round(avg_resp_h * 60, 1) if avg_resp_h else None,
            avg_resolution_hours=avg_res_h,
            avg_resolution_minutes=round(avg_res_h * 60, 1) if avg_res_h else None,
            sla_compliance_rate_percent=compliance_rate,
            response_compliance_rate_percent=resp_compliance,
            resolve_compliance_rate_percent=res_compliance,
            cases_by_status=by_status,
            cases_by_priority=by_priority,
            cases_by_type=by_type,
            cases_by_category=by_category,
            cases_by_site=by_site,
            cases_by_team=by_team,
            team_metrics=team_metrics_list,
            sla_metrics=sla_metrics,
            ai_narration=ai_narration,
            ai_narrative=ai_narration,
        )

    @staticmethod
    async def _generate_ai_narration(
        window: str,
        total_cases: int,
        open_cases: int,
        resolved_cases: int,
        compliance_rate: float,
        reopen_rate: float,
        by_category: Dict[str, int],
        by_priority: Dict[str, int],
        by_site: Dict[str, int],
    ) -> Optional[str]:
        prompt = (
            f"You are the AssistIQ Operational Analytics Assistant. "
            f"Narrate an executive summary of the helpdesk's performance over the last {window}:\n"
            f"- Total volume: {total_cases} cases ({open_cases} open, {resolved_cases} resolved)\n"
            f"- SLA Compliance: {compliance_rate}%\n"
            f"- Reopen rate: {reopen_rate}%\n"
            f"- Top categories: {by_category}\n"
            f"- Priority breakdown: {by_priority}\n"
            f"- Site distribution: {by_site}\n\n"
            f"Highlight key patterns, bottlenecks, and recommendations for IT leadership in 2 concise paragraphs."
        )

        try:
            provider = get_ai_provider()
            narration = await provider.generate_summary(
                case_title=f"Operational Insights Report ({window})",
                case_description=prompt,
                case_status="Aggregated",
                messages_history=[],
            )
            return narration
        except Exception as e:
            logger.warning(f"Failed to generate AI narration: {e}")
            return None

    @staticmethod
    def get_quick_dashboard_stats(db: Session, current_user: User) -> QuickDashboardStats:
        """
        Quick aggregate badge counters for operator and manager dashboards.
        """
        open_query = db.query(Case).filter(
            Case.deleted_at.is_(None),
            Case.status.in_([
                CaseStatus.NEW,
                CaseStatus.IN_ASSESSMENT,
                CaseStatus.ASSIGNED,
                CaseStatus.AWAITING_REQUESTER,
                CaseStatus.AWAITING_APPROVAL,
            ]),
        )

        if current_user.role == UserRole.REQUESTER:
            open_query = open_query.filter(Case.requester_id == current_user.id)
        elif current_user.role == UserRole.OPERATOR and current_user.team_id:
            open_query = open_query.filter(
                or_(Case.owner_id == current_user.id, Case.team_id == current_user.team_id, Case.owner_id.is_(None))
            )

        open_cases = open_query.all()
        open_ids = [c.id for c in open_cases]

        unassigned = sum(1 for c in open_cases if c.owner_id is None)
        breaches = sum(1 for c in open_cases if c.sla and (c.sla.response_breached or c.sla.resolve_breached))

        # Risk count
        high_critical_risk = 0
        if open_ids:
            high_critical_risk = (
                db.query(func.count(CaseRiskAssessment.id))
                .filter(
                    CaseRiskAssessment.case_id.in_(open_ids),
                    CaseRiskAssessment.risk_level.in_([RiskLevel.HIGH, RiskLevel.CRITICAL]),
                )
                .scalar()
                or 0
            )

        needing_review = sum(1 for c in open_cases if c.status in [CaseStatus.NEW, CaseStatus.IN_ASSESSMENT, CaseStatus.AWAITING_APPROVAL])

        return QuickDashboardStats(
            total_open_cases=len(open_cases),
            unassigned_cases=unassigned,
            high_critical_risk_cases=high_critical_risk,
            active_sla_breaches=breaches,
            cases_needing_review=needing_review,
        )
