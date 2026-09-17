from datetime import datetime, timezone, timedelta
import pytest
from sqlalchemy.orm import Session

from backend.models.enums import Priority, CaseType, CaseStatus
from backend.models.case import Case
from backend.models.user import User, UserRole
from backend.services.sla_service import SLAService


def test_sla_deadline_calculations():
    now = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    # P1: 15 min response, 4 hours resolve
    resp_p1, res_p1 = SLAService.calculate_deadlines(Priority.P1, now)
    assert resp_p1 == now + timedelta(minutes=15)
    assert res_p1 == now + timedelta(hours=4)

    # P2: 1 hour response, 8 hours resolve
    resp_p2, res_p2 = SLAService.calculate_deadlines(Priority.P2, now)
    assert resp_p2 == now + timedelta(hours=1)
    assert res_p2 == now + timedelta(hours=8)

    # P3: 4 hours response, 72 hours resolve
    resp_p3, res_p3 = SLAService.calculate_deadlines(Priority.P3, now)
    assert resp_p3 == now + timedelta(hours=4)
    assert res_p3 == now + timedelta(hours=72)

    # P4: 24 hours response, 120 hours resolve
    resp_p4, res_p4 = SLAService.calculate_deadlines(Priority.P4, now)
    assert resp_p4 == now + timedelta(hours=24)
    assert res_p4 == now + timedelta(hours=120)


def test_sla_lifecycle_and_breach_detection(db_session: Session):
    user = User(
        email="sla_test_user@example.com",
        password_hash="hash",
        role=UserRole.REQUESTER,
    )
    db_session.add(user)
    db_session.flush()

    past_time = datetime.now(timezone.utc) - timedelta(hours=5)
    case = Case(
        reference_number="INC-2026-000999",
        type=CaseType.INCIDENT,
        title="Server Down",
        description="P1 critical server failure",
        priority=Priority.P1,
        requester_id=user.id,
        created_at=past_time,
        version=1,
    )
    db_session.add(case)
    db_session.flush()

    sla = SLAService.create_sla_for_case(db_session, case)
    db_session.commit()

    assert sla.case_id == case.id
    assert sla.priority == Priority.P1
    assert sla.response_breached is False

    # Record first response after deadline has passed
    SLAService.record_first_response(db_session, case.id)
    db_session.commit()
    db_session.refresh(sla)

    assert sla.responded_at is not None
    assert sla.response_breached is True

    # Record resolution
    SLAService.record_resolution(db_session, case.id)
    db_session.commit()
    db_session.refresh(sla)

    assert sla.resolved_at is not None
    assert sla.resolve_breached is True

    # Test Reopen SLA Reset
    SLAService.reset_sla_on_reopen(db_session, case)
    db_session.commit()
    db_session.refresh(sla)

    assert sla.response_breached is False
    assert sla.resolve_breached is False
    assert sla.responded_at is None
    assert sla.resolved_at is None
