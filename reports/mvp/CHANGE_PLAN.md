# File-level rebuild change plan

The former implementation remains in Git history and its existing paths. No history rewrite or source deletion is needed for the urgent MVP.

- Add apps/api and apps/web as isolated Vercel roots; exclude all legacy source/checkpoints from deployment bundles.
- Replace the root README/data card/compliance entrypoints with Healthy U/Groq MVP instructions; preserve their old content in docs/LEGACY_* files.
- Append a rebuild-specific AI-use disclosure; no prior experiment is reattributed to Healthy U/Groq.
- Keep src/retailassist, web, artifacts, notebooks and reports/RetailAssist_Report.pdf as historical only; the new backend never imports them.
- Change the legacy checks workflow from push/PR triggers to manual triggering only. Add manual MVP validation workflows and guarded production workflow scaffolding. No workflows are executed/enabled by the agent.
- Keep original Dockerfile/docker-compose.yml as legacy. New academic reproduction uses apps/api/Dockerfile and docker-compose.mvp.yml.
- Keep the existing origin URL, main branch, commits and history unchanged. Proposed rebuild branch is a manual user action.
- Never edit the enclosing HU application's agent/frontend/rag_pipeline/data files. Only read its approved product export and create an allowlisted copy when the student explicitly runs ingestion.
