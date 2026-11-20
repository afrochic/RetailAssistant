# Current Client X cleanup validation

20 November 2026. These outcomes concern the current name-redacted source, not a new cloud release.

| Check | Actual outcome |
| --- | --- |
| API/privacy regression tests | PASS:25 tests,0.19s |
| Ruff (current app/scripts configuration) | PASS |
| Frontend Node22 typecheck | PASS |
| Frontend ESLint | PASS |
| Frontend Next standalone build | PASS |
| Local API readiness | PASS:ready=true |
| Local API response | PASS:fallback_missing_key,3real references,all URLs null,CX citations,budget<=KES1000 |
| Distribution and serving counts | PASS:5512 records each |
| Current index fit/repeat | PASS:12000features, byte-identical lexical refit |
| Current source/artifact checksums | PASS:source/manifest/products/lexical align |
| Current warm retrieval diagnostics | PASS:260calls,mean1.134ms,p952.265ms,640repeated references,zero exercised violations,5/5 expected abstentions |
| Relevance template guard | PASS:intentionally rejects unreviewed labels |
| Current client-alias/domain text scan | PASS:zero matches in scanned public UTF-8 files |
| Final PDF | PASS:exactly1page; rendered and visually checked |
| Current Docker builds | PASS:both Compose images and repository-root API image built |

Local HTTP evidence is in cleanup_local_api.json. Actual data/CSV/plots are in evaluation/. The private key was deliberately unset for the local response probe: no Groq call or production deployment occurred. Historical CI/provider successes are not relabelled as tests of the new Client X snapshot.

Original identifying screenshots, payloads and obsolete raw stdout duplicates were withdrawn; originals were archived privately where needed. The client name/domain is absent from the current submission text, not erased from Git/CI/cloud history. Product text/IDs may remain externally reidentifiable.

Commands: python -m pytest -q; python -m ruff check --config apps/api/pyproject.toml apps/api scripts/mvp; npm run typecheck/lint/build under apps/web; prepare.py ingest/index; audit_offline.py; docker compose build.

## GitHub verification

Current Client X application source5436ed8 passed all three manual workflows:
- Backend: https://github.com/afrochic/RetailAssistant/actions/runs/44692431692
- Frontend: https://github.com/afrochic/RetailAssistant/actions/runs/44692435830
- Docker: https://github.com/afrochic/RetailAssistant/actions/runs/44692439969

PR#3 https://github.com/afrochic/RetailAssistant/pull/3 is ready for review. Later evidence-only commits do not change tested application code. No merge or deployment is implied by these results.
