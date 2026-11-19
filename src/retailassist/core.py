from pathlib import Path
import re, json, os, time
import numpy as np
import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize
from .currency import resolve_currency, convert_price, present_product

ROOT = Path(__file__).resolve().parents[2]
MODEL = 'sentence-transformers/all-MiniLM-L6-v2'
REVISION = '1110a243fdf4706b3f48f1d95db1a4f5529b4d41'

def prepare(raw):
    raw = raw.copy()
    audit = {'raw_rows':len(raw), 'missing_by_column':raw.isna().sum().to_dict()}
    out = pd.DataFrame({'id':raw.pid, 'name':raw.product_name,
        'description':raw.description.fillna(''), 'brand':raw.brand.fillna('Unknown').str.strip(),
        'category':raw.product_category_tree.fillna('').str.extract(r'\["([^">]+)', expand=False).str.strip(),
        'category_path':raw.product_category_tree.fillna(''),
        'price':pd.to_numeric(raw.discounted_price, errors='coerce'),
        'rating':pd.to_numeric(raw.product_rating, errors='coerce'),
        'url':raw.product_url, 'currency':'INR', 'availability':'unknown'})
    out = out.dropna(subset=['id','name','price'])
    out = out[out.price.gt(0)].drop_duplicates('id').reset_index(drop=True)
    out['text'] = out.name + ' ' + out.name + ' ' + out.category_path + ' ' + out.brand + ' ' + out.description
    audit.update(clean_rows=len(out), removed_rows=len(raw)-len(out), unknown_rating=int(out.rating.isna().sum()), unknown_brand=int(out.brand.eq('Unknown').sum()))
    return out, audit

def fit(df, semantic=True):
    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1,2), min_df=2, max_features=40000, sublinear_tf=True)
    x = vectorizer.fit_transform(df.text)
    svd = TruncatedSVD(n_components=min(128, x.shape[0]-1, x.shape[1]-1), random_state=42)
    latent = normalize(svd.fit_transform(x))
    bundle = dict(vectorizer=vectorizer, tfidf=x, svd=svd, latent=latent, products=df)
    if semantic:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(MODEL, revision=REVISION, cache_folder=str(ROOT/'artifacts'/'model_cache'))
        bundle['embeddings'] = model.encode(df.text.tolist(), batch_size=64, normalize_embeddings=True, show_progress_bar=True)
        model.save(str(ROOT/'artifacts'/'encoder'))
    joblib.dump({key:bundle[key] for key in ['vectorizer','svd']}, ROOT/'artifacts'/'fitted_transformers.joblib', compress=3)
    index={key:value for key,value in bundle.items() if key!='products'}
    index['product_ids']=df.id.tolist()
    joblib.dump(index,ROOT/'artifacts/retriever_index.joblib',compress=3)
    joblib.dump(bundle, ROOT/'artifacts'/'retriever.joblib', compress=3)
    return bundle

class Engine:
    def __init__(self, bundle=None):
        self.b = bundle if bundle is not None else joblib.load(ROOT/'artifacts'/'retriever.joblib')
        self.df = self.b['products']
        self.encoder = None
    def parse(self, query, explicit=None):
        c = dict(explicit or {})
        resolve_currency(query)
        m = re.search(r'(?:under|below|up to|at most|budget(?: of)?)\s*(?:inr|rs\.?|kes|kshs?|₹)?\s*([\d,]+(?:\.\d+)?)\s*(k\b)?', query,re.I)
        if m and c.get('max_price') is None: c['max_price']=float(m[1].replace(',',''))*(1000 if m[2] else 1)
        m = re.search(r'(?:above|over|at least)\s*(?:inr|rs\.?|kes|kshs?|₹)?\s*([\d,]+(?:\.\d+)?)', query,re.I)
        if m and c.get('min_price') is None: c['min_price']=float(m[1].replace(',',''))
        if not c.get('brand'):
            matches=[b for b in self.df.brand.unique() if b!='Unknown' and re.search(r'\b(?:by|from|brand)\s+'+re.escape(b)+r'(?!\w)',query,re.I)]
            if matches: c['brand']=max(matches,key=len)
        # Explicit category is preferable: a wrong inferred category could eliminate useful candidates.
        if c.get('min_price',0) > c.get('max_price',float('inf')): raise ValueError('Minimum price exceeds maximum price.')
        return {k:v for k,v in c.items() if v is not None}
    def search(self, query, k=5, method='hybrid', constraints=None, currency=None):
        start=time.perf_counter(); currency=resolve_currency(query,currency); c=self.parse(query,constraints)
        prices=self.df.price.map(lambda price:convert_price(price,currency))
        if method not in ['tfidf','lsa','semantic','hybrid']: raise ValueError('Unknown retrieval method')
        q=self.b['vectorizer'].transform([query]); lex=(self.b['tfidf']@q.T).toarray().ravel()
        if method=='tfidf': scores=lex
        elif method=='lsa': scores=self.b['latent']@normalize(self.b['svd'].transform(q))[0]
        else:
            if 'embeddings' not in self.b: raise ValueError('Semantic encoder not built; train without --no-semantic.')
            if self.encoder is None:
                from sentence_transformers import SentenceTransformer
                self.encoder=SentenceTransformer(str(ROOT/'artifacts'/'encoder'))
            sem=self.b['embeddings']@self.encoder.encode(query,normalize_embeddings=True)
            scores=sem if method=='semantic' else .75*sem+.25*lex
        mask=np.ones(len(self.df),dtype=bool)
        if 'max_price' in c: mask &= prices.le(c['max_price']).to_numpy()
        if 'min_price' in c: mask &= prices.ge(c['min_price']).to_numpy()
        for field in ['brand','category']:
            if c.get(field): mask &= self.df[field].str.casefold().eq(c[field].casefold()).to_numpy()
        if c.get('min_rating') is not None: mask &= self.df.rating.ge(c['min_rating']).to_numpy()
        if c.get('in_stock'): mask &= self.df.availability.eq('in_stock').to_numpy()
        ids=np.flatnonzero(mask & (scores>0))
        ids=ids[np.argsort(-scores[ids],kind='stable')[:k]]
        products=[]
        for i in ids:
            p=self.df.iloc[i][['id','name','brand','category','price','currency','rating','availability','url']].to_dict()
            p['rating']=None if pd.isna(p['rating']) else p['rating']; p['score']=float(scores[i]); products.append(present_product(p,currency))
        return {'query':query,'constraints':c,'method':method,'products':products,'currency':currency,'latency_ms':(time.perf_counter()-start)*1000}

def explain(result, use_llm=False, provider='local'):
    from .generation import explain_result
    return explain_result(result,use_llm,provider)
