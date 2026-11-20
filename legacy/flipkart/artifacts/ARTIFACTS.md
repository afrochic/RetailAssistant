# Public serialized artifacts

- `retriever_index.joblib`: fitted TF-IDF/SVD, sparse/dense product vectors, and the ordered product-ID alignment. Includes **no product record DataFrame** or original descriptions.
- `fitted_transformers.joblib`: independently loadable fitted TF-IDF/SVD parameters.
- `encoder/`: pinned all-MiniLM-L6-v2 encoder, model card and Apache-2.0 license.
- `generator_manifest.json`: pinned Apache-2.0 local text-generator reference. `bootstrap --with-generator` downloads its weights; hosted API credentials are not required.
- `manifest.json`: exact source catalogue SHA-256 and embedding model revision.

Run `python -m retailassist.bootstrap --with-generator` after installing dependencies. This downloads and validates the original raw snapshot, binds cleaned records to the published vectors by exact ordered product IDs, creates the serving bundle, and downloads the local LLM. It does not retrain the indexes or recompute embeddings. The larger generator checkpoint remains reproducibly available at its pinned Hugging Face source, avoiding GitHub's per-file size limit.

The historical scraped records are not redistributed in Git because the source mirror's license is unknown. Indexes and model parameters are supplied for academic reproduction; this does not grant rights to the source catalogue or retailer photographs. Never load joblib files from an untrusted source.
