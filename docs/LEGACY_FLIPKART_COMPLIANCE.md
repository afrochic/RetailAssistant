# Project compliance and demonstration map

The supplied DSA 8401 capstone brief defines submission requirements; proposal 109419 defines RetailAssist's planned scope. This map separates implemented components from verification limits.

| Requirement or proposal component | Implementation | Evidence / limitation |
| --- | --- | --- |
| Real or semi-raw retail catalogue | Pinned historical scraped Flipkart source; missing brands, descriptions, numeric ratings and category inconsistencies | DATA_CARD.md, data audit, SHA-256 manifest; INR plus dated KES estimates; not verified Kenyan inventory |
| Scripted ingestion, preprocessing, training and prediction | pipeline.py, core.py | Executed on 20,000 raw rows; 19,920 usable products |
| Keyword/content baseline | TF-IDF | Saved model artifact and evaluated metrics |
| Semantic embeddings and vector index | Pinned MiniLM normalized embeddings and exact in-memory similarity index | Executed on full cleaned catalogue; no vector database needed at this scale |
| Preference extraction and hard filters | Budget/brand parser and confirmed structured category, brand, rating, price and stock filters | Constraint tests; no-match abstention; parser is intentionally limited |
| Grounded RAG / LLM layer | Local SmolLM2 verbalizes retrieved evidence into actual explanations; optional hosted structured explanations are also supported; claim checks and factual fallbacks protect output | 24 actual local generations evaluated: 7 accepted, 17 flagged/fallback. Hosted boundary tests use mocks; paid hosted calls not tested. Conservative fact planning is disclosed |
| Conversational web interface | AI assistant drawer with semantic search, factual summaries, current filters and budget-only intent follow-ups | AI chat requests actual local LLM explanations; generation/fallback provenance is visible |
| Explainable recommendations | Accepted constraint chips, match summaries, original product details, recorded prices/ratings and unknown-stock labels | No invented suitability/performance claims; no calibrated relevance-probability claims |
| Precision@K, Recall@K, MRR, NDCG@K | evaluate.py, query-level CSV and Insights metric tabs | K=5; 6 dev / 24 test queries; rule-based silver labels, not human customer judgments |
| Constraint satisfaction and unsupported-product checks | Benchmark checks and independent fixture tests | Price/category violations and invalid IDs saved; does not establish live LLM factual accuracy |
| FastAPI service | Recommendation, catalogue, discovery, product detail, insights and health endpoints | Unit tests plus real Docker HTTP smoke checks |
| Dockerfile and Compose | Non-root image and localhost service deployment | Built and run locally; public cloud hosting not claimed |
| Notebook with outputs | notebooks/RetailAssist_walkthrough.ipynb | Full end-to-end walkthrough executed; calls the authoritative scripted modules |
| README, architecture and reproduction | README.md and Mermaid architecture | Clean clone rebuild command documented; local submission archive contains trained runtime artifacts |
| Serialized model artifacts | Fitted TF-IDF/SVD, trained index and licensed MiniLM encoder are in public Git; pinned generator restored by bootstrap | Source records are restored by hash/ID alignment without training; CI exercises this public-artifact path |
| Final report and technique justification | reports/RetailAssist_Report.pdf | Covers model choices, excluded methods, data quality, results, operational limits and study steps |
| AI assistance disclosure | AI_USE.md | Substantial Codex assistance and silver-label authorship disclosed; student must follow individual-work policy |

## Verification limits

The saved browser permission setting blocked desktop/mobile visual inspection, even after renewed conversational authorization. JavaScript syntax, HTTP/API behaviour, static assets and automated tests were checked. Responsive layouts, keyboard focus states, native dialogs, reduced-motion support and image fallback handling are implemented, but browser interaction/visual QA is not represented as completed.

The Insights dashboard reports catalogue statistics and actual offline evaluation metrics. It does not claim sales, conversion, customer satisfaction or live usage analytics. KES values are dated conversions, not verified Kenyan offers. Current retailer stock and paid hosted LLM execution are not claimed.
