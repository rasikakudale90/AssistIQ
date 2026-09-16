from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from backend.models import (
    User,
    Team,
    Case,
    CaseRelationship,
    Message,
    Attachment,
    SLA,
    AITriageResult,
    CaseSummary,
    CaseRiskAssessment,
    EscalationEvent,
    CommunicationDraft,
    AuditLog,
    Approval,
    KnowledgeArticle,
    UserRole,
    AuthProvider,
    AvailabilityStatus,
    CaseType,
    CaseStatus,
    Priority,
    MessageVisibility,
    ConfidenceLevel,
    RiskLevel,
    EscalationReason,
    EscalationStatus,
    DraftType,
    DraftStatus,
    ApprovalDecision,
    KnowledgeState,
    CaseRelationshipType,
)


def test_create_team_and_users(db_session: Session):
    # 1. Create a Team
    team = Team(name="IT Infrastructure", description="Core infra team")
    db_session.add(team)
    db_session.commit()
    db_session.refresh(team)

    assert team.id is not None
    assert team.name == "IT Infrastructure"

    # 2. Create Users across roles
    requester = User(
        email="requester@test.com",
        password_hash="hashed_pw",
        role=UserRole.REQUESTER,
        site="Building A",
        email_verified=True,
    )
    operator = User(
        email="operator@test.com",
        password_hash="hashed_pw",
        role=UserRole.OPERATOR,
        team_id=team.id,
        site="Building A",
        availability_status=AvailabilityStatus.AVAILABLE,
        email_verified=True,
    )
    google_user = User(
        email="google.user@test.com",
        auth_provider=AuthProvider.GOOGLE,
        oauth_subject_id="google-sub-123456",
        role=UserRole.REQUESTER,
        email_verified=True,
    )
    db_session.add_all([requester, operator, google_user])
    db_session.commit()

    assert requester.id is not None
    assert operator.team_id == team.id
    assert google_user.password_hash is None
    assert google_user.auth_provider == AuthProvider.GOOGLE


def test_create_case_lifecycle_and_relations(db_session: Session):
    # Setup users
    requester = User(email="req2@test.com", role=UserRole.REQUESTER)
    operator = User(email="op2@test.com", role=UserRole.OPERATOR)
    db_session.add_all([requester, operator])
    db_session.commit()

    # 1. Create Case
    case = Case(
        reference_number="INC-2026-000001",
        type=CaseType.INCIDENT,
        title="VPN Connection Failure",
        description="Cannot connect to corporate VPN after password reset.",
        status=CaseStatus.NEW,
        priority=Priority.P2,
        requester_id=requester.id,
        version=1,
    )
    db_session.add(case)
    db_session.commit()
    db_session.refresh(case)

    assert case.id is not None
    assert case.version == 1
    assert case.status == CaseStatus.NEW

    # 2. Messages (requester visible vs internal)
    msg1 = Message(
        case_id=case.id,
        author_id=requester.id,
        body="Any update on this?",
        visibility=MessageVisibility.REQUESTER_VISIBLE,
    )
    msg2 = Message(
        case_id=case.id,
        author_id=operator.id,
        body="Checking RADIUS authentication logs.",
        visibility=MessageVisibility.INTERNAL_ONLY,
    )
    db_session.add_all([msg1, msg2])
    db_session.commit()

    assert len(case.messages) == 2

    # 3. Attachment
    attachment = Attachment(
        case_id=case.id,
        storage_path="cases/INC-2026-000001/screenshot.png",
        file_name="screenshot.png",
        file_type="image/png",
        file_size=204800,
        uploaded_by=requester.id,
    )
    db_session.add(attachment)
    db_session.commit()
    assert len(case.attachments) == 1

    # 4. SLA
    now = datetime.now(timezone.utc)
    sla = SLA(
        case_id=case.id,
        priority=Priority.P2,
        target_response_at=now + timedelta(hours=1),
        target_resolve_at=now + timedelta(hours=8),
    )
    db_session.add(sla)
    db_session.commit()
    assert case.sla is not None
    assert case.sla.response_breached is False


def test_create_ai_and_governance_models(db_session: Session):
    requester = User(email="req3@test.com", role=UserRole.REQUESTER)
    operator = User(email="op3@test.com", role=UserRole.OPERATOR)
    db_session.add_all([requester, operator])
    db_session.commit()

    case = Case(
        reference_number="REQ-2026-000002",
        type=CaseType.SERVICE_REQUEST,
        title="Request for Figma License",
        description="Need Figma design seat for Q3 project.",
        status=CaseStatus.IN_ASSESSMENT,
        priority=Priority.P3,
        requester_id=requester.id,
    )
    db_session.add(case)
    db_session.commit()

    # 1. AI Triage Result
    triage = AITriageResult(
        case_id=case.id,
        suggested_category="Software Access",
        suggested_severity="Low",
        suggested_priority="P3",
        confidence_level=ConfidenceLevel.HIGH,
        confidence_score=0.92,
        supporting_factors=["Figma license request", "Standard software catalog item"],
        missing_info=[],
        suggested_team="Software Licensing",
        recommended_next_action="Verify manager approval and assign to procurement.",
        related_case_ids=[],
    )
    db_session.add(triage)

    # 2. Case Summary
    summary = CaseSummary(
        case_id=case.id,
        summary_text="Requester is asking for Figma license for Q3 project.",
    )
    db_session.add(summary)

    # 3. Case Risk Assessment
    risk = CaseRiskAssessment(
        case_id=case.id,
        risk_level=RiskLevel.LOW,
        signals={"inactivity_hours": 0.5, "missing_info_flag": False},
    )
    db_session.add(risk)

    # 4. Escalation Event
    escalation = EscalationEvent(
        case_id=case.id,
        trigger_reason=EscalationReason.OPERATOR_REQUESTED,
        escalated_to=operator.id,
        escalated_by=operator.id,
        status=EscalationStatus.OPEN,
    )
    db_session.add(escalation)

    # 5. Communication Draft
    draft = CommunicationDraft(
        case_id=case.id,
        draft_type=DraftType.PROGRESS_UPDATE,
        body="Your Figma license request has been submitted for budget approval.",
        status=DraftStatus.DRAFT,
    )
    db_session.add(draft)

    # 6. Audit Log
    audit = AuditLog(
        actor_id=operator.id,
        action="status_change",
        target_type="case",
        target_id=case.id,
        before_value={"status": "New"},
        after_value={"status": "InAssessment"},
    )
    db_session.add(audit)

    # 7. Approval
    approval = Approval(
        case_id=case.id,
        approver_id=operator.id,
        decision=ApprovalDecision.PENDING,
    )
    db_session.add(approval)

    # 8. Knowledge Article
    article = KnowledgeArticle(
        title="How to request design software licenses",
        body="Follow these steps in the software catalog...",
        category="Software",
        owner_id=operator.id,
        state=KnowledgeState.PUBLISHED,
    )
    db_session.add(article)

    db_session.commit()

    assert case.triage_result.confidence_level == ConfidenceLevel.HIGH
    assert case.summary.summary_text.startswith("Requester is asking")
    assert len(case.risk_assessments) == 1
    assert len(case.escalations) == 1
    assert len(case.communication_drafts) == 1
    assert audit.id is not None
    assert article.id is not None
