# RetailAssist - capstone defense slide source

DSA 8401 Applied Machine Learning | MSc Data Science & Analytics | Admission 109419
Evidence cut-off: 20 November 2026. Twelve editable slides with speaker notes.
This is complete presentation content, not a PPTX export. Historical pre-anonymization verdict: READY WITH LIMITATIONS. Current anonymized local pipeline diagnostics are verified; publication and fresh live checks remain pending.

---

## Slide 1 - RetailAssist

**A conversational Client X product recommendation system**

Catalogue retrieval, constrained generation and honest deployment evaluation

Admission 109419 | DSA 8401 | 20 November 2026

**Speaker notes:** Describe this as an independent student project. Fresh anonymized local diagnostics passed. Controlled public end-to-end requests passed historically before anonymization, after explicitly authorized repair. State the remaining semantic, ranking-evaluation and UI-verification limits before the live demo.

---

## Slide 2 - Product discovery with incomplete evidence

- A customer asks for a product interest, a budget and preferences in ordinary language.
- A fluent answer can still invent a product, price or dietary property.
- Healthy-retail recommendations must remain distinct from medical advice.

**Research question:** How can catalogue retrieval support useful conversational responses while preserving identifiable product evidence and explicit constraints?

**Speaker notes:** Example: breakfast oats under KES 2,000, followed by a tighter budget. Explain that accounts, checkout and storefront browsing were intentionally excluded to keep the project focused on retrieval and generation.

---

## Slide 3 - Research objectives

1. Reproduce an approved product-data pipeline and fitted retrieval baseline.
2. Ground responses in catalogue IDs, KES prices and retailer references.
3. Enforce constraints and abstain when supporting attributes are unknown.
4. Compare retrieval methods only where artifacts and relevance judgments exist.
5. Separate local test evidence from deployed behavior.

**Speaker notes:** TF-IDF corpus-statistic fitting is the executed machine learning component. Groq-hosted GPT-OSS is pretrained; it was not trained or fine-tuned for this project. Optional semantic code is not evidence of a completed semantic experiment.

---

## Slide 4 - Client X dataset and data quality

**Fresh anonymized ingestion: 5,512 approved records, all accepted; zero rejects**

- No duplicate raw IDs or normalized product-name groups found.
- All records have valid positive KES prices; median KES 1,599.
- Price range: KES 35 to KES 19,999; 133 overlapping category labels.
- Structured ingredients, verified dietary labels, stock and snapshot date are unavailable.

**Figure:** `evaluation/category_distribution.png` (regenerated with Client X title).
**Supporting table:** `evaluation/missing_data.csv` (current anonymized snapshot).

**Speaker notes:** Permission and KES RRP were confirmed by the user. The current source hash is recorded in the anonymized manifest. Category labels overlap, so the chart is not a mutually exclusive class distribution. Name-uniqueness checks do not prove that no near-duplicate products exist. No customer data is part of the pipeline.

---

## Slide 5 - System architecture

Approved export -> offline adapter -> compact catalogue/index/manifest

Next.js chat -> FastAPI controls -> constrained retrieval -> Groq OR explicit fallback

Response -> verified product references, KES prices and generation mode

- Two app roots in the existing repository.
- Both services have multi-stage Dockerfiles; local image builds and disposable runtime checks passed.
- Shared Redis counters protect public requests; no account database is required.

**Speaker notes:** Training and embeddings preparation stay offline. Browser runtime configuration contains only the public API origin. Provider credentials belong only on the backend. Local image checks passed; Vercel production integration still failed.

---

## Slide 6 - Preprocessing and feature engineering

- Clean HTML, normalize text and validate source identifiers/retailer URLs.
- Preserve missing facts; never infer stock or allergen safety from silence.
- Fit 12,000 TF-IDF features and normalized sparse postings.
- Validate artifact hashes and product/index alignment at inference startup.

**Figure:** `evaluation/price_distribution.png` (current anonymized snapshot).

**Speaker notes:** The price figure uses measured catalogue values, not synthetic examples. Source-record IDs maintain traceability. Price filtering happens before ranking so an otherwise relevant over-budget record cannot be returned. The serialized lexical artifact was byte-identical across two local fits with the same inputs and environment.

---

## Slide 7 - Retrieval and response generation

**Executed:** fitted TF-IDF retrieval with hard metadata constraints.

**Optional, unexecuted:** MiniLM teacher embeddings, PCA, fitted lexical-to-semantic query projection and reciprocal rank fusion.

**Hosted generation:** Groq `openai/gpt-oss-120b`, constrained to retrieved IDs and supported reasons.

**Speaker notes:** The compact projection is not native MiniLM query encoding. Do not claim semantic or hybrid superiority. Literature motivates sentence embeddings [Reimers & Gurevych, 2019], RRF [Cormack et al., 2009] and RAG [Lewis et al., 2020]. Groq success must be shown by an actual generated-mode response; a configured key or catalogue fallback is insufficient.

---

## Slide 8 - Evaluation protocol and evidence limits

- Execute reproducible ingestion, integrity checks and deterministic retrieval diagnostics.
- Measure local latency, returned-ID existence, constraints and abstention behavior.
- Use human-reviewed held-out labels for Precision@K, Recall@K, MRR and NDCG@K.
- No reliable human relevance labels were available; ranking-effectiveness metrics remain BLOCKED.

