"""
AssistIQ — Comprehensive Demo Data Seeder Script (SRS §35, §11, §8.2)
Populates:
- 5 Users (one per role: Requester, Operator, TeamLead, Manager, Administrator)
- 3 Teams (Desktop Support, Network Engineering, Systems & Cloud Operations)
- 18 Cases across all lifecycle states (New, InAssessment, Assigned, AwaitingRequester, AwaitingApproval, Resolved, Closed, Cancelled, Reopened)
- 24/7 SLAs, Messages (Requester & Internal), AITriageResults, CaseSummaries, Risk Assessments, Escalations, Drafts, Knowledge Articles, and AuditLogs.
"""

import sys
import os
from datetime import datetime, timezone, timedelta

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.orm import Session
from backend.db.session import SessionLocal, Base, engine
from backend.core.security import hash_password
from backend.models.enums import (
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
    KnowledgeState,
)
from backend.models.user import User, Team
from backend.models.case import Case
from backend.models.sla import SLA
from backend.models.message import Message, Attachment
from backend.models.ai import (
    AITriageResult,
    CaseSummary,
    CaseRiskAssessment,
    EscalationEvent,
    CommunicationDraft,
)
from backend.models.governance import KnowledgeArticle, AuditLog
from backend.services.sla_service import SLAService


