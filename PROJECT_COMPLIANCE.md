# DSA 8401 submission compliance — Client X

Official capstone checklist and the student's instructions are mapped below. The final report is exactly one page. File presence is distinguished from execution evidence.

| Required item | Location | Evidence/status |
| --- | --- | --- |
| README overview/setup/architecture/reproduction | README.md; SUBMISSION_GUIDE.md; QUICKSTART.md | PASS: linked architecture and reproducible public-source commands |
| AI disclosure | AI_USE.md | PASS: exact text supplied by the student |
| Scripted pipeline | scripts/mvp/export_client_x.py; prepare.py; data/client_x_catalogue.json | PASS: approved distribution source ingested;5512 retained |
| Model fitting/artifacts | prepare.py index; apps/api/catalogue/products.json, lexical.json, manifest.json | PASS:12000-feature TF-IDF fitted with integrity checks; no GPT-OSS fine-tuning claim |
| Docker and Compose | Dockerfile; docker-compose.yml; apps/api and apps/web Dockerfiles | See CLEANUP_VALIDATION.md for current build outcome; legacy config isolated |
| API service | apps/api/app.py; apps/api/tests | PASS: current API tests exercised; Client X URL-redaction contract enforced |
| Final report or slides | reports/final/RETAILASSIST_FINAL_REPORT.pdf; PRESENTATION.md | PASS: one-page PDF verified, editable report and12-slide content included |

## Research and operational limitations

Current diagnostic measurements are real but not relevance ground truth. Precision/Recall/MRR/NDCG are BLOCKED pending independently reviewed Client X labels. Semantic/hybrid execution is PENDING. The original proposal's conversational baseline, grounded LLM, constraints and API/Docker are implemented; full semantic/ranking experiments remain incomplete.

Historical live and CI checks at7d46aea remain historical. New Client X changes are not deployed and require a separately approved release. Current cleanup validation, privacy scanning, artifact checks and frontend/build outcomes are recorded in reports/final/CLEANUP_VALIDATION.md. No history rewrite is claimed.
