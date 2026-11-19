# Initial public production verification — 20 November 2026 (Africa/Nairobi)

No authentication cookies or deployment bypass tokens were used. Direct HTTPS requests succeeded where noted. Raw responses, status codes and latencies are in http_baseline.json, chat_cases.json, alias_validation.json and cors.json. Vercel edge request IDs are not source commit evidence.

| Target | HTTP | Observation | Status |
| --- | --- | --- | --- |
| https://retail-assistant-tau.vercel.app/ | 200 | HTML delivered | PASS for HTTP delivery only |
| frontend /health | 200 | status ok, service retailassist-web | PASS for liveness |
| frontend /api/runtime-config | 503 | empty apiBaseUrl; missing/invalid API_BASE_URL | FAIL |
| https://retail-assist-api.vercel.app/health | 200 | alive, retailassist-mvp | PASS for liveness |
| backend /ready | 503 | catalogue_or_index_missing; catalogue_available=false | FAIL |
| backend /api/system-info | 200 | count 0, KES, retrieval unavailable, configured model openai/gpt-oss-120b | FAIL for application readiness |
| backend /openapi.json | 200 | valid route/schema document available | PASS |
| /api/recommend with invalid empty body | 422 | documented validation error | PASS for route/schema validation |
| OPTIONS /api/chat, real frontend origin | 400 | Disallowed CORS origin, no allow-origin header | FAIL |
| OPTIONS /api/chat, untrusted origin | 400 | Disallowed CORS origin | PASS for rejecting untrusted origin |

All five controlled chat cases A–E returned HTTP503, code shared_limiter_not_configured and Retry-After60. No case reached catalogue retrieval or Groq. This establishes fail-closed behavior, not successful retail recommendations, successful safety advice, or working rate-limit thresholds. Provider request count attributable to these public probes is zero because limiter enforcement precedes provider invocation.

## Exact blockers and corrections

1. Set frontend project Production API_BASE_URL=https://retail-assist-api.vercel.app. Runtime config must return 200 with that public origin.
2. Include apps/api/catalogue/products.json, lexical.json and manifest.json in the backend build context. Approved artifacts were generated locally and published on the nonproduction audit branch. Production should load 5512 records and report fitted_tfidf, not substitute another catalogue.
3. Set backend Production REQUIRE_SHARED_LIMITER=true, APP_ENV=production, valid UPSTASH_REDIS_REST_URL, UPSTASH_REDIS_REST_TOKEN and a private RATE_LIMIT_SALT. Do not disable public protections as a workaround.
4. Set backend ALLOWED_ORIGINS=https://retail-assistant-tau.vercel.app. Preserve exact origin matching and rejection of unrelated origins.
5. Keep PORT=8080 on both Container projects. Review the safety and budget-token fixes before an approved release. Redeployment is required for source/artifact fixes and environment settings to take effect.

The existing projects are retained. No production settings were modified and no rollout was performed. Read VERCEL_DEPLOYMENT.md for manual steps; the audit branch is not automatically deployed.

## Browser and provenance limits

Browser inventory worked, but attempts to create an audit tab failed in the automation integration before a page opened. No substitute raw browser protocol was used. Desktop rendering, actual browser message submission, New Chat, loading animation, product-link interaction, mobile layout and browser-console behavior remain UNVERIFIED. The HTTP CORS failure independently proves the supplied frontend origin cannot call this API under the observed configuration.

Production source Git revision is UNVERIFIED: public headers do not expose it, and no authenticated Vercel deployment metadata was used. No screenshot is claimed.

## Local integration, separately verified

local_chat_cases.json records the initial five actual ASGI requests using the full real catalogue and the configured Groq provider. A and E returned groq_grounded, B clarification, C urgent_safety and D no_matches. Inspection found poor relevance in the initial budget query: price text 2000 polluted lexical ranking and matched supplement strength. The regression was reproduced and corrected by removing parsed budget clauses from retrieval text while preserving standalone product-strength numbers.

local_chat_postfix.json records two additional actual Groq calls after correction. Both A (KES2000) and E (KES800) returned three actual rice-cake records at KES499 each. This is observed grounding and budget compliance on two examples, not human-rated relevance performance. Four total local provider calls were made; no uncontrolled retry loop was used. Backend final test output records 23 passing tests. The local integration cannot establish current public availability.

## Authorized repair and final verification — supersedes the initial failures above

The user explicitly authorized updating the two existing Vercel projects and redeploying the tested revision. Using the signed-in dashboard, the frontend API_BASE_URL was set to the actual API origin, API ALLOWED_ORIGINS was set to the frontend origin, and a private random RATE_LIMIT_SALT was added. Existing Redis variables were retained without revealing their values. Vercel identity verification was completed by the user. Preview builds were promoted through complete production-environment rebuilds; no new project or main merge was needed.

Both current production deployments show source7d46aea1dd6814044cb42ca8246b7df2cbd4cafc:
- API: https://vercel.com/dianamusee-5113/retail-assist-api/8VhQ6kgRWwAWbgtN4AUctsGHoTK3
- Web: https://vercel.com/dianamusee-5113/retail-assistant/Cmwahs6c9mKX89EXM8hfuDtpcvjx

Authenticated dashboard source/current/domain evidence is saved as api_production_deployment.png/.txt and web_production_deployment.png/.txt. Public HTTP evidence is independently unauthenticated. production_readiness_postrelease.json records both health200, API ready=true, count5512/fitted_tfidf/KES, frontend runtime-config200 with correct origin, trusted CORS200 and untrusted CORS400.

production_chat_postrelease.json contains five actual public HTTP200 responses: A budget=groq_grounded with3references; B suitability=clarification/no references; C medical=urgent_safety/no references; D impossible combination=no_matches/no references; E follow-up=groq_grounded with3references. Independent artifact checks found all6 repeated reference occurrences (3unique products) match catalogue facts and budget499KES<=2000/800. This is a small smoke sample, not general relevance or safety accuracy.

The live public browser was observed rendering a Groq-grounded breakfast-oats response with four actual records, KES799/195/390/449 and retailer links. browser_grounded_chat.png is a verified screenshot of that visible response. Browser interaction was performed by the user and observed by the agent; no automated mobile/NewChat/loading/keyboard/console sweep is claimed. The earlier browser automation integration failed, but native Chrome inspection later worked.

FINAL: READY WITH LIMITATIONS for the scoped presentation. Formal relevance evaluation and optional semantic/hybrid experiments remain blocked/pending, as documented separately. Previously exposed Groq key rotation remains UNVERIFIED.
