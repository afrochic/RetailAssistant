# RetailAssist — Client X / Groq presentation MVP

**Status: IMPLEMENTATION DRAFT; results PENDING EXECUTION.**

Admission 109419. DSA 8401 Applied Machine Learning. This draft does not reuse measured Flipkart or local SmolLM results as Client X/Groq evidence.

## Problem and source

Anonymous conversational retail discovery over an approved Client X export. The product is an independent student project, not an official store or medical practitioner. Read-only source audit observed 5,512 existing entries with SKU, ID, Name, Description, Categories, Images, RRP and Permalink. The user confirmed MVP-use permission and KES RRP. Current stock, structured ingredients/brands/labels and source-export date are absent. Actual accepted count after cleaning: **PENDING USER INGESTION**.

## Architecture and justification

Two Vercel projects from one existing repository: Next.js frontend and native FastAPI backend. Lightweight fitted TF-IDF indexes for the fastest MVP. Optional offline MiniLM teacher vectors with PCA and a fitted lexical-to-semantic query projection allow semantic/hybrid experiments without a transformer in the serverless runtime. This is an approximation and must not be reported as native MiniLM query encoding. RRF combines ranks when semantic artifacts are present. Hosted Groq model: openai/gpt-oss-120b, environment-configured. No supervised reranker without reliable labels; no account database or checkout.

## Safety and grounding

Hard price/category constraints and abstention for missing ingredient/brand/stock facts. Medical symptom/treatment requests are handled before retrieval/Groq; urgent warning signs produce urgent-care guidance. Marketing claims are excluded from generation evidence. Structured citations, numeric/vocabulary/medical checks and safe fact rendering constrain output. These checks are heuristic, not proof of clinical validity or semantic entailment.

## Experiments — PENDING EXECUTION

| Experiment | P@K | R@K | MRR | NDCG | Constraint satisfaction | ID grounding | Unsupported claims | Latency |
|---|---|---|---|---|---|---|---|---|
| A: fitted lexical baseline | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | N/A | PENDING |
| B: projected semantic | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | N/A | PENDING |
| C: hybrid + constraints | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | N/A | PENDING |
| D: hybrid + Groq explanations | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | HUMAN REVIEW PENDING | PENDING |

Protocol: collect independently human-reviewed queries and IDs; separate development from held-out test queries; freeze transformations/model revision/fusion before measuring test performance. Report query counts, unknown/unanswerable cases, confidence intervals where defensible, error analysis and actual fallback/429 rates. ID existence is not proof of product freshness, suitability or clinical efficacy. Human unsupported-claim review must be separate from automatic rejection rates.

## Deployment and verification

Configuration supplied, not built/deployed by the agent. Node 22 / Next.js; Python 3.12 / FastAPI; Vercel project roots apps/web and apps/api. Shared ephemeral Redis rate/quota counters are required for public deployment. Secrets server-side; no full prompt/customer logging. API calls bounded by input/output limits, conservative byte-based quota reservations and provider timeouts/retry rules. Vercel deployment protection/CORS/env/configuration require manual checks. See VERCEL_DEPLOYMENT.md.

## Limitations and future work

Snapshot freshness; absent structured allergen/ingredient fields; conservative false-positive safety checks; approximate semantic query projection; limited deterministic follow-ups; no model execution or UI verification performed in this rebuild; no live production URLs. Benchmark sample sizes, results, failures, screenshots and cloud costs remain PENDING until student execution.

## References

- Local read-only audit: reports/mvp/PHASE_0_AUDIT.md.
- Vercel FastAPI: https://vercel.com/docs/frameworks/backend/fastapi
- Vercel Python: https://vercel.com/docs/functions/runtimes/python
- Groq structured output: https://console.groq.com/docs/structured-outputs
- Groq model and quotas: https://console.groq.com/docs/model/openai/gpt-oss-120b and https://console.groq.com/docs/rate-limits
