"""Generate an explanatory notebook and a report from actual pipeline outputs."""
from pathlib import Path
import json, textwrap, html
import pandas as pd
import numpy as np
import nbformat as nbf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, Preformatted, KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
ROOT=Path(__file__).resolve().parents[1]
R=ROOT/'reports';R.mkdir(exist_ok=True)
audit=json.loads((R/'data_audit.json').read_text());manifest=json.loads((ROOT/'artifacts/manifest.json').read_text());metrics=pd.read_csv(R/'metrics.csv');test=metrics[metrics.split.eq('test')]
fig,ax=plt.subplots(figsize=(8,3.6));x=np.arange(len(test));w=.2
for j,key in enumerate(['precision_at_5','recall_at_5','mrr_at_5','ndcg_at_5']):ax.bar(x+(j-1.5)*w,test[key],w,label=key.replace('_at_5','@5'))
ax.set_xticks(x,test.method);ax.set_ylim(0,1);ax.set_ylabel('Macro average');ax.set_title('Test retrieval results - rule-based silver labels');ax.legend(ncol=4,fontsize=8);fig.tight_layout();fig.savefig(R/'retrieval_metrics.png',dpi=170);plt.close(fig)

sections=[
('1. Problem, scope and reading guide',[
'RetailAssist helps a shopper search a catalogue using natural language and explicit preferences. The output is a ranked list of existing catalogue items, with recorded price, brand and category. The system never guarantees that a product is suitable for an unrecorded purpose. For example, a request for a programming laptop cannot justify a claim about processor speed unless the underlying catalogue supports that fact.',
'The proposal is implemented with keyword retrieval, semantic embeddings, constraints, ranking, a local SmolLM2 text-generation layer, FastAPI and a shopping/chat interface. The LLM verbalizes an evidence plan derived from retrieved records. Claim checks reject questionable prose and use catalogue-fact fallbacks. The default local route needs no paid API key; an optional hosted structured-output adapter is also implemented.',
'Retrieval results and real local LLM outputs were executed and saved. All 24 frozen test queries received a local generated explanation: seven passed conservative checks; 17 were flagged and replaced with factual sentences. These flags are heuristic rather than human judgments. Hosted paid API quality is not evaluated. The project is served locally with Docker; public cloud hosting is not implied.',
'Read Sections 2-5 to understand data and preprocessing, Sections 6-9 for retrieval and evaluation, and Sections 10-13 to run and defend the system. The notebook gives executable examples and visible outputs; the Python modules are the authoritative reproducible implementation. Study both before submitting an individual assessment.'
]),
('2. Requirements and acceptance criteria',[
'The brief requires a scripted pipeline from ingestion through prediction, a model API containerized with Docker, and one Git repository with README, AI_USE disclosure, pipeline and training code, serialized artifacts, Dockerfile, Compose file, API and a report or slide deck. A notebook alone does not satisfy the assignment. Although Section 3.1 says three requirements, the supplied table visibly lists two; this project implements every listed item rather than inventing a missing third requirement.',
'The data-pipeline rubric is addressed by a pinned raw-data download, hash manifest, cleaning audit and rebuild command. Modelling/evaluation is addressed by four retrieval variants, query-level metrics and explicit limitations. Technique justification is addressed by comparisons with collaborative filtering, fine-tuning and vector databases. Deployment is addressed by FastAPI, a simple interface and Docker packaging. The report and notebook address the final communication component.',
'Acceptance checks are practical: run the pipeline from an empty artifact directory; send a valid API request and inspect catalogue IDs; confirm no returned price exceeds the accepted ceiling; request an impossible budget and get no products; reject an unsupported currency; and verify that an LLM cannot insert an invented product. Automated tests exercise these cases with independent fixtures.',
'An honest submission also needs the student to inspect relevance labels, review the source-data rights and explain limitations. AI assistance is disclosed in AI_USE.md. This document and code are a substantial AI-assisted draft, not evidence of the student independently completing or understanding the assessment.'
]),
('3. Set up a reproducible workspace',[
'Keep the project separate from the unrelated Client X repository. The project root contains src, data, artifacts, notebooks, reports, tests and web. Relative paths are resolved from the installed module location, so commands work from the repository root. Use Python 3.9 to match the verified environment and container major/minor version.',
'Create a virtual environment, activate it, install requirements-dev.txt, then install this project with pip install -e . --no-deps. The runtime dependencies include pandas, scikit-learn, sentence-transformers, FastAPI and requests. Development dependencies add pytest, notebook execution, plotting and report generation. requirements-lock.txt records the full executed environment; requirements.txt pins direct runtime dependencies.',
'For a clean public clone, run python -m retailassist.bootstrap --with-generator. It verifies the downloaded source SHA-256, checks exact ordered product IDs and binds records around published trained indexes without retraining. The licensed MiniLM encoder is uploaded, and the larger local generator is downloaded from a pinned revision. To reproduce training itself, run python -m retailassist.pipeline, then both evaluation modules.',
'Reproducibility controls include a fixed SVD seed of 42, a versioned source URL, a SHA-256 fingerprint, a pinned encoder revision and saved per-query results. Floating-point results can vary slightly across hardware and BLAS libraries. Internet access is necessary for initial reproduction; inference after a successful semantic build uses the saved local encoder.'
]),
('4. Ingest the real catalogue and assess quality',[
'The selected source is the historical PromptCloudHQ Flipkart sample, mirrored on Hugging Face. It contains 20,000 product rows with IDs, titles, category trees, descriptions, brands, retail and discounted prices, text-form ratings and retailer URLs. This is scraped retail data rather than a fabricated API product fixture. Its country and historical collection period limit how it may be used.',
'Preserve the downloaded CSV unchanged in data/raw. The pipeline saves its SHA-256 in artifacts/manifest.json, providing an integrity reference for reviewers. A hash proves which bytes were used; it does not establish accuracy, legal rights or freshness. The source mirror lists its license as unknown. Source records and record-level inference artifacts are excluded from the public repository; obtain permission before redistributing those records.',
'Original prices remain Indian rupees (INR). KES is now supported as a clearly labelled estimate using the dated KRA weekly reference 1 INR = 1.37 KES for 16-22 November 2026. Source INR values and provenance are preserved. Filters operate on the rounded selected-currency amount. This does not create Kenyan stock or current Kenyan retail prices. USD/EUR and contradictory currency requests are rejected.',
'Quality findings from this executed run: '+str(audit['raw_rows'])+' raw rows, '+str(audit['clean_rows'])+' usable unique-ID records, '+str(audit['removed_rows'])+' excluded rows, '+str(audit['unknown_brand'])+' unknown brands and '+str(audit['unknown_rating'])+' unknown/non-numeric ratings. These are real observed gaps. They motivate explicit unknown states and conservative filtering, rather than synthetic corruption added for appearance.'
]),
('5. Clean, represent and audit the data',[
'prepare() constructs a consistent product table. Missing descriptions become empty strings. Missing brands become Unknown. The first segment of a category tree becomes the primary category, while the complete tree remains in the retrieval text. Numeric conversion uses coercion: missing or textual ratings become null, not zero. A missing rating is not evidence of a bad product.',
'Rows without a product ID, title or valid positive discounted price are removed. Repeated product IDs are collapsed to the first record. This ID-based policy does not merge near-duplicate listings with different IDs, variants or spelling differences. That remaining duplication can make top-five results repetitive; deduplication by product family is a useful extension requiring careful variant handling.',
'Construct searchable text by concatenating the title twice, category path, brand and description. Repeating the title modestly emphasizes the named item compared with long scraped prose. TF-IDF then gives lower weight to terms shared by many products. Product IDs, URLs and numeric prices are not concatenated into this representation: structured fields are handled as constraints.',
'The data audit is saved in reports/data_audit.json, and cleaned records in data/processed/products.jsonl. Inspect category frequency, price quantiles, missingness and representative products in the notebook. Some raw category paths are malformed or look like product titles, so explicit category filters may occasionally under-retrieve. This limitation is documented rather than silently repaired with invented labels.'
]),
('6. Fit the baseline and semantic models',[
'TF-IDF is the lexical baseline. It learns vocabulary and inverse document frequencies from catalogue text, using unigrams/bigrams, English stop-word removal, min_df=2, a 40,000-feature cap and sublinear term frequency. Query and product vectors are compared with cosine-equivalent dot products because the vectorizer normalizes each row. This is inexpensive and works especially well for exact product names.',
'Latent semantic analysis (LSA) fits TruncatedSVD with up to 128 components to the same sparse matrix, then normalizes the result. It can capture catalogue co-occurrence patterns but has no external language knowledge. The fitting step is real unsupervised model training, not supervised purchase prediction. It may blur rare technical terms and does not guarantee an improvement over TF-IDF.',
'The semantic retriever uses sentence-transformers/all-MiniLM-L6-v2, pinned to the revision in the manifest. It encodes product text and queries into normalized dense vectors. Similarity is their dot product. This pretrained model can connect expressions such as jogging and running even where exact lexical overlap is weak. Long descriptions are truncated by the encoder; important late attributes can be lost.',
'The hybrid score is fixed in advance as 0.75 semantic cosine plus 0.25 TF-IDF cosine. Both scores use normalized vectors but their empirical distributions need not match. This is a transparent heuristic, not a calibrated relevance probability or a trained learning-to-rank model. The weights are not tuned on the test set. Saved vectorizer/SVD parameters, catalogue vectors and encoder support repeatable prediction.'
]),
('7. Extract constraints and generate grounded responses',[
'The parser recognizes common upper-budget phrases such as under, below and up to, and lower-budget phrases such as above or at least. It supports comma-separated amounts and an optional k multiplier for upper budgets. Catalogue brand mentions following by, from or brand are recognized; plain tokens are not imposed as hard brand filters. Confirmed structured fields supplied by the client take precedence over parsed values.',
'Category, minimum rating, brand and availability may be passed explicitly. The parser does not pretend to understand every natural-language preference: negation, multiple competing budgets and complex comparisons can be ambiguous. The client should ask for clarification or send confirmed fields. The simple interface is stateless; a client can carry forward prior constraints for follow-up turns, but no persistent dialogue memory is implemented.',
'Score catalogue entries, retain only those satisfying every accepted hard constraint, and sort the eligible entries. Filtering across the full catalogue before top-K truncation avoids a common failure where a small unconstrained candidate pool contains only expensive products. Unknown ratings fail a minimum-rating filter. Unknown availability fails an in-stock filter. An impossible request returns an empty list with guidance.',
'Actual local RAG generation uses retrieved catalogue facts to plan supported evidence about price, category, accepted budget and unknown stock. SmolLM2 then produces a conversational explanation. Generated numbers, words, stock/suitability claims and catalogue citations are checked; failed checks fall back to explicit facts. Raw and served text are retained for evaluation. This conservative evidence-planning design matches the intended grounded explanation task without allowing unsupported technical advice. Optional hosted generation uses a structured explanation schema, not ID-only reranking.'
]),
('8. Design evaluation without leaking results into labels',[
'The benchmark contains 30 authored natural-language queries: six development queries and 24 test queries. Intents include shoes, kitchen items, accessories, clocks and clothing, with both exact words and paraphrases. Binary silver judgments are generated by frozen title-pattern rules over the full catalogue, supplemented by category and price restrictions. qrels_silver.json records the resulting IDs for inspection.',
'These labels are weak, automatically derived references, not expert human annotations. For example, a broad title match may include a related accessory, and a relevant synonym may be missed. Rules were written independently of the retrieval rankings. No claim is made that they fully capture product usefulness. Several related intents occur across development and test queries, which weakens any claim of out-of-domain generalization.',
'All catalogue products are indexed. There is no train/test product partition because the task is search over known inventory, not prediction of unseen-product outcomes. Held-out queries assess retrieval behaviour against fixed rules. There are no customer interaction labels, so this project cannot estimate conversion, business uplift, causal effects or personalized recommendation accuracy.',
'Compare TF-IDF, LSA, MiniLM and hybrid using the same query constraints and relevance sets. A query with zero silver judgments is counted separately and excluded from summary means because relevance metrics lack a useful denominator; it is not evidence that the request has no relevant real product. A query with judgments but no retrieved results receives zero scores. All individual results remain available for audit.'
]),
('9. Understand metrics and interpret measured results',[
'Precision@5 is the number of relevant products in the first five divided by five, even when fewer than five products are returned. Recall@5 divides the same hit count by the full relevant set size. A broad query can have hundreds of relevant products, making recall low even for an excellent top-five list. These denominators answer different questions and should not be conflated.',
'MRR@5 is the reciprocal rank of the first relevant result within five, or zero if none appears. NDCG@5 discounts each binary hit by log2(rank+1), then divides by the best achievable discounted sum for that relevance set. It rewards putting relevant products near the top. No rating-based or graded relevance is claimed: labels are binary.',
'The executed hybrid test NDCG@5 is '+format(float(test.loc[test.method.eq('hybrid'),'ndcg_at_5'].iloc[0]),'.3f')+', compared with TF-IDF '+format(float(test.loc[test.method.eq('tfidf'),'ndcg_at_5'].iloc[0]),'.3f')+'. This supports hybrid retrieval for this demonstration, while overlapping uncertainty and weak labels preclude a strong claim of general superiority. The next table and chart are read directly from saved executed evaluation results. Bootstrap intervals resample query-level NDCG means 2,000 times using seed 42. They quantify sampling variability within this small benchmark only; they do not correct silver-label bias or prove statistical superiority. Model comparisons should use paired analysis before any formal claim of a significant improvement.',
'Latency is measured around search calls and includes the first encoder load on the first semantic call. It is affected by caches, hardware and workload. The reported average is descriptive rather than a production SLA. Review reports/per_query_metrics.csv for failed intents, zero judgments, returned counts and constraint violations. Do not claim that semantic retrieval must win: actual results determine which method is useful on this catalogue.'
]),
('10. Run the service and test behaviour',[
'After training, run uvicorn retailassist.api:app --host 127.0.0.1 --port 8000. Startup loads retriever.joblib; the first semantic search loads the saved encoder. /health reports product count, INR and whether semantic embeddings exist. /docs exposes the OpenAPI interface. / serves the simple browser search form.',
'Send POST /recommend with query, k, method and optional structured constraints. The response includes parsed constraints, method, product IDs and metadata, scores, elapsed search time, explanation mode and a historical-data notice. Validation rejects invalid k, negative prices, ratings outside 0-5, contradictory price bounds and unsupported currencies. No-match results are successful requests with an empty product array.',
'The interface exposes actual local LLM explanations in the assistant drawer, with transparent factual fallbacks when checks reject output. Budget-only follow-ups reuse the last product intent. The currency selector offers original INR or dated KES estimates. Insights shows real retrieval scores, 24 actual generation results, catalogue category/price distributions and data-quality coverage. No sales or conversion figures are invented.',
'Run pytest -q. The tests use a small controlled catalogue to verify constraints, no-match behaviour, currency rejection, contradictory budgets, API routes and request validation. A hand-calculated ranking checks metric formulas. A mocked LLM returns an invented product ID to verify safe fallback. Mock tests establish boundary behaviour, not real hosted LLM accuracy.',
'For the demonstration, search running shoes under KSh 2000 with KES selected. Inspect converted prices, original INR values and the dated reference. Ask the AI assistant for actual local LLM explanations, inspect generation/fallback provenance and open Insights. Then try an impossible budget, an unsupported USD request and a confirmed-stock constraint. Explain why a converted estimate cannot establish current Kenyan availability or programming performance.'
]),
('11. Containerize, deploy and monitor responsibly',[
'The Dockerfile uses a Python slim base, installs pinned direct dependencies, copies the service, interface and locally built artifacts, and runs as a non-root user. The Compose file maps 127.0.0.1:8000 to port 8000 in the container. The health check requests /health. .dockerignore excludes secrets, raw data and unnecessary caches from the build context.',
'Run bootstrap --with-generator before docker compose up --build -d for a fully prepared local build. From a clean clone the Dockerfile can also restore the serving bundle from public trained indexes and source records without model fitting. Confirm health and a prediction, review logs, and stop with docker compose down. CI performs the same public-artifact restore and a KES API check on Ubuntu 22.04 with Python 3.9.',
'For public hosting, use a managed container host with HTTPS, authentication, rate limits, resource limits and a secure secrets store. This project does not provision a paid server or publish customer data. Multi-worker semantic services consume extra memory because each worker can load its own encoder. For this small corpus, a single CPU worker is sufficient for a classroom demonstration.',
'Monitor request failures, no-match rate, latency percentiles, budget violations and source freshness. Compare live price, category and query distributions with the recorded baseline. Collect consented human feedback before retraining or adjusting weights. No monitoring or drift platform is represented as already deployed: these are operational next steps. A historical snapshot cannot substitute for a regularly refreshed retailer inventory feed.'
]),
('12. Technique choices, limitations and next experiments',[
'Collaborative filtering is excluded because there are no reliable user-item interactions. Supervised rankers and conversion prediction are excluded for the same reason. LLM fine-tuning is disproportionate for a small catalogue and supplies no guarantee against invented products. A pretrained encoder plus explicit filtering directly matches the proposal and is feasible on CPU.',
'A dedicated vector database is unnecessary at roughly twenty thousand products: an in-memory dense matrix gives transparent exact scoring. Approximate nearest-neighbour indexing becomes appropriate at larger scale. The current design evaluates every catalogue vector before truncating, simplifying correctness of constraints; production architectures may filter vector candidates with metadata indexes.',
'Main limitations include historic Indian prices, unknown stock, absent customer interactions, imperfect categories, incomplete brands and ratings, encoder truncation, limited explicit-brand parsing, no robust intent or dialogue state, silver rather than human labels, and no real hosted-LLM quality evaluation. Product grounding ensures an ID exists in this snapshot; it does not establish fact freshness, factual catalogue correctness or personal suitability.',
'Priority extensions: independently annotate a diverse held-out query set with at least two assessors; assess inter-rater agreement; collect Kenyan catalogue prices with explicit permissions; add product-family diversity; robustly parse negated/multi-constraint requests; validate live stock; compare hybrid weights only on development judgments; measure cold/warm p50 and p95 latency; and complete actual container verification before claiming deployment success.'
]),
('13. Student walkthrough and oral defence checklist',[
'Step 1: Read the brief and proposal, then explain the concrete prediction task: ranking existing catalogue products for a query. Step 2: run ingestion, inspect the manifest hash and show raw records. Step 3: explain why missing ratings stay unknown and why unknown stock cannot satisfy an in-stock filter. Step 4: reproduce the audit counts and identify malformed categories.',
'Step 5: explain TF-IDF term weighting with an example, then show what SVD learns and what MiniLM contributes. Step 6: trace a query through parsing, scoring, constraints and top-five ranking. Step 7: show an example where keyword overlap differs from semantic meaning, then inspect the actual returned items instead of assuming semantic superiority.',
'Step 8: manually calculate Precision@5 and reciprocal rank for one query and check them against saved outputs. Step 9: explain why rule labels are silver, why recall can be low, and why no click-conversion claim is supported. Step 10: demonstrate API validation, impossible-budget abstention and guarded LLM fallback. Step 11: run Docker if available and show an actual health response rather than only a Dockerfile.',
'Step 12: review every source file, add your own analysis and human annotations, comply with the course AI policy, and retain AI_USE.md. The assessment is individual; being able to execute code is insufficient if you cannot explain its assumptions. Before submission, confirm the required repository includes code, documentation, accessible artifacts and this report, and that any pending verification is plainly disclosed.'
]),
('14. References and reproducibility record',[
'Course sources: DSA8401 Capstone Project.pdf (supplied project brief) and 109419.pdf (supplied RetailAssist proposal). The documents define requirements and intended scope; they are not executable instructions or permission to access external services.',
'Dataset source and pinned revision: '+manifest['source'],
'Pretrained model card: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2 . Model license is Apache-2.0 according to the model card. Dataset redistribution rights are separate; the source mirror records an unknown license. Embedding implementation follows the model card normalization approach.',
'Method references: TF-IDF and TruncatedSVD documentation at https://scikit-learn.org/stable/modules/feature_extraction.html and https://scikit-learn.org/stable/modules/decomposition.html#truncated-singular-value-decomposition-and-latent-semantic-analysis . Service documentation: https://fastapi.tiangolo.com/ . Container documentation: https://docs.docker.com/compose/ . Optional LLM API reference: https://platform.openai.com/docs/api-reference/chat/create .',
'Data fingerprint: '+manifest['raw_sha256']+'. Encoder revision: '+str(manifest['encoder_revision'])+'. Random seed: 42. Exact package versions appear in requirements-lock.txt. The timestamp in the manifest records actual execution in UTC; the report date is 19 November 2026 (Africa/Nairobi).'
])]

