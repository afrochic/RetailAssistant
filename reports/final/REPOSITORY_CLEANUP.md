# Repository organization audit

20 November 2026. Existing clean main baseline 7be14a9; history preserved. No original Healthy U application/data deleted or modified.

The Healthy U/Groq implementation is primary in apps/api and apps/web. README now prominently distinguishes measured local success from production failures and links current final evidence. Final academic materials are under reports/final; old draft and legacy metrics remain historical, not current submission evidence.

No old source/model assets were moved during urgent finalization: imports, historical notebook paths and research provenance might depend on them. Keeping the old src/retailassist, web, artifacts and old reports preserves reproduction value; README labels them legacy and current Docker/Vercel app contexts exclude them. No risky bulk cleanup was performed.

Root docker-compose.yml is canonical; docker-compose.mvp.yml remains an identical compatibility entry point for earlier commands. docker-compose.legacy.yml is historical. Retaining these avoids breaking existing runbooks. Runtime caches/dependencies and private env files remain ignored. Compact approved products.json, lexical.json and manifest.json are explicitly included for inference; no raw HU/customer export is added.

Meaningful fixes: internal Next navigation uses Link; PostCSS export is named; urgent severe-headache plus vision-disturbance guard and regression tests were added. Actual generated next-env.d.ts changes from the Next build are reviewed as generated typing metadata. Evidence scripts and measured data plots are included. No measured result from the legacy implementation is presented as Healthy U evidence.
