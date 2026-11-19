> Final audit update (20 November 2026): ingestion, fitting, local tests/builds, Docker probes, CI and an explicitly authorized production repair have now been executed. Both existing projects run tested source7d46aea. See reports/final/FINAL_HANDOFF.md for actual outcomes; earlier source-only/unexecuted statements below describe the prior preparation phase.

> Container architecture update: both app images and the root two-service Compose stack are now defined. Use [CONTAINERS.md](CONTAINERS.md) locally and [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md) for the current Container-runtime deployment instructions, which supersede earlier native-framework hosting steps below. Builds and deployments remain unexecuted.

# Deployment entrypoint

The current MVP uses **Vercel for both applications**, not Render/Railway.

Follow [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md) after [QUICKSTART.md](QUICKSTART.md). No deployment was executed by the agent. Docker is provided for academic local reproduction only. Historical deployment material under legacy folders does not apply to the Healthy U/Groq MVP.
