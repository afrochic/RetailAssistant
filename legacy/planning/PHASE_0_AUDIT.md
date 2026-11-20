# Phase 0: read-only repository and Client X source audit

Date: 19 November 2026. Status: audit completed; implementation/testing/deployment results not implied.

## Repository evidence

- Canonical existing GitHub repository: `afrochic/RetailAssistant` (confirmed via public GitHub metadata).
- Local independent checkout: `retailassist/` under client-private-workspace. Its unchanged origin URL is `https://github.com/afrochic/AML_project.git`, which resolves to the renamed repository. HEAD before this rebuild: `23f528abb3188283b4d4c526285096223134b37f`.
- No new repository, branch, commit, push, reset or deployment performed. Manual branch proposal: `git switch -c mvp/Client X-groq-vercel`.
- Existing implementation: static storefront, local MiniLM/SmolLM inference, historical Flipkart data, CPU-heavy artifact bootstrap. Retained as legacy source/history; excluded from new Vercel root directories and not used by the MVP.
- Reused concepts: fitted TF-IDF/cosine retrieval, hard metadata constraints, reference-based grounding, honest evaluation separation. Existing learned Flipkart artifacts are NOT reused as Client X models.

## Real source evidence

Read-only source: `../rag_pipeline/data/Enhanced_Product_List.json` relative to this independent checkout.

- 5,512 existing product records; 4,214,397 bytes.
- SHA-256: `6d33c9d54279076aeb6105d675e327caf308c9590a47bf7cbe8c4382ed15840d`.
- Fields: SKU, ID, Name, Description, Categories, Images, RRP, Permalink.
- Supporting code: `rag_pipeline/src/routes/products.py` parses the weekly export, and `rag_pipeline/src/routes/ingest_data.py` normalizes it for the original RAG backend. `docs/adr/0005-hu-food-product-grounding.md` documents provenance/category enrichment.
- Existing Qdrant-backed service uses OpenAI embeddings. It is not called, re-ingested, modified or assumed accessible.
- Export does not encode current stock, ingredients as structured facts, brand as a structured field, currency, or export timestamp. User explicitly confirmed approval for this public presentation MVP and that RRP is KES. Snapshot freshness remains unknown.
- No customer, order, loyalty, health-history or account data read/copied. Configuration values/credentials not disclosed. No private APIs/databases contacted.

## Access decision

Source access and user-confirmed MVP use permission are available. Ingestion is **PENDING USER EXECUTION**, not blocked by inaccessible data. Run the allowlisted local export adapter; it does not modify the source. Reconfirm permission for any broader reuse/commercial use.

## Replacement structure

`apps/api`: lightweight FastAPI runtime and approved generated catalogue artifacts.
`apps/web`: Next.js chat-only frontend.
`scripts/mvp`: offline ingestion/index preparation and manual lifecycle tools.
`research/mvp`: unexecuted evaluation/report scaffolding.

## Verification and limitations

Verified only by read-only repository/source/schema inspection and official Vercel/Groq documentation. No ingestion, fitting, tests, service requests, builds or deployments executed. Model/API availability and quota require the user's Groq key and manual smoke check. Final public URLs are not known or invented.