def seed_demo_data(db: Session) -> None:
    print("🌱 [AssistIQ Seeder] Starting database seeding...")

    # Default password hash for all demo users: Password123!@#
    default_password_hash = hash_password("Password123!@#")
    now = datetime.now(timezone.utc)

    # 1. Seed Teams
    print("  -> Seeding Teams...")
    desktop_team = db.query(Team).filter(Team.name == "Desktop Support").first()
    if not desktop_team:
        desktop_team = Team(name="Desktop Support", description="Hardware, OS, and local peripherals")
        db.add(desktop_team)

    network_team = db.query(Team).filter(Team.name == "Network Engineering").first()
    if not network_team:
        network_team = Team(name="Network Engineering", description="Firewalls, VPNs, switches, and corporate Wi-Fi")
        db.add(network_team)

    systems_team = db.query(Team).filter(Team.name == "Systems & Cloud Operations").first()
    if not systems_team:
        systems_team = Team(name="Systems & Cloud Operations", description="Cloud infrastructure, databases, and enterprise identity")
        db.add(systems_team)

    db.flush()

    # 2. Seed Users (1 per implemented role)
    print("  -> Seeding 5 Role-Representative Users...")
    users_spec = [
        ("requester@assistiq.local", UserRole.REQUESTER, None, "NYC HQ", AvailabilityStatus.AVAILABLE),
        ("operator@assistiq.local", UserRole.OPERATOR, desktop_team.id, "NYC HQ", AvailabilityStatus.AVAILABLE),
        ("lead@assistiq.local", UserRole.TEAM_LEAD, network_team.id, "London Office", AvailabilityStatus.AVAILABLE),
        ("manager@assistiq.local", UserRole.MANAGER, None, "NYC HQ", AvailabilityStatus.AVAILABLE),
        ("admin@assistiq.local", UserRole.ADMINISTRATOR, None, "Remote", AvailabilityStatus.AVAILABLE),
    ]

    user_map = {}
    for email, role, team_id, site, avail in users_spec:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                email=email,
                password_hash=default_password_hash,
                role=role,
                team_id=team_id,
                site=site,
                availability_status=avail,
                email_verified=True,
            )
            db.add(user)
            db.flush()
        user_map[role] = user

    # Set team leads
    desktop_team.lead_id = user_map[UserRole.OPERATOR].id
    network_team.lead_id = user_map[UserRole.TEAM_LEAD].id

    # 3. Seed Knowledge Base Articles
    print("  -> Seeding Knowledge Base Articles...")
    kb_specs = [
        (
            "Global VPN Setup Guide (Cisco AnyConnect)",
            "Step-by-step instructions for connecting to the corporate VPN using AnyConnect with multi-factor authentication.",
            "Network",
            KnowledgeState.PUBLISHED,
        ),
        (
            "Self-Service Password Reset (SSPR) Protocol",
            "How to unlock your corporate directory account and reset your domain password securely without calling the helpdesk.",
            "Access & Identity",
            KnowledgeState.PUBLISHED,
        ),
        (
            "Standard Developer Laptop Provisioning Baseline",
            "Hardware specs, pre-installed developer runtimes (Docker, Node.js, Python), and corporate security certificates.",
            "Hardware",
            KnowledgeState.PUBLISHED,
        ),
        (
            "Emergency Escalation Procedures for P1 Incidents",
            "Tier-1 operator response checklist when major database or network outages occur outside core business hours.",
            "Security",
            KnowledgeState.DRAFT,
        ),
    ]

    for title, body, cat, state in kb_specs:
        existing_kb = db.query(KnowledgeArticle).filter(KnowledgeArticle.title == title).first()
        if not existing_kb:
            kb = KnowledgeArticle(
                title=title,
                body=body,
                category=cat,
                state=state,
                owner_id=user_map[UserRole.ADMINISTRATOR].id,
            )
            db.add(kb)

    # 4. Seed 18 Cases Across All Lifecycle States
    print("  -> Seeding 18 Cases across diverse lifecycle states...")
    cases_spec = [
        # 1. Critical Database Outage (P1, Breached, Escalated)
        {
            "ref": "INC-2026-000001",
            "type": CaseType.INCIDENT,
            "title": "Production PostgreSQL Cluster Read Replica Failure",
            "description": "Primary read replica is failing health checks; reporting dashboard experiencing database timeouts.",
            "status": CaseStatus.ASSIGNED,
            "priority": Priority.P1,
            "team": systems_team,
            "owner": user_map[UserRole.OPERATOR],
            "site": "NYC HQ",
            "hours_ago": 6.0,
            "category": "Software",
            "risk": RiskLevel.CRITICAL,
            "escalated": True,
        },
        # 2. Wi-Fi Connectivity Drops (P2, High Risk)
        {
            "ref": "INC-2026-000002",
            "type": CaseType.INCIDENT,
            "title": "Executive Boardroom Wi-Fi Constant Disconnections",
            "description": "Access point AP-304 in boardroom drops connections every 10 minutes during video conferences.",
            "status": CaseStatus.IN_ASSESSMENT,
            "priority": Priority.P2,
            "team": network_team,
            "owner": None,
            "site": "NYC HQ",
            "hours_ago": 2.5,
            "category": "Network",
            "risk": RiskLevel.HIGH,
            "escalated": False,
        },
        # 3. New Hire Laptop Provisioning (Service Request, Assigned)
        {
            "ref": "REQ-2026-000003",
            "type": CaseType.SERVICE_REQUEST,
            "title": "New Senior Frontend Engineer Onboarding Hardware",
            "description": "Please prepare a 16-inch MacBook Pro M3, 32GB RAM, 4K external monitor, and dock for new engineer starting Monday.",
            "status": CaseStatus.ASSIGNED,
            "priority": Priority.P3,
            "team": desktop_team,
            "owner": user_map[UserRole.OPERATOR],
            "site": "London Office",
            "hours_ago": 24.0,
            "category": "Hardware",
            "risk": RiskLevel.LOW,
            "escalated": False,
        },
        # 4. VPN Gateway Certificate Expiration (P2, Awaiting Approval)
        {
            "ref": "INC-2026-000004",
            "type": CaseType.INCIDENT,
            "title": "EMEA VPN Gateway SSL Certificate Renewal",
            "description": "SSL certificate expires in 48 hours. Requires CA renewal approval before certificate replacement.",
            "status": CaseStatus.AWAITING_APPROVAL,
            "priority": Priority.P2,
            "team": network_team,
            "owner": user_map[UserRole.TEAM_LEAD],
            "site": "London Office",
            "hours_ago": 12.0,
            "category": "Security",
            "risk": RiskLevel.MODERATE,
            "escalated": False,
        },
        # 5. SAP ERP Account Locked (P3, Awaiting Requester)
        {
            "ref": "INC-2026-000005",
            "type": CaseType.INCIDENT,
            "title": "SAP Financial Module Account Locked After 3 Failed Logins",
            "description": "Account locked during month-end payroll reconciliation. Need unlocking and password reset.",
            "status": CaseStatus.AWAITING_REQUESTER,
            "priority": Priority.P3,
            "team": systems_team,
            "owner": user_map[UserRole.OPERATOR],
            "site": "NYC HQ",
            "hours_ago": 18.0,
            "category": "Access & Identity",
            "risk": RiskLevel.LOW,
            "escalated": False,
        },
        # 6. Outlook Crashing on Attachment Open (Resolved)
        {
            "ref": "INC-2026-000006",
            "type": CaseType.INCIDENT,
            "title": "Outlook 365 Crashes When Opening Encrypted PDF Invoices",
            "description": "Outlook terminates unexpectedly whenever Adobe Acrobat Reader plugin renders protected attachments.",
            "status": CaseStatus.RESOLVED,
            "priority": Priority.P3,
            "team": desktop_team,
            "owner": user_map[UserRole.OPERATOR],
            "site": "NYC HQ",
            "hours_ago": 36.0,
            "resolved_ago": 4.0,
            "category": "Software",
            "risk": RiskLevel.LOW,
            "escalated": False,
        },
        # 7. Monitor Replacement Request (Closed)
        {
            "ref": "REQ-2026-000007",
            "type": CaseType.SERVICE_REQUEST,
            "title": "Dell 27-inch 4K Monitor Replacement for Finance Team",
            "description": "Flickering backlight on asset MON-2024-991. Replaced under manufacturer warranty.",
            "status": CaseStatus.CLOSED,
            "priority": Priority.P4,
            "team": desktop_team,
            "owner": user_map[UserRole.OPERATOR],
            "site": "NYC HQ",
            "hours_ago": 96.0,
            "resolved_ago": 48.0,
            "closed_ago": 24.0,
            "category": "Hardware",
            "risk": RiskLevel.LOW,
            "escalated": False,
        },
        # 8. Unresolved Network Issue (Reopened Case)
        {
            "ref": "INC-2026-000008",
            "type": CaseType.INCIDENT,
            "title": "Floor 4 Switch Port Speed Dropping to 10Mbps",
            "description": "Ethernet wall jacks dropping speed negotiation. Closed earlier but issue recurred for marketing workstations.",
            "status": CaseStatus.ASSIGNED,
            "priority": Priority.P2,
            "team": network_team,
            "owner": user_map[UserRole.TEAM_LEAD],
            "site": "NYC HQ",
            "hours_ago": 48.0,
            "category": "Network",
            "risk": RiskLevel.HIGH,
            "escalated": True,
            "reopened": True,
        },
        # 9. Cancelled Case
        {
            "ref": "REQ-2026-000009",
            "type": CaseType.SERVICE_REQUEST,
            "title": "Temporary Admin Rights on Build Machine",
            "description": "Requested local admin rights; user realized project was rescheduled. Withdrawn by requester.",
            "status": CaseStatus.CANCELLED,
            "priority": Priority.P4,
            "team": systems_team,
            "owner": None,
            "site": "Remote",
            "hours_ago": 10.0,
            "category": "Access & Identity",
            "risk": RiskLevel.LOW,
            "escalated": False,
        },
        # 10. New Incoming Case
        {
            "ref": "INC-2026-000010",
            "type": CaseType.INCIDENT,
            "title": "Color Laser Printer Paper Jam in Tray 2",
            "description": "HP LaserJet Enterprise 500 paper feed stuck on thick letterhead paper in 2nd floor copy room.",
            "status": CaseStatus.NEW,
            "priority": Priority.P4,
            "team": desktop_team,
            "owner": None,
            "site": "London Office",
            "hours_ago": 0.5,
            "category": "Hardware",
            "risk": RiskLevel.LOW,
            "escalated": False,
        },
        # 11. Cloud Storage Quota Increase (Service Request)
        {
            "ref": "REQ-2026-000011",
            "type": CaseType.SERVICE_REQUEST,
            "title": "AWS S3 Analytics Data Lake Bucket Quota Expansion",
            "description": "Data engineering pipeline reaching 90% capacity. Requesting increase from 5TB to 15TB.",
            "status": CaseStatus.ASSIGNED,
            "priority": Priority.P3,
            "team": systems_team,
            "owner": user_map[UserRole.OPERATOR],
            "site": "Remote",
            "hours_ago": 15.0,
            "category": "Software",
            "risk": RiskLevel.LOW,
            "escalated": False,
        },
        # 12. Security Phishing Email Report (Incident)
        {
            "ref": "INC-2026-000012",
            "type": CaseType.INCIDENT,
            "title": "Suspicious Wire Transfer Request Email Targeting Finance",
            "description": "Received spoofed CEO email requesting urgent bank transfer. Domain was ceo-office-corp.co.",
            "status": CaseStatus.ASSIGNED,
            "priority": Priority.P1,
            "team": network_team,
            "owner": user_map[UserRole.TEAM_LEAD],
            "site": "NYC HQ",
            "hours_ago": 3.0,
            "category": "Security",
            "risk": RiskLevel.CRITICAL,
            "escalated": True,
        },
        # 13. Office Badge Reader Offline (Incident)
        {
            "ref": "INC-2026-000013",
            "type": CaseType.INCIDENT,
            "title": "Server Room Physical Access Badge Reader Not Responding",
            "description": "HID reader beeping red constantly. Physical keys required to enter server room.",
            "status": CaseStatus.ASSIGNED,
            "priority": Priority.P2,
            "team": systems_team,
            "owner": user_map[UserRole.OPERATOR],
            "site": "NYC HQ",
            "hours_ago": 5.0,
            "category": "Access & Identity",
            "risk": RiskLevel.HIGH,
            "escalated": True,
        },
        # 14. Docker Desktop License Assignment (Service Request)
        {
            "ref": "REQ-2026-000014",
            "type": CaseType.SERVICE_REQUEST,
            "title": "Docker Desktop Business License Seat for Contractor",
            "description": "Assign Docker license seat to contractor email for local microservice debugging.",
            "status": CaseStatus.RESOLVED,
            "priority": Priority.P4,
            "team": systems_team,
            "owner": user_map[UserRole.OPERATOR],
            "site": "Remote",
            "hours_ago": 50.0,
            "resolved_ago": 10.0,
            "category": "Software",
            "risk": RiskLevel.LOW,
            "escalated": False,
        },
        # 15. Zoom Room Audio Echo (Incident)
        {
            "ref": "INC-2026-000015",
            "type": CaseType.INCIDENT,
            "title": "Conference Room B Polycom Ceiling Mic Severe Echo",
            "description": "Remote participants hear loud echo feedback during hybrid standup meetings.",
            "status": CaseStatus.CLOSED,
            "priority": Priority.P3,
            "team": desktop_team,
            "owner": user_map[UserRole.OPERATOR],
            "site": "London Office",
            "hours_ago": 120.0,
            "resolved_ago": 70.0,
            "closed_ago": 40.0,
            "category": "Hardware",
            "risk": RiskLevel.LOW,
            "escalated": False,
        },
        # 16. GitHub Enterprise Team Access (Service Request)
        {
            "ref": "REQ-2026-000016",
            "type": CaseType.SERVICE_REQUEST,
            "title": "Add Read-Write Access to Payments Core Repository",
            "description": "New developer requires repository write permission after passing security review.",
            "status": CaseStatus.CLOSED,
            "priority": Priority.P3,
            "team": systems_team,
            "owner": user_map[UserRole.OPERATOR],
            "site": "NYC HQ",
            "hours_ago": 150.0,
            "resolved_ago": 90.0,
            "closed_ago": 60.0,
            "category": "Access & Identity",
            "risk": RiskLevel.LOW,
            "escalated": False,
        },
        # 17. High Latency to Singapore Office (Incident)
        {
            "ref": "INC-2026-000017",
            "type": CaseType.INCIDENT,
            "title": "IPSec VPN Tunnel Latency Spike from Singapore to US East",
            "description": "Ping latency jumped from 180ms to 450ms with 5% packet loss on transatlantic route.",
            "status": CaseStatus.IN_ASSESSMENT,
            "priority": Priority.P2,
            "team": network_team,
            "owner": user_map[UserRole.TEAM_LEAD],
            "site": "Singapore Office",
            "hours_ago": 4.0,
            "category": "Network",
            "risk": RiskLevel.MODERATE,
            "escalated": False,
        },
        # 18. Ergonomic Keyboard Request (Service Request)
        {
            "ref": "REQ-2026-000018",
            "type": CaseType.SERVICE_REQUEST,
            "title": "Logitech Ergo K860 Split Wireless Keyboard Order",
            "description": "Workplace health assessment approved ergonomic split keyboard for workstation desk 402.",
            "status": CaseStatus.RESOLVED,
            "priority": Priority.P4,
            "team": desktop_team,
            "owner": user_map[UserRole.OPERATOR],
            "site": "London Office",
            "hours_ago": 60.0,
            "resolved_ago": 12.0,
            "category": "Hardware",
            "risk": RiskLevel.LOW,
            "escalated": False,
        },
    ]

    for spec in cases_spec:
        existing_case = db.query(Case).filter(Case.reference_number == spec["ref"]).first()
        created_time = now - timedelta(hours=spec["hours_ago"])

        if not existing_case:
            case = Case(
                reference_number=spec["ref"],
                type=spec["type"],
                title=spec["title"],
                description=spec["description"],
                status=spec["status"],
                priority=spec["priority"],
                requester_id=user_map[UserRole.REQUESTER].id,
                owner_id=spec["owner"].id if spec["owner"] else None,
                team_id=spec["team"].id if spec["team"] else None,
                site=spec["site"],
                version=1,
                created_at=created_time,
                updated_at=created_time + timedelta(minutes=15),
            )
            if "resolved_ago" in spec:
                case.resolved_at = now - timedelta(hours=spec["resolved_ago"])
            if "closed_ago" in spec:
                case.closed_at = now - timedelta(hours=spec["closed_ago"])

            db.add(case)
            db.flush()

            # SLA
            resp_target, res_target = SLAService.calculate_deadlines(spec["priority"], created_time)
            resp_breached = (now > resp_target) and ("resolved_ago" not in spec and spec["status"] != CaseStatus.CLOSED)
            res_breached = (now > res_target) and ("resolved_ago" not in spec and spec["status"] != CaseStatus.CLOSED)

            sla = SLA(
                case_id=case.id,
                priority=spec["priority"],
                target_response_at=resp_target,
                target_resolve_at=res_target,
                response_breached=resp_breached,
                resolve_breached=res_breached,
                responded_at=created_time + timedelta(minutes=10) if spec["owner"] else None,
                resolved_at=case.resolved_at,
                created_at=created_time,
            )
            db.add(sla)

            # AI Triage Result
            conf_score = 0.88 if spec["priority"] in [Priority.P1, Priority.P2] else 0.72
            triage = AITriageResult(
                case_id=case.id,
                suggested_category=spec["category"],
                suggested_severity="High" if spec["priority"] in [Priority.P1, Priority.P2] else "Medium",
                suggested_priority=spec["priority"].value,
                confidence_level=ConfidenceLevel.HIGH if conf_score >= 0.8 else ConfidenceLevel.MODERATE,
                confidence_score=conf_score,
                supporting_factors=[f"Identified '{spec['category']}' keyword signature in case description"],
                missing_info=[],
                suggested_team=spec["team"].name if spec["team"] else None,
                recommended_next_action=f"Assign to {spec['team'].name if spec['team'] else 'Service Desk'} for triage.",
                created_at=created_time,
            )
            db.add(triage)

            # Case Summary
            summary = CaseSummary(
                case_id=case.id,
                summary_text=(
                    f"**What was reported**: {spec['title']}\n"
                    f"**What happened since**: Status advanced to {spec['status'].value}.\n"
                    f"**What's confirmed**: Issue logged under category {spec['category']}.\n"
                    f"**What remains unresolved**: Final verification."
                ),
                updated_at=created_time,
            )
            db.add(summary)

            # Risk Assessment
            risk = CaseRiskAssessment(
                case_id=case.id,
                risk_level=spec["risk"],
                signals={"inactivity_hours": round(spec["hours_ago"], 1), "priority": spec["priority"].value},
                computed_at=now,
            )
            db.add(risk)

            # Messages
            msg1 = Message(
                case_id=case.id,
                author_id=user_map[UserRole.REQUESTER].id,
                body=spec["description"],
                visibility=MessageVisibility.REQUESTER_VISIBLE,
                created_at=created_time,
            )
            db.add(msg1)

            if spec["owner"]:
                msg2 = Message(
                    case_id=case.id,
                    author_id=spec["owner"].id,
                    body="Investigating issue and checking relevant service metrics.",
                    visibility=MessageVisibility.REQUESTER_VISIBLE,
                    created_at=created_time + timedelta(minutes=12),
                )
                db.add(msg2)

                note = Message(
                    case_id=case.id,
                    author_id=spec["owner"].id,
                    body="Internal Note: Verified firewall logs; trace route shows normal gateway hop.",
                    visibility=MessageVisibility.INTERNAL_ONLY,
                    created_at=created_time + timedelta(minutes=15),
                )
                db.add(note)

            # Escalation
            if spec.get("escalated"):
                esc = EscalationEvent(
                    case_id=case.id,
                    trigger_reason=EscalationReason.HIGH_RISK if spec["risk"] == RiskLevel.CRITICAL else EscalationReason.OPERATOR_REQUESTED,
                    escalated_to="TeamLead",
                    escalated_by=spec["owner"].id if spec["owner"] else "system",
                    status=EscalationStatus.OPEN,
                    created_at=now - timedelta(hours=1),
                )
                db.add(esc)

            # Communication Draft
            draft = CommunicationDraft(
                case_id=case.id,
                draft_type=DraftType.PROGRESS_UPDATE,
                body=f"Hello,\n\nWe are actively working on '{spec['title']}' and will provide an update shortly.\n\nBest regards,\nAssistIQ Team",
                status=DraftStatus.DRAFT,
                created_at=created_time + timedelta(minutes=20),
            )
            db.add(draft)

            # Audit Logs
            audit1 = AuditLog(
                actor_id=user_map[UserRole.REQUESTER].id,
                action="case_created",
                target_type="case",
                target_id=case.id,
                after_value={"reference_number": spec["ref"], "priority": spec["priority"].value},
                created_at=created_time,
            )
            db.add(audit1)

            if spec.get("reopened"):
                audit_reopen = AuditLog(
                    actor_id=user_map[UserRole.REQUESTER].id,
                    action="reopened",
                    target_type="case",
                    target_id=case.id,
                    before_value={"status": "Closed"},
                    after_value={"status": "Assigned", "reason": "Issue re-occurred"},
                    created_at=now - timedelta(hours=2),
                )
                db.add(audit_reopen)

    db.commit()
    print("✅ [AssistIQ Seeder] Database seeded successfully!")
    print("\nRepresentative Demo Accounts Created:")
    print("  1. Requester:     requester@assistiq.local  / Password123!@#")
    print("  2. Operator:      operator@assistiq.local   / Password123!@#")
    print("  3. Team Lead:     lead@assistiq.local       / Password123!@#")
    print("  4. Manager:       manager@assistiq.local    / Password123!@#")
    print("  5. Administrator: admin@assistiq.local      / Password123!@#")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_demo_data(db)
    finally:
        db.close()
