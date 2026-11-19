# Approved, generated inference artifacts

Initially empty by design. Run the manual ingestion and fitting commands in QUICKSTART.md.

Required: `products.json`, `lexical.json`, `manifest.json`. Optional: `semantic.npz`.

Only the approved Healthy U product export may populate these files. Runtime rejects absent/misaligned artifacts and non-approved provenance. Never place customer data, credentials, the old Flipkart snapshot or old learned indexes here. Review generated fields before staging artifacts for a public deployment.
