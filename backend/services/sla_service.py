from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy.orm import Session

from backend.models.enums import Priority
from backend.models.case import Case
from backend.models.sla import SLA
from backend.schemas.sla import SLAResponse


class SLAService:
    # 24/7 wall-clock targets per SRS §4.3
    TARGETS = {
        Priority.P1: {"response": timedelta(minutes=15), "resolve": timedelta(hours=4)},
        Priority.P2: {"response": timedelta(hours=1), "resolve": timedelta(hours=8)},
        Priority.P3: {"response": timedelta(hours=4), "resolve": timedelta(hours=72)},
        Priority.P4: {"response": timedelta(hours=24), "resolve": timedelta(hours=120)},
    }

    @staticmethod
    def calculate_deadlines(priority: Priority, start_time: Optional[datetime] = None) -> tuple[datetime, datetime]:
        base_time = start_time or datetime.now(timezone.utc)
        if base_time.tzinfo is None:
            base_time = base_time.replace(tzinfo=timezone.utc)

        config = SLAService.TARGETS.get(priority, SLAService.TARGETS[Priority.P3])
        target_response = base_time + config["response"]
        target_resolve = base_time + config["resolve"]
        return target_response, target_resolve

    @staticmethod
    def create_sla_for_case(db: Session, case: Case) -> SLA:
        """
        Initializes the 24/7 SLA record for a new case.
        """
        target_response, target_resolve = SLAService.calculate_deadlines(case.priority, case.created_at)

        sla = SLA(
            case_id=case.id,
            priority=case.priority,
            target_response_at=target_response,
            target_resolve_at=target_resolve,
            response_breached=False,
            resolve_breached=False,
        )
        db.add(sla)
        return sla

    @staticmethod
    def record_first_response(db: Session, case_id: str) -> Optional[SLA]:
        """
        Records the first response timestamp when an IT staff member sends a message.
        """
        sla = db.query(SLA).filter(SLA.case_id == case_id).first()
        if not sla or sla.responded_at is not None:
            return sla

        now = datetime.now(timezone.utc)
        sla.responded_at = now
        target_resp = sla.target_response_at
        if target_resp.tzinfo is None:
            target_resp = target_resp.replace(tzinfo=timezone.utc)

        if now > target_resp:
            sla.response_breached = True

        db.flush()
        return sla

    @staticmethod
    def record_resolution(db: Session, case_id: str) -> Optional[SLA]:
        """
        Records resolution timestamp when case is marked Resolved.
        """
        sla = db.query(SLA).filter(SLA.case_id == case_id).first()
        if not sla:
            return None

        now = datetime.now(timezone.utc)
        sla.resolved_at = now
        target_res = sla.target_resolve_at
        if target_res.tzinfo is None:
            target_res = target_res.replace(tzinfo=timezone.utc)

        if now > target_res:
            sla.resolve_breached = True

        db.flush()
        return sla

    @staticmethod
    def reset_sla_on_reopen(db: Session, case: Case) -> SLA:
        """
        When a closed case is reopened within 7 days, starts a new SLA clock per SRS §6 (Reopen rules).
        """
        sla = db.query(SLA).filter(SLA.case_id == case.id).first()
        now = datetime.now(timezone.utc)
        target_response, target_resolve = SLAService.calculate_deadlines(case.priority, now)

        if not sla:
            sla = SLA(
                case_id=case.id,
                priority=case.priority,
                target_response_at=target_response,
                target_resolve_at=target_resolve,
                response_breached=False,
                resolve_breached=False,
            )
            db.add(sla)
        else:
            sla.target_response_at = target_response
            sla.target_resolve_at = target_resolve
            sla.response_breached = False
            sla.resolve_breached = False
            sla.responded_at = None
            sla.resolved_at = None
            sla.updated_at = now

        db.flush()
        return sla

    @staticmethod
    def build_sla_response(sla: SLA) -> SLAResponse:
        now = datetime.now(timezone.utc)
        resp = SLAResponse.model_validate(sla)

        # Calculate time remaining for response
        target_resp = sla.target_response_at
        if target_resp.tzinfo is None:
            target_resp = target_resp.replace(tzinfo=timezone.utc)

        if not sla.responded_at:
            resp_diff = int((target_resp - now).total_seconds())
            resp.response_time_remaining_seconds = max(0, resp_diff)
            # Approaching if <= 20% of window remains
            total_window = SLAService.TARGETS.get(sla.priority, SLAService.TARGETS[Priority.P3])["response"].total_seconds()
            if 0 < resp_diff <= (0.2 * total_window):
                resp.is_response_approaching = True

        # Calculate time remaining for resolution
        target_res = sla.target_resolve_at
        if target_res.tzinfo is None:
            target_res = target_res.replace(tzinfo=timezone.utc)

        if not sla.resolved_at:
            res_diff = int((target_res - now).total_seconds())
            resp.resolve_time_remaining_seconds = max(0, res_diff)
            total_res_window = SLAService.TARGETS.get(sla.priority, SLAService.TARGETS[Priority.P3])["resolve"].total_seconds()
            if 0 < res_diff <= (0.2 * total_res_window):
                resp.is_resolve_approaching = True

        return resp
