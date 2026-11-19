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
    with pytest.raises(ValueError):engine.search('running shoes under KSh 80000',method='tfidf')
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
        def json(self):return {'choices':[{'message':{'content':'{"product_ids":["invented"]}'}}]}
    monkeypatch.setenv('OPENAI_API_KEY','fake-test-key');monkeypatch.setattr(requests,'post',lambda *a,**k:Response())
    r=explain(engine.search('running shoe',method='tfidf'),True)
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
        def json(self):return {'choices':[{'message':{'content':'{"product_ids":["a"]}'}}]}
    monkeypatch.setenv('OPENAI_API_KEY','fake-test-key');monkeypatch.setattr(requests,'post',lambda *a,**k:Response())
    r=explain(engine.search('running shoe',method='tfidf'),True)
    assert r['generation_mode']=='llm_validated_ids';assert [p['id'] for p in r['products']]==['a']

def test_plain_brand_word_does_not_overfilter(engine):
    # A catalogue brand token in prose is not always an intended brand constraint.
    assert 'brand' not in engine.parse('Acme running shoe')
    assert engine.parse('running shoe by Acme')['brand']=='Acme'
