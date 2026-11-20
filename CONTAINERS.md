# Current container reproduction

The root Compose file builds both current apps. Root Dockerfile is an API-only build from repository context; apps/api/Dockerfile and apps/web/Dockerfile are the app-root images. Matching Dockerfile.vercel files support separate existing Vercel projects. Historical Docker configuration is under legacy/flipkart.

Prepare the current artifacts as described in QUICKSTART.md, then:

```bash
(cd apps/web && npm ci)
docker compose config --quiet
docker compose build
docker compose up -d
docker compose ps
curl --fail http://localhost:8001/health
curl --fail http://localhost:8001/ready
curl --fail http://localhost:3000/health
curl --fail http://localhost:3000/api/runtime-config
docker compose down
```

Open http://localhost:3000. Expected: Client X copy, KES prices, CX product IDs, no retailer URLs and explicit generation/fallback mode. /health is liveness; /ready also requires valid artifacts and configured controls. Local Compose uses development in-memory counters and loopback-only host bindings; it is not a public security configuration.

Both images run non-root with runtime PORT8080, health checks and graceful shutdown. Compose drops capabilities, uses read-only roots/temporary mounts and sets sensible CPU/memory/PID limits. Next uses standalone output. API copies only runtime code, requirements and compact artifacts; fitting/training stays offline. No secret is supplied as a build argument. Frontend API_BASE_URL is runtime public-origin configuration; backend provider credentials stay private.

Standalone root API build:

```bash
docker build -t retailassist-client-x-api -f Dockerfile .
```

Dockerfile.vercel copies must remain synchronized with their app-root Dockerfile. Vercel builds services separately, not with Compose; local resource/health settings do not automatically become platform settings. See VERCEL_DEPLOYMENT.md. Current cleanup validation is recorded separately from historical builds.
