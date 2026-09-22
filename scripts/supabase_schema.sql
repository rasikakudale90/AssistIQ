-- AssistIQ Complete Supabase PostgreSQL Schema DDL
CREATE EXTENSION IF NOT EXISTS pg_trgm;

DROP TABLE IF EXISTS teams CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS audit_logs CASCADE;
DROP TABLE IF EXISTS cases CASCADE;
DROP TABLE IF EXISTS ai_triage_results CASCADE;
DROP TABLE IF EXISTS approvals CASCADE;
DROP TABLE IF EXISTS attachments CASCADE;
DROP TABLE IF EXISTS case_relationships CASCADE;
DROP TABLE IF EXISTS case_risk_assessments CASCADE;
DROP TABLE IF EXISTS case_summaries CASCADE;
DROP TABLE IF EXISTS escalation_events CASCADE;
DROP TABLE IF EXISTS knowledge_articles CASCADE;
DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS slas CASCADE;
DROP TABLE IF EXISTS communication_drafts CASCADE;

CREATE TABLE teams (
	id VARCHAR(36) NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	description VARCHAR(255), 
	lead_id VARCHAR(36), 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_teams_name ON teams (name);

CREATE TABLE users (
	id VARCHAR(36) NOT NULL, 
	email VARCHAR(255) NOT NULL, 
	password_hash VARCHAR(255), 
	auth_provider authprovider NOT NULL, 
	oauth_subject_id VARCHAR(255), 
	role userrole NOT NULL, 
	team_id VARCHAR(36), 
	site VARCHAR(100), 
	availability_status availabilitystatus NOT NULL, 
	email_verified BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	deleted_at TIMESTAMP WITH TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(team_id) REFERENCES teams (id) ON DELETE SET NULL
);

CREATE INDEX ix_users_team_role ON users (team_id, role);
CREATE UNIQUE INDEX ix_users_email ON users (email);
CREATE UNIQUE INDEX ix_users_oauth_subject_id ON users (oauth_subject_id);
CREATE INDEX ix_users_role_availability ON users (role, availability_status);
CREATE INDEX ix_users_team_id ON users (team_id);
CREATE INDEX ix_users_role ON users (role);

CREATE TABLE audit_logs (
	id VARCHAR(36) NOT NULL, 
	actor_id VARCHAR(36), 
	action VARCHAR(100) NOT NULL, 
	target_type VARCHAR(50) NOT NULL, 
	target_id VARCHAR(36) NOT NULL, 
	before_value JSON, 
	after_value JSON, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(actor_id) REFERENCES users (id) ON DELETE SET NULL
);

CREATE INDEX ix_audit_logs_target_type ON audit_logs (target_type);
CREATE INDEX ix_audit_logs_action ON audit_logs (action);
CREATE INDEX ix_audit_target ON audit_logs (target_type, target_id, created_at);
CREATE INDEX ix_audit_logs_actor_id ON audit_logs (actor_id);
CREATE INDEX ix_audit_logs_target_id ON audit_logs (target_id);
CREATE INDEX ix_audit_logs_created_at ON audit_logs (created_at);

CREATE TABLE cases (
	id VARCHAR(36) NOT NULL, 
	reference_number VARCHAR(50) NOT NULL, 
	type casetype NOT NULL, 
	title VARCHAR(200) NOT NULL, 
	description TEXT NOT NULL, 
	status casestatus NOT NULL, 
	priority priority NOT NULL, 
	requester_id VARCHAR(36) NOT NULL, 
	owner_id VARCHAR(36), 
	team_id VARCHAR(36), 
	site VARCHAR(100), 
	service_id VARCHAR(100), 
	version INTEGER NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	resolved_at TIMESTAMP WITH TIME ZONE, 
	closed_at TIMESTAMP WITH TIME ZONE, 
	deleted_at TIMESTAMP WITH TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(requester_id) REFERENCES users (id) ON DELETE RESTRICT, 
	FOREIGN KEY(owner_id) REFERENCES users (id) ON DELETE SET NULL, 
	FOREIGN KEY(team_id) REFERENCES teams (id) ON DELETE SET NULL
);

CREATE INDEX ix_cases_type ON cases (type);
CREATE INDEX ix_cases_status_priority ON cases (status, priority);
CREATE INDEX ix_cases_owner_status ON cases (owner_id, status);
CREATE INDEX ix_cases_team_status ON cases (team_id, status);
CREATE INDEX ix_cases_priority ON cases (priority);
CREATE INDEX ix_cases_team_id ON cases (team_id);
CREATE INDEX ix_cases_title ON cases (title);
CREATE INDEX ix_cases_requester_id ON cases (requester_id);
CREATE INDEX ix_cases_status ON cases (status);
CREATE UNIQUE INDEX ix_cases_reference_number ON cases (reference_number);
CREATE INDEX ix_cases_created_at ON cases (created_at);
CREATE INDEX ix_cases_owner_id ON cases (owner_id);
CREATE INDEX ix_cases_service_id ON cases (service_id);
CREATE INDEX ix_cases_site ON cases (site);

CREATE TABLE ai_triage_results (
	id VARCHAR(36) NOT NULL, 
	case_id VARCHAR(36) NOT NULL, 
	suggested_category VARCHAR(100), 
	suggested_severity VARCHAR(50), 
	suggested_priority VARCHAR(10), 
	confidence_level confidencelevel NOT NULL, 
	confidence_score FLOAT, 
	supporting_factors JSON NOT NULL, 
	missing_info JSON NOT NULL, 
	suggested_team VARCHAR(100), 
	recommended_next_action TEXT, 
	related_case_ids JSON NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(case_id) REFERENCES cases (id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX ix_ai_triage_results_case_id ON ai_triage_results (case_id);

CREATE TABLE approvals (
	id VARCHAR(36) NOT NULL, 
	case_id VARCHAR(36) NOT NULL, 
	approver_id VARCHAR(36) NOT NULL, 
	decision approvaldecision NOT NULL, 
	reason TEXT, 
	decided_at TIMESTAMP WITH TIME ZONE, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(case_id) REFERENCES cases (id) ON DELETE CASCADE, 
	FOREIGN KEY(approver_id) REFERENCES users (id) ON DELETE RESTRICT
);

CREATE INDEX ix_approvals_decision ON approvals (decision);
CREATE INDEX ix_approvals_approver_id ON approvals (approver_id);
CREATE INDEX ix_approvals_case_id ON approvals (case_id);

CREATE TABLE attachments (
	id VARCHAR(36) NOT NULL, 
	case_id VARCHAR(36) NOT NULL, 
	storage_path VARCHAR(500) NOT NULL, 
	file_name VARCHAR(255) NOT NULL, 
	file_type VARCHAR(100) NOT NULL, 
	file_size INTEGER NOT NULL, 
	uploaded_by VARCHAR(36), 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(case_id) REFERENCES cases (id) ON DELETE CASCADE, 
	FOREIGN KEY(uploaded_by) REFERENCES users (id) ON DELETE SET NULL
);

CREATE INDEX ix_attachments_uploaded_by ON attachments (uploaded_by);
CREATE INDEX ix_attachments_case_id ON attachments (case_id);

CREATE TABLE case_relationships (
	id VARCHAR(36) NOT NULL, 
	case_id VARCHAR(36) NOT NULL, 
	related_case_id VARCHAR(36) NOT NULL, 
	relationship_type caserelationshiptype NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(case_id) REFERENCES cases (id) ON DELETE CASCADE, 
	FOREIGN KEY(related_case_id) REFERENCES cases (id) ON DELETE CASCADE
);

CREATE INDEX ix_case_relationships_case_id ON case_relationships (case_id);
CREATE UNIQUE INDEX ix_case_rel_unique ON case_relationships (case_id, related_case_id, relationship_type);
CREATE INDEX ix_case_relationships_related_case_id ON case_relationships (related_case_id);

CREATE TABLE case_risk_assessments (
	id VARCHAR(36) NOT NULL, 
	case_id VARCHAR(36) NOT NULL, 
	risk_level risklevel NOT NULL, 
	signals JSON NOT NULL, 
	computed_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(case_id) REFERENCES cases (id) ON DELETE CASCADE
);

CREATE INDEX ix_case_risk_assessments_risk_level ON case_risk_assessments (risk_level);
CREATE INDEX ix_case_risk_assessments_case_id ON case_risk_assessments (case_id);
CREATE INDEX ix_risk_case_computed ON case_risk_assessments (case_id, computed_at);
CREATE INDEX ix_case_risk_assessments_computed_at ON case_risk_assessments (computed_at);

CREATE TABLE case_summaries (
	id VARCHAR(36) NOT NULL, 
	case_id VARCHAR(36) NOT NULL, 
	summary_text TEXT NOT NULL, 
	last_source_message_id VARCHAR(36), 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(case_id) REFERENCES cases (id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX ix_case_summaries_case_id ON case_summaries (case_id);

CREATE TABLE escalation_events (
	id VARCHAR(36) NOT NULL, 
	case_id VARCHAR(36) NOT NULL, 
	trigger_reason escalationreason NOT NULL, 
	escalated_to VARCHAR(36), 
	escalated_by VARCHAR(36) NOT NULL, 
	status escalationstatus NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(case_id) REFERENCES cases (id) ON DELETE CASCADE
);

CREATE INDEX ix_escalation_events_created_at ON escalation_events (created_at);
CREATE INDEX ix_escalation_events_status ON escalation_events (status);
CREATE INDEX ix_escalation_events_trigger_reason ON escalation_events (trigger_reason);
CREATE INDEX ix_escalation_events_case_id ON escalation_events (case_id);

CREATE TABLE knowledge_articles (
	id VARCHAR(36) NOT NULL, 
	title VARCHAR(255) NOT NULL, 
	body TEXT NOT NULL, 
	category VARCHAR(100) NOT NULL, 
	owner_id VARCHAR(36) NOT NULL, 
	state knowledgestate NOT NULL, 
	review_date TIMESTAMP WITH TIME ZONE, 
	source_case_id VARCHAR(36), 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(owner_id) REFERENCES users (id) ON DELETE RESTRICT, 
	FOREIGN KEY(source_case_id) REFERENCES cases (id) ON DELETE SET NULL
);

CREATE INDEX ix_knowledge_articles_title ON knowledge_articles (title);
CREATE INDEX ix_knowledge_articles_state ON knowledge_articles (state);
CREATE INDEX ix_knowledge_articles_category ON knowledge_articles (category);
CREATE INDEX ix_knowledge_articles_owner_id ON knowledge_articles (owner_id);

CREATE TABLE messages (
	id VARCHAR(36) NOT NULL, 
	case_id VARCHAR(36) NOT NULL, 
	author_id VARCHAR(36), 
	body TEXT NOT NULL, 
	visibility messagevisibility NOT NULL, 
	ai_generated BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(case_id) REFERENCES cases (id) ON DELETE CASCADE, 
	FOREIGN KEY(author_id) REFERENCES users (id) ON DELETE SET NULL
);

CREATE INDEX ix_messages_case_id ON messages (case_id);
CREATE INDEX ix_messages_case_visibility ON messages (case_id, visibility);
CREATE INDEX ix_messages_visibility ON messages (visibility);
CREATE INDEX ix_messages_created_at ON messages (created_at);
CREATE INDEX ix_messages_author_id ON messages (author_id);

CREATE TABLE slas (
	id VARCHAR(36) NOT NULL, 
	case_id VARCHAR(36) NOT NULL, 
	priority priority NOT NULL, 
	target_response_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	target_resolve_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	response_breached BOOLEAN NOT NULL, 
	resolve_breached BOOLEAN NOT NULL, 
	responded_at TIMESTAMP WITH TIME ZONE, 
	resolved_at TIMESTAMP WITH TIME ZONE, 
	paused_reason VARCHAR(255), 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(case_id) REFERENCES cases (id) ON DELETE CASCADE
);

CREATE INDEX ix_slas_resolve_breached ON slas (resolve_breached);
CREATE INDEX ix_sla_breach_monitoring ON slas (resolve_breached, target_resolve_at);
CREATE INDEX ix_slas_target_response_at ON slas (target_response_at);
CREATE INDEX ix_slas_response_breached ON slas (response_breached);
CREATE UNIQUE INDEX ix_slas_case_id ON slas (case_id);
CREATE INDEX ix_slas_target_resolve_at ON slas (target_resolve_at);

CREATE TABLE communication_drafts (
	id VARCHAR(36) NOT NULL, 
	case_id VARCHAR(36) NOT NULL, 
	draft_type drafttype NOT NULL, 
	body TEXT NOT NULL, 
	status draftstatus NOT NULL, 
	reviewed_by VARCHAR(36), 
	sent_message_id VARCHAR(36), 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(case_id) REFERENCES cases (id) ON DELETE CASCADE, 
	FOREIGN KEY(reviewed_by) REFERENCES users (id) ON DELETE SET NULL, 
	FOREIGN KEY(sent_message_id) REFERENCES messages (id) ON DELETE SET NULL
);

CREATE INDEX ix_communication_drafts_draft_type ON communication_drafts (draft_type);
CREATE INDEX ix_communication_drafts_case_id ON communication_drafts (case_id);
CREATE INDEX ix_communication_drafts_status ON communication_drafts (status);


-- Seed Initial Demo Teams & Users
INSERT INTO teams (id, name, description, created_at) VALUES
('team-001', 'Desktop & Hardware Support', 'Client workstation troubleshooting, peripherals, OS installs', NOW()),
('team-002', 'Network Engineering', 'VPN, Wi-Fi, switches, routers, and corporate firewall management', NOW()),
('team-003', 'Systems & Cloud Operations', 'Identity, AWS/GCP infrastructure, SSO, and server access', NOW());

INSERT INTO users (id, email, password_hash, auth_provider, role, team_id, site, availability_status, email_verified, created_at, updated_at) VALUES
('usr-admin-001', 'admin@assistiq.local', '=19=19456,t=2,p=1', 'password', 'Administrator', 'team-003', 'HQ-North', 'available', TRUE, NOW(), NOW()),
('usr-mgr-001', 'manager@assistiq.local', '=19=19456,t=2,p=1', 'password', 'Manager', 'team-001', 'HQ-North', 'available', TRUE, NOW(), NOW()),
('usr-lead-001', 'lead@assistiq.local', '=19=19456,t=2,p=1', 'password', 'TeamLead', 'team-001', 'HQ-North', 'available', TRUE, NOW(), NOW()),
('usr-op-001', 'operator@assistiq.local', '=19=19456,t=2,p=1', 'password', 'Operator', 'team-001', 'HQ-North', 'available', TRUE, NOW(), NOW()),
('usr-req-001', 'requester@assistiq.local', '=19=19456,t=2,p=1', 'password', 'Requester', NULL, 'HQ-North', 'available', TRUE, NOW(), NOW());

UPDATE teams SET lead_id = 'usr-lead-001' WHERE id = 'team-001';
UPDATE teams SET lead_id = 'usr-mgr-001' WHERE id = 'team-002';
UPDATE teams SET lead_id = 'usr-admin-001' WHERE id = 'team-003';
