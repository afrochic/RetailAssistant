# Manual runbook

Use Python3.12 and Node22 from repository root. The current distribution dataset is included; no private original path is needed.

```bash
python3.12 -m venv .venv-mvp
source .venv-mvp/bin/activate
pip install -r requirements-dev.txt
python scripts/mvp/manage.py env --execute
python scripts/mvp/prepare.py ingest --source data/client_x_catalogue.json --currency KES --approved
python scripts/mvp/prepare.py index
python -m pytest -q
python -m ruff check --config apps/api/pyproject.toml apps/api scripts/mvp
(cd apps/web && npm ci && npm run typecheck && npm run lint && npm run build)
python scripts/mvp/audit_offline.py
docker compose config --quiet
docker compose build
docker compose up -d
```

Expected endpoints and private environment settings are in QUICKSTART.md and CONTAINERS.md. Use only bounded real Groq calls. Shared limiter failure is not a reason to disable public security controls. For an approved release use VERCEL_DEPLOYMENT.md; local scripts are dry-run by default unless --execute is supplied.

The relevance evaluator requires independently reviewed labels; the template is intentionally not valid ground truth. Academic report and evidence reproduction are in reports/final/ACADEMIC_DELIVERABLES.md. Historical Flipkart commands run only from legacy/flipkart and do not validate the current submission.
