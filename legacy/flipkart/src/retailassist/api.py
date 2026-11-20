from contextlib import asynccontextmanager
from typing import Optional, Literal
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .currency import FX, resolve_currency, present_product
from .presentation import CATEGORIES, load_images, enrich
from pydantic import BaseModel, Field, model_validator, ConfigDict
from .core import Engine, ROOT, explain

class Constraints(BaseModel):
    model_config=ConfigDict(extra='forbid')
    max_price: Optional[float]=Field(None,gt=0)
    min_price: Optional[float]=Field(None,ge=0)
    brand: Optional[str]=None
    category: Optional[str]=None
    min_rating: Optional[float]=Field(None,ge=0,le=5)
    in_stock: bool=False
    @model_validator(mode='after')
    def price_order(self):
        if self.min_price is not None and self.max_price is not None and self.min_price>self.max_price: raise ValueError('Minimum price exceeds maximum price')
        return self
class Request(BaseModel):
    model_config=ConfigDict(extra='forbid')
    query:str=Field(min_length=2,max_length=1500)
    k:int=Field(5,ge=1,le=20)
    method:Literal['tfidf','lsa','semantic','hybrid']='hybrid'
    constraints:Constraints=Field(default_factory=Constraints)
    use_llm:bool=False
    generation_provider:Literal['local','openai']='local'
    currency:Optional[Literal['INR','KES']]=None
@asynccontextmanager
async def lifespan(app):
    app.state.engine=Engine()
    app.state.images=load_images()
    yield
app=FastAPI(title='RetailAssist',version='1.1',lifespan=lifespan)
app.mount('/assets', StaticFiles(directory=str(ROOT/'web/assets')), name='assets')
@app.get('/health')
def health():return {'status':'ok','products':len(app.state.engine.df),'currency':'INR','supported_currencies':['INR','KES'],'conversion':FX,'semantic_available':'embeddings' in app.state.engine.b}
@app.get('/')
def ui():return FileResponse(ROOT/'web/index.html')
@app.post('/recommend')
def recommend(req:Request):
    try:
        result=explain(app.state.engine.search(req.query,req.k,req.method,req.constraints.model_dump(exclude_none=True),req.currency),req.use_llm,req.generation_provider)
        result['products']=enrich(result['products'],app.state.images)
        return result
    except ValueError as e:raise HTTPException(status_code=422,detail=str(e))

@app.get('/catalogue')
def catalogue():
    df=app.state.engine.df
    counts=df.category.value_counts()
    return {'total':len(df),'currency':'INR','supported_currencies':['INR','KES'],'conversion':FX,'categories':[{'name':c,'count':int(counts[c])} for c in CATEGORIES if c in counts], 'semantic_available':'embeddings' in app.state.engine.b}

@app.get('/discover')
def discover(currency:Literal['INR','KES']='INR'):
    products=[]
    for query in ['headphones','running shoes','backpack','table lamp','watch','ceramic mug','sunglasses','keyboard']:
        hits=app.state.engine.search(query,k=2,method='tfidf',currency=currency)['products']
        for product in hits:
            if product['id'] not in {p['id'] for p in products}:
                products.append(product)
                break
    return {'products':enrich(products,app.state.images),'currency':currency}

@app.get('/products/{product_id}')
def product_details(product_id:str,currency:Literal['INR','KES']='INR'):
    matches=app.state.engine.df[app.state.engine.df.id.eq(product_id)]
    if matches.empty:
        raise HTTPException(status_code=404,detail='This product is not in the catalogue.')
    row=matches.iloc[0]
    import pandas as pd
    fields=['id','name','brand','category','price','currency','availability','url']
    product={key:row[key] for key in fields}
    product['rating']=None if pd.isna(row['rating']) else float(row['rating'])
    product['description']=str(row.get('description',''))
    return enrich([present_product(product,currency)],app.state.images)[0]

@app.get('/insights')
def insights():
    import json
    import numpy as np
    df=app.state.engine.df
    counts=df.category.value_counts()
    bins=[0,500,1000,2000,5000,10000,50000,float('inf')]
    hist,_=np.histogram(df.price.to_numpy(),bins=bins)
    labels=['Under 500','500–999','1,000–1,999','2,000–4,999','5,000–9,999','10,000–49,999','50,000+']
    path=ROOT/'artifacts/evaluation_summary.json'
    evaluation=json.loads(path.read_text()) if path.exists() else []
    return {'catalogue':{'total_products':len(df),'brands':int(df.loc[df.brand.ne('Unknown'),'brand'].nunique()),'rated_products':int(df.rating.notna().sum()),'unknown_brands':int(df.brand.eq('Unknown').sum()),'unknown_stock':int(df.availability.eq('unknown').sum()),'median_price':float(df.price.median()),'currency':'INR','top_categories':[{'name':name,'count':int(count)} for name,count in counts.head(8).items()],'price_distribution':[{'label':label,'count':int(count)} for label,count in zip(labels,hist)]},'evaluation':evaluation,'generation_evaluation':json.loads((ROOT/'artifacts/generation_summary.json').read_text()) if (ROOT/'artifacts/generation_summary.json').exists() else None,'evaluation_note':'Offline evaluation: 30 AI-authored queries (6 development, 24 test), with rule-based silver relevance judgments. This is not customer satisfaction, sales, or conversion data.','model':{'name':'all-MiniLM-L6-v2','semantic_available':'embeddings' in app.state.engine.b,'hybrid_weights':{'semantic':0.75,'keyword':0.25},'generation':'Local SmolLM2 generates actual grounded explanations; optional hosted structured-output provider. Raw outputs and heuristic claim checks are evaluated separately.'}}
