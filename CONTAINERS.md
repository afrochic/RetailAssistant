> Final audit update (20 November 2026): ingestion, fitting, local tests/builds, Docker probes, CI and an explicitly authorized production repair have now been executed. Both existing projects run tested source7d46aea. See reports/final/FINAL_HANDOFF.md for actual outcomes; earlier source-only/unexecuted statements below describe the prior preparation phase.

# Local container runbook

All commands are manual and unexecuted by the agent. Requires Docker Desktop with Compose v2, Python 3.12 for offline preparation, Node 22/npm to generate a reviewed lockfile. No training or raw export ingestion runs in a production image.

## Prepare

From the repository root, follow QUICKSTART.md steps 1–2 for dependencies, local secrets and approved Healthy U ingestion/index fitting, then:

```bash
cd apps/web
npm install
cd ../..
# Preserve existing apps/api/.env; edit privately using apps/api/.env.example as the template.
docker compose config --quiet
docker compose build
docker compose up -d
docker compose ps
curl --fail http://localhost:8001/health
curl --fail http://localhost:8001/ready
curl --fail http://localhost:3000/health
curl --fail http://localhost:3000/api/runtime-config
```

Open http://localhost:3000 and check a real catalogue query, KES budget follow-up, medical refusal and visible source references. Readiness must say ready=true; /health only confirms the HTTP process is alive. Missing/invalid catalogue artifacts intentionally prevent recommendations. A missing/failed Groq key gives transparent catalogue fallback, not fabricated AI output.

```bash
# A real request may consume Groq quota.
curl --fail-with-body http://localhost:8001/api/chat -H 'Content-Type: application/json' --data '{"message":"Find breakfast oats under KSh 1000","history":[],"preferences":{"currency":"KES"},"k":3}'
docker compose logs --tail=80 api web
docker compose down
```

Both services bind host loopback only. Compose deliberately sets APP_ENV=local and in-memory development limits; it is not a public production security configuration. The browser needs http://localhost:8001, not Docker's internal api hostname. No secrets are injected into the web container. Both images run UID/GID 10001, with read-only root filesystems, writable temporary/cache mounts, dropped capabilities, resource limits, health checks and graceful shutdown. Probe failure/readiness, filesystem permissions and resource sufficiency still require actual testing. Base images use maintained major/minor tags; pin reviewed image digests after successful build verification for stricter reproducibility.

The frontend is a multi-stage Next.js standalone build; the backend copies only runtime dependencies, service code and prepared catalogue artifacts. Both default to PORT=8080. Missing frontend package-lock.json intentionally fails npm ci. Runtime API_BASE_URL prevents backend domains being baked into the web image. Files named Dockerfile.vercel are synchronized copies for Vercel selection.

Optional manual Vercel-image parity builds:

```bash
docker build -f apps/api/Dockerfile.vercel -t retailassist-api:vercel apps/api
docker build -f apps/web/Dockerfile.vercel -t retailassist-web:vercel apps/web
```

`docker-compose.mvp.yml` mirrors the root Compose file for earlier runbook compatibility. The previous unrelated/legacy stack is preserved in docker-compose.legacy.yml and is not the new MVP. Keep both MVP Compose files synchronized. Vercel-specific configuration and exact manual deployment/Git commands are in VERCEL_DEPLOYMENT.md.
