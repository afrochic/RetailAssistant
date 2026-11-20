# Client X public-submission source review

Reviewed: 20 November 2026 (Africa/Nairobi). Scope: current local source/artifacts and cleanup paths, without changing application files, calling production services or rewriting Git history.

## Result

No critical functional or client-name disclosure defect was identified in the reviewed current application and distributable catalogue. One noncritical evidence-tooling issue was reported to the primary agent for resolution before final handoff.

## Verified findings

- The distributable product source and inference catalogue each contain **5,512 records**. The source file SHA-256 matches the current manifest. Public source fields are limited to ID, SKU, Name, Description, Categories and RRP; no customer/order fields are distributed by the export utility.
- Every inference product URL is null. The loader accepts null URLs only when the source manifest explicitly declares both Client X and retailer-links-redacted=true, in addition to the existing permission, currency, integrity and product/index alignment checks. Runtime retailer-host configuration defaults empty; no original retailer hostname is embedded in current source.
- The privacy module strips HTTP(S) URLs and replaces supplied private aliases. Export and ingestion apply it to the intended textual product fields. The actual current source text scan found no configured identity aliases/domain patterns in any existing tracked or nonignored untracked UTF-8 text file examined.
- Citations use CX identifiers. The frontend omits retailer links for null URLs and retains source record IDs, prices, categories and explicit stock/metadata uncertainty. Provider keys remain server-side configuration rather than client code or catalogue fields.
- The root Dockerfile copies current `apps/api` paths into the API image; the root Docker ignore rules allow the matching runtime paths. Root requirements are intentional current-API shims. The relocated historical source, scripts, Dockerfile and Compose file exist under `legacy/flipkart`; their relative paths resolve within that historical directory.
- Public reproduction now reads `data/client_x_catalogue.json`, rather than a private enclosing-workspace source path. Existing product/index hashes and source provenance are consistent with this pseudonymized distribution input.

## Evidence-tooling issue

At review time, `scripts/mvp/audit_production_evidence.py` still referenced a raw production evidence JSON withdrawn from the public tree. Without a supplied private evidence file, that script would fail with FileNotFoundError. It also expected current CX citation/URL conventions, while privately preserved historical responses used the former public conventions. The primary agent was notified: archive/document the script as historical private-evidence tooling or add an explicit operator-supplied input/clear guard; do not claim the withdrawn raw captures can be regenerated from the public tree. This issue does not affect chat inference.

## Limits and release scope

This is client-name redaction, not full de-identification: product text, SKUs and source IDs may permit external reidentification. Alias replacement is only as complete as operator-supplied aliases and review; future unreviewed exports are not automatically safe. The text scan does not substitute for binary/PDF/image inspection or a credential scan. Those require the separate final artifact/security checks.

Prior Git history, old external logs and the previously deployed application are unchanged by this local cleanup and can retain earlier identifying material. The current source changes require an explicitly authorized, validated production update before the live application can be described as Client X. No history purge or live update is implied by this review. Current local test/build outcomes belong in the final execution evidence, not inferred from file presence.

## Follow-up correction
The primary agent added an explicit missing-evidence guard to the historical evidence checker. It now explains that approved new Client X captures are required instead of raising FileNotFoundError or producing fabricated results. Current public source reproduction does not depend on the withdrawn historical payloads.
