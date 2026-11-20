"""Silver-label retrieval evaluation, not a substitute for human relevance judgments."""
import json
import numpy as np
import pandas as pd
from .core import ROOT, Engine, explain

def judgments(df,q):
    # Independent full-catalogue predicate; no retrieved pool or model scores used.
    rel=df.name.str.contains(q['pattern'],case=False,regex=True,na=False)
    if q.get('category'):rel &= df.category.eq(q['category'])
    if q.get('max_price'):rel &= df.price.le(q['max_price'])
    return set(df.loc[rel,'id'])

def metrics(ids,relevant,k=5):
    hits=np.array([int(i in relevant) for i in ids[:k]])
    dcg=sum(h/np.log2(i+2) for i,h in enumerate(hits))
    ideal=sum(1/np.log2(i+2) for i in range(min(k,len(relevant))))
    return {'precision_at_5':float(hits.sum()/k),'recall_at_5':float(hits.sum()/len(relevant)) if relevant else 0.,'mrr_at_5':next((1/(i+1) for i,h in enumerate(hits) if h),0.),'ndcg_at_5':float(dcg/ideal) if ideal else 0.}

def main():
    engine=Engine();queries=json.loads((ROOT/'data/queries.json').read_text());rows=[]; qrels={}
    methods=['tfidf','lsa']+(['semantic','hybrid'] if 'embeddings' in engine.b else [])
    for q in queries:
        rel=judgments(engine.df,q);qrels[q['id']]=sorted(rel)
        for method in methods:
            c={key:q[key] for key in ['category','max_price'] if q.get(key) is not None}
            result=engine.search(q['query'],method=method,constraints=c)
            ids=[p['id'] for p in result['products']]
            grounding=explain(result)
            rows.append({'query_id':q['id'],'split':q['split'],'method':method,'relevant_count':len(rel),'returned':len(ids),**metrics(ids,rel),'latency_ms':result['latency_ms'],'constraint_violations':sum(p['price']>c.get('max_price',float('inf')) or (c.get('category') is not None and p['category']!=c['category']) for p in result['products']),'invalid_product_ids':sum(i not in set(engine.df.id) for i in ids),'generation_mode':grounding['generation_mode']})
    per=pd.DataFrame(rows);per.to_csv(ROOT/'reports/per_query_metrics.csv',index=False)
    (ROOT/'data/qrels_silver.json').write_text(json.dumps(qrels,indent=2))
    summary=[];rng=np.random.default_rng(42)
    for (split,method),g in per.groupby(['split','method']):
        valid=g[g.relevant_count.gt(0)]
        item={'split':split,'method':method,'queries':len(g),'queries_with_judgments':len(valid),'zero_judgment_queries':int(g.relevant_count.eq(0).sum())}
        for m in ['precision_at_5','recall_at_5','mrr_at_5','ndcg_at_5','latency_ms']:
            item[m]=float(valid[m].mean())
        if len(valid):
            samples=rng.choice(valid.ndcg_at_5.to_numpy(),size=(2000,len(valid)),replace=True).mean(axis=1)
            item['ndcg_ci_low'],item['ndcg_ci_high']=map(float,np.quantile(samples,[.025,.975]))
        summary.append(item)
    pd.DataFrame(summary).to_csv(ROOT/'reports/metrics.csv',index=False)
    (ROOT/'artifacts/evaluation_summary.json').write_text(json.dumps(summary,indent=2))
    print(pd.DataFrame(summary).to_string(index=False))
if __name__=='__main__':main()
