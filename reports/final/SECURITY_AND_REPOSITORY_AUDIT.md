# Security and repository audit - 20 November 2026

## Repository identity and preservation

Git root: /Users/dianamusee/Desktop/HU-NutritionistsVA/retailassist. Origin fetch/push: https://github.com/afrochic/RetailAssistant.git. Audit started on clean main at 7be14a9 (Organize RetailAssist MVP and academic evaluation). Fetch succeeded and origin/main matched 7be14a9. No reset, force push, history rewrite or production deployment was performed. Root published the non-production audit branch final/healthyu-production-audit, with source fixes verified at 7d46aea1dd6814044cb42ca8246b7df2cbd4cafc. Main was not rewritten; consult final handoff for the final documentation commit.

## Credentials

A pattern scan of all 152 tracked baseline files found zero Groq/OpenAI key literals, private-key blocks or JWT-shaped literals. Scanner evidence: ci/tracked_secret_scan.json. This is a bounded source scan, not proof that every possible secret format or historical commit is clean. .env files were not opened or printed. Tracked environment files are templates only. Runtime deployment secrets and GitHub environment-protection settings are not publicly inspectable.

Previously chat-exposed Groq key rotation: UNVERIFIED. No evidence was available linking a rotated provider credential to production. Corrective action: revoke the old key in GroqCloud and set a new private key only in the backend environment, then validate actual mode=groq. Never paste credentials into reports, frontend variables, Docker arguments or repository files.

GitHub credential-helper authentication was verified as afrochic; no credential value was emitted or written to evidence.

## Data authorization and privacy

User explicitly approved Healthy U product fields for this public presentation MVP and confirmed RRP is KES. The approved source is the 5,512-product Enhanced_Product_List.json export, not customer/order data. Original source SHA256 is recorded in DATA_CARD and ingestion manifest. New compact artifacts are generated from allowlisted product fields; raw source export is not required in deployment. Baseline tracked files contain no customer/order export paths; legacy files data/queries.json and data/qrels_silver.json belong to older retrieval work and are not Healthy U evaluation ground truth. This path/source review is not a complete forensic PII classifier.

The parent Healthy U application and raw export were not changed. Product descriptions are retailer marketing content and do not constitute verified clinical, allergen, ingredient or stock evidence.

## Production provenance

The supplied domains must be audited separately from local source. A successful HTTP response does not prove a specific Git revision was deployed. Production source commit remains UNVERIFIED unless deployment metadata explicitly exposes it; do not equate Vercel edge IDs with Git commit IDs. Live network evidence is in production/. No production rollout was authorized or executed by this audit.

## Status

Repository identity: PASS. Current tracked-file credential-pattern scan: PASS within stated scope. Product-use permission: PASS based on explicit user approval. Key rotation: UNVERIFIED. Full-history secret scanning: UNVERIFIED. Production revision: UNVERIFIED pending deployment provenance. Production operational state: use the live test report, not this source audit.

Final working-tree pattern scan covered 210 tracked and nonignored untracked files and found no Groq-key/private-key/JWT literal patterns (ci/final_worktree_secret_scan.json). Approved generated catalogue artifacts were separately handled by allowlisted ingestion and root publication.

## Authorized release amendment
After the initial no-rollout audit, the user explicitly approved production repair/redeployment and completed Vercel identity verification. Both current dashboard deployments identify source7d46aea; production source provenance is now PASS for these deployments. Public readiness, CORS and actual Groq outputs were retested successfully. Existing Redis credentials were not revealed; a private quota-counter salt was generated and saved without printing its value. No main merge/history rewrite occurred. Key rotation and GitHub environment reviewer protections remain UNVERIFIED.
