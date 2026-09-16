"""Initial schema with all 15 models, indexes, and pg_trgm extension

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-09-16 19:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Enable pg_trgm extension on PostgreSQL for trigram similarity search (SRS §5.5, §5.14)
    conn = op.get_bind()
    if conn.dialect.name == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")

    # 2. Create teams table
    op.create_table(
        "teams",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("lead_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_teams_name", "teams", ["name"])

    # 3. Create users table
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=True),
        sa.Column("auth_provider", sa.String(length=50), nullable=False),
        sa.Column("oauth_subject_id", sa.String(length=255), nullable=True),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("team_id", sa.String(length=36), nullable=True),
        sa.Column("site", sa.String(length=100), nullable=True),
        sa.Column("availability_status", sa.String(length=50), nullable=False),
        sa.Column("email_verified", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("oauth_subject_id"),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_oauth_subject_id", "users", ["oauth_subject_id"])
    op.create_index("ix_users_role", "users", ["role"])
    op.create_index("ix_users_team_id", "users", ["team_id"])
    op.create_index("ix_users_role_availability", "users", ["role", "availability_status"])
    op.create_index("ix_users_team_role", "users", ["team_id", "role"])

    # Add foreign key from teams.lead_id to users.id
    op.create_foreign_key("fk_teams_lead_id_users", "teams", "users", ["lead_id"], ["id"], ondelete="SET NULL")

    # 4. Create cases table
    op.create_table(
        "cases",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("reference_number", sa.String(length=50), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("priority", sa.String(length=10), nullable=False),
        sa.Column("requester_id", sa.String(length=36), nullable=False),
        sa.Column("owner_id", sa.String(length=36), nullable=True),
        sa.Column("team_id", sa.String(length=36), nullable=True),
        sa.Column("site", sa.String(length=100), nullable=True),
        sa.Column("service_id", sa.String(length=100), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["requester_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("reference_number"),
    )
    op.create_index("ix_cases_reference_number", "cases", ["reference_number"])
    op.create_index("ix_cases_type", "cases", ["type"])
    op.create_index("ix_cases_title", "cases", ["title"])
    op.create_index("ix_cases_status", "cases", ["status"])
    op.create_index("ix_cases_priority", "cases", ["priority"])
    op.create_index("ix_cases_requester_id", "cases", ["requester_id"])
    op.create_index("ix_cases_owner_id", "cases", ["owner_id"])
    op.create_index("ix_cases_team_id", "cases", ["team_id"])
    op.create_index("ix_cases_site", "cases", ["site"])
    op.create_index("ix_cases_service_id", "cases", ["service_id"])
    op.create_index("ix_cases_created_at", "cases", ["created_at"])
    op.create_index("ix_cases_status_priority", "cases", ["status", "priority"])
    op.create_index("ix_cases_owner_status", "cases", ["owner_id", "status"])
    op.create_index("ix_cases_team_status", "cases", ["team_id", "status"])

    # 5. Create case_relationships table
    op.create_table(
        "case_relationships",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("case_id", sa.String(length=36), nullable=False),
        sa.Column("related_case_id", sa.String(length=36), nullable=False),
        sa.Column("relationship_type", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["related_case_id"], ["cases.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_case_rel_unique", "case_relationships", ["case_id", "related_case_id", "relationship_type"], unique=True)

    # 6. Create messages table
    op.create_table(
        "messages",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("case_id", sa.String(length=36), nullable=False),
        sa.Column("author_id", sa.String(length=36), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("visibility", sa.String(length=50), nullable=False),
        sa.Column("ai_generated", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_messages_case_id", "messages", ["case_id"])
    op.create_index("ix_messages_author_id", "messages", ["author_id"])
    op.create_index("ix_messages_visibility", "messages", ["visibility"])
    op.create_index("ix_messages_created_at", "messages", ["created_at"])
    op.create_index("ix_messages_case_visibility", "messages", ["case_id", "visibility"])

    # 7. Create attachments table
    op.create_table(
        "attachments",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("case_id", sa.String(length=36), nullable=False),
        sa.Column("storage_path", sa.String(length=500), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_type", sa.String(length=100), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("uploaded_by", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_attachments_case_id", "attachments", ["case_id"])
    op.create_index("ix_attachments_uploaded_by", "attachments", ["uploaded_by"])

    # 8. Create slas table
    op.create_table(
        "slas",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("case_id", sa.String(length=36), nullable=False),
        sa.Column("priority", sa.String(length=10), nullable=False),
        sa.Column("target_response_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("target_resolve_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("response_breached", sa.Boolean(), nullable=False),
        sa.Column("resolve_breached", sa.Boolean(), nullable=False),
        sa.Column("responded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("paused_reason", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("case_id"),
    )
    op.create_index("ix_slas_case_id", "slas", ["case_id"])
    op.create_index("ix_slas_target_response_at", "slas", ["target_response_at"])
    op.create_index("ix_slas_target_resolve_at", "slas", ["target_resolve_at"])
    op.create_index("ix_slas_response_breached", "slas", ["response_breached"])
    op.create_index("ix_slas_resolve_breached", "slas", ["resolve_breached"])
    op.create_index("ix_sla_breach_monitoring", "slas", ["resolve_breached", "target_resolve_at"])

    # 9. Create ai_triage_results table
    op.create_table(
        "ai_triage_results",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("case_id", sa.String(length=36), nullable=False),
        sa.Column("suggested_category", sa.String(length=100), nullable=True),
        sa.Column("suggested_severity", sa.String(length=50), nullable=True),
        sa.Column("suggested_priority", sa.String(length=10), nullable=True),
        sa.Column("confidence_level", sa.String(length=20), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("supporting_factors", sa.JSON(), nullable=False),
        sa.Column("missing_info", sa.JSON(), nullable=False),
        sa.Column("suggested_team", sa.String(length=100), nullable=True),
        sa.Column("recommended_next_action", sa.Text(), nullable=True),
        sa.Column("related_case_ids", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("case_id"),
    )
    op.create_index("ix_ai_triage_results_case_id", "ai_triage_results", ["case_id"])

    # 10. Create case_summaries table
    op.create_table(
        "case_summaries",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("case_id", sa.String(length=36), nullable=False),
        sa.Column("summary_text", sa.Text(), nullable=False),
        sa.Column("last_source_message_id", sa.String(length=36), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("case_id"),
    )
    op.create_index("ix_case_summaries_case_id", "case_summaries", ["case_id"])

    # 11. Create case_risk_assessments table
    op.create_table(
        "case_risk_assessments",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("case_id", sa.String(length=36), nullable=False),
        sa.Column("risk_level", sa.String(length=20), nullable=False),
        sa.Column("signals", sa.JSON(), nullable=False),
        sa.Column("computed_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_case_risk_assessments_case_id", "case_risk_assessments", ["case_id"])
    op.create_index("ix_case_risk_assessments_risk_level", "case_risk_assessments", ["risk_level"])
    op.create_index("ix_case_risk_assessments_computed_at", "case_risk_assessments", ["computed_at"])
    op.create_index("ix_risk_case_computed", "case_risk_assessments", ["case_id", "computed_at"])

    # 12. Create escalation_events table
    op.create_table(
        "escalation_events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("case_id", sa.String(length=36), nullable=False),
        sa.Column("trigger_reason", sa.String(length=50), nullable=False),
        sa.Column("escalated_to", sa.String(length=36), nullable=True),
        sa.Column("escalated_by", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_escalation_events_case_id", "escalation_events", ["case_id"])
    op.create_index("ix_escalation_events_trigger_reason", "escalation_events", ["trigger_reason"])
    op.create_index("ix_escalation_events_status", "escalation_events", ["status"])
    op.create_index("ix_escalation_events_created_at", "escalation_events", ["created_at"])

    # 13. Create communication_drafts table
    op.create_table(
        "communication_drafts",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("case_id", sa.String(length=36), nullable=False),
        sa.Column("draft_type", sa.String(length=50), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("reviewed_by", sa.String(length=36), nullable=True),
        sa.Column("sent_message_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reviewed_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["sent_message_id"], ["messages.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_communication_drafts_case_id", "communication_drafts", ["case_id"])
    op.create_index("ix_communication_drafts_draft_type", "communication_drafts", ["draft_type"])
    op.create_index("ix_communication_drafts_status", "communication_drafts", ["status"])

    # 14. Create audit_logs table
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("actor_id", sa.String(length=36), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("target_type", sa.String(length=50), nullable=False),
        sa.Column("target_id", sa.String(length=36), nullable=False),
        sa.Column("before_value", sa.JSON(), nullable=True),
        sa.Column("after_value", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["actor_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_logs_actor_id", "audit_logs", ["actor_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_target_type", "audit_logs", ["target_type"])
    op.create_index("ix_audit_logs_target_id", "audit_logs", ["target_id"])
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])
    op.create_index("ix_audit_target", "audit_logs", ["target_type", "target_id", "created_at"])

    # 15. Create approvals table
    op.create_table(
        "approvals",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("case_id", sa.String(length=36), nullable=False),
        sa.Column("approver_id", sa.String(length=36), nullable=False),
        sa.Column("decision", sa.String(length=20), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["approver_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_approvals_case_id", "approvals", ["case_id"])
    op.create_index("ix_approvals_approver_id", "approvals", ["approver_id"])
    op.create_index("ix_approvals_decision", "approvals", ["decision"])

    # 16. Create knowledge_articles table
    op.create_table(
        "knowledge_articles",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("owner_id", sa.String(length=36), nullable=False),
        sa.Column("state", sa.String(length=20), nullable=False),
        sa.Column("review_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source_case_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["source_case_id"], ["cases.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_knowledge_articles_title", "knowledge_articles", ["title"])
    op.create_index("ix_knowledge_articles_category", "knowledge_articles", ["category"])
    op.create_index("ix_knowledge_articles_owner_id", "knowledge_articles", ["owner_id"])
    op.create_index("ix_knowledge_articles_state", "knowledge_articles", ["state"])


def downgrade() -> None:
    op.drop_table("knowledge_articles")
    op.drop_table("approvals")
    op.drop_table("audit_logs")
    op.drop_table("communication_drafts")
    op.drop_table("escalation_events")
    op.drop_table("case_risk_assessments")
    op.drop_table("case_summaries")
    op.drop_table("ai_triage_results")
    op.drop_table("slas")
    op.drop_table("attachments")
    op.drop_table("messages")
    op.drop_table("case_relationships")
    op.drop_table("cases")
    op.drop_table("users")
    op.drop_table("teams")
