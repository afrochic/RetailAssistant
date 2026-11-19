import numpy as np
import pandas as pd
import pytest
from sklearn.feature_extraction.text import TfidfVectorizer
from retailassist.core import Engine, prepare, explain
from retailassist.evaluate import metrics
from retailassist.api import Request

@pytest.fixture
def engine():
    df=pd.DataFrame([{'id':'a','name':'Running shoe','brand':'Acme','category':'Footwear','price':500.,'rating':4.,'currency':'INR','availability':'unknown','url':'https://example.com/a','text':'running shoe jog sports'}, {'id':'b','name':'Luxury shoe','brand':'Other','category':'Footwear','price':5000.,'rating':None,'currency':'INR','availability':'unknown','url':'https://example.com/b','text':'running shoe luxury sports'}])
    v=TfidfVectorizer();x=v.fit_transform(df.text)
    return Engine({'products':df,'vectorizer':v,'tfidf':x})
def test_budget_and_brand(engine):
    r=engine.search('running shoe by Acme below INR 1,000',method='tfidf')
    assert [p['id'] for p in r['products']]==['a'];assert r['constraints']['max_price']==1000
@pytest.mark.parametrize('c',[{'max_price':1},{'in_stock':True},{'category':'Unknown'},{'min_rating':5}])
def test_impossible_constraints_abstain(engine,c):
    assert engine.search('running shoe',method='tfidf',constraints=c)['products']==[]
def test_currency_rejected(engine):
    with pytest.raises(ValueError):engine.search('running shoes under USD 80000',method='tfidf')
def test_conflicting_budget(engine):
    with pytest.raises(ValueError):engine.search('shoes',method='tfidf',constraints={'min_price':10,'max_price':1})
def test_schema():
    with pytest.raises(ValueError):Request(query='shoes',k=21)
    with pytest.raises(ValueError):Request(query='shoes',constraints={'max_price':-1})
def test_metric_hand_calculation():
    m=metrics(['a','x','b'],{'a','b'});assert m['precision_at_5']==.4;assert m['recall_at_5']==1;assert m['mrr_at_5']==1;assert 0<m['ndcg_at_5']<1
def test_llm_invented_id_fallback(engine,monkeypatch):
    import requests
    class Response:
        def raise_for_status(self):pass
        def json(self):return {'choices':[{'message':{'content':'{"explanations":[{"product_id":"invented","text":"Invented"}]}'}}]}
    monkeypatch.setenv('OPENAI_API_KEY','fake-test-key');monkeypatch.setattr(requests,'post',lambda *a,**k:Response())
    r=explain(engine.search('running shoe',method='tfidf'),True,provider='openai')
    assert r['generation_mode']=='llm_failed_safe_fallback';assert 'invented' not in r['answer']
def test_api(engine,monkeypatch):
    from fastapi.testclient import TestClient
    import retailassist.api as api
    monkeypatch.setattr(api,'Engine',lambda:engine)
    with TestClient(api.app) as client:
        assert client.get('/health').status_code==200
        assert client.get('/').status_code==200
        r=client.post('/recommend',json={'query':'running shoe under INR 1000','method':'tfidf'})
        assert r.status_code==200;assert len(r.json()['products'])==1
        assert client.post('/recommend',json={'query':'shoe','k':0}).status_code==422
def test_cleaning_retains_unknowns_and_rejects_bad_prices():
    rows=[]
    for pid,price in [('a','500'),('a','500'),('b','bad'),('c','-2')]:
        rows.append({'pid':pid,'product_name':'Test mug','description':None,'brand':None,'product_category_tree':'["Kitchen & Dining >> Mugs"]','discounted_price':price,'product_rating':'No rating available','product_url':'https://example.com'})
    clean,audit=prepare(pd.DataFrame(rows))
    assert len(clean)==1 and audit['removed_rows']==3
    assert clean.iloc[0].brand=='Unknown' and pd.isna(clean.iloc[0].rating)
    assert clean.iloc[0].availability=='unknown'
def test_llm_valid_selection(engine,monkeypatch):
    import requests
    class Response:
        def raise_for_status(self):pass
        def json(self):return {'choices':[{'message':{'content':'{"explanations":[{"product_id":"a","text":"This option is listed at INR 500.00 in Footwear. Stock availability is unknown."}]}'}}]}
    monkeypatch.setenv('OPENAI_API_KEY','fake-test-key');monkeypatch.setattr(requests,'post',lambda *a,**k:Response())
    r=explain(engine.search('running shoe',method='tfidf'),True,provider='openai')
    assert r['generation_mode']=='openai_llm'
    assert r['explanations'][0]['source']=='openai_llm'
    assert r['explanations'][1]['source']=='fact_fallback'

