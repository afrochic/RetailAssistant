"""Manual evaluation only. Refuses unreviewed/template ground truth; stores actual outputs."""
import argparse
import asyncio
import csv
import json
import math
from pathlib import Path
import resource
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'apps/api'))
from retail_mvp.catalogue import get_catalogue  # noqa: E402
from retail_mvp.models import ChatRequest, Preferences  # noqa: E402
from retail_mvp.safety import boundary, resolve_request  # noqa: E402


def ranking_metrics(ids, relevant, k):
    hits = [int(pid in relevant) for pid in ids[:k]]
    dcg = sum(hit / math.log2(i + 2) for i, hit in enumerate(hits))
    ideal = sum(1 / math.log2(i + 2) for i in range(min(k, len(relevant))))
    return {'precision_at_k': sum(hits) / k, 'recall_at_k': sum(hits) / len(relevant) if relevant else None, 'mrr': next((1 / (i + 1) for i, hit in enumerate(hits) if hit), 0), 'ndcg_at_k': dcg / ideal if ideal else None}

async def run(args):
    catalogue = get_catalogue(); queries = json.loads(Path(args.queries).read_text())
    if not args.confirm_human_labels or not queries or any(q.get('judgment_status') != 'human_reviewed' or not q.get('reviewer') for q in queries):
        raise ValueError('Replace the template with independently reviewed judgments and pass --confirm-human-labels. No results produced.')
    seen = set(); valid_ids = {p['id'] for p in catalogue.products}
    for q in queries:
        normalized = ' '.join(q['query'].lower().split())
        if normalized in seen: raise ValueError('Repeated query across the evaluation set; check split leakage.')
        seen.add(normalized)
        if q['split'] not in {'dev', 'test'} or not set(q['relevant_ids']).issubset(valid_ids): raise ValueError('Invalid split or non-catalogue relevance IDs.')
    methods = ['lexical'] + (['semantic', 'hybrid'] if catalogue.semantic is not None else [])
    rows = []
    for q in queries:
        request = ChatRequest(message=q['query'], preferences=q.get('preferences', {}), k=args.k)
        query, preferences = resolve_request(request)
        safety = boundary(query)
        for method in methods:
            start = time.perf_counter()
            products = [] if safety else catalogue.search(query, preferences, args.k, method=method)
            ids = [p['id'] for p in products]
            rows.append({'query_id': q['id'], 'split': q['split'], 'method': method, 'k': args.k, 'latency_ms': (time.perf_counter() - start) * 1000, 'returned': len(ids), 'constraint_violations': sum(not catalogue.eligible(p, preferences) for p in products), 'invalid_ids': sum(pid not in valid_ids for pid in ids), 'safety_mode': safety[0] if safety else '', **ranking_metrics(ids, set(q['relevant_ids']), args.k)})
    outputs = []
    if args.include_groq:
        if not args.api_url: raise ValueError('--api-url is required for actual bounded Groq/API evaluation.')
        import httpx
        async with httpx.AsyncClient(timeout=50) as client:
            for q in queries:
                started = time.perf_counter()
                response = await client.post(args.api_url.rstrip('/') + '/api/chat', json={'message': q['query'], 'preferences': q.get('preferences', {}), 'k': args.k})
                # Never relabel 429, fallback or missing data as successful generated text.
                outputs.append({'query_id': q['id'], 'status': response.status_code, 'latency_ms': (time.perf_counter() - started) * 1000, 'response': response.json(), 'human_unsupported_claim_review': 'PENDING', 'unsupported_claim_rate': None})
    directory = Path(args.output); directory.mkdir(parents=True, exist_ok=True)
    with (directory / 'retrieval.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    metadata = {'queries': len(queries), 'test_queries': sum(q['split'] == 'test' for q in queries), 'methods': methods, 'groq_requests': len(outputs), 'process_peak_rss_bytes': peak if sys.platform == 'darwin' else peak * 1024, 'rss_note': 'Whole-process high-water mark, not isolated per-method memory.', 'claim_review': 'Human unsupported-claim annotations pending; no rate fabricated.'}
    (directory / 'metadata.json').write_text(json.dumps(metadata, indent=2)); (directory / 'generation.json').write_text(json.dumps(outputs, indent=2))
    print(json.dumps(metadata, indent=2))

def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--queries', required=True); parser.add_argument('--output', default=str(ROOT / 'reports/mvp/results')); parser.add_argument('--confirm-human-labels', action='store_true'); parser.add_argument('--k', type=int, choices=range(1, 6), default=4); parser.add_argument('--include-groq', action='store_true'); parser.add_argument('--api-url'); args = parser.parse_args()
    try: asyncio.run(run(args))
    except Exception as error: parser.exit(1, f'Evaluation stopped: {type(error).__name__}: {error}\n')
if __name__ == '__main__': main()
