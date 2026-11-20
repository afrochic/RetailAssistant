# RetailAssist: Client X Catalogue-Grounded Recommendations

**DSA 8401 - Applied Machine Learning | MSc Data Science & Analytics | Admission 109419**
**Client X (pseudonym) | 20 November 2026 | One-page final report**

## Problem and objectives

Help users discover catalogue products by interest and KES budget without inventing products, prices or dietary claims. Objectives are reproducible preprocessing, fitted retrieval, evidence-based language generation, conservative safety controls and an anonymous chat interface; accounts, checkout and medical diagnosis are excluded.

## Data and implemented method

The approved source contains 5,512 product records with KES prices. The public input, data/client_x_catalogue.json, uses Client X and omits identifying retailer links; the private input is unchanged. Offline scripts clean product text, validate records and fit 12,000 normalized TF-IDF features. FastAPI filters explicit constraints and retrieves catalogue evidence; Groq-hosted `openai/gpt-oss-120b` composes validated responses or returns a transparent fallback. GPT-OSS was neither trained nor fine-tuned. Optional projected-semantic/hybrid source exists, but those experiments were not executed.

**Architecture:** approved export -> offline cleaning/index fitting -> compact catalogue/index/manifest -> FastAPI validation, quota/safety controls and retrieval -> Groq or fallback -> Next.js chat. Both services are Dockerized; model preparation stays outside production images.

## Actual evidence and current status

Fresh anonymized execution retained all 5,512 records with zero rejects and fitted 12,000 features. In 260 local retrieval timings, mean latency was 1.13 ms and P95 2.26 ms; 640 returned-reference occurrences had zero ID/constraint violations, and all five expected abstention cases passed. These are engineering diagnostics, excluding network, Groq and UI, not human relevance judgments. The expanded API suite passed 25 tests; backend Ruff, frontend type checking, lint and standalone build passed. Local API readiness and three-reference fallback passed with retailer URLs omitted. Both Compose images and the root API image built successfully; disposable container readiness and anonymized fallback checks passed.

Historical pre-anonymization evidence: 23 API tests passed; backend, frontend and Docker CI completed successfully at revision 7d46aea. Five public API cases returned HTTP 200: budget and follow-up used actual Groq generation with three references each; dietary uncertainty prompted clarification, urgent symptoms triggered safety guidance and an impossible budget produced no matches. These results are historical, not fresh verification of the anonymized snapshot. Main incorporated confirmed merged PR #2 at 7c871ae before cleanup.

## Limitations and conclusion

Human-reviewed relevance labels are unavailable; Precision@K, Recall@K, MRR and NDCG remain unreported. Semantic comparisons are incomplete. Ingredients, verified dietary labels, current stock and snapshot freshness are unknown. Earlier public smoke checks establish targeted behavior, not clinical safety or general ranking quality. Anonymized production rollout and remaining mobile/UI checks require separate verification. The project has partial proposal alignment: a fitted lexical/RAG baseline is implemented, but the proposed semantic and labelled ranking evaluation remains outstanding.

## Reproduction and access

Repository: https://github.com/afrochic/RetailAssistant . Follow README.md and QUICKSTART.md for the approved-data adapter, index fitting, tests and Docker reproduction; see reports/final/evaluation/ for raw measurements and AI_USE.md for disclosure. Public endpoints: https://retail-assistant-tau.vercel.app/ and https://retail-assist-api.vercel.app/ . Historical public success does not establish that these endpoints serve the new anonymized snapshot. Further technical details belong in repository documentation rather than additional final-report pages.