**Speaker notes:** The 13 diagnostic cases are engineering checks, not an independently sampled user study. Twenty repeated timings per case produce 260 timed requests but not 260 independent relevance judgments. Local inference excludes UI, network, Groq and startup. LLM-generated labels were not substituted for ground truth.

---

## Slide 9 - Fresh anonymized local results

| Measure | Actual local result |
| --- | --- |
| Mean warm retrieval latency | 1.13 ms |
| P95 warm retrieval latency | 2.26 ms |
| Cold artifact load | 55.90 ms |
| Returned reference occurrences | 640 |
| Invalid IDs / constraint violations | 0 / 0 |
| Expected abstention cases | 5 of 5 passed |
| Repeat result ordering | Identical across repetitions |

**Current verification:** 25 API tests, backend Ruff and frontend type/lint/standalone build passed. Local readiness and three-reference fallback passed with retailer URLs omitted. Both Compose images and the root API image built; disposable container readiness and anonymized fallback passed. Anonymized production verification remains pending. Historical pre-anonymization backend, frontend and Docker CI passed at 7d46aea.

**Historical integration:** actual local Groq responses and safety checks passed before anonymization; they are not represented as new provider tests of this snapshot.

**Figure:** `evaluation/retrieval_latency.png` (fresh anonymized local measurements; 260 timings).

**Speaker notes:** A budget-number retrieval defect was historically found and fixed with a red/green regression. The fresh anonymous measurements came from one local Python 3.12 process. Zero failures on these cases does not prove universal grounding, medical safety or relevance. P@K, R@K, MRR and NDCG were intentionally not computed without judgments. No semantic comparison chart is included because the semantic artifact was unavailable.

---

## Slide 10 - Historical public application and current cleanup

Frontend: https://retail-assistant-tau.vercel.app/
Backend: https://retail-assist-api.vercel.app/

- Public API ready=true; 5,512 records; KES; fitted TF-IDF.
- Frontend runtime origin and trusted-origin CORS: HTTP 200.
- Five public cases: 200; two Groq-grounded responses, dietary clarification, urgent medical safety and no-match abstention.
- Browser interaction rendered four product references, KES prices and retailer links.

**Screenshot omitted:** original capture exposed the client identity or retailer links. A new anonymized capture is required.

**Historical live verdict: READY WITH LIMITATIONS; anonymized rollout pending**

**Speaker notes:** Initial readiness, origin, limiter and CORS failures were preserved in the evidence and repaired only after explicit authorization. Both historical pre-anonymization production source revisions were confirmed as 7d46aea. Mobile layout and several UI interactions remain unverified. The original identifying screenshots are not included in this public presentation; they are not relabelled as anonymous evidence. Current anonymized deployment has not been verified. Public requests A/E each returned three KES499 rice-cake references with genuine groq_grounded mode. This is successful targeted smoke evidence, not general relevance validation.

---

## Slide 11 - Safety and limitations

- Medical requests must avoid supplement treatment recommendations and prioritize urgent assessment when needed.
- Missing ingredient/stock evidence means abstention, not a suitability claim.
- Private keys stay server-side; key rotation remains unverified without evidence.
- Snapshot freshness, semantic evaluation and human relevance judgments remain unresolved.

**Speaker notes:** The initial shared limiter blocked public chat. After repair, the specified severe-headache/blurred-vision prompt returned urgent_safety with no products in production. That single test does not establish comprehensive clinical safety. Rule-based safety has false-positive and false-negative risks. Catalogue references are traceability, not medical validation.

---

## Slide 12 - Conclusion and immediate next steps

**Delivered evidence:** approved-data ingestion, fitted lexical artifact, reproducibility checks, real local measurements and successful controlled public Groq/API tests after documented repair.

**Before presenting the anonymized snapshot:**

1. Complete fresh anonymized checks; confirm deployment source and free-tier quota.
2. Check mobile layout, New Chat and remaining UI states.
3. Inspect live references; avoid inferring current stock or dietary suitability.
4. Complete semantic experiments and human relevance annotation to meet the proposal’s remaining evaluation commitments.

**Speaker notes:** The earlier presentation MVP worked under controlled checks. The anonymized pipeline has fresh local diagnostics; its production rollout, ranking-effectiveness and full-interface validation remain incomplete. Future work includes source freshness, verified dietary attributes, a faithful semantic comparison and systematic safety evaluation. AI assistance was used for code, audit and writing; see AI_USE.md.

## References for speaker notes

- Reimers, N., & Gurevych, I. (2019). Sentence-BERT. https://arxiv.org/abs/1908.10084
- Cormack, G. V., Clarke, C. L. A., & Buettcher, S. (2009). Reciprocal Rank Fusion. https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf
- Lewis, P., et al. (2020). Retrieval-Augmented Generation. https://arxiv.org/abs/2005.11401
- Groq model documentation. https://console.groq.com/docs/model/openai/gpt-oss-120b
- Vercel Container Runtime. https://vercel.com/docs/functions/runtimes/container

## PowerPoint export limitation

The required presentation artifact-tool runtime loader was unavailable in this environment. No PPTX was generated with an unsupported substitute. This complete editable slide source is the fallback authorized in the finalization brief. The student may transfer it to PowerPoint and insert the genuine figures at the indicated paths.
