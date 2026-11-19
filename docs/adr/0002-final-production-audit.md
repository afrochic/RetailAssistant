# ADR 0002: Final production audit fixes

20 November 2026. Preserve current production deployments/history. Controlled audit requests proved missing frontend API configuration, deployed catalogue/index and shared limiter. Generate approved artifacts locally; production changes require approval. Add regression for severe headache plus blurred vision: deterministic urgent-care advice must precede retrieval/provider calls. Keep the existing safety function/API seam.

Frontend validation also exposed a plain internal homepage anchor rejected by the Next.js ESLint rule. Use Next Link with unchanged appearance/accessible label and name the PostCSS export. The existing typecheck/lint/build is the regression surface; no new dependencies or behaviour are introduced.

Frontend lint correction: use Next Link for the internal homepage navigation and a named PostCSS configuration export. Both changes passed local Node22 type-check/lint/build. Include only the three user-approved compact catalogue artifacts, with checksum verification; production preflight must require the manifest alongside products and lexical index.
