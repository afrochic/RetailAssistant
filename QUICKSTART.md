# Quickstart — current Client X application

Run these commands from the repository root. Requires Python 3.12 and Node 22. The distributable source is included; do not use a private client-workspace path.

```bash
python3.12 -m venv .venv-mvp
source .venv-mvp/bin/activate
pip install -r requirements-dev.txt
python scripts/mvp/manage.py env --execute
python scripts/mvp/prepare.py ingest --source data/client_x_catalogue.json --currency KES --approved
python scripts/mvp/prepare.py index
python -m pytest -q
```

Expected: 5,512 products retained, fitted TF-IDF artifacts under apps/api/catalogue, and passing tests. The environment command preserves existing private files. Configure a private Groq key only in apps/api/.env if actual generation is needed; missing credentials transparently use catalogue fallback. No provider credentials belong in the frontend.

Terminal A:

```bash
source .venv-mvp/bin/activate
python scripts/mvp/manage.py serve --execute
```

Terminal B:

```bash
cd apps/web
npm ci
npm run dev
```

Open http://localhost:3000. API http://127.0.0.1:8001/ready should report ready=true. The frontend reads the public API origin from its server runtime configuration; the local environment template supplies API_BASE_URL. Ask for oats under KES1000, narrow the budget and inspect CX record IDs. A dietary exclusion cannot be verified from absent ingredient metadata; no medical recommendation should appear.

For both containers, use [CONTAINERS.md](CONTAINERS.md). For actual results and the one-page report, start at [SUBMISSION_GUIDE.md](SUBMISSION_GUIDE.md). New Client X content is not live until an explicitly approved release.
