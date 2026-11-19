# RetailAssist final handoff — 20 November 2026

## A. Overall status

| Area | Status | Evidence and limit |
| --- | --- | --- |
| Production frontend | PASS | Public page/config/health HTTP200; real browser grounded answer observed; both projects source7d46aea |
| Production backend | PASS | Public ready=true; all5 controlled chat cases HTTP200 |
| Healthy U catalogue | PASS | 5512 approved records, zero rejected, manifest/integrity checked |
| Groq generation | PASS | Two actual public recommendation cases mode=groq_grounded, plus four controlled local provider successes |
| Product grounding | PASS | Six repeated public reference occurrences match source fields and budgets; only3unique records/small sample |
| Medical safety | PASS | Exact requested severe-headache/blurred-vision case urgent_safety with no products; no broad clinical-validation claim |
| Docker | PASS | Both images built locally and in CI; disposable health/readiness/budget/safety probes passed |
| GitHub Actions | PASS | Backend/frontend/Docker completed successfully at exact7d46aea; ranking workflow separately BLOCKED |
| ML pipeline | PASS | Approved ingestion, preprocessing, 12000-feature TF-IDF fitting, deterministic serialized inference/refit executed |
| ML evaluation | BLOCKED | Actual diagnostics/data quality measured; ranking metrics require independent human labels; semantic comparison pending |
| Academic report | PASS | Editable source, visually checked PDF and real figures |
| Presentation | PASS | Complete12-slide editable content/notes; PPTX export unavailable |

**Recommendation: READY WITH LIMITATIONS** for a scoped presentation. This is not evidence of production load resilience, clinical suitability or fully completed proposal experiments.

## B. Public production verification

- Frontend: https://retail-assistant-tau.vercel.app/
- Backend: https://retail-assist-api.vercel.app/health
- Readiness: https://retail-assist-api.vercel.app/ready

Initial failures were real: frontend config503, missing catalogue, missing quota salt/config and disallowed frontend CORS. They were retained in production/http_baseline.json, chat_cases.json and cors.json. After explicit user authorization, existing Vercel projects were configured and tested source7d46aea was rebuilt/promoted with production settings. No project replacement or main merge occurred.

Final API current deployment: dpl_8VhQ6kgRWwAWbgtN4AUctsGHoTK3. Frontend: dpl_Cmwahs6c9mKX89EXM8hfuDtpcvjx. Dashboard source evidence and screenshots are under production/.

Final public evidence: production/production_readiness_postrelease.json and production_chat_postrelease.json. Both health/config/ready200; count5512/KES/fitted_tfidf; trusted CORS200, untrusted400. A/E used actual Groq; B clarified unverified sugar suitability; C advised urgent care without supplements; D abstained. Browser rendered four real oat references and KES prices in production/browser_grounded_chat.png. Mobile/NewChat/loading/accessibility/console sweeps remain UNVERIFIED.

## C. Actual GitHub Actions

All below validate source7d46aea1dd6814044cb42ca8246b7df2cbd4cafc:

| Workflow | Outcome | Run |
| --- | --- | --- |
| MVP backend | PASS | https://github.com/afrochic/RetailAssistant/actions/runs/44630560678 |
| MVP frontend | PASS | https://github.com/afrochic/RetailAssistant/actions/runs/44630566673 |
| MVP Docker | PASS | https://github.com/afrochic/RetailAssistant/actions/runs/44630571832 |
| Reviewed relevance evaluation | BLOCKED | No independent labels; not disguised as a successful run |
| Legacy checks | PASS at older source only | Not Healthy U evidence; full audit distinguishes historical failures |
| Production Actions workflows | UNVERIFIED | Not triggered; deployment was through authorized existing Vercel dashboard |

Backend final23tests and Ruff passed. Frontend typecheck/lint/build passed. Fixes address Next Link lint, named PostCSS export, urgent visual symptoms and numeric budget contamination. Production workflow preflight now requires manifest.json. See GITHUB_ACTIONS_AUDIT.md for failed baseline job IDs, logs and final runs.

