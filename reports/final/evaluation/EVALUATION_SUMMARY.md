# Current Client X evaluation

The anonymized distribution source was actually ingested/refitted. Read offline_summary.json and retrieval_diagnostics.csv for exact current measurements. Data:5512 retained, zero rejected,12000 TF-IDF features. All records have positive KES prices; normalized IDs/names are unique. Categories overlap and unknown metadata is not fabricated.

Thirteen scripted diagnostic cases were repeated20times (260 warm retrieval calls). Current mean latency1.134ms and p952.265ms exclude startup, HTTP, Groq and UI. There were640 repeated reference occurrences, zero invalid IDs/exercised hard-constraint violations, and5/5 expected-abstention cases passed. These repeated software diagnostics are not independent relevance judgments or general safety accuracy.

Four regenerated PNGs show actual Client X category distribution, missing metadata, prices and local retrieval latency. Source/artifact hashes are in the current manifest. The current source is the public distribution copy, not the unmodified private export. Repeat the pipeline from repository root using scripts/mvp/prepare.py and scripts/mvp/audit_offline.py.

Precision@K, Recall@K, MRR and NDCG remain BLOCKED by missing independent human relevance labels. Optional semantic/hybrid artifacts were not fitted; no superiority claim is made. Earlier production checks belong to pre-cleanup source7d46aea and are not an anonymous deployment claim. Old identifying raw payloads were withdrawn; do not run a comparison that pretends original URLs equal the new null-URL snapshot.
