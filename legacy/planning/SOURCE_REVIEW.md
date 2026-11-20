# Source review — not test execution

A read-only architecture/source review identified and addressed these concrete issues:

- Generation→response Interface: word/number membership alone can swap a budget into a price or assert stock. Replaced with per-record supported explanation choices, strict structured output, ID-specific validation and deterministic rendering. Groq performs bounded answer composition rather than unrestricted clinical/product-advice generation.
- Safety→retrieval Interface: expanded deterministic clinical gates and dietary/allergen predicates. Unknown ingredient/verified-label facts cannot satisfy requirements. History-only API clients re-derive prior hard constraints; explicit preference resets remain authoritative.
- Provider Adapter: no automatic retries in the MVP; one bounded request avoids duplicate quota charges and makes the 45s frontend/60s Vercel envelope more predictable. 429 is reported transparently with fallback and Retry-After metadata.
- Privacy: clarified local tab persistence versus submission to backend/Groq. Browser Markdown images and generated links are suppressed; only validated Client X reference URLs are clickable.
- Keep the existing Modules; no broad refactor during the MVP sprint. Primary Interfaces have injectable/isolated test surfaces and synthetic unit fixtures excluded from deployment.

All proposed tests, package installs, type/lint/build checks, catalogue ingestion, model fitting, service calls, Docker operations and deployment remain **UNEXECUTED** in this rebuild. Source review is not runtime verification.

A second read-only review of the revised source found no remaining high-priority syntax/API-shape/deployment-root issue. This remains source inspection only, not a typecheck, import, test, build or runtime proof. Provider byte reservations include both message context and the response schema; the per-minute reservation budget is configurable and does not claim to replicate Groq's tokenizer/quota meter.
