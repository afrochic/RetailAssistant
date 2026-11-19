# Current MVP compliance map — implementation is not verification

| User/project requirement | Concrete source | Evidence/status |
|---|---|---|
| Existing repository/history | Independent retailassist checkout; proposed manual branch | Read-only metadata confirms afrochic/RetailAssistant; no Git mutations/pushes by agent |
| Real Healthy U source | reports/mvp/PHASE_0_AUDIT.md; scripts/mvp/prepare.py | 5,512 records observed; permission/KES user-confirmed; extraction PENDING |
| Reproducible ingestion/cleaning | prepare.py ingest | Allowlisted, read-only approved local export; hashes and rejected counts generated only on manual run |
| Genuine fitted baseline/artifacts | prepare.py index; apps/api/retail_mvp/catalogue.py | TF-IDF fit/serialization implemented; no fitting run |
| Semantic/hybrid | optional prepare.py index --semantic | Offline teacher embeddings + approximate fitted query projection, RRF; no artifact/performance claimed |
| Hard constraints / missing evidence | models.py, safety.py, catalogue.py | KES budget and explicit preferences; unknown ingredients/labels/stock do not pass hard filters; untested |
| Groq GPT RAG | retail_mvp/groq.py | Configurable openai/gpt-oss-120b; strict IDs and record-specific supported explanation choices; no actual API calls |
| Medical/abuse controls | safety.py, limits.py, app.py | Conservative abstention, input/body limits, shared quota counters, provider limits/fallback; tests written but unexecuted |
| ChatGPT-style frontend | apps/web | Anonymous session-local chat, examples, Markdown, new chat, loading/error/retry/preferences/references; no storefront/auth/account DB/cart/checkout |
| Vercel frontend + backend | apps/web/vercel.json; apps/api/vercel.json | Two Container roots configured, automatic Git deploys disabled; no projects/deployments created |
| Docker | apps/api/Dockerfile; apps/web/Dockerfile; both Dockerfile.vercel files; docker-compose.yml | Both multi-stage images and local two-service Compose authored; not built/run |
| Evaluation | scripts/mvp/evaluate.py; research/mvp/queries.template.json | Human-reviewed labels required; no new measured results/claims rates invented |
| README / architecture / commands | README.md, QUICKSTART.md, MANUAL_RUNBOOK.md, VERCEL_DEPLOYMENT.md | Written, unexecuted manual guidance; actual values/URLs must come from user account |
| AI-use and provenance | AI_USE.md, DATA_CARD.md | Updated for this rebuild; old data/results explicitly legacy |
| Notebook/report/slides | research/mvp | Unexecuted notebook, PENDING report draft and outline; final measured PDF/deck follow MVP demonstration |
| Manual workflows | .github/workflows/mvp-*.yml | Validation manual-only; production additionally locked by explicit enable/confirmation/secrets/environment |

## Honest completion state

Phase 0 read-only audit completed. Phases 1–3 source/configuration implemented, **UNTESTED / UNDEPLOYED**. Phase 4 research scaffolding only. Source/key access is available locally; operator execution, actual cloud setup and quota validation remain required. See BLOCKERS.md. The old final PDF/test results are not a final submission for this revised Healthy U/Groq implementation.
