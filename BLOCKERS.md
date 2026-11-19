# MVP blockers and pending actions

## Available by read-only evidence

- Existing canonical repository afrochic/RetailAssistant; history/remote preserved locally.
- Real Healthy U export: 5,512 existing records, schema/hash in the Phase 0 audit.
- User explicitly approved public presentation-MVP product use and confirmed KES RRP.
- Supplied Groq key stored only in ignored local backend .env, owner-only permissions. It has NOT been validated or called. Rotate it because it was pasted in chat.

## Required before a working local MVP

1. **PENDING USER EXECUTION:** Python 3.12 / Node 22 environment and pinned package installation. No dependency installation was performed by the agent.
2. **PENDING USER EXECUTION:** approved ingestion and fitted lexical index. Catalogue directory initially contains no generated product/index files. Backend must return unready rather than silently using other products.
3. **PENDING USER EXECUTION:** npm install, reviewed lockfile, backend tests, frontend type/lint/build checks and browser acceptance.
4. **UNVERIFIED:** Groq key validity, model access and actual account quota. The fallback path is implemented, not tested here.

## Required before live public hosting

- User-created/configured two Vercel projects with correct Root Directories and actual project/org IDs.
- Backend server env, rotated Groq key, shared Redis REST quota counters, stable secret salt, actual CORS origin.
- Frontend runtime API_BASE_URL set to the actual backend production origin; PORT=8080 set on both Container projects.
- Public-readiness, quota, medical-safety, CORS and browser smoke checks by the student.
- No public MVP URL is known or claimed. No cloud resources, environment variables or deployments were created by the agent.

## Research work after the demo

- Optional offline semantic fitting; no semantic artifact or performance claimed yet.
- Human-reviewed dev/test relevance data and generation/safety assessment; no invented ground truth or scores.
- Docker reproduction and all six manual workflow validations.
- Complete reviewed report, charts, notebook outputs and presentation with actual results. Current academic materials are scaffolding, not a measured final submission.

The original source lacks live inventory and structured brand/ingredients/allergen/verified-label fields. This is a real data limitation, not a credential problem. The system abstains when a hard constraint depends on absent evidence. A refreshed approved export with these fields and source timestamp is needed to expand capability.

Container implementation is source-only: generate the lockfile/catalogue artifacts and manually verify both images, health endpoints and resource limits using CONTAINERS.md. Vercel Container beta project availability and deployments are unverified.
