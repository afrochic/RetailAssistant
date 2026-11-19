"""Exercise a running service and save verifiable HTTP results."""
import json, time, urllib.request, urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    base='http://127.0.0.1:8000'
    health=None
    for attempt in range(30):
        try:
            with urllib.request.urlopen(base+'/health',timeout=3) as r:health=json.load(r)
            break
        except (OSError,urllib.error.URLError):time.sleep(1)
    assert health and health['products']==19920,health
    payload={'query':'running shoes under INR 1500','method':'hybrid','constraints':{'category':'Footwear'}}
    request=urllib.request.Request(base+'/recommend',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(request,timeout=90) as r:recommendation=json.load(r)
    assert recommendation['products']
    assert all(p['price']<=1500 and p['category']=='Footwear' for p in recommendation['products'])
    with urllib.request.urlopen(base+'/',timeout=10) as r:assert b'RetailAssist' in r.read()
    (ROOT/'reports/http_smoke_test.json').write_text(json.dumps({'health':health,'request':payload,'response':recommendation,'ui_status':200},indent=2))
    print(json.dumps({'health':health,'recommendations':len(recommendation['products']),'constraint_checks':'passed','ui_status':200}))

if __name__=='__main__':
    main()
