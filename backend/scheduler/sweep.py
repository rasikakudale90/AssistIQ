import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.db.session import SessionLocal
from backend.models.enums import (
    CaseStatus,
    Priority,
    RiskLevel,
    EscalationReason,
    EscalationStatus,
    MessageVisibility,
    UserRole,
)
from backend.models.case import Case
from backend.models.sla import SLA
from backend.models.message import Message
from backend.models.ai import CaseRiskAssessment, EscalationEvent, AITriageResult
from backend.models.governance import AuditLog
from backend.providers.notifications import get_notification_provider
from backend.repositories.audit_repository import AuditRepository
from backend.services.sla_service import SLAService

logger = logging.getLogger("assistiq.scheduler.sweep")


def evaluate_case_risk(
    case: Case,
    sla: Optional[SLA],
    triage: Optional[AITriageResult],
    now: datetime,
    audit_logs: List[AuditLog],
    messages: List[Message],
) -> tuple[RiskLevel, Dict[str, any]]:
    """
    Computes signals and assigns a RiskLevel (Low, Moderate, High, Critical) per SRS §5.7.
    """
    signals = {}

    # 1. Inactivity duration (hours since last update or message)
    last_activity = case.updated_at
    if messages:
        last_msg_time = messages[-1].created_at
        if last_msg_time.tzinfo is None:
            last_msg_time = last_msg_time.replace(tzinfo=timezone.utc)
        if last_activity.tzinfo is None:
            last_activity = last_activity.replace(tzinfo=timezone.utc)
        last_activity = max(last_activity, last_msg_time)

    if last_activity.tzinfo is None:
        last_activity = last_activity.replace(tzinfo=timezone.utc)
    inactivity_hours = max(0.0, round((now - last_activity).total_seconds() / 3600.0, 1))
    signals["inactivity_hours"] = inactivity_hours

    # 2. Consecutive unanswered requester follow-ups
    unanswered_follow_ups = 0
    for msg in reversed(messages):
        if msg.author_id == case.requester_id and msg.visibility == MessageVisibility.REQUESTER_VISIBLE:
            unanswered_follow_ups += 1
        else:
            break
    signals["unanswered_follow_ups"] = unanswered_follow_ups

    # 3. Reassignment count from audit log
    reassignment_count = sum(1 for log in audit_logs if log.action == "assignment")
    signals["reassignment_count"] = reassignment_count

    # 4. Missing info flag
    missing_info_flag = bool(triage and triage.missing_info and len(triage.missing_info) > 0)
    signals["missing_info_flag"] = missing_info_flag

    # 5. Hours remaining to SLA deadline & breach status
    hours_to_resolve_deadline = None
    resolve_breached = False
    if sla:
        target_res = sla.target_resolve_at
        if target_res.tzinfo is None:
            target_res = target_res.replace(tzinfo=timezone.utc)
        hours_to_resolve_deadline = round((target_res - now).total_seconds() / 3600.0, 1)
        resolve_breached = now > target_res and not sla.resolved_at
    signals["hours_to_resolve_deadline"] = hours_to_resolve_deadline
    signals["resolve_breached"] = resolve_breached

    # 6. Reopen count
    reopen_count = sum(1 for log in audit_logs if log.action == "reopened")
    signals["reopen_count"] = reopen_count

    # Calculate overall risk level
    # Critical conditions: SLA breached, or reopened >= 2 times, or >= 3 unanswered follow-ups with inactivity > 12h
    if resolve_breached or reopen_count >= 2 or (unanswered_follow_ups >= 3 and inactivity_hours > 12):
        risk_level = RiskLevel.CRITICAL
    # High conditions: < 20% SLA window remaining, or reassigned >= 3 times, or unanswered followups >= 2
    elif (hours_to_resolve_deadline is not None and hours_to_resolve_deadline <= 2 and case.priority in [Priority.P1, Priority.P2]) or reassignment_count >= 3 or unanswered_follow_ups >= 2:
        risk_level = RiskLevel.HIGH
    # Moderate conditions: inactivity > 24h, or missing info flag, or reassigned >= 2
    elif inactivity_hours >= 24 or missing_info_flag or reassignment_count >= 2:
        risk_level = RiskLevel.MODERATE
    else:
        risk_level = RiskLevel.LOW

    return risk_level, signals


