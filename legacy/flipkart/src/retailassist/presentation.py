"""Catalogue presentation metadata; independent of retrieval model fitting."""
import json
from urllib.parse import urlparse
from .core import ROOT

CATEGORIES = ['Clothing', 'Footwear', 'Mobiles & Accessories', 'Computers', 'Home Decor & Festive Needs', 'Kitchen & Dining', 'Bags, Wallets & Belts', 'Watches', 'Beauty and Personal Care', 'Jewellery', 'Home Furnishing', 'Sports & Fitness', 'Toys & School Supplies', 'Furniture']

def image_lookup(raw):
    """Preserve the actual listing image path, upgrading the obsolete CDN hostname."""
    images = {}
    for _, row in raw[['pid','image']].dropna().iterrows():
        try:
            urls = json.loads(row['image'])
            if not isinstance(urls, list) or not urls or not isinstance(urls[0], str):
                continue
            parsed = urlparse(urls[0])
            if parsed.scheme not in ('http', 'https') or not parsed.hostname or not parsed.hostname.endswith('.flixcart.com') or not parsed.path.startswith('/image/'):
                continue
            images.setdefault(str(row['pid']), 'https://rukminim2.flixcart.com' + parsed.path)
        except (ValueError, TypeError):
            continue
    return images

def save_images(raw):
    (ROOT/'artifacts/product_images.json').write_text(json.dumps(image_lookup(raw)))

def load_images():
    path = ROOT/'artifacts/product_images.json'
    return json.loads(path.read_text()) if path.exists() else {}

def enrich(products, images):
    return [{**p, 'image_url': images.get(p['id'])} for p in products]