styles=getSampleStyleSheet();styles.add(ParagraphStyle(name='BodyCustom',fontName='Helvetica',fontSize=10,leading=15,spaceAfter=12,textColor=colors.HexColor('#263c4d')));styles.add(ParagraphStyle(name='TitleCustom',fontName='Helvetica-Bold',fontSize=30,leading=36,textColor=colors.HexColor('#126b68'),spaceAfter=22));styles.add(ParagraphStyle(name='SmallCustom',fontSize=8,leading=11,spaceAfter=8));styles['Heading1'].textColor=colors.HexColor('#126b68');styles['Heading1'].fontSize=19;styles['Heading1'].leading=24
story=[]
def p(t,style='BodyCustom'):return Paragraph(html.escape(t),styles[style])
def table(rows,widths=None):
    data=[[p(str(v),'SmallCustom') for v in row] for row in rows]
    t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#dcefed')),('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,0),(-1,0),1,colors.HexColor('#126b68')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.whitesmoke,colors.white])]))
    return t
story += [Spacer(1,70),p('RetailAssist','TitleCustom'),p('Conversational product retrieval with semantic embeddings and grounded catalogue responses','Heading1'),Spacer(1,25),p('DSA 8401 - Applied Machine Learning | Capstone project'),p('Admission number: 109419'),p('Implementation, evaluation and step-by-step study report'),p('19 November 2026 | MSc Data Science & Analytics'),Spacer(1,25),p('AI-assisted implementation. Review AI_USE.md and course requirements before submission. Results are from an executed historical-catalogue retrieval experiment using silver labels. Actual local LLM results and verified local deployment are documented. Hosted API quality is not claimed.'),PageBreak()]
story.append(p('Contents and deliverable map','Heading1'))
for title,_ in sections:story.append(p(title))
story.append(p('Appendices: measured results, execution status and commands.'))
story.append(PageBreak())
for title,paras in sections:
    story.append(p(title,'Heading1'));story.append(Spacer(1,10))
    for para in paras:story.append(p(para))
    if title.startswith('9.'):
        story.append(Image(str(R/'retrieval_metrics.png'),width=465,height=209))
        rows=[['Method','P@5','R@5','MRR@5','NDCG@5']]+[[r.method]+[f'{getattr(r,m):.3f}' for m in ['precision_at_5','recall_at_5','mrr_at_5','ndcg_at_5']] for r in test.itertuples()]
        story.append(table(rows,[105,90,90,90,90]))
    story.append(PageBreak())
