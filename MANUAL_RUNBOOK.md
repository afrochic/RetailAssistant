> Final audit update (20 November 2026): ingestion, fitting, local tests/builds, Docker probes, CI and an explicitly authorized production repair have now been executed. Both existing projects run tested source7d46aea. See reports/final/FINAL_HANDOFF.md for actual outcomes; earlier source-only/unexecuted statements below describe the prior preparation phase.

> Container architecture update: both app images and the root two-service Compose stack are now defined. Use [CONTAINERS.md](CONTAINERS.md) locally and [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md) for the current Container-runtime deployment instructions, which supersede earlier native-framework hosting steps below. Builds and deployments remain unexecuted.

# Manual execution order

These commands are intentionally **unexecuted** by the agent. `manage.py` defaults to dry run; `--execute` is an explicit operator action. Each Python script exposes `--help`.

1. Read `reports/mvp/PHASE_0_AUDIT.md`, the ADR and `BLOCKERS.md`. Use the independent `retailassist` checkout; the enclosing Healthy U application is not the target.
2. Create the proposed branch yourself: `git switch -c mvp/healthyu-groq-vercel`. Never reset or force-push.
3. Prepare Python 3.12 and Node 22. Create `.venv-mvp`, install `apps/api/requirements-dev.txt`, and preserve the ignored backend `.env` (`manage.py env --execute` never overwrites it). Rotate the chat-exposed key privately.
4. Run `prepare.py ingest --source ../rag_pipeline/data/Enhanced_Product_List.json --currency KES --approved`; review accepted/rejected counts, provenance and product-only fields.
5. Run `prepare.py index`. Lexical retrieval is the MVP. Do not claim semantic retrieval before building the optional artifact.
6. Optional later: `pip install -r apps/api/requirements-offline.txt`, then `python scripts/mvp/prepare.py index --semantic --model-revision 1110a243fdf4706b3f48f1d95db1a4f5529b4d41`. This downloads/fits offline models only when you run it. The runtime query projection is approximate; evaluate it separately.
7. Start API: `python scripts/mvp/manage.py serve --execute`. Inspect `/ready` and `/docs` at port 8001.
8. Start frontend: `python scripts/mvp/manage.py web-install --execute`, then `python scripts/mvp/manage.py web-dev --execute` in another terminal. Complete `apps/web/FRONTEND_ACCEPTANCE.md`.
9. Run tests and static/build checks: `manage.py test --execute`, `manage.py lint --execute`, `manage.py web-build --execute`. These are new Healthy U/Groq tests; previous legacy passes do not count.
10. Run the actual local API smoke check: `python scripts/mvp/manage.py smoke --execute`. This can consume real Groq quota.
11. Run `python scripts/mvp/manage.py preflight --execute`. Review and commit the generated npm lockfile and approved inference artifacts manually as shown in VERCEL_DEPLOYMENT.md.
12. Configure both Vercel projects, server-only Groq key, shared Redis counters, salt, CORS and frontend backend-origin setting. No accounts/user database needed. Never enable automatic Git production releases.
13. Follow manual production confirmation/commands in VERCEL_DEPLOYMENT.md. Test actual public origins yourself before calling the MVP live.
14. After the MVP demo, reproduce Docker: `manage.py docker-build --execute`, `manage.py compose-up --execute`, smoke, then `manage.py compose-down --execute`. These are not Vercel deployment commands.
15. Create independently reviewed relevance labels from the real approved snapshot, saving `research/mvp/queries.reviewed.json`. Do not relabel the example template as measured ground truth.
16. Run `python scripts/mvp/evaluate.py --queries research/mvp/queries.reviewed.json --confirm-human-labels`. Optional `--include-groq --api-url <actual origin>` makes real bounded provider requests. Respect quotas and document fallbacks, actual sample sizes and missing semantic runs.
17. Run `python scripts/mvp/report.py --results reports/mvp/results --output reports/mvp/results/evidence.html`. Review actual results, manually annotate unsupported claims, complete report/slides and export the reviewed report to PDF. All unrun sections stay PENDING EXECUTION.

## Workflow controls

All new validation workflows are `workflow_dispatch` only. Production workflows additionally require the repository variable `ENABLE_RETAILASSIST_PRODUCTION=true`, exact `DEPLOY` confirmation, actual project IDs/token secrets, and a manually configured protected GitHub environment `retailassist-production`. Leave the enable variable unset until you have reviewed these controls. No workflow is triggered by this local implementation work.

## Exact lifecycle help

```bash
python scripts/mvp/prepare.py --help
python scripts/mvp/manage.py --help
python scripts/mvp/evaluate.py --help
python scripts/mvp/report.py --help
```

For live deployment, manual project creation/environment setup is essential; an app source tree alone is not a hosted service.
