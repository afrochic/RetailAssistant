# Healthy U evaluation evidence — 20 November 2026 (Africa/Nairobi)

## What was executed

The existing approved ingestion and lexical fitting commands were run in the existing Python 3.12.16 `.venv-mvp` environment. They read only the authorized product export at `../rag_pipeline/data/Enhanced_Product_List.json`; they did not modify the original export, call customer databases, fit semantic embeddings, train GPT-OSS or call Groq. The ingestion and index scripts completed successfully. The source SHA-256 was `6d33c9d54279076aeb6105d675e327caf308c9590a47bf7cbe8c4382ed15840d`, matching the manifest. Index bytes were identical across a second fit with the same corpus/settings (`index_reproducibility.json`).

The new `scripts/mvp/audit_offline.py` diagnostic was executed against the resulting real artifacts. The first authoring run exposed a boolean-conversion bug in the diagnostic's aggregation; this was corrected, and the complete run then succeeded. This correction concerns the measurement script, not production retrieval. `scripts/mvp/plot_offline.R` used base R to produce four figures directly from exported CSV measurements. Figures were visually inspected, and a clipped long category label was wrapped before final export.

## Dataset results

| Measurement | Actual result |
| --- | ---: |
| Source records / retained records | 5,512 / 5,512 |
| Rejected records | 0 |
| Duplicate source ID occurrences | 0 |
| Duplicate normalized-name groups | 0 |
| Missing/nonpositive price records | 0 |
| Currency | KES (user confirmed source RRP) |
| Minimum / median / 95th-percentile / maximum price | 35 / 1,599 / 6,999 / 19,999 KES |
| Distinct category labels | 133 |
| Fitted TF-IDF vocabulary | 12,000 terms |
| Serialized product / lexical artifact size | 3,950,322 / 4,830,002 bytes |

Categories overlap: they are not mutually exclusive classes. Source names, descriptions, SKUs, prices and category lists are populated, but every record lacks structured verified brand, ingredients, dietary labels and live stock fields in the normalized schema. Some category strings describe “Free From” categories; this is not independent verification of dietary safety, and the implementation deliberately does not promote them into verified ingredient labels. No source snapshot date was supplied. Price completeness does not prove prices are current.

## Retrieval and constraint diagnostics

Thirteen explicit scripted cases were run with one untimed warm-up followed by 20 timed repeats per case (260 timed retrieval calls). Cases cover ordinary terms/budgets and deliberately unsupported labels, unknown ingredients/stock, absent query terms and impossible budgets. There are no relevance judgments in these cases.

| Measurement | Actual result |
| --- | ---: |
| Method executed | Fitted TF-IDF only |
| One cold artifact load | 102.383 ms |
| Mean / median warm retrieval latency | 1.332 / 1.253 ms |
| 95th-percentile warm retrieval latency | 2.528 ms |
| Returned reference occurrences across repeated calls | 640 |
| Invalid catalogue ID occurrences | 0 |
| Numeric/currency/label/stock constraint violations in returned references | 0 |
| Constraint satisfaction among returned reference occurrences | 100% (640/640) |
| Expected abstention diagnostic cases | 5/5 |
| Repeated ranked IDs identical | Yes |

The reference count includes repeated calls and is **not** 640 independent products or queries. The 100% rate measures a narrow deterministic software contract on scripted cases; it is not evidence of relevance, medical effectiveness, user satisfaction or generalization. Latency excludes HTTP, hosted Groq generation, UI work, cold starts and deployment infrastructure. It is a single-machine diagnostic, not a production service-level guarantee.

## What cannot honestly be reported

Precision@K, Recall@K, MRR and NDCG@K are **BLOCKED** because no independent human-reviewed Healthy U relevance labels exist in the repository. The template explicitly says PENDING_HUMAN_REVIEW, and legacy `data/queries.json` contains unrelated INR/Flipkart queries. Those labels and historical metrics were excluded. The existing evaluation command was actually invoked with the template and exited 1, correctly refusing to report invented results; see `label_guard_stderr.txt`.

Semantic and hybrid code paths exist but no compatible semantic artifact was present or generated. They were not evaluated and are not claimed to outperform the lexical baseline. No retrieval model-comparison graph is supplied because only one approach was executed. GPT-OSS was not trained or fine-tuned. This offline diagnostic does not establish hosted generation success: use the separate actual production request evidence for generation/fallback and safety outcomes.

## Reproduce

```bash
cd /Users/dianamusee/Desktop/HU-NutritionistsVA/retailassist
source .venv-mvp/bin/activate
python scripts/mvp/prepare.py ingest --source ../rag_pipeline/data/Enhanced_Product_List.json --currency KES --approved
python scripts/mvp/prepare.py index
python scripts/mvp/audit_offline.py
Rscript scripts/mvp/plot_offline.R
```

The original source export is authorized for this presentation MVP but is not newly published by these evaluation steps. The generated compact product/index/manifest artifacts remain subject to `.gitignore` until explicitly reviewed for inclusion. The fitting output is deterministic for the corpus/parameters; wall-clock timestamps and performance measurements will differ.

For publishable retrieval-quality comparisons, the student must independently annotate relevant product IDs for distinct development/test queries, record reviewer/split metadata and review the catalogued source records. Then run `scripts/mvp/evaluate.py` with the reviewed file and `--confirm-human-labels`. Optional semantic teacher fitting requires separate offline dependencies/model download and independent evaluation, not a claim based on source-code presence.

## Evidence inventory

- `offline_summary.json`, `offline_execution_stdout.json`: actual aggregate results.
- `retrieval_diagnostics.csv`: all 260 actual timed calls, IDs, constraints and deterministic checks.
- `categories.csv`, `missing_data.csv`, `prices.csv`: data behind figures.
- `artifact_manifest.json`: actual approved-source provenance and artifact hashes.
- `index_reproducibility.json`: identical lexical bytes across repeated fitting.
- `label_guard_exit_code.txt`, `label_guard_stderr.txt`: honest missing-ground-truth guard evidence.
- `category_distribution.png`, `missing_data.png`, `price_distribution.png`, `retrieval_latency.png`: actual-data plots.

## Interpretation

The complete approved catalogue can be served through a lightweight reproducible lexical index, and the exercised budget/metadata contracts behaved deterministically. The strongest limitation is not model loading or price coverage: it is missing verified suitability metadata and missing independent relevance labels. This is sufficient evidence of an implemented ML pipeline and measured software diagnostics, but it is not a completed comparative recommendation-quality study.

## Subsequent public production verification

After the authorized production repair, five actual unauthenticated HTTPS acceptance responses were recorded separately in `production/production_chat_postrelease.json`. Offline source validation of those records is in `production_rag_checks.json` and `PRODUCTION_RAG_SUMMARY.md`: all five expected modes passed, including two `groq_grounded` cases; six reference occurrences matched the exact approved source fields and budgets. These are a separate small acceptance sample, not the 260 local diagnostic calls and not a substitute for reviewed ranking relevance labels.
