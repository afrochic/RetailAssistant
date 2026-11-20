# Existing Vercel projects — controlled release

Use the same existing repository and projects. No replacement project is required. This Client X cleanup has not been deployed; the previously verified release remains source7d46aea. Prior Git/cloud history may expose the original identity. Do not assume a repository rename updates a running deployment.

| Existing project | Root | Framework | Runtime port |
| --- | --- | --- | --- |
| retail-assist-api | apps/api | Container | 8080 |
| retail-assistant | apps/web | Container | 8080 |

Both roots contain Dockerfile.vercel and framework=container. Vercel Container Runtime is beta; verify current account/platform limits before a release. Official documentation: https://vercel.com/docs/functions/runtimes/container . Set PORT=8080 in each project; EXPOSE alone does not change Vercel routing. Containers are stateless; shared quota controls are required. Automatic Git deployments remain disabled in configuration.

## Environment settings

Backend Production settings:

```dotenv
PORT=8080
APP_ENV=production
GROQ_MODEL=openai/gpt-oss-120b
GROQ_API_KEY=<private-provider-key>
ALLOWED_ORIGINS=https://retail-assistant-tau.vercel.app
REQUIRE_SHARED_LIMITER=true
UPSTASH_REDIS_REST_URL=<private-redis-rest-url>
UPSTASH_REDIS_REST_TOKEN=<private-redis-token>
RATE_LIMIT_SALT=<private-random-secret>
```

Frontend Production settings:

```dotenv
PORT=8080
API_BASE_URL=https://retail-assist-api.vercel.app
```

No provider key belongs in the frontend. The public Client X source has null URLs; leave RETAILER_ALLOWED_HOSTS unset. Do not add identifying link hosts to public source. If preview environments are used, configure their controls separately and preserve appropriate protection.

## Manual release after explicit approval

Review the cleanup PR, its tests/builds, catalogue checksums and one-page report. Deploy the reviewed application commit, not an arbitrary old main import. The existing dashboard can Create Deployment from an exact commit and then Promote to Production; promotion rebuilds with Production variables. Complete account identity checks privately when prompted. Do not merge or promote without authorization.

Alternatively, authenticated CLI commands from the repository root, using project roots already configured in Vercel:

```bash
npx --yes vercel@66.4.0 login
python3 scripts/mvp/manage.py deploy --org-id YOUR_ORG_ID --project-id YOUR_API_PROJECT_ID --execute --confirm-production DEPLOY
python3 scripts/mvp/manage.py deploy --org-id YOUR_ORG_ID --project-id YOUR_WEB_PROJECT_ID --execute --confirm-production DEPLOY
```

Verify public /ready=true, count5512/KES/fitted_tfidf, correct runtime API origin, exact CORS, null retailer URLs and actual generation mode. A small number of controlled chat calls consumes quota; fallback is not Groq success. Confirm the current deployed Git SHA in both dashboards.

Troubleshooting: catalogue errors require products.json, lexical.json and manifest.json together. Shared-limiter503 requires valid Redis/salt settings, not disabled safeguards. Browser fetch errors require correct runtime API URL, exact CORS and public production access. Missing package-lock fails npm ci deliberately. Port mismatches cause startup/routing failures. No Render/Railway fallback is configured.