async def run_the_sweep(db: Optional[Session] = None) -> Dict[str, int]:
    """
    Executes 'The Sweep' periodic evaluation for all open cases (SRS §3.5, §5.7, §5.8).
    Runs in-process via APScheduler.
    """
    logger.info("Starting AssistIQ Sweep job...")
    owns_session = False
    if db is None:
        db = SessionLocal()
        owns_session = True

    stats = {
        "cases_evaluated": 0,
        "sla_breaches_detected": 0,
        "risk_assessments_written": 0,
        "escalations_raised": 0,
    }

    try:
        now = datetime.now(timezone.utc)
        # 1. Fetch all open, non-terminal cases
        open_cases = (
            db.query(Case)
            .filter(
                Case.status.in_([
                    CaseStatus.NEW,
                    CaseStatus.IN_ASSESSMENT,
                    CaseStatus.ASSIGNED,
                    CaseStatus.AWAITING_REQUESTER,
                    CaseStatus.AWAITING_APPROVAL,
                ]),
                Case.deleted_at.is_(None),
            )
            .all()
        )

        notification_provider = get_notification_provider()

        for case in open_cases:
            stats["cases_evaluated"] += 1
            sla = db.query(SLA).filter(SLA.case_id == case.id).first()
            triage = db.query(AITriageResult).filter(AITriageResult.case_id == case.id).first()
            audit_logs = (
                db.query(AuditLog)
                .filter(AuditLog.target_type == "case", AuditLog.target_id == case.id)
                .all()
            )
            messages = (
                db.query(Message)
                .filter(Message.case_id == case.id)
                .order_by(Message.created_at.asc())
                .all()
            )

            # --- A. Check SLA Breaches & Deadlines ---
            if sla:
                target_resp = sla.target_response_at
                if target_resp.tzinfo is None:
                    target_resp = target_resp.replace(tzinfo=timezone.utc)
                if not sla.responded_at and now > target_resp and not sla.response_breached:
                    sla.response_breached = True
                    stats["sla_breaches_detected"] += 1
                    AuditRepository.create_log(
                        db=db,
                        actor_id="system",
                        action="sla_response_breached",
                        target_type="case",
                        target_id=case.id,
                        after_value={"priority": case.priority.value},
                    )

                target_res = sla.target_resolve_at
                if target_res.tzinfo is None:
                    target_res = target_res.replace(tzinfo=timezone.utc)
                if not sla.resolved_at and now > target_res and not sla.resolve_breached:
                    sla.resolve_breached = True
                    stats["sla_breaches_detected"] += 1
                    AuditRepository.create_log(
                        db=db,
                        actor_id="system",
                        action="sla_resolve_breached",
                        target_type="case",
                        target_id=case.id,
                        after_value={"priority": case.priority.value},
                    )

            # --- B. Compute & Record Risk Assessment ---
            risk_level, signals = evaluate_case_risk(case, sla, triage, now, audit_logs, messages)
            risk_record = CaseRiskAssessment(
                case_id=case.id,
                risk_level=risk_level,
                signals=signals,
                computed_at=now,
            )
            db.add(risk_record)
            stats["risk_assessments_written"] += 1

            # --- C. Evaluate Escalation Triggers (SRS §5.8) ---
            # Existing open escalations for this case
            existing_open_escalations = (
                db.query(EscalationEvent)
                .filter(EscalationEvent.case_id == case.id, EscalationEvent.status == EscalationStatus.OPEN)
                .all()
            )

            should_escalate = False
            escalation_reason = None

            if sla and sla.resolve_breached:
                should_escalate = True
                escalation_reason = EscalationReason.MISSED_DEADLINE
            elif signals.get("reopen_count", 0) > 1:
                should_escalate = True
                escalation_reason = EscalationReason.REPEATED_REOPEN
            elif risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                should_escalate = True
                escalation_reason = EscalationReason.HIGH_RISK

            if should_escalate and not existing_open_escalations:
                escalated_to = "TeamLead" if case.team_id else "Manager"
                esc_event = EscalationEvent(
                    case_id=case.id,
                    trigger_reason=escalation_reason,
                    escalated_to=escalated_to,
                    escalated_by="system",
                    status=EscalationStatus.OPEN,
                )
                db.add(esc_event)
                stats["escalations_raised"] += 1

                AuditRepository.create_log(
                    db=db,
                    actor_id="system",
                    action="automatic_escalation",
                    target_type="case",
                    target_id=case.id,
                    after_value={
                        "reason": escalation_reason.value,
                        "risk_level": risk_level.value,
                        "escalated_to": escalated_to,
                    },
                )

                # Trigger notifications via NotificationProvider (SRS §5.10)
                try:
                    if case.owner and case.owner.email:
                        await notification_provider.send_email(
                            to_email=case.owner.email,
                            subject=f"[ESCALATION] Case {case.reference_number}: {case.title}",
                            html_content=f"<p>Case <strong>{case.reference_number}</strong> has been escalated due to <em>{escalation_reason.value}</em> (Risk: {risk_level.value}).</p>",
                        )
                except Exception as notif_err:
                    logger.warning(f"Failed to send escalation notification email: {notif_err}")

        db.commit()
        logger.info(f"Sweep completed successfully. Evaluated: {stats['cases_evaluated']}, Breaches: {stats['sla_breaches_detected']}, Risks: {stats['risk_assessments_written']}, Escalations: {stats['escalations_raised']}.")
    except Exception as e:
        logger.error(f"Error executing Sweep job: {e}", exc_info=True)
        db.rollback()
    finally:
        if owns_session:
            db.close()

    return stats
