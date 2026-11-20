"""Restore catalogue records around published indexes without retraining."""
import argparse,hashlib,json
from pathlib import Path
import joblib,requests,pandas as pd
from .core import ROOT,prepare
from .presentation import save_images

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--with-generator',action='store_true');args=parser.parse_args()
    manifest=json.loads((ROOT/'artifacts/manifest.json').read_text());raw=ROOT/'data/raw/catalogue.csv';raw.parent.mkdir(parents=True,exist_ok=True)
    if not raw.exists():
        r=requests.get(manifest['source'],timeout=600);r.raise_for_status();raw.write_bytes(r.content)
    if hashlib.sha256(raw.read_bytes()).hexdigest()!=manifest['raw_sha256']:raise ValueError('Catalogue checksum differs from the trained snapshot; refusing to bind indexes.')
    frame=pd.read_csv(raw);df,audit=prepare(frame);index=joblib.load(ROOT/'artifacts/retriever_index.joblib')
    if index.pop('product_ids')!=df.id.tolist():raise ValueError('Product alignment differs from the trained index.')
    index['products']=df;joblib.dump(index,ROOT/'artifacts/retriever.joblib',compress=3);save_images(frame)
    (ROOT/'data/processed').mkdir(parents=True,exist_ok=True);df.to_json(ROOT/'data/processed/products.jsonl',orient='records',lines=True)
    (ROOT/'reports').mkdir(exist_ok=True);(ROOT/'reports/data_audit.json').write_text(json.dumps(audit,indent=2))
    if args.with_generator:
        from .generation import setup_generator
        setup_generator()
    print('Serving artifacts restored without model training:',len(df),'products')
if __name__=='__main__':main()
