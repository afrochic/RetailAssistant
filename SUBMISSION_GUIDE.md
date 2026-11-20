# Submission guide — start here

DSA 8401 Applied Machine Learning · Admission 109419 · Client X.

| Required item | Canonical location | What to inspect |
| --- | --- | --- |
| README | [README.md](README.md) | Problem, architecture, methods, setup and reproduction |
| AI disclosure | [AI_USE.md](AI_USE.md) | Exact disclosure supplied by the student |
| Data pipeline | [prepare.py](scripts/mvp/prepare.py), [distribution source](data/client_x_catalogue.json), [data card](DATA_CARD.md) | Scripted preprocessing and reproducible source |
| Model fitting and artifacts | [prepare.py index](scripts/mvp/prepare.py), [catalogue folder](apps/api/catalogue/), [methodology](docs/METHODOLOGY.md) | Fitted TF-IDF products/index/checksum manifest; not GPT-OSS fine-tuning |
| Docker | [root Dockerfile](Dockerfile), [Compose](docker-compose.yml), [API image](apps/api/Dockerfile), [web image](apps/web/Dockerfile) | Current API and frontend runtime images |
| API | [FastAPI entry point](apps/api/app.py), [tests](apps/api/tests/), [run instructions](QUICKSTART.md) | Prediction, validation, safety, health and readiness |
| Final report or slides | **[One-page PDF report](reports/final/RETAILASSIST_FINAL_REPORT.pdf)**, [editable source](reports/final/RETAILASSIST_FINAL_REPORT.md), [presentation](reports/final/PRESENTATION.md) | Problem, justification, actual results and limits |

The presentation is complete editable slide content; no PPTX export is claimed. The report PDF must contain exactly one page. Detailed evidence is supporting material, not additional report pages.

## Supporting material

- [Current validation](reports/final/CLEANUP_VALIDATION.md)
- [Evaluation and real figures](reports/final/evaluation/EVALUATION_SUMMARY.md)
- [Requirement-by-requirement compliance](PROJECT_COMPLIANCE.md)
- [Client-name redaction and history limits](docs/PRIVACY.md)
- [Current notebook](research/mvp/RetailAssist_MVP_walkthrough.ipynb)

**Historical files:** `legacy/` is not the current application. Older raw screenshots/audit payloads that identified the client were withdrawn from the current public snapshot; originals are privately retained. Historical tests and deployment outcomes are not presented as a release of the new Client X code. Independent relevance annotation and semantic comparison remain outstanding.
