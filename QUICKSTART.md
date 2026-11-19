> Final audit update (20 November 2026): ingestion, fitting, local tests/builds, Docker probes, CI and an explicitly authorized production repair have now been executed. Both existing projects run tested source7d46aea. See reports/final/FINAL_HANDOFF.md for actual outcomes; earlier source-only/unexecuted statements below describe the prior preparation phase.

# Get the presentation MVP running

**All commands below are for you to execute. None were run by the agent.** Use the existing checkout `retailassist/`, not the enclosing Healthy U application's frontend. A live website still requires your manual deployment.

## 1. Environment (Python 3.12 and Node 22)

```bash
cd /Users/dianamusee/Desktop/HU-NutritionistsVA/retailassist
python3.12 -m venv .venv-mvp
source .venv-mvp/bin/activate
python -m pip install -r apps/api/requirements-dev.txt
python scripts/mvp/manage.py env --execute
```

If Python 3.12 is unavailable on macOS, install it yourself (`brew install python@3.12`), then repeat. Use Node 22 (`nvm install 22 && nvm use 22` if you use nvm). The local backend `.env` already contains the supplied key and is Git-ignored with restricted file permissions. **Rotate the chat-exposed key** and replace it privately before public use. Never put it in frontend settings or a command argument.

## 2. Prepare the real Healthy U catalogue and fast fitted baseline

```bash
python scripts/mvp/prepare.py ingest \
  --source ../rag_pipeline/data/Enhanced_Product_List.json \
  --currency KES --approved
python scripts/mvp/prepare.py index
```

Expected: allowlisted `products.json`, fitted `lexical.json` and integrity `manifest.json` under `apps/api/catalogue`. Accepted counts/rejected rows are printed by the actual execution. The original export is never changed. Do not add a made-up snapshot date.

## 3. Start backend and frontend (two terminals)

Terminal A, with the Python environment activated:

```bash
python scripts/mvp/manage.py serve --execute
```

Expected local endpoint: http://127.0.0.1:8001 . `/health` is liveness; `/ready` must return ready=true after artifact preparation; `/docs` is OpenAPI. The backend reads `apps/api/.env` locally. Local-only in-memory rate limiting is enabled; public Vercel forces shared controls.

Terminal B:

```bash
cd /Users/dianamusee/Desktop/HU-NutritionistsVA/retailassist/apps/web
npm install
npm run dev
```

Expected local frontend: http://localhost:3000 . `apps/web/.env.local` points to port 8001. Open it and ask “Find breakfast oats under KSh 1000”, then “under KSh 800”. Check record IDs and prices against the approved export. A quota/provider/key failure must display a transparent fallback, not a pretend generated success.

## 4. Verify before deploying

```bash
cd /Users/dianamusee/Desktop/HU-NutritionistsVA/retailassist
source .venv-mvp/bin/activate
python scripts/mvp/manage.py test --execute
python scripts/mvp/manage.py lint --execute
python scripts/mvp/manage.py web-build --execute
python scripts/mvp/manage.py smoke --execute
python scripts/mvp/manage.py preflight --execute
```

The smoke check can use real Groq quota. The frontend install creates the still-pending lockfile; review and commit it. Perform the manual checks in `apps/web/FRONTEND_ACCEPTANCE.md`. Do not claim tests/builds passed until these actually finish.

## 5. Get it live

Follow **VERCEL_DEPLOYMENT.md**: two projects, same repository, roots `apps/api` and `apps/web`; Container preset, PORT=8080 on both projects. Configure the Groq key and shared Redis counters on the backend, actual frontend origin for CORS, and backend origin on the frontend. All cloud setup and deployment are manual. No Render/Railway or paid OpenAI configuration is used.

**Fastest route:** lexical MVP first. Optional semantic preparation and academic evaluation come after the working chat demo.

## Run both apps with Docker

After offline artifact preparation and npm install, follow [CONTAINERS.md](CONTAINERS.md). The root docker-compose.yml builds both apps; http://localhost:3000 serves chat and port 8001 serves the API. Vercel uses each app’s Dockerfile.vercel independently. No Docker commands have been executed.
