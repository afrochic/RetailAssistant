"""Run with python -m retailassist.pipeline [--no-semantic]."""
import argparse, hashlib, json
from datetime import datetime, timezone
import requests
import pandas as pd
from .core import ROOT, prepare, fit, MODEL, REVISION
URL='https://huggingface.co/datasets/jason1966/PromptCloudHQ_flipkart-products/resolve/ac16731c75907ab9f212c372ec637c00f257c36a/flipkart_com-ecommerce_sample.csv'
def main():
    p=argparse.ArgumentParser(); p.add_argument('--no-semantic', action='store_true'); p.add_argument('--refresh', action='store_true'); a=p.parse_args()
    for d in ['data/raw','data/processed','artifacts','reports']: (ROOT/d).mkdir(parents=True,exist_ok=True)
    path=ROOT/'data/raw/catalogue.csv'
    if not path.exists() or a.refresh:
        r=requests.get(URL,timeout=600);r.raise_for_status();path.write_bytes(r.content)
    raw=pd.read_csv(path); df,audit=prepare(raw)
    df.to_json(ROOT/'data/processed/products.jsonl',orient='records',lines=True)
    (ROOT/'reports/data_audit.json').write_text(json.dumps(audit,indent=2))
    fit(df,semantic=not a.no_semantic)
    manifest={'source':URL,'raw_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'rows':len(df),'created_utc':datetime.now(timezone.utc).isoformat(),'seed':42,'encoder':None if a.no_semantic else MODEL,'encoder_revision':None if a.no_semantic else REVISION,'currency':'INR','availability':'unknown','split':'Catalogue indexed in full; evaluation queries split into dev/test. No interactions available.'}
    (ROOT/'artifacts/manifest.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(manifest,indent=2))
if __name__=='__main__':main()
