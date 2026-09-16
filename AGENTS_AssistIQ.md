# AGENTS.md — AI IT Helpdesk Project Rules

> Source of truth: `RAS_AI_Helpdesk_SRS_v3.3.md`. Follow the SRS for scope, architecture, roles, workflows, AI behavior, security, and deployment.

## 1. SRS Is the Source of Truth
- Follow the SRS exactly.
- Phase 1 is the active college-project scope.
- Do not implement Phase 2 or Future Scope unless explicitly requested.
- Do not invent requirements or silently change SRS decisions.
- When ambiguous, choose the smallest interpretation consistent with the SRS.

## 2. Phase 1 Scope
Implement:
- Incident and Service Request management.
- AI case analysis and summarization.
- Duplicate/similar-case detection.
- Missing-information detection.
- Assignment recommendation.
- SLA/risk detection.
- Level 1/2 escalation.
- AI-drafted communication.
- In-app + email notifications.
- Audit logging.
- Operational Insights.
- Search.
- Basic manually authored knowledge base.
- File attachments.
- Role-specific dashboards.
- Authentication and RBAC.

Do not implement without explicit instruction:
- Problem, Change, or Major Incident workflows.
- Controlled Auto-Fix.
- AI knowledge drafting/auto-publishing.
- Slack/Teams integrations.
- Identity/directory synchronization.
- Endpoint/asset integrations.
- Formal retention/deletion implementation.
- PDF export.
- Deep CMDB, monitoring, procurement/security-tool integrations.
- Multi-tenant SaaS.
- Advanced predictive analytics.
- Broad autonomous orchestration.

## 3. Free-Tier First
- The entire project must remain suitable for $0-tier development and deployment.
- Do not introduce paid infrastructure or paid APIs.
- Prefer existing free-tier services defined by the SRS.
- Avoid unnecessary third-party services and dependencies.
- Keep AI calls efficient and purposeful.
- Do not add infrastructure that requires a paid tier.

## 4. Approved Architecture
Use the SRS architecture:

Flutter Mobile/Desktop/Web
        ↓
     FastAPI
        ↓
Services → Providers → Supabase
                    ├─ Postgres
                    └─ Storage

- One shared Flutter codebase for Mobile, Desktop, and Web.
- FastAPI is the backend API.
- Supabase is used for Postgres + Storage.
- Gemini is the AI provider.
- Clients communicate through FastAPI.
- Do not perform direct client-to-Supabase CRUD.
- Business logic, RBAC, lifecycle rules, SLA logic, and audit writes belong in the backend.

## 5. No Heavy Background Architecture
Do not introduce:
- Celery
- Redis
- RabbitMQ/Kafka
- n8n
- Message queues/brokers
- Separate worker services
- Long-running workers

Synchronous AI operations include:
- Case analysis.
- Summarization.
- Duplicate detection.
- Missing-information detection.
- Assignment recommendation.
- Communication drafting.

These run inline in the relevant FastAPI request.

SLA/risk/escalation checks use the single in-process APScheduler Sweep defined by the SRS.

## 6. Scheduler Rules
- Use one lightweight periodic Sweep.
- Default interval: 5 minutes, configurable.
- Sweep checks SLA, risk, and escalation conditions.
- Keep it inside the same backend service.
- Make repeated execution safe.
- Respect the free-tier hosting sleep limitation documented by the SRS.

## 7. Environment and Secrets
Never hardcode:
- URLs, ports, credentials, API keys, JWT secrets.
- Gemini/Supabase credentials.
- Gmail/Brevo credentials.
- Google OAuth credentials or redirect URIs.
- Deployment-specific settings.

Rules:
- Never commit, expose, or modify `.env` as part of source control.
- Maintain `.env.example`.
- Use environment variables for local and production.
- Fail clearly when required configuration is missing.

## 8. Authentication
Support both:
- Password authentication using the SRS password hashing + JWT rules.
- Google OAuth 2.0/OIDC.

Production rules follow the SRS:
- Password signup email verification is enforced.
- Google OAuth signups are treated as verified after successful verified Google authentication.
- Do not silently merge password and Google accounts.
- Follow the SRS conflict behavior for email collisions.
- Protect authenticated routes.
- Enforce authorization server-side.
- Never trust role data supplied by the client.
- Never store plaintext passwords.

