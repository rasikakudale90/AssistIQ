from datetime import datetime, timezone, timedelta
from backend.models.enums import Priority, RiskLevel, CaseType, CaseStatus, MessageVisibility
from backend.models.case import Case
from backend.models.sla import SLA
from backend.models.message import Message
from backend.models.ai import AITriageResult
from backend.models.governance import AuditLog
from backend.scheduler.sweep import evaluate_case_risk


def test_evaluate_case_risk_low():
    now = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    case = Case(
        id="case-1",
        title="Software update",
        description="Normal request",
        status=CaseStatus.ASSIGNED,
        priority=Priority.P3,
        updated_at=now - timedelta(hours=2),
        requester_id="user-1",
    )
    sla = SLA(
        case_id="case-1",
        priority=Priority.P3,
        target_response_at=now + timedelta(hours=2),
        target_resolve_at=now + timedelta(hours=70),
        responded_at=now - timedelta(hours=1),
        resolved_at=None,
    )
    risk_level, signals = evaluate_case_risk(
        case=case,
        sla=sla,
        triage=None,
        now=now,
        audit_logs=[],
        messages=[],
    )
    assert risk_level == RiskLevel.LOW
    assert signals["inactivity_hours"] == 2.0
    assert signals["unanswered_follow_ups"] == 0


def test_evaluate_case_risk_critical_on_sla_breach():
    now = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    case = Case(
        id="case-2",
        title="Critical Database Outage",
        description="P1 issue",
        status=CaseStatus.ASSIGNED,
        priority=Priority.P1,
        updated_at=now - timedelta(hours=5),
        requester_id="user-1",
    )
    sla = SLA(
        case_id="case-2",
        priority=Priority.P1,
        target_response_at=now - timedelta(hours=4),
        target_resolve_at=now - timedelta(hours=1),  # Breached
        responded_at=now - timedelta(hours=3),
        resolved_at=None,
    )
    risk_level, signals = evaluate_case_risk(
        case=case,
        sla=sla,
        triage=None,
        now=now,
        audit_logs=[],
        messages=[],
    )
    assert risk_level == RiskLevel.CRITICAL
    assert signals["resolve_breached"] is True


def test_evaluate_case_risk_repeated_reopens():
    now = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    case = Case(
        id="case-3",
        title="Recurring Wi-Fi issue",
        description="Keeps dropping",
        status=CaseStatus.ASSIGNED,
        priority=Priority.P3,
        updated_at=now - timedelta(hours=1),
        requester_id="user-1",
    )
    audit_logs = [
        AuditLog(action="reopened", target_type="case", target_id="case-3"),
        AuditLog(action="reopened", target_type="case", target_id="case-3"),
    ]
    risk_level, signals = evaluate_case_risk(
        case=case,
        sla=None,
        triage=None,
        now=now,
        audit_logs=audit_logs,
        messages=[],
    )
    assert risk_level == RiskLevel.CRITICAL
    assert signals["reopen_count"] == 2