def test_plain_brand_word_does_not_overfilter(engine):
    # A catalogue brand token in prose is not always an intended brand constraint.
    assert 'brand' not in engine.parse('Acme running shoe')
    assert engine.parse('running shoe by Acme')['brand']=='Acme'

def test_catalogue_discovery_details_and_assets(engine,monkeypatch):
    from fastapi.testclient import TestClient
    import retailassist.api as api
    monkeypatch.setattr(api,'Engine',lambda:engine)
    with TestClient(api.app) as client:
        catalogue=client.get('/catalogue').json()
        assert catalogue['total']==2 and catalogue['currency']=='INR'
        assert catalogue['semantic_available'] is False
        assert catalogue['categories']==[{'name':'Footwear','count':2}]
        products=client.get('/discover').json()['products']
        assert len({p['id'] for p in products})==len(products)
        assert all('image_url' in p for p in products)
        details=client.get('/products/a').json()
        assert details['name']=='Running shoe' and details['price']==500.
        assert details['availability']=='unknown' and details['description']==''
        assert client.get('/products/does-not-exist').status_code==404
        assert client.get('/assets/style.css').status_code==200
        assert client.get('/assets/app.js').status_code==200

def test_listing_image_provenance_and_host_validation():
    from retailassist.presentation import image_lookup
    raw=pd.DataFrame([
        {'pid':'a','image':'["http://img5a.flixcart.com/image/shoe/original.jpeg"]'},
        {'pid':'b','image':'["https://attacker.example/image/fake.jpeg"]'},
        {'pid':'c','image':'not json'},
        {'pid':'d','image':'["https://flixcart.com.attacker.example/image/fake.jpeg"]'},
        {'pid':'e','image':'"https://img5a.flixcart.com/image/string-not-list.jpeg"'},
    ])
    assert image_lookup(raw)=={'a':'https://rukminim2.flixcart.com/image/shoe/original.jpeg'}

def test_insights_uses_real_catalogue_counts(engine,monkeypatch):
    from fastapi.testclient import TestClient
    import retailassist.api as api
    monkeypatch.setattr(api,'Engine',lambda:engine)
    with TestClient(api.app) as client:
        data=client.get('/insights').json()
        catalogue=data['catalogue']
        assert catalogue['total_products']==2
        assert catalogue['brands']==2 and catalogue['unknown_brands']==0
        assert catalogue['rated_products']==1 and catalogue['unknown_stock']==2
        assert catalogue['median_price']==2750.
        assert sum(bucket['count'] for bucket in catalogue['price_distribution'])==2
        assert sum(c['count'] for c in catalogue['top_categories'])==2
        assert data['model']['semantic_available'] is False
        assert 'silver' in data['evaluation_note']


def test_kes_conversion_budget_and_provenance(engine):
    r=engine.search('running shoe under KSh 700',method='tfidf')
    assert r['currency']=='KES' and len(r['products'])==1
    p=r['products'][0]
    assert p['price']==685.0 and p['source_price']==500.0
    assert p['source_currency']=='INR' and p['price_is_estimate'] is True
    assert p['conversion']['rate']==1.37
    assert engine.search('running shoe',method='tfidf',currency='KES',constraints={'max_price':684.99})['products']==[]
    with pytest.raises(ValueError):engine.search('running shoe under INR 1000',method='tfidf',currency='KES')

def test_claim_checks_reject_invented_attributes_and_prices():
    from retailassist.generation import check_claims
    p={'name':'Shoe','brand':'Acme','category':'Footwear','price':500.,'currency':'INR','rating':4.,'availability':'unknown'}
    assert check_claims('This option is listed at INR 500.00 in Footwear. Stock availability is unknown.',p,{})==[]
    assert check_claims('This is perfect for gaming and is in stock for INR 1.',p,{})

def test_actual_local_generation_boundary(engine,monkeypatch):
    import retailassist.generation as generation
    monkeypatch.setattr(generation,'local_generate',lambda messages:'This option is listed at INR 500.00 in Footwear. Stock availability is unknown.')
    r=explain(engine.search('running shoe under INR 1000',method='tfidf'),True)
    assert r['generation_mode']=='local_llm'
    assert r['explanations'][0]['source']=='local_llm'
    monkeypatch.setattr(generation,'local_generate',lambda messages:'This is perfect for gaming for INR 1.')
    r=explain(engine.search('running shoe under INR 1000',method='tfidf'),True)
    assert r['generation_mode']=='local_llm_guarded_fallback'
    assert 'gaming' not in r['answer'] and r['explanations'][0]['raw_generated_text']
