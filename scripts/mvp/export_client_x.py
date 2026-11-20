"""Create a name-redacted, product-only distribution source from an approved private export.

No customer/order fields or retailer URLs are copied. This is client-name redaction,
not a guarantee that product text cannot be reidentified from external catalogues.
"""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'apps/api'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from retail_mvp.privacy import public_text  # noqa: E402
from prepare import plain, write_json  # noqa: E402


def export(source, output, private_terms):
    records = json.loads(Path(source).read_text())
    if not isinstance(records, list):
        raise ValueError('Approved export must be a product array.')
    result = []
    for record in records:
        if not isinstance(record, dict):
            continue
        cleaned = {key: public_text(plain(record.get(key)), private_terms)
                   for key in ['ID', 'SKU', 'Name', 'Description', 'Categories']}
        cleaned['RRP'] = record.get('RRP')
        result.append(cleaned)
    if not result:
        raise ValueError('No products; distribution source not written.')
    digest = write_json(Path(output), result)
    return {'records': len(result), 'sha256': digest, 'retailer_urls_copied': False,
            'fields': ['ID', 'SKU', 'Name', 'Description', 'Categories', 'RRP']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True)
    parser.add_argument('--output', default=str(ROOT / 'data/client_x_catalogue.json'))
    parser.add_argument('--redact-term', action='append', required=True,
                        help='Private alias to redact; do not put actual names in public commands.')
    parser.add_argument('--approved', action='store_true', required=True)
    args = parser.parse_args()
    print(json.dumps(export(args.source, args.output, args.redact_term), indent=2))


if __name__ == '__main__':
    main()
