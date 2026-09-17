# AssistIQ — Project Progress & State Tracker

> **Project Identity**: AssistIQ — AI-Assisted IT Helpdesk (Incidents & Service Requests).
> **Rules & Architecture Source of Truth**: `AGENTS_AssistIQ.md` and `docs/RAS_AI_IT_Helpdesk_SRS_v3.3.md`.
> **Primary Rule**: AI is an assistant, not an authority. Strict $0 free-tier compatibility, FastAPI backend, Supabase Postgres/Storage, Gemini AI, in-process APScheduler, and Flutter multi-target client.

---

## 📊 Phase Roadmap & Current Status

| Phase | Description | Status | Test Coverage | Git Branch |
|---|---|---|---|---|
| **Phase 1** | Backend Scaffolding, Directory Setup, Config, Health Check | ✅ Completed | 2 passed | `feature/phase-1-scaffold` |
| **Phase 2** | Database Models, Relational Schema & Alembic Migrations | ✅ Completed | 3 passed | `feature/phase-2-database` |
| **Phase 3** | Dual-Path Auth (Argon2id + Google OAuth), Server-Side RBAC & Notification Providers | ✅ Completed | 9 passed | `feature/phase-3-auth` |
| **Phase 4** | Case Management Engine, State Machine, Optimistic Concurrency & Audit Logging | ✅ Completed | 5 passed | `feature/phase-4-cases` |
| **Phase 5** | Case Messaging (Visibility Scoping), File Attachments (Storage Providers) & Idempotency | ✅ Completed | 6 passed | `feature/phase-5-messaging` |
| **Phase 6** | Unified Full-Text Search, Candidate Similarity Detection & Knowledge Base | ✅ Completed | 3 passed | `feature/phase-6-search-knowledge` |
| **Phase 7** | Gemini AI Capabilities & In-Process Scheduler (The Sweep, SLA, Risk, Escalations) | ✅ Completed | 16 passed | `feature/phase-7-ai-sweep` |
| **Phase 8** | Operational Insights, CSV Export, Demo Seeder (`seed_demo_data.py`) & Full Test Suite | ✅ Completed | 50 passed | `feature/phase-8-insights-seeder` |
| **Phase 9** | Frontend Web & Multi-Platform Client (`web`, `android`, `ios`, `desktop`) | ✅ Completed | Dual Web & Flutter | `feature/phase-9-frontend` |

---

## 🛠️ Summary of Completed Phases (1 to 8)

