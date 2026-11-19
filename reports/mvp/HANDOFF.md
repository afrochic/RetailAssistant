# Rebuild handoff — source-only, manual control preserved

## Phase 0 — rapid audit

**Status:** IMPLEMENTED (read-only audit).
**Files created or changed:** PHASE_0_AUDIT.md; CHANGE_PLAN.md; ADR 0001.
**Data source evidence:** Existing 5,512-record Healthy U export, observed schema/size/hash, original backend parser and category ADR. User confirmed public presentation permission and KES RRP.
**What is implemented:** Two-Vercel-project plan; existing renamed repository verified; export-only adapter design.
**What has actually been verified:** File/source/schema/Git metadata and official documentation, read-only only.
**What remains unexecuted:** All runtime/model/build/cloud verification.
**Known blockers:** No source-access blocker; source freshness and missing structured attributes remain unknown.
**Security and privacy considerations:** No customer/order/health database read or copied; source HU application unchanged; no secret values disclosed.
**Manual commands for me to run:** QUICKSTART.md and MANUAL_RUNBOOK.md.
**Expected output and acceptance criteria:** Review the audited source and approve operator execution before extracting a snapshot.
**Decision required before next phase:** Source use/KES was already confirmed; updated user instructions authorized nonblocked implementation without phase pauses.

## Phase 1 — retrieval, FastAPI, Groq

**Status:** IMPLEMENTED source, UNTESTED.
**Files created or changed:** apps/api; scripts/mvp/prepare.py; tests/test_contract.py.
**Data source evidence:** Runtime rejects missing/unapproved Healthy U provenance; no substitute seed data.
**What is implemented:** Manual export normalization, actual TF-IDF fitting/serialization, optional offline projected semantic/hybrid retrieval, KES/metadata constraints, Groq strict composition, citation checks, medical safeguards, quotas, body/input limits and safe fallback modes.
**What has actually been verified:** Read-only source review; local secret files are Git-ignored. No provider request was made.
**What remains unexecuted:** Ingestion, fitting, dependency installation, tests, actual provider/model/quota checks.
**Known blockers:** Generated catalogue/index files do not exist until student execution; key validity/access is unverified.
**Security and privacy considerations:** Key server-only in ignored local .env; rotate the chat-exposed key; shared HMAC Redis counters required on Vercel; no chat text/accounts persisted by the app.
**Manual commands for me to run:** QUICKSTART sections 1–4; prepare.py ingest/index; manage.py test/lint/smoke.
**Expected output and acceptance criteria:** /ready true; references are approved source IDs; prices obey KES budget; unsupported fields abstain; quota failures are explicit.
**Decision required before next phase:** Student execution, not further source-choice clarification.

## Phase 2 — Next.js chat

**Status:** IMPLEMENTED source, UNTESTED.
**Files created or changed:** apps/web (Next.js, React, TypeScript, Tailwind, local licensed fonts).
**Data source evidence:** All recommendations are API response references; no storefront or invented product records.
**What is implemented:** Anonymous session-local messages, New Conversation, examples, Markdown, loading, Stop, retry, preferences, citations, safe retailer links, responsive styling and modal keyboard handling.
**What has actually been verified:** Source/API-shape review only.
**What remains unexecuted:** npm install/lockfile generation, typecheck/lint/build, browser/mobile/accessibility/integration checks.
**Known blockers:** Frontend package lock not generated; backend origin/public URL depends on operator setup.
**Security and privacy considerations:** No Groq key in client; HTML/images/generated links suppressed; only allowlisted retailer links; privacy text distinguishes local persistence from provider transfer.
**Manual commands for me to run:** npm install/dev; manage.py web-build; apps/web/FRONTEND_ACCEPTANCE.md.
**Expected output and acceptance criteria:** Chat is usable anonymously on actual local/public origins, with accurate ready/fallback/error state and safe references.
**Decision required before next phase:** Run the manual acceptance checklist.

## Phase 3 — deployment/testing preparation

**Status:** IMPLEMENTED configuration, UNDEPLOYED.
**Files created or changed:** Vercel configs, env examples, .vercelignore, QUICKSTART.md, VERCEL_DEPLOYMENT.md, MANUAL_RUNBOOK.md, DEPLOYMENT.md, Dockerfile/Compose, manual workflows.
**Data source evidence:** Generated approved lightweight files must be prepared/reviewed before staging/deploying. No old checkpoints bundled.
**What is implemented:** Two native Vercel roots, Python 3.12/Node 22, bounded calls, explicit deployment confirmation and disabled automatic Git releases.
**What has actually been verified:** Official documentation and source configuration inspected; no actual platform build or deployment verified.
**What remains unexecuted:** All local checks, Git operations, Vercel project/env/Redis setup, builds/deployments and public smoke checks.
**Known blockers:** Actual project/org IDs, public origins, remote server secrets and shared limiter settings are operator-supplied.
**Security and privacy considerations:** Production workflow enable variable remains unset by the agent; require protected environment/review and explicit DEPLOY. No cloud settings changed.
**Manual commands for me to run:** Exact commands in VERCEL_DEPLOYMENT.md. Validation workflows are manual only.
**Expected output and acceptance criteria:** Both actual production origins work; /ready and CORS pass; public chat requires no app/deployment login; no secrets reach frontend.
**Decision required before next phase:** Student must demonstrate the local/live MVP before treating Phase 4 as measured research.

## Phase 4 — academic materials

**Status:** PARTIAL scaffolding; PENDING EXECUTION.
**Files created or changed:** research/mvp notebook/report/slide/query templates; scripts/mvp/evaluate.py and report.py; AI_USE.md, DATA_CARD.md, PROJECT_COMPLIANCE.md.
**Data source evidence:** Only new approved snapshot/actual outputs can support the new report. Legacy Flipkart scores are explicitly excluded.
**What is implemented:** Human-label gating, retrieval metrics, constraint/ID checks, actual optional API request capture, process RSS/latency output and evidence-sheet generation.
**What has actually been verified:** Source/template inspection only; notebook code cells have null execution counts and no outputs.
**What remains unexecuted:** Human judgments, fitting/evaluation, generation/clinical review, charts, Docker reproduction and final measured PDF/slides.
**Known blockers:** No real human-reviewed labels or new outputs exist yet.
**Security and privacy considerations:** Synthetic UNIT FIXTURES are test-only and excluded from deployment. Do not publish private/sensitive request text from evaluation.
**Manual commands for me to run:** MANUAL_RUNBOOK steps 14–17 after MVP demonstration.
**Expected output and acceptance criteria:** Actual held-out results with sample sizes, error analysis, explicit missing runs, claims-review limits and honest source/AI disclosure.
**Decision required before next phase:** Student review and evidence collection; no automated academic success is claimed.

## Container amendment — 20 November 2026

Implemented: both multi-stage images, matching Dockerfile.vercel copies, standalone Next output, frontend liveness/runtime-config routes, root two-service Compose, resource/security settings, manual image workflow and new container/deployment runbooks. Legacy Compose preserved separately. Not executed: dependency installation, artifact preparation, builds, tests, Docker, Git mutations or cloud deployment. Blockers: generated approved catalogue artifacts, reviewed frontend lockfile, rotated private Groq key, public Redis credentials, Vercel project/environment setup and manual verification. No working public deployment is claimed.