## 9. RBAC
Phase 1 implemented roles:
1. Requester
2. Operator
3. Team Lead
4. Manager
5. Administrator

Requester:
- Create and track own cases.
- Communicate on own cases.
- Add permitted attachments.
- Confirm resolution/reopen where allowed.
- Cannot access other users' cases or management functions.

Operator:
- Work assigned cases.
- Update permitted fields/status.
- Communicate with requesters.
- Add internal notes.
- Resolve cases.
- Request escalation.
- Use AI assistance.

Team Lead:
- Oversee team queue.
- Reassign within team.
- Monitor team workload.
- Handle team-level escalation.

Manager:
- Cross-team visibility.
- Reassign across teams/operators.
- Override priority.
- View cross-team dashboards and Operational Insights.
- Monitor SLA/escalation risk.

Administrator:
- Manage users, teams, roles, categories, service targets, notification settings.
- Access audit history.

Approver, Knowledge Owner, Service Owner, and Auditor may remain modeled with minimal UI as specified by the SRS. Do not build full workflows for them unless explicitly requested.

## 10. Server-Side Authorization
Never rely on UI hiding alone.
- Check permissions on every protected backend operation.
- Prevent ID-based access to unauthorized cases.
- Apply authorization to cases, search, reports, notifications, attachments, AI context, and future exports.
- Do not allow clients to bypass audit or business rules.

## 11. Case Types
Phase 1 supports exactly:
- Incident.
- Service Request.

Do not implement Problem, Change, or Major Incident workflows in Phase 1.

## 12. Case Lifecycle
Follow the SRS lifecycle:

Draft → New → InAssessment → Assigned
Assigned ↔ AwaitingRequester
Assigned ↔ AwaitingApproval
Assigned → Resolved → Closed

Also support:
- New → Cancelled.
- Assigned → Cancelled.
- Resolved → Assigned when requester rejects the fix.
- Closed → Assigned when reopened within the permitted 7-day window.

- Enforce transitions in backend business logic.
- Do not invent statuses or transitions.

## 13. AI Is an Assistant, Not an Authority
AI:
- Recommends.
- Summarizes.
- Surfaces context.
- Shows uncertainty.
- Supports human decisions.
- Has a documented fallback.

AI must not:
- Perform consequential IT actions autonomously.
- Automatically send AI-generated communications.
- Invent case history/knowledge.
- Pretend certainty.
- Change important records outside approved workflows.

Authorized humans remain responsible for consequential decisions.

## 14. AI Features
Phase 1 AI capabilities:
- Case analysis.
- Summarization.
- Duplicate/similar-case detection.
- Missing-information detection.
- Assignment recommendation.
- AI communication drafting.
- AI-assisted operational insight narration.

Confidence display:
- Low: 0.00–0.49
- Moderate: 0.50–0.79
- High: 0.80–1.00

Do not build a custom model or training pipeline.

## 15. AI Safety
Treat case/user text as untrusted input.
- Defend against prompt injection.
- Never reveal prompts, secrets, credentials, or internal configuration.
- Never request passwords, OTPs, API keys, or private credentials.
- Avoid destructive/risky troubleshooting.
- Escalate uncertain or high-risk situations to human support.

## 16. AI Fallback
If Gemini is unavailable:
- Show a clear AI-unavailable state.
- Never fabricate an AI response.
- Allow manual case workflow where possible.
- Preserve the case and user work.
- Follow SRS fallback/audit behavior.

## 17. AI Communication Drafts
Supported drafts:
- Information request.
- Progress update.
- Resolution message.
- Escalation summary.

Workflow:
Generate → Human reviews → Human may edit → Human explicitly sends.

Never auto-send an AI draft.

## 18. Search and Similar Cases
- Use the SRS database-native search approach.
- Do not introduce Elasticsearch, OpenSearch, Algolia, Pinecone, or another search service.
- Respect permissions during search and similarity detection.
- Similarity is a recommendation, not proof of common root cause.
- Human users decide whether cases are related.

