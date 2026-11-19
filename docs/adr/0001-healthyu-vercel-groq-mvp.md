# ADR: Healthy U chat-first presentation MVP

Date: 2026-11-19. Status: implemented source/configuration; all execution pending student action.

## Decisions

- Two Vercel projects, one existing `afrochic/RetailAssistant` repository: roots `apps/api` (native Python FastAPI) and `apps/web` (Next.js). The existing local remote still uses the old repository name, which GitHub redirects to the canonical repository; do not rewrite it or history automatically.
- Do not modify the enclosing HU-NutritionistsVA application. Reuse its approved export schema only. No accounts, customer database, checkout, cart or catalogue browsing.
- User confirmed permission for this presentation MVP and KES prices in the existing 5,512-product Healthy U export. Source file is inspected read-only. Actual ingestion and artifact fitting are NOT executed by the agent.
- Groq compatible HTTP API, primary model `openai/gpt-oss-120b`; server-only key. Strict structured response, validated product IDs/evidence and deterministic safe rendering. No paid OpenAI provider or local LLM in the MVP runtime.
- MVP retrieval: fitted lexical TF-IDF, serialized as portable JSON; optional offline MiniLM product vectors plus a fitted lightweight semantic query projection. Query projection is an approximation, explicitly distinguished from native transformer query encoding. No Torch, sklearn, model downloads, training or disk writes in serverless inference.
- Rate limiting: shared Redis REST atomic Lua limits for public deployment; process-local limiter only for explicit local development. Fail closed when shared controls are required/unavailable. No user-account store.
- Medical requests receive deterministic non-diagnostic boundaries; acute warning signs receive urgent-care guidance; no supplements/medication recommended as treatment. Raw marketing claims are excluded from generation evidence.
- All tests/builds/ingestion/training/Git operations and deployments are manual. Existing measured Flipkart/SmolLM results are historical and do not count as Healthy U/Groq results.

## Scope and sequencing

Phase 0 audit documented; Phase 1 backend/retrieval/Groq implementation; Phase 2 anonymous chat; Phase 3 Vercel/manual runbook; Phase 4 academic scaffolding only. No benchmark or live deployment success can be claimed before student execution.

## Container architecture amendment — 20 November 2026

User now requires both apps Dockerized and Vercel Container Runtime hosting. Use two existing-repository project roots, apps/api and apps/web, framework container and Dockerfile.vercel; both runtime servers respect PORT (set 8080 in Vercel). Official Container Runtime documentation confirms beta support on all plans. Compose is local only. The standalone Next frontend reads its public API origin through an allowlisted runtime route to avoid build-time environment coupling. Inference images exclude training and raw exports. Public shared quota counters remain required. No execution/deployment is authorized; compatibility is source-level until operator validation.
