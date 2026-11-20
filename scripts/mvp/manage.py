"""Manual operator commands. Never performs a deployment without explicit confirmation."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
API = ROOT / 'apps/api'
WEB = ROOT / 'apps/web'
VERCEL_VERSION = '66.4.0'  # Override with --vercel-version after checking the version recorded in VERCEL_DEPLOYMENT.md.

def invoke(command, cwd=ROOT, execute=False, env=None):
    import shlex
    print('Working directory:', cwd)
    print('Command:', shlex.join(command))
    if not execute:
        print('DRY RUN. Add --execute to run this command yourself.'); return
    subprocess.run(command, cwd=cwd, check=True, env=env)

def preflight():
    findings = []
    manifest = API / 'catalogue/manifest.json'
    for name in ['products.json', 'lexical.json', 'manifest.json']:
        if not (API / 'catalogue' / name).exists(): findings.append('Missing ' + name + ': run manual ingestion/index fitting.')
    if manifest.exists():
        data = json.loads(manifest.read_text())
        if data.get('source_kind') != 'client_x_export' or not data.get('permission_approved') or data.get('currency') != 'KES': findings.append('Source provenance or currency is not approved.')
    if manifest.exists() and all((API / 'catalogue' / name).exists() for name in ['products.json', 'lexical.json']):
        sys.path.insert(0, str(API))
        try:
            from retail_mvp.catalogue import Catalogue
            Catalogue(API / 'catalogue')
        except Exception as error:
            findings.append('Artifact validation failed: ' + type(error).__name__)
    if not (WEB / 'package-lock.json').exists(): findings.append('Frontend lockfile missing: run npm install, review and commit package-lock.json.')
    print(json.dumps({'scope': 'Local file inspection only; not a test, build or deployment.', 'findings': findings}, indent=2))
    if findings: raise SystemExit(1)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for name, help_text in [('env', 'Create local example files without overwriting secrets.'), ('serve', 'Start local FastAPI on 8001.'), ('test', 'Run the unexecuted backend tests.'), ('lint', 'Run backend static checks.'), ('web-install', 'Install pinned frontend dependencies and generate the lockfile.'), ('web-dev', 'Start Next.js on 3000.'), ('web-build', 'Run typecheck, lint and production build.'), ('docker-build', 'Build the academic MVP image.'), ('compose-up', 'Start local MVP Compose.'), ('compose-down', 'Stop local MVP Compose.'), ('preflight', 'Inspect required local files only.')]:
        p = commands.add_parser(name, help=help_text); p.add_argument('--execute', action='store_true')
    p = commands.add_parser('smoke', help='GET ready and make a real chat request against a running backend. May use Groq quota.')
    p.add_argument('--url', default='http://127.0.0.1:8001'); p.add_argument('--execute', action='store_true')
    p = commands.add_parser('deploy', help='Explicit manual Vercel production deployment, from repository root with configured root directories.')
    p.add_argument('--project-id', required=True); p.add_argument('--org-id', required=True); p.add_argument('--vercel-version', default=VERCEL_VERSION); p.add_argument('--confirm-production', default=''); p.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    if args.command == 'env':
        for path, example in [(API / '.env', API / '.env.example'), (WEB / '.env.local', WEB / '.env.example')]:
            print('Preserve existing' if path.exists() else 'Would create', path.relative_to(ROOT))
            if args.execute and not path.exists(): shutil.copy2(example, path); path.chmod(0o600)
        return
    if args.command == 'preflight':
        if args.execute: preflight()
        else: print('Dry run: add --execute for a local file-read preflight. No build/deployment is performed.')
        return
    if args.command == 'smoke':
        if not args.execute: print('Dry run: GET /ready, then POST /api/chat (real quota may be used). Add --execute.'); return
        base = args.url.rstrip('/')
        with urllib.request.urlopen(base + '/ready', timeout=15) as response: ready = json.load(response)
        if not ready.get('ready'): raise SystemExit('Backend not ready; inspect catalogue and shared-limiter settings.')
        body = json.dumps({'message': 'Find breakfast oats under KSh 1000', 'history': [], 'preferences': {'currency': 'KES'}, 'k': 3}).encode()
        request = urllib.request.Request(base + '/api/chat', data=body, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(request, timeout=50) as response: result = json.load(response)
        print(json.dumps({'mode': result['mode'], 'references': len(result['references']), 'notices': result['notices']}, indent=2))
        if any(p['price'] is None or p['price'] > 1000 or p['currency'] != 'KES' for p in result['references']): raise SystemExit('Budget/currency smoke check failed.')
        return
    if args.command == 'deploy':
        env = {**os.environ, 'VERCEL_PROJECT_ID': args.project_id, 'VERCEL_ORG_ID': args.org_id}
        if args.execute and args.confirm_production != 'DEPLOY': parser.error('Production requires --confirm-production DEPLOY. Nothing deployed.')
        invoke(['npx', '--yes', 'vercel@' + args.vercel_version, '--prod'], execute=args.execute, env=env)
        return
    mapping = {
        'serve': ([sys.executable, '-m', 'uvicorn', 'app:app', '--host', '127.0.0.1', '--port', '8001'], API),
        'test': ([sys.executable, '-m', 'pytest', '-q'], API),
        'lint': ([sys.executable, '-m', 'ruff', 'check', '.'], API),
        'web-install': (['npm', 'install'], WEB),
        'web-dev': (['npm', 'run', 'dev'], WEB),
        'docker-build': (['docker', 'compose', 'build'], ROOT),
        'compose-up': (['docker', 'compose', '-f', 'docker-compose.yml', 'up', '--build', '-d'], ROOT),
        'compose-down': (['docker', 'compose', '-f', 'docker-compose.yml', 'down'], ROOT),
    }
    if args.command == 'web-build':
        for step in ['typecheck', 'lint', 'build']: invoke(['npm', 'run', step], WEB, args.execute)
        return
    command, cwd = mapping[args.command]; invoke(command, cwd, args.execute)

if __name__ == '__main__': main()