## 19. SLA
- SLA uses 24/7 elapsed time.
- No business-hours calendar.
- Service targets are configurable.
- Support countdown, warning, breach, and risk states.
- Follow SRS escalation conditions.
- Do not invent alternative SLA rules.

## 20. Escalation
The Sweep may raise escalation events for SRS-defined conditions such as:
- SLA approaching/missed.
- High/Critical risk.
- Repeated reopening.
- Explicit Operator request for managerial help.

Escalation path:
Team Lead → Manager if unacknowledged.

Operator-requested managerial help is always human-triggered.
Every escalation event must be auditable.

## 21. Notifications
Phase 1:
- In-app notifications.
- Email notifications.

Do not implement:
- FCM push.
- SMS.
- WhatsApp.
- Slack/Teams.

Email providers:
- Local: Gmail SMTP.
- Staging/Production: Brevo HTTP API.

Notification failure must not destroy the underlying case action.
Notifications must respect authorization and privacy.

## 22. Audit Logging
Audit material actions including:
- Assignment.
- Status changes.
- AI recommendations generated/accepted.
- Priority overrides.
- Escalations.
- Resolution.
- Reopening.
- Closure.

Audit records should be written as part of the relevant business transaction where required.
Do not provide a normal client path that bypasses audit logging.

## 23. Operational Insights
Phase 1 uses aggregate existing case data:
- Case counts.
- Reopen rates.
- Category/site/team trends.
- Selectable time windows.

AI may narrate aggregate results.
Do not build separate analytics infrastructure or advanced predictive analytics.

## 24. Knowledge Base
- Phase 1 knowledge is manually authored.
- Do not automatically publish AI-generated articles.
- AI-assisted knowledge drafting is Phase 2.

## 25. Attachments
- Use the SRS storage approach.
- Enforce file size/type constraints.
- Do not expose private files publicly.
- Check authorization before access.
- Avoid unnecessary large-file processing.

## 26. API Rules
- Backend routes use `/api/v1/...`.
- Breaking response changes require a new API version.
- Validate requests.
- Use consistent errors.
- Protect endpoints with authentication/authorization.
- Do not expose unnecessary database implementation details.

## 27. Backend Layering
Follow:
API/Routes → Services → Repositories → Database

Use provider abstractions for:
- AI.
- Storage.
- Authentication.
- Notifications.

Rules:
- Reuse existing services.
- Keep business logic out of route handlers where it belongs in services.
- Repository is the database access boundary.
- Keep external providers replaceable.

## 28. Database
Use:
- Supabase Postgres.
- SQLAlchemy ORM.
- Alembic migrations.

Rules:
- Schema changes go through migrations.
- Do not manually alter production schema.
- Do not create unnecessary tables.
- Preserve case history and audit requirements.
- Maintain authorization boundaries.

## 29. Flutter
One shared Flutter codebase targets:
- Android.
- iOS.
- Windows.
- macOS.
- Linux.
- Web.

Rules:
- Reuse shared components.
- Isolate platform-specific code.
- Keep layouts responsive.
- Do not duplicate complete screens unnecessarily.
- Do not hardcode API URLs.

## 30. UI/UX
The product should be:
- Simple for Requesters.
- Operational for Operators/Team Leads.
- Analytical for Managers.
- Administrative for Administrators.

Always:
- Distinguish AI suggestions from human decisions.
- Clearly show status, owner, priority, and SLA.
- Show loading/pending states for AI.
- Show useful error/fallback states.
- Respect role permissions in the UI.

## 31. Responsive Design
Every UI feature must work across mobile, tablet, desktop, and web.
Avoid fixed-width layouts and desktop-only interactions.

## 32. Performance
Follow SRS targets:
- Non-AI API p95 < 2 seconds.
- AI operations may take longer.
- Show a visible pending state if an AI operation exceeds approximately 3 seconds.
- Avoid unnecessary DB and AI calls.
- Do not add performance infrastructure outside the SRS.

## 33. Free-Tier AI Usage
- Use AI only at meaningful workflow points.
- Prefer well-structured, efficient calls.
- Reuse available case context.
- Use structured outputs.
- Mock Gemini during development/testing where practical.
- Do not call AI on every UI interaction.
- Do not create autonomous AI loops.