story.append(p('Appendix A. Results with uncertainty','Heading1'))
rows=[['Split / method','Judged / total','NDCG@5','95% bootstrap interval','Mean search ms']]
for r in metrics.itertuples():rows.append([r.split+' / '+r.method,f'{r.queries_with_judgments}/{r.queries}',f'{r.ndcg_at_5:.3f}',f'{r.ndcg_ci_low:.3f} - {r.ndcg_ci_high:.3f}',f'{r.latency_ms:.1f}'])
story.append(table(rows,[125,80,75,110,75]));story.append(Spacer(1,18))
per=pd.read_csv(R/'per_query_metrics.csv');story.append(p('Measured returned-product constraint violations: '+str(int(per.constraint_violations.sum()))+'. Invalid product IDs: '+str(int(per.invalid_product_ids.sum()))+'. These checks cover supplied category and price constraints on this benchmark; they are not a comprehensive natural-language understanding or live-LLM safety evaluation.'))
story.append(PageBreak());story.append(p('Appendix B. Verification and remaining work','Heading1'))
verification=json.loads((R/'verification.json').read_text()) if (R/'verification.json').exists() else {'status':'See verification.json after final execution.'}
for key,val in verification.items():story.append(p(key.replace('_',' ').capitalize()+': '+str(val)))
story.append(p('The Git source contains fitted transformation parameters and the model manifest. The local submission archive also includes record-level inference artifacts and the saved encoder. A clean clone can regenerate them using the pipeline. Do not treat a GitHub upload or passing unit tests as proof of a publicly running service.'))
story.append(PageBreak());story.append(p('Appendix C. Commands and file guide','Heading1'))
for title,code in [('Install and rebuild','python3.9 -m venv .venv\nsource .venv/bin/activate\npip install -r requirements-dev.txt\npip install -e . --no-deps\npython -m retailassist.pipeline\npython -m retailassist.evaluate'),('Verify and serve','pytest -q\npython scripts/execute_notebook.py\nuvicorn retailassist.api:app --host 127.0.0.1 --port 8000'),('Container deployment','docker compose up --build -d\ncurl http://localhost:8000/health\ndocker compose logs --tail=50\ndocker compose down')]:
 story.append(p(title,'Heading2'));story.append(Preformatted(code,styles['Code']));story.append(Spacer(1,14))
