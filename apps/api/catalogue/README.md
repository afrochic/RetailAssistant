# Current Client X inference artifacts

- products.json: normalized approved products; external URLs are null.
- lexical.json: fitted 12,000-feature TF-IDF postings and vocabulary.
- manifest.json: source approval, Client X redaction contract and SHA-256 integrity checks.

Reproduce from data/client_x_catalogue.json using scripts/mvp/prepare.py ingest and index. Training/fitting stays outside inference containers. Optional semantic.npz is not supplied; semantic/hybrid performance is not claimed. Unknown metadata is not invented. These are current artifacts; legacy models are isolated under legacy/.