## 34. Error Handling
Handle failures for:
- Gemini.
- Supabase/database.
- Storage.
- Gmail/Brevo.
- Google OAuth.
- Network requests.

Rules:
- User-friendly errors.
- Preserve work where possible.
- Never expose stack traces/secrets.
- Use documented fallbacks.
- Log technical details safely.

## 35. Demo/Seed Data
Use the SRS seed approach:
- One representative user per implemented role.
- Approximately 15–20 cases across lifecycle states.
- Sample messages/attachments where appropriate.
- AI results, summaries, and risk assessments.
- Enough data for all dashboards and Operational Insights.

Do not hardcode fake dashboard numbers.

## 36. Testing
Test every meaningful feature.

Backend:
- Unit tests.
- Integration tests.
- Authentication/RBAC.
- Lifecycle transitions.
- SLA.
- AI fallback.
- Notification failures.
- Audit logging.
- Security/access isolation.

Flutter:
- Widget tests where appropriate.
- Important user-flow tests.
- Responsive layouts.
- Loading/error states.

## 37. Deployment
- Development, staging, and production configuration must be environment-driven.
- Do not commit production secrets.
- Follow the SRS free-tier deployment plan.
- Respect free-tier sleeping/scheduler limitations.
- Do not add CI/CD because the SRS explicitly keeps builds/tests/deployments manual.

## 38. Dependencies
Before adding a dependency:
1. Check whether the project already supports the need.
2. Check whether the SRS requires it.
3. Prefer a simpler existing solution.
4. Check free-tier/deployment impact.
5. Add only when justified.

## 39. Reuse Before Creating
Before creating a new screen, component, service, repository, provider, utility, model, or validation rule:
- Check for an existing implementation.
- Extend/reuse where practical.
- Avoid duplicate logic.

## 40. No Hardcoded Business Values
Do not hardcode:
- SLA durations.
- Roles/permissions.
- Case statuses.
- Categories.
- AI thresholds.
- API URLs.
- Environment settings.
- Notification behavior.

Use configuration, database values, or shared business rules.

## 41. Validate Every Change
After every task:
1. Run relevant tests.
2. Verify affected workflows.
3. Verify authorization.
4. Verify error/fallback states.
5. Verify responsive UI when applicable.
6. Confirm existing functionality still works.
7. Fix introduced issues before completion.

## 42. Git Discipline
- Commit meaningful completed changes with clear messages.
- Push according to the repository workflow.
- Never commit `.env`, credentials, API keys, tokens, or secrets.
- Avoid unrelated changes.

## 43. Documentation
Keep these aligned with implementation:
- `SRS.md`
- `.env.example`
- `README.md`
- Relevant ADRs.

README should cover:
- Product purpose.
- Roles.
- Main features.
- Stack.
- Local setup.
- Environment variables.
- Migrations.
- Running backend.
- Running Flutter targets.
- Tests.
- Deployment overview.
- SRS reference.

## 44. Scope Change Rule
If a requested feature conflicts with the SRS:
- Do not silently implement it.
- Identify the conflict.
- Follow the current SRS behavior.
- Treat valuable conflicting features as proposed scope changes.
- Do not implement Phase 2/Future features merely because they are easy.

## 45. Definition of Done
A task is complete only when:
- Requested behavior works.
- It follows the SRS.
- RBAC is enforced where relevant.
- Errors/fallbacks are handled.
- Tests are updated where appropriate.
- Existing functionality is not broken.
- No unnecessary infrastructure/dependency was added.
- No secrets are exposed.
- Documentation is updated when needed.
- The change remains free-tier compatible.

## 46. Decision Priority

When choices conflict:

1. SRS requirements
2. Security and authorization
3. Phase 1 scope
4. Free-tier constraint
5. Simplicity/maintainability
6. Performance
7. Optional enhancements

> **Default rule: Build the smallest implementation that satisfies the SRS correctly, securely, and within the free-tier constraint.**

## 47. What should u call me?
u hav to call me Rasika Babe after each and every phase or task ur done with or whatevr u wanna ask me or want me to check or verify anything.