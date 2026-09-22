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
| **Phase 9** | Frontend Web & Multi-Platform Client (`web`, `desktop`) | ✅ Completed | React 19 + TypeScript + Vite | `dev` |
| **Phase 10** | UI/UX Elevation: Crystal Glassmorphism, 3D Physics, Theme Toggle & Microinteractions | ✅ Completed | 100% Theme Fidelity | `dev` |
| **Phase 11** | Flutter Android Mobile App: 100% Web Parity, Responsiveness & Physical Device Deployment | ✅ Completed | 50 Pytest + Flutter Analyze Pass | `dev` |
| **Phase 12** | Cloud Deployment (Render, Supabase DB & Storage, Vercel), Multiplatform Client Hub & Branding | ✅ Completed | 53 passed (100%) | `main` & `dev` |

---

## 🛠️ Summary of Completed Phases (1 to 11)

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

### Phase 9: Frontend Architecture & Desktop Application
* Modern React 19 + TypeScript + Vite architecture ([`frontend/`](file:///e:/AssistIQ/frontend/)).
* Complete SPA Views: [`WorkbenchView`](file:///e:/AssistIQ/frontend/src/views/WorkbenchView.tsx), [`InsightsView`](file:///e:/AssistIQ/frontend/src/views/InsightsView.tsx), [`DispatchView`](file:///e:/AssistIQ/frontend/src/views/DispatchView.tsx), [`KnowledgeView`](file:///e:/AssistIQ/frontend/src/views/KnowledgeView.tsx), [`AdminView`](file:///e:/AssistIQ/frontend/src/views/AdminView.tsx), and [`LoginView`](file:///e:/AssistIQ/frontend/src/views/LoginView.tsx).
* Standalone Windows Desktop App package with custom icon, automated installer scripts, and single-click startup.

### Phase 10: UI/UX Elevation & Crystal Glassmorphism
* **Ultra-Clear Crystal Glassmorphism**: Complete removal of milky/faded white tints in favor of optical transparent glass with refractive specular edges and ambient lighting.
* **3D Physics & Micro-Lift**: Card depth lift with specular glint on hover across all cards, KPI tiles, and list items.
* **Tactile Spring Microinteractions**: Smooth 60fps compression feedback on all buttons, tabs, and filter pills.
* **Radiant Warm Shimmers**: Elegant, non-flashy warm amber and terracotta shimmer loading states.
* **Top-Right Dark/Light Mode Switcher**: Instant theme toggle persisting state in `localStorage` with smooth rotating icon.
* **Top-Right Notification Bell Flyout**: Live breach counter badge, hover shake/ringing microinteraction, and direct dispatch link.
* **High-Contrast Search Icons**: Magnifying glass search icons engineered for clear visibility in both light and dark themes.

### Phase 11: Flutter Android Mobile Client & Layout Parity
* **Full Mobile Parity**:
  * [`LoginScreen`](file:///e:/AssistIQ/flutter_app/lib/screens/login_screen.dart): Clean Sign In and Register Account tabs with password length validation and enterprise fields, matching the React web app. Removed 1-click demo personas from login in favor of top-header profile switching.
  * [`WorkbenchScreen`](file:///e:/AssistIQ/flutter_app/lib/screens/workbench_screen.dart): Queue list, scrollable filter chips (`ALL`, `ACTIVE`, `BREACHED`, `UNASSIGNED`), detail pane with 7-Day Reopen modal, Reject Fix, Confirm Fix & Close, and Escalate L2 modal.
  * [`InsightsScreen`](file:///e:/AssistIQ/flutter_app/lib/screens/insights_screen.dart): Cycle selector (`7d`, `30d`, `90d`, `all`), AI diagnostic narrative with System Recommendation card, 4 responsive KPI cards, and Support Team Breakdown.
  * [`DispatchScreen`](file:///e:/AssistIQ/flutter_app/lib/screens/dispatch_screen.dart): Dynamic escalation alerts list, Acknowledge button, and Trigger Sweep manual background execution.
* **Mobile Responsiveness & RenderFlex Overflow Fixes**:
  * Resolved the 7.4px layout overflow by tuning grid aspect ratios (`1.1`), wrapping metric values in `FittedBox(fit: BoxFit.scaleDown)`, and setting ellipsis truncation on all text headers.
  * Replaced fixed-width rows with `Wrap` and `SingleChildScrollView(scrollDirection: Axis.horizontal)` across all screens and widgets.
* **ADB Device Deployment**:
  * Configured local Wi-Fi API gateway (`http://192.168.0.197:8000/api/v1`).
  * Automated compilation and streaming installation directly onto connected Android physical device (`BE4DOBD6LBEEBMLJ`).

### Phase 11.1: Docket Intake Engine, Severity Descriptions & Non-Overflow Polish
* **"Submit & AI Triage" Full-Stack Pipeline Fix**:
  * Resolved backend Pydantic schema rejection by adding `@model_validator(mode="before")` in [`backend/schemas/case.py`](file:///e:/AssistIQ/backend/schemas/case.py) to dynamically normalize `case_type`/`type` and `category`/`service_id` aliases with `extra="ignore"`.
  * Updated Flutter client payload in [`CaseProvider.createCase`](file:///e:/AssistIQ/flutter_app/lib/providers/case_provider.dart) to cleanly dispatch standard schema keys.
  * Added validation & full try/catch error surfacing in [`CaseIntakeSheet`](file:///e:/AssistIQ/flutter_app/lib/screens/case_intake_sheet.dart) ensuring minimum field lengths (title ≥ 3 chars, description ≥ 5 chars) and displaying error banners on network or server exceptions.
* **Rich Severity Descriptions & 24/7 SLA Target Guidelines**:
  * Added real-time dynamic severity guideline cards on both Flutter ([`CaseIntakeSheet`](file:///e:/AssistIQ/flutter_app/lib/screens/case_intake_sheet.dart)) and React Web ([`CaseIntakeModal`](file:///e:/AssistIQ/frontend/src/components/cases/CaseIntakeModal.tsx)).
  * Detailed breakdown with color-coded badges:
    * **P1 — Critical**: Immediate operational stoppage / severe hazard. (15m Response • 4h Resolve SLA)
    * **P2 — High**: Major component impairment with limited workaround. (1h Response • 8h Resolve SLA)
    * **P3 — Medium**: Standard operational issue with viable workaround. (4h Response • 72h Resolve SLA)
    * **P4 — Low**: Minor cosmetic anomaly or standard service request. (24h Response • 120h Resolve SLA)
* **Comprehensive Layout Overflow & Keyboard Inset Fixes**:
  * Eliminated hardcoded height constraints from bottom sheets, wrapping modal views in `SafeArea` + dynamic `EdgeInsets.only(bottom: MediaQuery.of(context).viewInsets.bottom)` for keyboard entry without pixel clipping.
  * Constrained top-header user email blocks with ellipsis to prevent horizontal AppBar overflow on narrow displays.

### Phase 12: Production Cloud Architecture, Multiplatform Client Hub & Branding
* **Custom Cyber-Shield Branding & High-Res App Assets**:
  * Generated unified cyber-shield with glowing neural core identity across all targets:
    * `frontend/build/icon.ico` (256x256 multi-layer Windows executable icon)
    * `frontend/build/icon.png` and `frontend/public/icon.png` (512x512 PNG)
    * `frontend/public/favicon.ico` and `frontend/public/favicon.png` (64x64 favicon)
    * `flutter_app/assets/images/app_logo.png` (512x512 Flutter asset)
* **Multiplatform Client Download Hub**:
  * Added instant **Download Hub modal** (`ClientInstallModal.tsx`) directly accessible from the web top navigation bar.
  * Windows NSIS Standalone Installer: `frontend/dist-desktop/AssistIQ Helpdesk Setup 1.0.0.exe` (~107.6 MB) with single-click setup.
  * Android Release APK: `flutter_app/build/app/outputs/flutter-apk/app-release.apk` (~50.2 MB) compiled with AOT optimization and resource tree-shaking.
  * Added REST download delivery endpoints:
    * `GET /api/v1/downloads/info` (dynamic platform metadata and file sizes)
    * `GET /api/v1/downloads/desktop` (streamed `.exe` binary download)
    * `GET /api/v1/downloads/android` (streamed `.apk` binary download)
* **Cloud Deployment Architecture**:
  * **Backend (Render)**: Created `render.yaml` blueprint for Python 3 FastAPI service with Uvicorn, health checks, and environment configurations.
  * **Frontend (Vercel)**: Configured `frontend/vercel.json` with SPA URL rewrites for seamless client-side routing on page refresh.
  * **Database & Storage (Supabase)**:
    * Created `scripts/supabase_schema.sql` containing full PostgreSQL DDL and initial demo data.
    * Configured and validated `SupabaseStorageProvider` connected to bucket `assistiq-attachments`.
    * Implemented pooler compatibility, `sslmode=require`, and fail-fast connection timeouts in `backend/db/session.py`.
* **Git Synchronization**:
  * Synchronized all commits across `dev` and `main` branches to remote repository: `https://github.com/rasikakudale90/AssistIQ.git`.

---

## 🧪 Test Suite Status
* **Backend**: **53 tests passed (100% pass rate)** (`pytest backend/tests -v`).
* **Frontend Web**: TypeScript compilation passed with `0` errors; Vite production build passes cleanly (`dist/assets/`).
* **Flutter Mobile**: `flutter analyze` completed with `0` errors and `0` warnings.
* **Storage Integration**: Verified Supabase Bucket `assistiq-attachments` connectivity and service role authentication.

---

## 🚀 Deployment Checklist & Next Steps
1. **Supabase**: Execute `scripts/supabase_schema.sql` in SQL Editor to populate all 12 tables and seed demo accounts.
2. **Render**: Create Web Service linked to repository `main` branch with `render.yaml` environment variables.
3. **Vercel**: Import repository `main` branch with root directory `frontend` and set `VITE_API_URL` to the Render backend URL.
4. **CORS**: Verify `ALLOWED_ORIGINS` on Render contains the live Vercel domain.