story.append(p('core.py contains preprocessing, fitting, retrieval and guarded generation. pipeline.py orchestrates ingestion and training. evaluate.py defines silver judgments and retrieval metrics. api.py defines validated HTTP contracts and startup. The notebook links each stage to executable examples.'))

story.append(PageBreak());story.append(p('Appendix D. Actual generation and KES evidence','Heading1'))
generation=json.loads((R/'generation_summary.json').read_text())
story.append(p('A real local SmolLM2-135M-Instruct model was run on all 24 frozen test queries, using the top retrieved product for each. Evidence planning supplied catalogue price, category, accepted constraints and unknown stock before text generation. The prompt was developed with development/dry-run examples, then frozen for this test execution.'))
story.append(table([['Measured item','Result'],['Actual local outputs',generation['actual_llm_outputs']],['Accepted generated explanations',generation['accepted_llm_explanations']],['Flagged outputs / factual fallbacks',generation['fallback_responses']],['Price/category violations',str(generation['price_constraint_violations'])+' / '+str(generation['category_constraint_violations'])]],[330,135]))
story.append(Spacer(1,15));story.append(p('The 17 flagged outputs are not automatically 17 hallucinations: numeric, vocabulary and suitability checks are conservative heuristics with false positives and false negatives. All raw text, served text, IDs and flags are retained in reports/generation_evaluation.json. The small model is therefore a bounded verbalizer rather than a general retail adviser. Independent human factuality/relevance review remains future work.'))
story.append(p('KES conversion uses Kenya Revenue Authority weekly reference rates for 16-22 November 2026: 1 INR = 1.37 KES. Each converted response keeps the original INR price and marks the KES amount as an estimate. This is a dated conversion of historical Indian prices, not Kenyan inventory or a live offer. Source: https://www.kra.go.ke/images/foreignexchange/EXCHANGE-RATE-RUNNING-FROM-16th-November-2026-to-22nd-November-2026.pdf .'))
story.append(p('Generator: https://huggingface.co/HuggingFaceTB/SmolLM2-135M-Instruct . The pinned revision is recorded in artifacts/generator_manifest.json. Public artifacts and source alignment are explained in artifacts/ARTIFACTS.md; the CI workflow tests restoration without training.'))

