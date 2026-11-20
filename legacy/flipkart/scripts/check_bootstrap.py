"""CI smoke check after restoring the serving index from a clean public clone."""
from fastapi.testclient import TestClient
from retailassist.api import app
with TestClient(app) as client:
    assert client.get('/health').json()['products']==19920
    r=client.post('/recommend',json={'query':'running shoes under KSh 2000','currency':'KES','method':'tfidf','constraints':{'category':'Footwear'}})
    assert r.status_code==200,r.text
    products=r.json()['products'];assert products
    assert all(p['currency']=='KES' and p['price']<=2000 and p['source_currency']=='INR' for p in products)
    assert client.get('/insights').status_code==200
print('Public-artifact restore and KES API smoke check passed')
