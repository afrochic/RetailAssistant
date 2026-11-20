# Client X product data card

**Purpose:** reproducible retail retrieval and grounded response generation; not clinical advice or customer profiling.

**Distribution source:** data/client_x_catalogue.json, 5,512 real product records. The client approved product-field use for the presentation and confirmed RRP currency KES. Only ID, SKU, name, description, categories and RRP are distributed. No customer/order records, original retailer URLs, imagery or client name are copied. The private original is unchanged.

The distribution exporter converts text to plain text, replaces configured private client aliases with Client X and removes URLs. This is a transformed product-only distribution copy, not the untouched private export. Product IDs, product facts and prices are retained rather than fabricated. Product text may still permit external reidentification; no irreversible anonymization is claimed.

The serving pipeline normalizes fields, handles invalid/missing values, enforces unique IDs and fits TF-IDF. Missing structured brand, ingredients, verified dietary labels, current stock and snapshot date remain explicitly unknown. Categories overlap. No absence of an ingredient word establishes allergen safety. Marketing descriptions are not clinical evidence.

The current manifest includes source and artifact SHA-256 hashes, client_label=Client X, source_kind=client_x_export and retailer_links_redacted=true. Public product URLs are null. Exact data quality and price summaries are under reports/final/evaluation. TF-IDF is fitted offline; optional semantic fitting and independently reviewed relevance labels remain outstanding.

Reproduce from the included source:

```bash
python scripts/mvp/prepare.py ingest --source data/client_x_catalogue.json --currency KES --approved
python scripts/mvp/prepare.py index
python scripts/mvp/audit_offline.py
```
