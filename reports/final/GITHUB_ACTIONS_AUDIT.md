# GitHub Actions audit - 20 November 2026

## Verified repository and access

Repository: afrochic/RetailAssistant. Baseline: 7be14a9ce0bd041a9f7bade3931b3ffde269eedd, main. Git fetch succeeded. GitHub CLI is absent; authenticated Git credential-helper access was verified as afrochic without printing credentials. Public REST metadata and authenticated workflow dispatch were used. No production workflow was dispatched.

## Actual workflow execution

| Workflow | Actual outcome | Evidence |
|---|---|---|
| mvp-backend.yml | PASS at final source 7d46aea | https://github.com/afrochic/RetailAssistant/actions/runs/44630560678 |
| mvp-frontend.yml | PASS at final source 7d46aea; baseline lint failure repaired | https://github.com/afrochic/RetailAssistant/actions/runs/44630566673 |
| checks.yml (legacy) | PASS at old 23f528a only; does not validate Healthy U MVP | https://github.com/afrochic/RetailAssistant/actions/runs/44573313287 |
| mvp-docker.yml | PASS at final source 7d46aea | https://github.com/afrochic/RetailAssistant/actions/runs/44630571832 |
| mvp-evaluation.yml | BLOCKED: no reviewed human relevance labels | Requires research/mvp/queries.reviewed.json and approved artifacts |
| mvp-production-api.yml | UNVERIFIED, intentionally not dispatched | Manual dispatch, DEPLOY confirmation, repository variable and protected environment |
| mvp-production-web.yml | UNVERIFIED, intentionally not dispatched | Same explicit production gates |

Baseline MVP frontend run 44629843678, job 135933252565, failed npm run lint before the Link correction; baseline backend run 44629838451 passed. Failed historical run 44572713859, job 135731842612, failed at pytest collection; later 23f528a commit addressed manual HTTP smoke checks being collected during pytest. The newer historical success is not counted as MVP evidence. Logs/metadata are in ci/.

## Concrete correction and local checks

Node 22.17.0 was selected from existing nvm installation because default Homebrew Node 24 cannot load libsimdjson.26.dylib. Before correction frontend typecheck passed; lint rejected Chat.tsx's plain internal homepage anchor. ADR 0002 records replacing it with Next Link and using a named PostCSS export. After correction: typecheck PASS, lint PASS, Next 16.4.6 production build PASS. This correction is local until a new branch is published and validated. Do not call the failed baseline frontend run a pass.

Python 3.12 .venv-mvp: initial API 20 tests passed in 0.21 seconds; Ruff passed. After urgent-medical and budget-feature regressions, final 7d46aea API tests: 23 passed in 0.19 seconds.

## Workflow source audit

All seven YAML files parsed successfully with existing js-yaml (ci/workflow_syntax.json). MVP backend uses Python 3.12; frontend uses Node 22, npm ci and correct apps/web directory. API tests run under apps/api. Non-production workflows use contents:read. Production jobs have contents:read, exact DEPLOY confirmation, ENABLE_RETAILASSIST_PRODUCTION variable gate and retailassist-production environment. Runtime secrets are referenced only through GitHub secrets. The environment's reviewer protection must be configured in GitHub; its existence/configuration was not inferred from YAML. All workflows remain workflow_dispatch only. The Python 3.9 workflow is explicitly legacy, not the MVP pipeline.

Docker workflow builds both ordinary images and both Vercel Dockerfile variants. Evaluation uses an allowlisted query file path and requires explicit reviewed labels; it does not manufacture labels. Artifact absence causes honest failure rather than silently substituting legacy data. API production preflight currently checks products/lexical but deployment also needs manifest.json, which the inference loader validates.

## Local Docker evidence

Compose configuration validation PASS; both images built successfully. Disposable secretless containers were tested on random loopback ports and removed. Both health endpoints returned 200; API ready returned true; frontend runtime config resolved the actual audit API port. A catalogue query returned mode fallback_missing_key with three real Healthy U references and compliant KES prices. This proves factual fallback, not Groq generation. The first API image preceded the final urgent medical fix. A final rebuilt API image was then started without credentials and returned urgent_safety, no references and retrieval=not_invoked for severe headache with blurred vision; see ci/docker_final_medical.json. No existing running service was stopped or replaced.

## Outstanding actions

The reviewed fixes were published on a non-production branch and frontend/backend/Docker workflows all completed successfully against 7d46aea (see revision evidence below). Production redeployment remains separately controlled. Human-reviewed query labels are still required before retrieval-quality CI can produce Precision/Recall/MRR/NDCG.

## Published fix revision and new validation

Root published non-production branch final/healthyu-production-audit, commits fc44d8d and 7d46aea1dd6814044cb42ca8246b7df2cbd4cafc. Controlled CI was dispatched against the latter exact revision:

- Backend: PASS https://github.com/afrochic/RetailAssistant/actions/runs/44630560678
- Frontend: PASS https://github.com/afrochic/RetailAssistant/actions/runs/44630566673
- Docker: PASS https://github.com/afrochic/RetailAssistant/actions/runs/44630571832

Final API image after both fixes: sha256:311b831ed785626330d90edacbf7d98d3eef1abb9bbfb76cb3ff5cce5c01bffd. Isolated secretless runtime showed ready=true, correct budget prices and urgent_safety with no references. See ci/docker_final_budget_and_medical.json. Rice-cake results under the broad breakfast/healthy query meet price constraints but do not establish human-rated relevance quality. No Groq success is claimed.
