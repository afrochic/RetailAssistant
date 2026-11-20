"""MANUAL ONLY: allowlisted Client X export and reproducible fitted retrieval artifacts."""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import hashlib
from html import unescape
from html.parser import HTMLParser
import json
import math
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'apps/api'))
from retail_mvp.catalogue import tokens  # noqa: E402
from retail_mvp.privacy import public_text  # noqa: E402

class Plain(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts = []; self.hidden = 0
    def handle_starttag(self, tag, attrs):
        if tag in {'script', 'style'}: self.hidden += 1
    def handle_endtag(self, tag):
        if tag in {'script', 'style'}: self.hidden = max(0, self.hidden - 1)
    def handle_data(self, data):
        if not self.hidden: self.parts.append(data)

def plain(value):
    parser = Plain(); parser.feed(str(value or ''))
    return re.sub(r'\s+', ' ', re.sub(r'\[/?vc_[^\]]*\]', '', unescape(' '.join(parser.parts)))).strip()

def write_json(path, value):
    data = json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp'); temporary.write_bytes(data); temporary.replace(path)
    return hashlib.sha256(data).hexdigest()

def ingest(args):
    if not args.approved or args.currency != 'KES':
        raise ValueError('Explicit approved-source acknowledgement and confirmed KES currency are required.')
    source = Path(args.source).expanduser().resolve()
    raw = source.read_bytes(); rows = json.loads(raw)
    if not isinstance(rows, list): raise ValueError('Expected the approved Client X JSON product export array.')
    products = []; seen = set(); rejected = Counter()
    for record in rows:
        if not isinstance(record, dict): rejected['non_object'] += 1; continue
        pid = str(record.get('ID') or record.get('Product ID') or '').strip()
        name = public_text(plain(record.get('Name')), args.redact_term)
        if not pid or not name: rejected['missing_id_or_name'] += 1; continue
        if pid in seen: rejected['duplicate_id'] += 1; continue
        price = None
        try:
            value = Decimal(str(record.get('RRP', record.get('Regular price', ''))).replace(',', '').strip())
            if value.is_finite() and value > 0: price = float(value.quantize(Decimal('.01'), rounding=ROUND_HALF_UP))
        except (InvalidOperation, ValueError, TypeError): pass
        products.append({'id': pid, 'sku': public_text(str(record.get('SKU') or ''), args.redact_term), 'name': name[:300], 'description': public_text(plain(record.get('Description') or record.get('Short description')), args.redact_term)[:6000], 'category': [public_text(plain(c), args.redact_term) for c in str(record.get('Categories') or '').split(',') if plain(c)], 'price': price, 'currency': 'KES', 'stock': 'unknown', 'brand': None, 'ingredients': None, 'verified_labels': [], 'url': None, 'source_record_id': pid})
        seen.add(pid)
    if not products: raise ValueError('No usable approved-source records; nothing written.')
    output = Path(args.output); digest = write_json(output / 'products.json', products)
    manifest = {'schema_version': 1, 'source_kind': 'client_x_export', 'client_label': 'Client X', 'retailer_links_redacted': True, 'source_filename': source.name, 'source_sha256': hashlib.sha256(raw).hexdigest(), 'source_snapshot_date': args.snapshot_date, 'extracted_at': datetime.now(timezone.utc).isoformat(), 'permission_approved': True, 'permission_basis': 'User confirmed public presentation MVP use and KES RRP on 2026-11-19; re-confirm broader reuse separately.', 'currency': 'KES', 'raw_count': len(rows), 'count': len(products), 'rejected': dict(rejected), 'missing_prices': sum(p['price'] is None for p in products), 'products_sha256': digest, 'limitations': ['No live stock', 'No structured brand/ingredients/allergens/verified dietary labels', 'Marketing descriptions are not clinical evidence', 'Snapshot date not provided unless supplied by operator']}
    write_json(output / 'manifest.json', manifest)
    # Discard stale indexes so a changed snapshot cannot silently use old vectors.
    for name in ['lexical.json', 'semantic.npz']:
        path = output / name
        if path.exists(): path.unlink()
    print(json.dumps({'products': len(products), 'rejected': dict(rejected), 'next': 'Run the index subcommand before serving.'}, indent=2))

def fit(args):
    output = Path(args.output); products = json.loads((output / 'products.json').read_text()); manifest = json.loads((output / 'manifest.json').read_text())
    if manifest.get('source_kind') != 'client_x_export' or not manifest.get('permission_approved'): raise ValueError('Approved Client X manifest required.')
    if hashlib.sha256((output / 'products.json').read_bytes()).hexdigest() != manifest['products_sha256']: raise ValueError('Snapshot was changed after ingestion.')
    texts = [(p['name'] + ' ') * 2 + ' '.join(p['category']) + ' ' + p['description'] for p in products]
    counts = [Counter(tokens(text)) for text in texts]; df = Counter(word for c in counts for word in c)
    vocabulary = sorted(sorted(df, key=lambda w: (-df[w], w))[:args.max_features]); allowed = set(vocabulary)
    idf = {word: math.log((1 + len(products)) / (1 + df[word])) + 1 for word in vocabulary}
    postings = defaultdict(list); sparse_rows = []
    positions = {word: i for i, word in enumerate(vocabulary)}
    for i, counter in enumerate(counts):
        weights = {word: (1 + math.log(n)) * idf[word] for word, n in counter.items() if word in allowed}
        norm = math.sqrt(sum(v * v for v in weights.values())) or 1
        sparse_rows.append({positions[word]: value / norm for word, value in weights.items()})
        for word, value in weights.items(): postings[word].append([i, round(value / norm, 9)])
    lexical = {'schema_version': 1, 'product_ids': [p['id'] for p in products], 'vocabulary': vocabulary, 'idf': idf, 'postings': dict(postings)}
    manifest['lexical_sha256'] = write_json(output / 'lexical.json', lexical)
    manifest['fitted_at'] = datetime.now(timezone.utc).isoformat(); manifest['retrieval'] = 'fitted_tfidf'; manifest['seed'] = 42
    if args.semantic:
        import numpy as np
        from scipy.sparse import csr_matrix
        from sklearn.decomposition import PCA
        from sklearn.linear_model import Ridge
        from sentence_transformers import SentenceTransformer
        if not args.model_revision: raise ValueError('--model-revision must be an explicit pinned Hugging Face commit; do not use main.')
        if not re.fullmatch(r'[0-9a-f]{40}', args.model_revision): raise ValueError('Expected a 40-character commit revision.')
        rr = []; cc = []; vv = []
        for row, weights in enumerate(sparse_rows):
            for col, value in weights.items(): rr.append(row); cc.append(col); vv.append(value)
        x = csr_matrix((vv, (rr, cc)), shape=(len(products), len(vocabulary)), dtype=np.float32)
        teacher = SentenceTransformer(args.model, revision=args.model_revision)
        embedding = teacher.encode(texts, batch_size=32, normalize_embeddings=True, show_progress_bar=True)
        dimensions = min(96, len(products) - 1, embedding.shape[1])
        if dimensions < 2: raise ValueError('Semantic fitting needs at least three records.')
        y = PCA(n_components=dimensions, random_state=42).fit_transform(embedding).astype(np.float32)
        ridge = Ridge(alpha=5.0, solver='lsqr', fit_intercept=False).fit(x, y)
        vectors = y / np.maximum(np.linalg.norm(y, axis=1, keepdims=True), 1e-9)
        np.savez_compressed(output / 'semantic.npz', vectors=vectors, projection=ridge.coef_.T.astype(np.float32))
        manifest.update(semantic_sha256=hashlib.sha256((output / 'semantic.npz').read_bytes()).hexdigest(), retrieval='hybrid_offline_projected_minilm', semantic_model=args.model, semantic_revision=args.model_revision, semantic_dimensions=dimensions, semantic_query_encoder='Offline-fitted TF-IDF-to-teacher projection; approximate, not a transformer at query time.', fusion='Reciprocal rank fusion, k=60, equal lexical/semantic weights')
    else:
        (output / 'semantic.npz').unlink(missing_ok=True)
        for key in ['semantic_sha256', 'semantic_model', 'semantic_revision', 'semantic_dimensions', 'semantic_query_encoder', 'fusion']: manifest.pop(key, None)
    write_json(output / 'manifest.json', manifest)
    print(json.dumps({'products': len(products), 'features': len(vocabulary), 'retrieval': manifest['retrieval'], 'status': 'Artifacts written by the operator. Evaluation still required.'}, indent=2))

def main():
    parser = argparse.ArgumentParser(description=__doc__); commands = parser.add_subparsers(dest='command', required=True)
    default = str(ROOT / 'apps/api/catalogue')
    p = commands.add_parser('ingest', help='Read an approved local product export; never touches original client application or databases.')
    p.add_argument('--source', required=True); p.add_argument('--redact-term', action='append', default=[], help='Private client alias to replace; do not store private values in public commands.'); p.add_argument('--output', default=default); p.add_argument('--currency', choices=['KES'], required=True); p.add_argument('--approved', action='store_true'); p.add_argument('--snapshot-date', default=None); p.set_defaults(run=ingest)
    p = commands.add_parser('index', help='Fit the lexical baseline; optional offline teacher embeddings and lightweight query projection.')
    p.add_argument('--output', default=default); p.add_argument('--max-features', type=int, default=12000); p.add_argument('--semantic', action='store_true'); p.add_argument('--model', default='sentence-transformers/all-MiniLM-L6-v2'); p.add_argument('--model-revision', default='1110a243fdf4706b3f48f1d95db1a4f5529b4d41'); p.set_defaults(run=fit)
    args = parser.parse_args()
    try: args.run(args)
    except Exception as error: parser.exit(1, f'Preparation stopped safely: {type(error).__name__}: {error}\n')
if __name__ == '__main__': main()
