from contextlib import asynccontextmanager
from typing import Optional, Literal
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
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
@asynccontextmanager
async def lifespan(app):
    app.state.engine=Engine();yield
app=FastAPI(title='RetailAssist',version='1.0',lifespan=lifespan)
@app.get('/health')
def health():return {'status':'ok','products':len(app.state.engine.df),'currency':'INR','semantic_available':'embeddings' in app.state.engine.b}
@app.get('/')
def ui():return FileResponse(ROOT/'web/index.html')
@app.post('/recommend')
def recommend(req:Request):
    try:return explain(app.state.engine.search(req.query,req.k,req.method,req.constraints.model_dump(exclude_none=True)),req.use_llm)
    except ValueError as e:raise HTTPException(status_code=422,detail=str(e))
