"""Run real local RAG generation on the frozen test queries, saving raw outputs."""
import json
import pandas as pd
from .core import ROOT,Engine,explain

def main():
    engine=Engine();queries=json.loads((ROOT/'data/queries.json').read_text());rows=[]
    for q in queries:
        if q['split']!='test':continue
        constraints={k:q[k] for k in ['category','max_price'] if q.get(k) is not None}
        result=explain(engine.search(q['query'],k=1,constraints=constraints),True)
        for item,p in zip(result['explanations'],result['products']):
            rows.append({'query_id':q['id'],'product_id':p['id'],'provider':'local','model':'HuggingFaceTB/SmolLM2-135M-Instruct','raw_text':item['raw_generated_text'],'served_text':item['text'],'source':item['source'],'claim_check_issues':item['claim_check_issues'],'generation_mode':result['generation_mode'],'latency_ms':result['generation_latency_ms'],'price_constraint_satisfied':p['price']<=constraints.get('max_price',float('inf')),'category_constraint_satisfied':not constraints.get('category') or p['category']==constraints['category']})
        print(q['id'],result['generation_mode'],flush=True)
    path=ROOT/'reports/generation_evaluation.json';path.write_text(json.dumps(rows,indent=2))
    raw_count=sum(r['raw_text'] is not None for r in rows);flagged=sum(bool(r['claim_check_issues']) for r in rows);accepted=sum(r['source']=='local_llm' for r in rows)
    summary={'test_queries':24,'responses':len(rows),'actual_llm_outputs':raw_count,'accepted_llm_explanations':accepted,'flagged_raw_outputs':flagged,'raw_flag_rate':flagged/raw_count if raw_count else None,'fallback_responses':len(rows)-accepted,'price_constraint_violations':sum(not r['price_constraint_satisfied'] for r in rows),'category_constraint_violations':sum(not r['category_constraint_satisfied'] for r in rows),'assessment':'Real local model calls. Claim flags are automated heuristics, not human-grounded hallucination measurements. Evidence planning precedes LLM verbalization; no free-form suitability advice is claimed.'}
    (ROOT/'reports/generation_summary.json').write_text(json.dumps(summary,indent=2));(ROOT/'artifacts/generation_summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
