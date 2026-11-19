"""Reproducible data-quality and retrieval diagnostics; no relevance labels or LLM calls.

This diagnostic deliberately does not compute ranking quality without reviewed labels.
Run with Python 3.12 from the repository root after approved ingestion/index fitting.
"""
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import csv
import hashlib
import json
from pathlib import Path
import statistics
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'apps/api'))
from retail_mvp.catalogue import Catalogue  # noqa: E402
from retail_mvp.models import Preferences  # noqa: E402

OUT = ROOT / 'reports/final/evaluation'
SOURCE = ROOT.parent / 'rag_pipeline/data/Enhanced_Product_List.json'


def write_csv(name, rows):
    with (OUT / name).open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def percentile(values, probability):
    values = sorted(values)
    position = (len(values) - 1) * probability
    low = int(position)
    high = min(low + 1, len(values) - 1)
    return values[low] + (values[high] - values[low]) * (position - low)


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    original_bytes = SOURCE.read_bytes()
    raw = json.loads(original_bytes)
    start = time.perf_counter()
    catalogue = Catalogue(ROOT / 'apps/api/catalogue')
    load_ms = (time.perf_counter() - start) * 1000
    products = catalogue.products
    ids = {p['id'] for p in products}
    fields = ['name', 'description', 'price', 'category', 'sku', 'brand', 'ingredients', 'verified_labels']
    missing = [{'field': f, 'missing_count': sum(p.get(f) in [None, '', []] for p in products), 'total': len(products)} for f in fields]
    missing.append({'field': 'verified_stock', 'missing_count': sum(p.get('stock') == 'unknown' for p in products), 'total': len(products)})
    categories = Counter(c for p in products for c in p['category'])
    prices = [p['price'] for p in products if p['price'] is not None]
    raw_ids = Counter(str(p.get('ID') or '').strip() for p in raw)
    normalized_names = Counter(' '.join(p['name'].casefold().split()) for p in products)
    raw_invalid_prices = 0
    for p in raw:
        try:
            d = Decimal(str(p.get('RRP', '')).replace(',', '').strip())
            raw_invalid_prices += int(not d.is_finite() or d <= 0)
        except (InvalidOperation, ValueError):
            raw_invalid_prices += 1
    source_by_id = {str(p['ID']): p for p in raw}
    mismatched_prices = 0
    for p in products:
        if p['price'] is not None:
            source_price = Decimal(str(source_by_id[p['source_record_id']]['RRP']).replace(',', ''))
            mismatched_prices += int(abs(float(source_price) - p['price']) > 0.0051)
    cases = [
        ('oats_budget', 'breakfast oats', {'max_price': 1000}, False),
        ('tea_budget', 'tea', {'max_price': 1500}, False),
        ('coconut_oil', 'coconut oil', {'max_price': 2000}, False),
        ('breakfast', 'healthy breakfast products', {'max_price': 2000}, False),
        ('snacks', 'snacks', {'max_price': 2000}, False),
        ('peanut_butter', 'peanut butter', {'max_price': 1500}, False),
        ('coffee', 'coffee', {'max_price': 1500}, False),
        ('seeds', 'chia seeds', {'max_price': 2000}, False),
        ('unsupported_label', 'snacks', {'required_labels': ['sugar free']}, True),
        ('unknown_ingredients', 'snacks', {'excluded_ingredients': ['sugar']}, True),
        ('unknown_stock', 'tea', {'in_stock': True}, True),
        ('absent_terms', 'zzqxjvnonexistentproduct', {}, True),
        ('impossible_budget', 'coconut oil', {'max_price': 0.01}, True),
    ]
    rows = []
    for name, query, values, abstain in cases:
        preferences = Preferences(currency='KES', **values)
        # One warm-up excluded from timed runs; loading measured separately.
        catalogue.search(query, preferences, 4, method='lexical')
        previous = None
        for repeat in range(20):
            started = time.perf_counter()
            result = catalogue.search(query, preferences, 4, method='lexical')
            latency = (time.perf_counter() - started) * 1000
            result_ids = [p['id'] for p in result]
            violations = sum(bool(p['currency'] != 'KES' or (values.get('max_price') is not None and (p['price'] is None or p['price'] > values['max_price'])) or (values.get('required_labels') and not set(values['required_labels']).issubset(set(p.get('verified_labels', [])))) or (values.get('excluded_ingredients') and not p.get('ingredients')) or (values.get('in_stock') and p.get('stock') != 'in_stock')) for p in result)
            rows.append({'case_id': name, 'query': query, 'method': 'lexical', 'repeat': repeat, 'k': 4, 'latency_ms': latency, 'returned': len(result), 'invalid_ids': sum(i not in ids for i in result_ids), 'constraint_violations': violations, 'expected_abstention': abstain, 'abstention_correct': not result if abstain else '', 'deterministic_repeat': previous is None or previous == result_ids, 'result_ids': '|'.join(result_ids), 'preferences': json.dumps(values, sort_keys=True)})
            previous = result_ids
    latencies = [r['latency_ms'] for r in rows]
    returned = sum(r['returned'] for r in rows)
    summary = {
        'measured_at_utc': datetime.now(timezone.utc).isoformat(),
        'python_version': sys.version.split()[0],
        'source_sha256': hashlib.sha256(original_bytes).hexdigest(),
        'source_hash_matches_manifest': hashlib.sha256(original_bytes).hexdigest() == catalogue.manifest['source_sha256'],
        'raw_records': len(raw), 'accepted_records': len(products), 'rejected_records': catalogue.manifest['rejected'],
        'duplicate_raw_id_occurrences': sum(n - 1 for i, n in raw_ids.items() if i and n > 1),
        'duplicate_normalized_name_groups': sum(n > 1 for n in normalized_names.values()),
        'duplicate_normalized_name_extra_occurrences': sum(n - 1 for n in normalized_names.values() if n > 1),
        'missing_price_records': len(products) - len(prices),
        'invalid_or_nonpositive_raw_prices': raw_invalid_prices,
        'price_rounding_mismatches_over_half_cent': mismatched_prices,
        'currency': 'KES', 'priced_records': len(prices),
        'price_min': min(prices), 'price_median': statistics.median(prices),
        'price_p95': percentile(prices, .95), 'price_max': max(prices),
        'distinct_category_labels': len(categories),
        'category_counting_note': 'Multiple category labels per product; counts overlap.',
        'method_available': catalogue.method, 'semantic_artifact_available': catalogue.semantic is not None,
        'tfidf_features': len(catalogue.lexical['vocabulary']),
        'artifact_sizes_bytes': {f: (ROOT / 'apps/api/catalogue' / f).stat().st_size for f in ['products.json', 'lexical.json', 'manifest.json']},
        'cold_artifact_load_ms': load_ms,
        'diagnostic_cases': len(cases), 'timed_repetitions_per_case': 20, 'timed_requests': len(rows),
        'latency_mean_ms': statistics.mean(latencies), 'latency_p50_ms': percentile(latencies, .5), 'latency_p95_ms': percentile(latencies, .95),
        'returned_reference_occurrences': returned,
        'invalid_reference_occurrences': sum(r['invalid_ids'] for r in rows),
        'constraint_violation_occurrences': sum(r['constraint_violations'] for r in rows),
        'constraint_satisfaction_rate_returned_references': (returned - sum(r['constraint_violations'] for r in rows)) / returned if returned else None,
        'expected_abstention_cases': sum(c[3] for c in cases),
        'abstention_case_passes': sum(all(r['abstention_correct'] for r in rows if r['case_id'] == c[0]) for c in cases if c[3]),
        'all_repeated_results_identical': all(r['deterministic_repeat'] for r in rows),
        'human_reviewed_relevance_labels_available': False,
        'precision_at_k': None, 'recall_at_k': None, 'mrr': None, 'ndcg_at_k': None,
        'ranking_quality_status': 'BLOCKED: independent human-reviewed Healthy U relevance labels are unavailable. Legacy INR/Flipkart query labels excluded.',
        'latency_scope': 'Single local Python process; warm per-query pure retrieval only, excluding network, Groq, startup and UI. Diagnostic cases are not independent sampled research judgments.',
        'no_training_claim': 'Only lexical corpus statistics fitted; GPT-OSS was neither trained nor fine-tuned. Semantic/hybrid optional code not executed.',
    }
    (OUT / 'offline_summary.json').write_text(json.dumps(summary, indent=2))
    write_csv('missing_data.csv', missing)
    write_csv('categories.csv', [{'category': c, 'product_assignments': n} for c, n in categories.most_common()])
    write_csv('prices.csv', [{'product_id': p['id'], 'price_kes': p['price']} for p in products if p['price'] is not None])
    write_csv('retrieval_diagnostics.csv', rows)
    (OUT / 'artifact_manifest.json').write_text(json.dumps(catalogue.manifest, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    run()
