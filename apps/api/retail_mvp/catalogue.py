"""Portable fitted TF-IDF inference; optional offline distilled semantic projection."""
from collections import Counter
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import re
import unicodedata
from urllib.parse import urlparse
from .config import ROOT
from .models import Preferences

STOP = set('a an the is are i me my for to of with and or please show find looking need want some any can you have do it that these those under below above budget than more less cheaper'.split())

def tokens(text: str) -> list[str]:
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode().lower()
    return [t for t in re.findall(r'[a-z0-9]+(?:-[a-z0-9]+)?', text) if t not in STOP]

def safe_url(url: str | None) -> str | None:
    if not url:
        return None
    parsed = urlparse(url)
    if parsed.scheme not in {'http', 'https'} or parsed.hostname not in {'healthyu.co.ke', 'www.healthyu.co.ke'} or parsed.username or parsed.password:
        return None
    return parsed._replace(scheme='https', query='', fragment='').geturl()

class NotReady(Exception):
    pass

class Catalogue:
    def __init__(self, directory: Path):
        try:
            manifest = json.loads((directory / 'manifest.json').read_text())
            raw = (directory / 'products.json').read_bytes()
            lexical_raw = (directory / 'lexical.json').read_bytes()
            if manifest.get('source_kind') != 'healthyu_export' or not manifest.get('permission_approved') or manifest.get('currency') != 'KES':
                raise NotReady('unapproved_catalogue')
            if hashlib.sha256(raw).hexdigest() != manifest['products_sha256'] or hashlib.sha256(lexical_raw).hexdigest() != manifest['lexical_sha256']:
                raise NotReady('artifact_integrity_mismatch')
            self.products = json.loads(raw)
            self.lexical = json.loads(lexical_raw)
            if not self.products or [p['id'] for p in self.products] != self.lexical['product_ids']:
                raise NotReady('artifact_alignment_mismatch')
            if len(self.products) > 20000 or len({p['id'] for p in self.products}) != len(self.products):
                raise NotReady('invalid_catalogue_size_or_ids')
            if any(p.get('currency') != 'KES' or not safe_url(p.get('url')) for p in self.products):
                raise NotReady('invalid_product_provenance')
            self.manifest = manifest
            self.semantic = None
            semantic_path = directory / 'semantic.npz'
            if semantic_path.exists():
                if hashlib.sha256(semantic_path.read_bytes()).hexdigest() != manifest.get('semantic_sha256'):
                    raise NotReady('semantic_integrity_mismatch')
                import numpy as np
                self.semantic = np.load(semantic_path, allow_pickle=False)
                if self.semantic['vectors'].ndim != 2 or self.semantic['projection'].ndim != 2 or self.semantic['vectors'].shape[0] != len(self.products) or self.semantic['projection'].shape != (len(self.lexical['vocabulary']), self.semantic['vectors'].shape[1]) or not np.isfinite(self.semantic['vectors']).all() or not np.isfinite(self.semantic['projection']).all():
                    raise NotReady('semantic_alignment_mismatch')
        except NotReady:
            raise
        except (OSError, KeyError, ValueError, TypeError):
            raise NotReady('catalogue_or_index_missing') from None

    @property
    def method(self) -> str:
        return 'hybrid_offline_projected_minilm' if self.semantic is not None else 'fitted_tfidf'

    def eligible(self, p: dict, c: Preferences) -> bool:
        price = p.get('price')
        if c.max_price is not None and (price is None or price > c.max_price):
            return False
        if c.min_price is not None and (price is None or price < c.min_price):
            return False
        if c.category and not any(c.category.casefold() in v.casefold() for v in p['category']):
            return False
        if c.brand and (p.get('brand') or '').casefold() != c.brand.casefold():
            return False
        if c.in_stock and p.get('stock') != 'in_stock':
            return False
        labels = {x.casefold() for x in p.get('verified_labels', [])}
        if any(label.casefold() not in labels for label in c.required_labels):
            return False
        # Absence of an allergen word is NOT evidence that a product is allergen-free.
        if c.excluded_ingredients:
            ingredients = p.get('ingredients')
            if not ingredients:
                return False
            text = ' '.join(ingredients).casefold()
            if any(word.casefold() in text for word in c.excluded_ingredients):
                return False
        return True

    def search(self, query: str, c: Preferences, k: int = 4, method: str = 'hybrid') -> list[dict]:
        counts = Counter(tokens(query))
        q = {word: (1 + math.log(count)) * self.lexical['idf'][word] for word, count in counts.items() if word in self.lexical['idf']}
        norm = math.sqrt(sum(v * v for v in q.values()))
        if not norm:
            return []
        q = {word: value / norm for word, value in q.items()}
        scores = [0.0] * len(self.products)
        for word, weight in q.items():
            for index, document_weight in self.lexical['postings'].get(word, []):
                scores[index] += weight * document_weight
        eligible = [i for i, p in enumerate(self.products) if self.eligible(p, c)]
        lexical = sorted((i for i in eligible if scores[i] > 0), key=lambda i: (-scores[i], self.products[i]['id']))
        ranked = lexical
        if self.semantic is not None and method != 'lexical':
            import numpy as np
            vocabulary = self.lexical['vocabulary']
            positions = {word: i for i, word in enumerate(vocabulary)}
            projection = self.semantic['projection']
            vector = sum((projection[positions[word]] * value for word, value in q.items()), start=np.zeros(projection.shape[1], dtype=np.float32))
            length = float(np.linalg.norm(vector))
            if length:
                similarities = self.semantic['vectors'] @ (vector / length)
                semantic = sorted((i for i in eligible if similarities[i] > 0), key=lambda i: (-float(similarities[i]), self.products[i]['id']))
                if method == 'semantic':
                    ranked = semantic
                else:
                    fused = {}
                    for ordering in [lexical, semantic]:
                        for rank, index in enumerate(ordering):
                            fused[index] = fused.get(index, 0.0) + 1.0 / (60 + rank + 1)
                    ranked = sorted(fused, key=lambda i: (-fused[i], self.products[i]['id']))
        elif method == 'semantic':
            raise NotReady('semantic_artifact_missing')
        return [self.products[i] for i in ranked[:k]]

@lru_cache(maxsize=1)
def get_catalogue() -> Catalogue:
    return Catalogue(ROOT / 'catalogue')