### Phase 1: Backend Scaffolding & Environment Setup
* Root configuration: [`.gitignore`](file:///e:/AssistIQ/.gitignore), [`docker-compose.yml`](file:///e:/AssistIQ/docker-compose.yml) (Postgres 16), [`backend/requirements.txt`](file:///e:/AssistIQ/backend/requirements.txt), [`backend/.env.example`](file:///e:/AssistIQ/backend/.env.example).
* Backend core: [`backend/core/config.py`](file:///e:/AssistIQ/backend/core/config.py) (startup environment validation per SRS §3.3), [`backend/core/errors.py`](file:///e:/AssistIQ/backend/core/errors.py) (standardized error envelope), [`backend/db/session.py`](file:///e:/AssistIQ/backend/db/session.py) (SQLAlchemy engine & `get_db`).
* Health check: [`backend/api/health.py`](file:///e:/AssistIQ/backend/api/health.py) (`GET /api/v1/health` verifying DB connectivity without consuming AI quotas).

### Phase 2: Database Layer & Migrations
* Enumerations: [`backend/models/enums.py`](file:///e:/AssistIQ/backend/models/enums.py) (all 15 system enums).
* 15 Relational Models:
  * [`backend/models/user.py`](file:///e:/AssistIQ/backend/models/user.py): `User`, `Team`.
  * [`backend/models/case.py`](file:///e:/AssistIQ/backend/models/case.py): `Case` (with optimistic lock `version: int`), `CaseRelationship`.
  * [`backend/models/message.py`](file:///e:/AssistIQ/backend/models/message.py): `Message`, `Attachment`.
  * [`backend/models/sla.py`](file:///e:/AssistIQ/backend/models/sla.py): `SLA` (24/7 elapsed wall-clock deadlines).
  * [`backend/models/ai.py`](file:///e:/AssistIQ/backend/models/ai.py): `AITriageResult`, `CaseSummary`, `CaseRiskAssessment`, `EscalationEvent`, `CommunicationDraft`.
  * [`backend/models/governance.py`](file:///e:/AssistIQ/backend/models/governance.py): `AuditLog`, `Approval`, `KnowledgeArticle`.
* Alembic migrations: [`backend/alembic.ini`](file:///e:/AssistIQ/backend/alembic.ini), [`backend/db/migrations/env.py`](file:///e:/AssistIQ/backend/db/migrations/env.py), [`backend/db/migrations/versions/0001_initial_schema.py`](file:///e:/AssistIQ/backend/db/migrations/versions/0001_initial_schema.py) (creates all tables and enables `pg_trgm`).

### Phase 3: Authentication, RBAC & Notification Providers
* Security: [`backend/core/security.py`](file:///e:/AssistIQ/backend/core/security.py) (Argon2id password hashing, JWT access/refresh token rotation, email verification & password reset signed tokens).
* Swappable Notifications: [`backend/providers/notifications/`](file:///e:/AssistIQ/backend/providers/notifications/) (`GmailSmtpNotificationProvider` locally, `BrevoNotificationProvider` over HTTPS for staging/prod).
* Server-side RBAC: [`backend/core/dependencies.py`](file:///e:/AssistIQ/backend/core/dependencies.py) (`require_roles` for `Requester`, `Operator`, `TeamLead`, `Manager`, `Administrator`).
* Auth Endpoints: [`backend/api/auth.py`](file:///e:/AssistIQ/backend/api/auth.py) (`signup`, `login`, `google` with account collision conflict protection `409`, `refresh`, `verify-email`, `password-reset`, `me`).

### Phase 4: Case Management Engine & Lifecycle
* Reference number generator: `<INC|REQ>-<YEAR>-<6_DIGIT_SEQ>` (e.g. `INC-2026-000001`).
* State Machine: Enforcing valid transitions (`Draft` → `New` → `InAssessment` → `Assigned` ↔ `AwaitingRequester` / `AwaitingApproval` → `Resolved` → `Closed` / `Cancelled` / `Reopened`).
* Optimistic Concurrency: Enforces `expected_version == case.version`, increments `version += 1`, raises `409 STALE_VERSION` on mismatch.
* 7-Day Reopen Rule: Enforces that closed cases can only be reopened within 7 calendar days of `closed_at`.
* Append-Only Audit Logging: [`backend/repositories/audit_repository.py`](file:///e:/AssistIQ/backend/repositories/audit_repository.py) writing `AuditLog` records in the same transaction.
* Case Endpoints: [`backend/api/cases.py`](file:///e:/AssistIQ/backend/api/cases.py) (`POST /cases`, `GET /cases`, `GET /cases/{id}`, `PATCH /status`, `PATCH /assign`, `PATCH /priority`, `POST /reopen`, `GET /timeline`).

### Phase 5: Messaging, Attachments & Idempotency
* Visibility Scoping: `requester_visible` (accessible to all) vs `internal_only` (strictly filtered out for requesters).
* Storage Provider: [`backend/providers/storage/`](file:///e:/AssistIQ/backend/providers/storage/) (`LocalStorageProvider` + `SupabaseStorageProvider`).
* File Validation: [`backend/core/file_validation.py`](file:///e:/AssistIQ/backend/core/file_validation.py) (10MB limit, 50MB case total, extension whitelist, magic bytes validation).
* Idempotency: [`backend/core/idempotency.py`](file:///e:/AssistIQ/backend/core/idempotency.py) (24-hour TTL caching on `Idempotency-Key` headers).
* Lifecycle Trigger: Requester reply on `AwaitingRequester` moves case to `Assigned`.
* Endpoints: [`backend/api/messages.py`](file:///e:/AssistIQ/backend/api/messages.py) (`POST /messages`, `GET /messages`, `POST /attachments`, `GET /attachments`, `GET /attachments/{id}/download`).

### Phase 6: Search Engine, Similarity & Knowledge Base
* Manually Authored Knowledge Base: [`backend/services/knowledge_service.py`](file:///e:/AssistIQ/backend/services/knowledge_service.py) & [`backend/api/knowledge.py`](file:///e:/AssistIQ/backend/api/knowledge.py) (category filtering, Markdown bodies, draft/published/archived states).
* Duplicate & Similar Case Detection: [`backend/services/search_service.py`](file:///e:/AssistIQ/backend/services/search_service.py) (token and trigram Jaccard similarity score from 0.0 to 1.0; suggestions for human review without auto-merging).
* Unified Full-Text Search: `GET /api/v1/search?q=...` across permitted cases and published knowledge articles with strict RBAC isolation.

### Phase 7: Gemini AI Capabilities & In-Process Scheduler (The Sweep)
* AI Provider Layer: [`backend/providers/ai/`](file:///e:/AssistIQ/backend/providers/ai/) (`GeminiAIProvider` with structured JSON, retry with exponential backoff, prompt injection safety, and `MockAIProvider` for testing).
* Versioned Prompt Templates: [`backend/ai/`](file:///e:/AssistIQ/backend/ai/) (`triage_prompt.py`, `summary_prompt.py`, `draft_prompt.py`).
* 24/7 SLA Service: [`backend/services/sla_service.py`](file:///e:/AssistIQ/backend/services/sla_service.py) (P1: 15m/4h, P2: 1h/8h, P3: 4h/72h, P4: 24h/120h wall-clock deadlines, first-response recording, breach detection, 7-day reopen reset).
* AI Service Engine: [`backend/services/ai_service.py`](file:///e:/AssistIQ/backend/services/ai_service.py) (triage generation, inline summary recomputation, smart workload-aware assignment recommendation, draft review & send workflow creating `Message` with `ai_generated=True`).
* In-Process Scheduler ("The Sweep"): [`backend/scheduler/`](file:///e:/AssistIQ/backend/scheduler/) (APScheduler running `run_the_sweep` evaluating open cases for SLA breaches, computing `CaseRiskAssessment` scores, and raising automatic `EscalationEvent` records).
* Level 2 Human Escalation & Endpoints: [`backend/api/ai.py`](file:///e:/AssistIQ/backend/api/ai.py), [`backend/api/sla.py`](file:///e:/AssistIQ/backend/api/sla.py), [`backend/api/escalations.py`](file:///e:/AssistIQ/backend/api/escalations.py).

### Phase 8: Operational Insights, CSV Export, Demo Seeder & Full Verification
* Operational Insights Service: [`backend/services/insights_service.py`](file:///e:/AssistIQ/backend/services/insights_service.py) (SQL aggregations across `7d`, `30d`, `90d`, and `all` time windows; volume by category, priority, status, site; reopen rate; average MTTR/resolution time; SLA compliance rate; AI plain-language operational narrative).
* Role-Scoped CSV Export: [`backend/services/export_service.py`](file:///e:/AssistIQ/backend/services/export_service.py) & [`backend/api/reports.py`](file:///e:/AssistIQ/backend/api/reports.py) (`GET /api/v1/reports/export/cases.csv` enforcing requester vs staff visibility boundaries with streaming `text/csv`).
* Quick Dashboard Stats: `GET /api/v1/insights/dashboard` returning real-time active, unassigned, breached, and critical counts.
* Demo Seeder Script: [`scripts/seed_demo_data.py`](file:///e:/AssistIQ/scripts/seed_demo_data.py) (idempotent seeder creating 5 role-representative test users, 3 teams, 18 cases spanning all lifecycle states, SLAs, messages, attachments, AI triage/summaries/risk assessments, escalation events, and knowledge articles).

---

## 🧪 Test Suite Status
Total tests passing: **50 tests (100% pass rate)**.
Command to run full backend tests:
```cmd
python -m pytest backend/tests/ -v
```

---

## 🚀 Next Steps (Phase 9+: Frontend & Production Readiness)

1. **Phase 9: Flutter Multi-Target Web/Desktop/Mobile Application**:
   * Scaffolding Flutter app with responsive split-screen layouts, glassmorphism dark mode aesthetic.
   * State management, auth session storage, RBAC-aware navigation, and reactive notifications.
   * Case creation wizards, AI triage inspection badges, message threads with visibility toggles, and live operational insights dashboards.
