-- ==========================================================
-- AssistIQ Production Database Schema & Seed for Supabase
-- Run this in Supabase Dashboard -> SQL Editor -> New Query -> Run
-- ==========================================================

-- 1. Drop existing tables if re-running
DROP TABLE IF EXISTS audit_logs CASCADE;
DROP TABLE IF EXISTS communication_drafts CASCADE;
DROP TABLE IF EXISTS escalation_events CASCADE;
DROP TABLE IF EXISTS case_risk_assessments CASCADE;
DROP TABLE IF EXISTS case_summaries CASCADE;
DROP TABLE IF EXISTS ai_triage_results CASCADE;
DROP TABLE IF EXISTS attachments CASCADE;
DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS slas CASCADE;
DROP TABLE IF EXISTS knowledge_articles CASCADE;
DROP TABLE IF EXISTS cases CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS teams CASCADE;

-- 2. Create Tables
CREATE TABLE teams (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(255),
    lead_id VARCHAR(36),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    auth_provider VARCHAR(50) NOT NULL DEFAULT 'local',
    oauth_subject_id VARCHAR(255),
    role VARCHAR(50) NOT NULL,
    team_id VARCHAR(36) REFERENCES teams(id) ON DELETE SET NULL,
    site VARCHAR(100) DEFAULT 'HQ-North',
    availability_status VARCHAR(50) NOT NULL DEFAULT 'Available',
    email_verified BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

ALTER TABLE teams ADD CONSTRAINT fk_team_lead FOREIGN KEY (lead_id) REFERENCES users(id) ON DELETE SET NULL;

CREATE TABLE cases (
    id VARCHAR(36) PRIMARY KEY,
    reference_number VARCHAR(50) UNIQUE NOT NULL,
    type VARCHAR(50) NOT NULL DEFAULT 'Incident',
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'New',
    priority VARCHAR(50) NOT NULL DEFAULT 'Medium',
    requester_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    owner_id VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
    team_id VARCHAR(36) REFERENCES teams(id) ON DELETE SET NULL,
    site VARCHAR(100) DEFAULT 'HQ-North',
    service_id VARCHAR(100),
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMPTZ,
    closed_at TIMESTAMPTZ,
    deleted_at TIMESTAMPTZ
);

CREATE TABLE slas (
    id VARCHAR(36) PRIMARY KEY,
    case_id VARCHAR(36) UNIQUE NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    response_deadline TIMESTAMPTZ NOT NULL,
    resolution_deadline TIMESTAMPTZ NOT NULL,
    responded_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ,
    is_response_breached BOOLEAN NOT NULL DEFAULT FALSE,
    is_resolution_breached BOOLEAN NOT NULL DEFAULT FALSE,
    paused_at TIMESTAMPTZ,
    total_paused_seconds INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE messages (
    id VARCHAR(36) PRIMARY KEY,
    case_id VARCHAR(36) NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    sender_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    body TEXT NOT NULL,
    visibility VARCHAR(50) NOT NULL DEFAULT 'Public',
    idempotency_key VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE attachments (
    id VARCHAR(36) PRIMARY KEY,
    message_id VARCHAR(36) REFERENCES messages(id) ON DELETE CASCADE,
    case_id VARCHAR(36) REFERENCES cases(id) ON DELETE CASCADE,
    uploader_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    filename VARCHAR(255) NOT NULL,
    file_size_bytes INTEGER NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    storage_key VARCHAR(500) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE ai_triage_results (
    id VARCHAR(36) PRIMARY KEY,
    case_id VARCHAR(36) UNIQUE NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    suggested_type VARCHAR(50),
    suggested_priority VARCHAR(50),
    suggested_team_id VARCHAR(36) REFERENCES teams(id) ON DELETE SET NULL,
    confidence_score DOUBLE PRECISION NOT NULL DEFAULT 0.85,
    confidence_level VARCHAR(50) NOT NULL DEFAULT 'High',
    reasoning TEXT,
    auto_routed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE case_summaries (
    id VARCHAR(36) PRIMARY KEY,
    case_id VARCHAR(36) NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    summary_text TEXT NOT NULL,
    sentiment_trend VARCHAR(50) DEFAULT 'Neutral',
    model_version VARCHAR(50) NOT NULL DEFAULT 'gemini-2.5-flash',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE case_risk_assessments (
    id VARCHAR(36) PRIMARY KEY,
    case_id VARCHAR(36) UNIQUE NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    risk_level VARCHAR(50) NOT NULL DEFAULT 'Low',
    risk_score DOUBLE PRECISION NOT NULL DEFAULT 0.1,
    factors JSON NOT NULL DEFAULT '[]'::json,
    assessed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE escalation_events (
    id VARCHAR(36) PRIMARY KEY,
    case_id VARCHAR(36) NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    escalated_by_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    previous_level VARCHAR(50) NOT NULL DEFAULT 'L1',
    new_level VARCHAR(50) NOT NULL DEFAULT 'L2',
    reason VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE communication_drafts (
    id VARCHAR(36) PRIMARY KEY,
    case_id VARCHAR(36) NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    draft_type VARCHAR(50) NOT NULL DEFAULT 'RequesterUpdate',
    draft_text TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'PendingReview',
    created_by_ai BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE knowledge_articles (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(100) NOT NULL,
    tags JSON NOT NULL DEFAULT '[]'::json,
    state VARCHAR(50) NOT NULL DEFAULT 'Published',
    author_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE audit_logs (
    id VARCHAR(36) PRIMARY KEY,
    actor_id VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    target_type VARCHAR(50) NOT NULL,
    target_id VARCHAR(36) NOT NULL,
    before_value JSON,
    after_value JSON,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3. Seed Demo Data (Teams & Users with password Password123!@#)
-- Password hash generated using argon2id per AssistIQ specification
INSERT INTO teams (id, name, description, created_at) VALUES
('team-001', 'Desktop & Hardware Support', 'Client workstation troubleshooting, peripherals, OS installs', NOW()),
('team-002', 'Network Engineering', 'VPN, Wi-Fi, switches, routers, and corporate firewall management', NOW()),
('team-003', 'Systems & Cloud Operations', 'Identity, AWS/GCP infrastructure, SSO, and server access', NOW());

INSERT INTO users (id, email, password_hash, auth_provider, role, team_id, site, availability_status, email_verified, created_at, updated_at) VALUES
('usr-admin-001', 'admin@assistiq.local', '$argon2id$v=19$m=19456,t=2,p=1$KcUYozTGGANgzFlLaU2J0Q$4ChXiSRmd6Tk4blO28WQaEb7fGtTfSEVYYHrkNvHRIo', 'password', 'Administrator', 'team-003', 'HQ-North', 'Available', TRUE, NOW(), NOW()),
('usr-mgr-001', 'manager@assistiq.local', '$argon2id$v=19$m=19456,t=2,p=1$KcUYozTGGANgzFlLaU2J0Q$4ChXiSRmd6Tk4blO28WQaEb7fGtTfSEVYYHrkNvHRIo', 'password', 'Manager', 'team-001', 'HQ-North', 'Available', TRUE, NOW(), NOW()),
('usr-lead-001', 'lead@assistiq.local', '$argon2id$v=19$m=19456,t=2,p=1$KcUYozTGGANgzFlLaU2J0Q$4ChXiSRmd6Tk4blO28WQaEb7fGtTfSEVYYHrkNvHRIo', 'password', 'TeamLead', 'team-001', 'HQ-North', 'Available', TRUE, NOW(), NOW()),
('usr-op-001', 'operator@assistiq.local', '$argon2id$v=19$m=19456,t=2,p=1$KcUYozTGGANgzFlLaU2J0Q$4ChXiSRmd6Tk4blO28WQaEb7fGtTfSEVYYHrkNvHRIo', 'password', 'Operator', 'team-001', 'HQ-North', 'Available', TRUE, NOW(), NOW()),
('usr-req-001', 'requester@assistiq.local', '$argon2id$v=19$m=19456,t=2,p=1$KcUYozTGGANgzFlLaU2J0Q$4ChXiSRmd6Tk4blO28WQaEb7fGtTfSEVYYHrkNvHRIo', 'password', 'Requester', NULL, 'HQ-North', 'Available', TRUE, NOW(), NOW());

UPDATE teams SET lead_id = 'usr-lead-001' WHERE id = 'team-001';
UPDATE teams SET lead_id = 'usr-mgr-001' WHERE id = 'team-002';
UPDATE teams SET lead_id = 'usr-admin-001' WHERE id = 'team-003';

-- 4. Seed Representative Tickets & SLAs
INSERT INTO cases (id, reference_number, type, title, description, status, priority, requester_id, owner_id, team_id, site, service_id, version, created_at, updated_at) VALUES
('case-001', 'INC-2026-0001', 'Incident', 'Primary VPN Gateway Connectivity Drop', 'Unable to connect to Tokyo VPN gateway following the weekend firewall update. Blocking finance department.', 'Assigned', 'Critical', 'usr-req-001', 'usr-op-001', 'team-002', 'HQ-North', 'VPN-Service', 1, NOW() - INTERVAL '3 hours', NOW()),
('case-002', 'REQ-2026-0002', 'ServiceRequest', 'Developer Laptop Provisioning Request', 'New Senior Frontend Engineer joining next Monday. Standard macOS M3 Max setup with Docker & IDEs needed.', 'New', 'Medium', 'usr-req-001', NULL, 'team-001', 'HQ-North', 'Hardware-Provisioning', 1, NOW() - INTERVAL '5 hours', NOW()),
('case-003', 'INC-2026-0003', 'Incident', 'SSO Login Failure for Production Database Console', 'Receiving 403 Forbidden when authenticating into Supabase DB Console with corporate Google OAuth.', 'InAssessment', 'High', 'usr-req-001', 'usr-lead-001', 'team-003', 'HQ-North', 'Identity-SSO', 1, NOW() - INTERVAL '1 hour', NOW());

INSERT INTO slas (id, case_id, response_deadline, resolution_deadline, responded_at, is_response_breached, is_resolution_breached, created_at, updated_at) VALUES
('sla-001', 'case-001', NOW() - INTERVAL '2 hours', NOW() + INTERVAL '1 hour', NOW() - INTERVAL '2 hours 45 minutes', FALSE, FALSE, NOW() - INTERVAL '3 hours', NOW()),
('sla-002', 'case-002', NOW() + INTERVAL '3 hours', NOW() + INTERVAL '24 hours', NULL, FALSE, FALSE, NOW() - INTERVAL '5 hours', NOW()),
('sla-003', 'case-003', NOW() + INTERVAL '30 minutes', NOW() + INTERVAL '3 hours', NOW() - INTERVAL '45 minutes', FALSE, FALSE, NOW() - INTERVAL '1 hour', NOW());

-- 5. Seed Knowledge Base Articles
INSERT INTO knowledge_articles (id, title, content, category, tags, state, author_id, created_at, updated_at) VALUES
('kb-001', 'Global VPN Troubleshooting Guide', 'Step 1: Disconnect and flush DNS using ipconfig /flushdns.\nStep 2: Verify Tokyo / Singapore gateway routing.\nStep 3: If 2FA fails, re-sync your Authenticator time.', 'Network', '["vpn", "remote-work", "troubleshooting"]'::json, 'Published', 'usr-lead-001', NOW(), NOW()),
('kb-002', 'Workstation Setup & SSH Key Generation', 'Comprehensive guide for new team members configuring SSH access to staging and production clusters.', 'Hardware', '["onboarding", "ssh", "git"]'::json, 'Published', 'usr-admin-001', NOW(), NOW());
