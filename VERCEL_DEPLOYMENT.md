# Two Vercel Container projects — manual deployment

Source configuration only. No image has been built, no deployment has been made, and no public URL has been verified. Run commands yourself from the independent `retailassist` checkout.

## Compatibility and limitations

Vercel's Container Runtime is currently beta on all plans. Official documentation: https://vercel.com/docs/functions/runtimes/container . `Dockerfile.vercel` selects Container even when Next.js/FastAPI detection would otherwise win. Both app roots include this file and `framework: container`.

Set **PORT=8080 in each project's environment settings**. Vercel defaults to port 80 otherwise; EXPOSE alone does not configure Vercel routing. The images listen on 0.0.0.0 and respect PORT. Dockerfile and Dockerfile.vercel are identical per app; keep them synchronized.

Vercel does not deploy this Compose stack. It builds each app independently and applies Function and Container Registry limits and billing. Containers are stateless and scale down; Redis-backed public abuse controls are mandatory. Compose CPU/memory limits and Docker HEALTHCHECK are local settings: do not assume Vercel applies them as health routing or resource settings. Inspect project Function settings and platform limits separately. Account/project availability and image compatibility remain unverified until your manual deployment. Container pricing and Groq free-tier quotas are independent; free Groq access does not guarantee free hosting or model availability.

## 1. Prepare and verify locally

Follow QUICKSTART.md for the approved Healthy U ingestion, offline index fitting and npm install. Run the commands in CONTAINERS.md. You must generate and review package-lock.json and the compact catalogue artifacts first. Never deploy the raw HU backend, customer data, training environment or legacy Flipkart artifacts.

## 2. Configure two projects

In Vercel, create/connect two projects to the existing GitHub repository `afrochic/AML_project` (GitHub may show its renamed canonical repository `afrochic/RetailAssistant`). Preserve its history. Set roots:

| Project | Root directory | Framework | Port |
| --- | --- | --- | --- |
| retailassist-api | apps/api | Container | 8080 |
| retailassist-web | apps/web | Container | 8080 |

Clear inherited build/output/install overrides from prior native framework configurations. Each build context must be its app root. Keep Git automatic deployments disabled: both vercel.json files have git.deploymentEnabled=false. Deploy manually below. Record the actual project IDs and team/org ID from settings. Reserve the frontend production domain before final API CORS configuration.

Backend environment settings (Production; configure Preview separately if needed):

```dotenv
PORT=8080
APP_ENV=production
GROQ_MODEL=openai/gpt-oss-120b
GROQ_API_KEY=<new-private-key>
ALLOWED_ORIGINS=https://YOUR-WEB-DOMAIN.vercel.app
REQUIRE_SHARED_LIMITER=true
UPSTASH_REDIS_REST_URL=<private-rest-url>
UPSTASH_REDIS_REST_TOKEN=<private-rest-token>
RATE_LIMIT_SALT=<private-random-value>
REQUESTS_PER_MINUTE=8
GLOBAL_REQUESTS_PER_DAY=150
GLOBAL_TOKEN_RESERVATION_PER_DAY=150000
GLOBAL_TOKEN_RESERVATION_PER_MINUTE=24000
GROQ_TIMEOUT_SECONDS=18
GROQ_MAX_OUTPUT_TOKENS=900
```

Generate a salt locally with `openssl rand -hex 32` and paste it privately in settings. Rotate the Groq key previously exposed in chat. Never pass credentials as Docker build arguments or NEXT_PUBLIC variables. Set only the frontend variables:

```dotenv
PORT=8080
API_BASE_URL=https://YOUR-API-DOMAIN.vercel.app
```

The frontend's `/api/runtime-config` exposes only the public API origin. API_BASE_URL is runtime configuration, so the same built image can use different API domains. Use HTTPS origins without credentials, paths or queries. No account database is needed; Redis stores anonymous expiring quota counters.

## 3. Commit reviewed source and generated artifacts manually

```bash
cd /Users/dianamusee/Desktop/HU-NutritionistsVA/retailassist
git status --short
git switch -c mvp/healthyu-groq-vercel
git add apps scripts/mvp docs/adr research/mvp reports/mvp .github/workflows .gitignore .vercelignore README.md AI_USE.md DATA_CARD.md PROJECT_COMPLIANCE.md BLOCKERS.md QUICKSTART.md MANUAL_RUNBOOK.md DEPLOYMENT.md VERCEL_DEPLOYMENT.md CONTAINERS.md docker-compose.yml docker-compose.mvp.yml docker-compose.legacy.yml
git add -f apps/api/catalogue/products.json apps/api/catalogue/lexical.json apps/api/catalogue/manifest.json
git diff --cached --stat
git diff --cached --check
# Review staged changes locally for secrets and unwanted records before committing.
git commit -m "Build Healthy U Groq chatbot with two Vercel containers"
git push -u origin mvp/healthyu-groq-vercel
```

If using optional semantic inference, explicitly review/add semantic.npz and its updated manifest too. Do not force-push, reset history or stage .env files. If the branch already exists, switch to it without recreating it. Merge via your normal review process when ready; CLI deployment below deploys the local checkout you provide.

## 4. Deploy API, then frontend manually

From the **repository root**, with project roots already configured in Vercel (do not cd into apps and accidentally apply the root twice):

```bash
npx --yes vercel@66.4.0 login
python3 scripts/mvp/manage.py deploy --org-id YOUR_ORG_ID --project-id YOUR_API_PROJECT_ID --execute --confirm-production DEPLOY
curl --fail https://YOUR-API-DOMAIN.vercel.app/health
curl --fail https://YOUR-API-DOMAIN.vercel.app/ready
python3 scripts/mvp/manage.py deploy --org-id YOUR_ORG_ID --project-id YOUR_WEB_PROJECT_ID --execute --confirm-production DEPLOY
curl --fail https://YOUR-WEB-DOMAIN.vercel.app/health
curl --fail https://YOUR-WEB-DOMAIN.vercel.app/api/runtime-config
```

Expected: liveness 200, API ready=true, frontend config contains the actual HTTPS API origin, then chat shows real source references and KES prices. Verify public incognito access: deployment protection can block browser requests to the API even if you are signed in. Configure the intended public production domains accordingly. Check ALLOWED_ORIGINS exactly matches the frontend origin, then manually redeploy API after any change.

## Troubleshooting

- Build missing package-lock.json: run npm install under apps/web, inspect and commit the lockfile. Docker deliberately uses npm ci and fails without it.
- Missing catalogue/503 ready: manually ingest/index the approved export; inspect manifest and include compact artifacts in deployment. No substitute data is loaded.
- Container timeout/502: check platform PORT=8080 on both projects, Container preset, root directory, image build logs and Function limits.
- 503 shared limiter: supply real Upstash REST settings and salt. Never disable public safeguards to bypass this.
- Browser fetch failure: verify public API access, exact CORS origin, HTTPS API_BASE_URL and /api/runtime-config response; redeploy after environment changes.
- 429: inspect Retry-After. Local/global safeguards may block requests; Groq quota failures return a clearly identified catalogue fallback when retrieval is available. No invented successful generation.
- Container beta/account restriction or image limit: record the exact platform error. Do not silently switch hosts or claim a live deployment; source-native Vercel deployment would be a separate architecture decision.

Academic results remain pending actual evaluation. Docker/deployment success alone is not ML evidence.