def footer(canvas,doc):
 canvas.setStrokeColor(colors.HexColor('#c2d4d6'));canvas.line(44,43,550,43);canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#506476'));canvas.drawString(44,29,'RetailAssist | DSA 8401 | Admission 109419');canvas.drawRightString(550,29,str(doc.page))
SimpleDocTemplate(str(R/'RetailAssist_Report.pdf'),pagesize=(595,842),rightMargin=44,leftMargin=44,topMargin=48,bottomMargin=59,title='RetailAssist - implementation and study report',author='Admission 109419 (AI assistance disclosed)').build(story,onFirstPage=footer,onLaterPages=footer)

cells=[]
def md(s):cells.append(nbf.v4.new_markdown_cell(s))
def code(s):cells.append(nbf.v4.new_code_cell(textwrap.dedent(s).strip()))
md('# RetailAssist: complete executable walkthrough\nDSA 8401 | Admission 109419\n\nAI-assisted implementation: read `AI_USE.md`. Historical Indian catalogue; INR plus dated KES estimates; availability unknown. This notebook runs the same modules as the scripted pipeline. It does not call a paid LLM by default. Run the documented pipeline first, or set `REBUILD=True` below for a full rebuild.')
md('## 1. Locate the project and import the implementation\nRun cells in order. The working directory can be the project root or notebooks folder. Dependencies must be installed from requirements-dev.txt.')
code('''
from pathlib import Path
import sys, json, os
ROOT = Path.cwd()
if not (ROOT / 'src/retailassist').exists(): ROOT = ROOT.parent
assert (ROOT / 'src/retailassist').exists(), 'Start from project root or notebooks/'
sys.path.insert(0, str(ROOT / 'src'))
import pandas as pd
import numpy as np
from IPython.display import display
from retailassist.core import prepare, Engine, explain
print('Project:', ROOT.name)
''')
md('## 2. Rebuild from raw data when needed\n`pipeline.main()` downloads the pinned source, cleans it, fits TF-IDF and SVD, embeds the catalogue, and saves artifacts. REBUILD=False uses the already executed build. This avoids expensive retraining every time you explore a result.')
code('''
REBUILD = False
if REBUILD or not (ROOT/'artifacts/retriever.joblib').exists():
    import subprocess
    subprocess.run([sys.executable, '-m', 'retailassist.pipeline'], cwd=ROOT, check=True,
                   env={**os.environ,'PYTHONPATH':str(ROOT/'src')})
manifest = json.loads((ROOT/'artifacts/manifest.json').read_text())
display(manifest)
''')
md('## 3. Inspect semi-raw data\nA rating stored as "No rating available" is not a numeric zero. A missing stock field does not imply availability. Preserve INR prices and do not invent missing values.')
code('''
raw = pd.read_csv(ROOT/'data/raw/catalogue.csv')
print('Raw shape:', raw.shape)
display(raw[['product_name','brand','discounted_price','product_rating']].head(8))
display(raw.isna().sum().sort_values(ascending=False).to_frame('Missing cells'))
''')
md('## 4. Run and explain preprocessing\nInvalid prices and duplicate IDs are removed; brand, ratings and descriptions have explicit missingness policies. Inspect `prepare` to understand each transformation.')
code('''
clean, audit = prepare(raw)
display(audit)
display(clean[['id','name','category','price','rating','availability']].head())
assert clean.id.is_unique and clean.price.gt(0).all()
assert clean.availability.eq('unknown').all()
''')
md('## 5. Explore imbalance, prices and missingness\nLarge categories dominate the corpus. Descriptive plots describe this snapshot, not market demand or sales volume.')
code('''
import matplotlib.pyplot as plt
fig, axes = plt.subplots(1, 2, figsize=(12,4))
clean.category.value_counts().head(10).sort_values().plot.barh(ax=axes[0],title='Largest catalogue categories')
np.log10(clean.price).plot.hist(bins=40,ax=axes[1],title='Price distribution (log10 INR)')
axes[1].set_xlabel('log10(INR)'); plt.tight_layout(); plt.show()
display(clean.price.describe(percentiles=[.1,.5,.9,.99]))
''')
md('## 6. Inspect the fitted representations\nTF-IDF learns term statistics; SVD learns latent co-occurrence factors. MiniLM is pretrained and not fine-tuned here. Full catalogue indexing is appropriate for search; held-out queries test retrieval.')
code('''
engine = Engine()
print('TF-IDF matrix:', engine.b['tfidf'].shape)
print('LSA matrix:', engine.b['latent'].shape)
print('Semantic matrix:', engine.b.get('embeddings', np.empty((0,0))).shape)
print('SVD explained variance sum:', engine.b['svd'].explained_variance_ratio_.sum())
terms = engine.b['vectorizer'].get_feature_names_out()
weights = engine.b['svd'].components_[0]
print('First latent direction terms:', terms[np.argsort(weights)[-12:]].tolist())
''')
md('## 7. Trace query parsing and hard filters\nStructured constraints express confirmed user intent. Prices never exceed the accepted ceiling. The parser handles common budget phrases but is not a general language-understanding system.')
code('''
query = 'comfortable running shoes under INR 1500'
print(engine.parse(query))
result = engine.search(query,method='hybrid',constraints={'category':'Footwear'})
display(pd.DataFrame(result['products']))
assert all(p['price'] <= 1500 and p['category']=='Footwear' for p in result['products'])
print(explain(result)['answer'])
''')
md('## 8. Compare lexical and semantic rankings\nInspect actual items for paraphrased intent. A larger score is not a calibrated probability, and different methods have different score distributions.')
code('''
for method in ['tfidf','lsa','semantic','hybrid']:
    r = engine.search('footwear for jogging',method=method,k=3,constraints={'category':'Footwear'})
    print('\\n',method)
    display(pd.DataFrame(r['products'])[['id','name','price','score']])
''')
md('## 9. Test abstention, currency and unknown stock\nConservative refusal is appropriate when accepted constraints cannot be verified.')
code('''
assert engine.search('running shoes',constraints={'max_price':1})['products']==[]
assert engine.search('running shoes',constraints={'in_stock':True})['products']==[]
try:
    engine.search('laptop below USD 80000')
except ValueError as e:
    print('Expected validation:', e)
''')
md('## 10. Inspect the silver benchmark\nQueries and rule-based judgments are AI-authored weak labels. They do not represent human preferences. Test intent families overlap with development; this is exploratory evaluation.')
code('''
from retailassist.evaluate import judgments, metrics, main as evaluate
queries=json.loads((ROOT/'data/queries.json').read_text())
display(pd.DataFrame(queries))
q=queries[6]
relevant=judgments(clean,q)
print('Example query:',q['query'],'Silver positives:',len(relevant))
display(clean[clean.id.isin(relevant)][['id','name','price']].head())
''')
md('## 11. Recompute actual ranking metrics\nPrecision divides by five; recall divides by all silver positives; MRR rewards the first hit; NDCG discounts rank. Zero-judgment queries are explicitly excluded from summary means, but retained in per-query output.')
code('''
evaluate()
summary=pd.read_csv(ROOT/'reports/metrics.csv')
display(summary)
summary[summary.split.eq('test')].set_index('method')[['precision_at_5','recall_at_5','mrr_at_5','ndcg_at_5']].plot.bar(figsize=(10,4),ylim=(0,1),title='Test metrics: silver labels')
plt.tight_layout();plt.show()
''')
md('## 12. Inspect failures and verify constraints\nAveraging can hide poor intents. Review low-scoring queries and manually judge the recommendations before making any claim of quality.')
code('''
per=pd.read_csv(ROOT/'reports/per_query_metrics.csv')
display(per[(per.split=='test') & (per.method=='hybrid')].sort_values('ndcg_at_5').head(8))
print('Constraint violations:', per.constraint_violations.sum())
print('Invalid product IDs:', per.invalid_product_ids.sum())
assert per.constraint_violations.sum()==0
assert per.invalid_product_ids.sum()==0
print('Metric sanity:',metrics(['a','x','b'], {'a','b'}))
''')
md('## 13. Exercise the real API without a running server\nFastAPI TestClient runs startup and a prediction through the HTTP contract. Automated tests separately mock external LLM responses. This does not verify a live paid LLM.')
code('''
from fastapi.testclient import TestClient
from retailassist.api import app
with TestClient(app) as client:
    display(client.get('/health').json())
    response=client.post('/recommend',json={'query':'running shoes under INR 1500','method':'tfidf','constraints':{'category':'Footwear'}})
    assert response.status_code==200
    display(response.json())
''')
md('## 14. Actual local LLM, Docker and submission\nLocal SmolLM2 generates real text from retrieved evidence, with raw-output checks and factual fallbacks. Inspect reports/generation_evaluation.json and generation_summary.json for 24 real test outputs (7 accepted, 17 flagged/fallback). Hosted OpenAI calls are optional and untested.\n\nKES is a dated reference estimate, not Kenyan inventory. Run bootstrap --with-generator to restore public trained artifacts and the pinned generator without retraining, then docker compose up --build -d. Read PROJECT_COMPLIANCE.md, ARTIFACTS.md, AI_USE.md and the final report.')
nb=nbf.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Python 3 (RetailAssist)','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.9'}})
if not (ROOT/'notebooks/RetailAssist_walkthrough.ipynb').exists():
    nbf.write(nb,ROOT/'notebooks/RetailAssist_walkthrough.ipynb')
print('Generated report and notebook')
