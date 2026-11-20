"""Privacy regressions use invented private labels, never a real client identity."""
import hashlib
import json
import pytest
from retail_mvp.catalogue import Catalogue, NotReady


def test_public_text_removes_configured_name_and_urls():
    from retail_mvp.privacy import public_text
    result = public_text('Private Example Store stocks oats: https://shop.example/products/oats', ['Private Example Store'])
    assert 'Private Example Store' not in result
    assert 'shop.example' not in result
    assert 'Client X' in result


def test_redacted_url_requires_explicit_manifest_contract(tmp_path):
    products = [{'id':'FIXTURE','name':'Fixture oats','category':['Food'],'price':50,'currency':'KES','url':None}]
    lexical = {'product_ids':['FIXTURE'],'vocabulary':['oats'],'idf':{'oats':1},'postings':{'oats':[[0,1]]}}
    raw=json.dumps(products).encode(); idx=json.dumps(lexical).encode()
    (tmp_path/'products.json').write_bytes(raw); (tmp_path/'lexical.json').write_bytes(idx)
    manifest={'source_kind':'client_x_export','permission_approved':True,'currency':'KES','client_label':'Client X','retailer_links_redacted':True,'products_sha256':hashlib.sha256(raw).hexdigest(),'lexical_sha256':hashlib.sha256(idx).hexdigest()}
    (tmp_path/'manifest.json').write_text(json.dumps(manifest))
    assert Catalogue(tmp_path).products[0]['url'] is None
    manifest.pop('retailer_links_redacted')
    (tmp_path/'manifest.json').write_text(json.dumps(manifest))
    with pytest.raises(NotReady):
        Catalogue(tmp_path)
