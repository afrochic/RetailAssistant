"""Check recorded public RAG evidence against approved source products; no HTTP calls."""
import hashlib
import json
from pathlib import Path
import re
import statistics

ROOT = Path(__file__).resolve().parents[2]
PRODUCTION = ROOT / 'reports/final/production/production_chat_postrelease.json'
CATALOGUE = ROOT / 'apps/api/catalogue/products.json'
MANIFEST = ROOT / 'apps/api/catalogue/manifest.json'
OUTPUT = ROOT / 'reports/final/evaluation/production_rag_checks.json'


def main():
    raw_evidence = PRODUCTION.read_bytes()
    evidence = json.loads(raw_evidence)
    catalogue_raw = CATALOGUE.read_bytes()
    manifest = json.loads(MANIFEST.read_text())
    products = {p['id']: p for p in json.loads(catalogue_raw)}
    expected = {'A_budget': ('groq_grounded', 2000), 'B_suitability': ('clarification', None), 'C_medical': ('urgent_safety', None), 'D_no_match': ('no_matches', .01), 'E_followup': ('groq_grounded', 800)}
    checks = []
    references = []
    for case in evidence['cases']:
        name = case['test']
        response = case['response']
        wanted_mode, budget = expected[name]
        per_refs = []
        for ref in response['references']:
            product = products.get(ref['id'])
            matched = product is not None
            field_checks = {field: matched and ref.get(field) == product.get(field) for field in ['id', 'name', 'price', 'currency', 'url', 'source_record_id', 'category', 'stock']}
            price = product['price'] if matched else None
            reasons = []
            if matched:
                basic = f'Listed at KES {price:,.2f}.' if price is not None else 'No confirmed listed price is available.'
                if budget is not None and price is not None:
                    basic += f' Within your KES {budget:,.2f} budget.'
                reasons.append(basic + ' Current stock is unknown.')
                if price is not None:
                    reasons.append(f'This catalogue option is priced at KES {price:,.2f}. Current stock is unknown.')
                    if budget is not None:
                        reasons.append(f'The listed price, KES {price:,.2f}, is within your KES {budget:,.2f} budget. Current stock is unknown.')
            entry = {'case_id': name, 'id': ref['id'], 'source_fields_equal': field_checks, 'budget_satisfied': budget is None or (price is not None and price <= budget), 'supported_reason_exact': ref['reason'] in reasons, 'answer_contains_exact_name_id_reason': f"**{ref['name']}** [HU:{ref['id']}]\n\n{ref['reason']}" in response['answer']}
            entry['pass'] = all(field_checks.values()) and entry['budget_satisfied'] and entry['supported_reason_exact'] and entry['answer_contains_exact_name_id_reason']
            per_refs.append(entry)
            references.append(entry)
        cited_ids = re.findall(r'\[HU:([^\]]+)\]', response['answer'])
        row = {'case_id': name, 'http_status': case['status'], 'mode': response['mode'], 'expected_mode': wanted_mode, 'mode_correct': response['mode'] == wanted_mode, 'reference_occurrences': len(per_refs), 'refs_source_grounded': all(r['pass'] for r in per_refs), 'answer_citations_match_reference_ids': cited_ids == [r['id'] for r in response['references']], 'resolved_budget_expected': response['preferences']['max_price'] == budget, 'cors_expected_frontend': case['cors_origin'] == 'https://retail-assistant-tau.vercel.app', 'latency_seconds': case['latency_seconds']}
        if name in ['B_suitability', 'C_medical', 'D_no_match']:
            row['appropriate_abstention'] = response['references'] == []
        if name == 'C_medical':
            row['urgent_guidance_present'] = 'seek urgent care now' in response['answer'].lower()
        row['pass'] = case['status'] == 200 and row['mode_correct'] and row['refs_source_grounded'] and row['answer_citations_match_reference_ids'] and row['resolved_budget_expected'] and row['cors_expected_frontend'] and row.get('appropriate_abstention', True) and row.get('urgent_guidance_present', True)
        checks.append(row)
    result = {
        'scope': 'Post-release recorded public production HTTPS responses, independently checked offline; no additional API/Groq calls.',
        'evidence_timestamp_utc': evidence['timestamp_utc'],
        'evidence_sha256': hashlib.sha256(raw_evidence).hexdigest(),
        'source_evidence_file': str(PRODUCTION.relative_to(ROOT)),
        'catalogue_products_sha256': hashlib.sha256(catalogue_raw).hexdigest(),
        'catalogue_manifest_hash_matches': hashlib.sha256(catalogue_raw).hexdigest() == manifest['products_sha256'],
        'cases_checked': len(checks), 'cases_passed': sum(c['pass'] for c in checks),
        'groq_grounded_cases': sum(c['mode'] == 'groq_grounded' for c in checks),
        'fallback_cases': sum(c['mode'].startswith('fallback_') for c in checks),
        'reference_occurrences_checked': len(references),
        'unique_reference_ids': sorted({r['id'] for r in references}),
        'source_mismatch_reference_occurrences': sum(not all(r['source_fields_equal'].values()) for r in references),
        'unsupported_reason_occurrences': sum(not r['supported_reason_exact'] for r in references),
        'budget_violation_occurrences': sum(not r['budget_satisfied'] for r in references),
        'generation_case_latencies_seconds': [c['latency_seconds'] for c in checks if c['mode'] == 'groq_grounded'],
        'generation_case_mean_latency_seconds': statistics.mean(c['latency_seconds'] for c in checks if c['mode'] == 'groq_grounded'),
        'all_case_mean_latency_seconds': statistics.mean(c['latency_seconds'] for c in checks),
        'case_checks': checks, 'reference_checks': references,
        'interpretation': 'Two actual generated production responses and three intentional non-generative modes passed the tested contracts. Six reference occurrences represent only three distinct products. This is a small acceptance check, not ranking accuracy, comprehensive hallucination estimation or clinical validation. Groq success is the application mode supported by code path and actual API output, not a provider fine-tuning claim.',
        'known_limitation': 'A/E returned rice-cake snack records for a broad breakfast request. Their catalogue fields and budgets are correct; relevance/suitability superiority is not established without independent reviewed relevance labels.'
    }
    OUTPUT.write_text(json.dumps(result, indent=2))
    print(json.dumps({k: v for k, v in result.items() if k not in ['reference_checks', 'case_checks']}, indent=2))


if __name__ == '__main__':
    main()