## D. Genuine evaluation

- 5512 records; no missing/nonpositive prices or duplicate IDs/names; median KES1599.
- TF-IDF12000features; identical lexical bytes on refit.
- 13 scripted diagnostic cases ×20 repeats =260 warm retrievals: mean1.332ms, p952.528ms, excluding startup/network/Groq/UI.
- 640 repeated reference occurrences (32unique IDs), zero invalid IDs/exercised hard-constraint violations;5/5 expected abstention cases.
- Two public Groq recommendation requests: six repeated references, three unique products, exact field/budget validation; mean measured HTTP latency1.7115s for these two examples.
- Precision@K, Recall@K, MRR and NDCG are not available. Human relevance annotation and semantic/hybrid fitted artifacts are missing; diagnostic success is not relevance accuracy.

Raw CSV/JSON, four actual-data charts, validation scripts and interpretation are in evaluation/. No synthetic values were inserted into charts.

## E. Submission files

- README.md, AI_USE.md, PROJECT_COMPLIANCE.md, DATA_CARD.md
- apps/api and apps/web: tested service/frontend, containers and Vercel configuration
- apps/api/catalogue/products.json, lexical.json, manifest.json: approved compact inference artifacts
- scripts/mvp/prepare.py, audit_offline.py, audit_production_evidence.py, evaluate.py
- reports/final/RETAILASSIST_FINAL_REPORT.md and RETAILASSIST_FINAL_REPORT.pdf
- reports/final/PRESENTATION.md:12editable slides and speaker notes
- reports/final/ACADEMIC_DELIVERABLES.md, render_report.py and academic-requirements.txt
- research/mvp notebook/template: reproducible research scaffolding; not fabricated completed ranking experiments

## F. Repository and release

Origin is https://github.com/afrochic/RetailAssistant.git. History and parent HU application preserved. Safe review branch: final/healthyu-production-audit. Application commits fc44d8d (approved artifacts and regressions) and7d46aea (budget feature fix) were published. Additional documentation/evidence commit is recorded by git log. CI and both deployed apps correspond to7d46aea, even if the branch later contains documentation-only updates.

Legacy Flipkart material remains labelled historical; no old metric was reused. No force-push, main rewrite or unapproved merge occurred. See REPOSITORY_CLEANUP.md. Use the review branch/PR for final academic review; do not mistake old main PDFs for the new report.

## G. Remaining actions

1. Independently annotate/review Healthy U relevance queries and evaluate held-out retrieval ranking. Optional semantic/hybrid comparison remains pending.
2. Verify/revoke the chat-exposed Groq key if not already rotated; rotation is UNVERIFIED. Enter credentials privately only.
3. Verify GitHub production environment reviewer protection: API lookup returned404/not configured or not visible. Manual YAML gates are present but are not proof of actual reviewer protection.
4. Perform mobile/accessibility/load tests and obtain verified/current catalogue metadata before expanding scope.
5. Review/merge the submission branch normally when satisfied. No additional deployment is needed merely for documentation changes.

## H. Commands for a quick demonstration

```bash
curl --fail https://retail-assist-api.vercel.app/ready
curl --fail https://retail-assistant-tau.vercel.app/api/runtime-config
# Controlled request: consumes quota when a Groq match is generated.
curl --fail-with-body https://retail-assist-api.vercel.app/api/chat \
  -H 'Content-Type: application/json' \
  --data '{"message":"Find breakfast oats under KSh 1000","history":[],"preferences":{"currency":"KES"},"k":3}'
```

Open the public frontend and demonstrate oats/KES budget, a narrower follow-up, an unknown dietary exclusion and medical refusal. Check the mode badge: fallback is not a successful Groq generation. Full local/Docker/deployment commands remain in QUICKSTART.md, CONTAINERS.md and VERCEL_DEPLOYMENT.md. Keep provider calls bounded to the presentation need.
