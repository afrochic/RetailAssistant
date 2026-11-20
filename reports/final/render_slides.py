"""Render the 12-slide Client X PDF presentation from verified repository evidence."""
from pathlib import Path
import json
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'RETAILASSIST_PRESENTATION.pdf'
M = json.loads((ROOT / 'evaluation/offline_summary.json').read_text())
FONT_DIR = Path('/System/Library/Fonts/Supplemental')
if (FONT_DIR / 'Arial.ttf').exists():
    pdfmetrics.registerFont(TTFont('Deck', str(FONT_DIR / 'Arial.ttf')))
    pdfmetrics.registerFont(TTFont('DeckBold', str(FONT_DIR / 'Arial Bold.ttf')))
else:
    # Standard PDF fonts keep rendering portable on Linux/offline CI.
    pdfmetrics.registerFontFamily('Helvetica', normal='Helvetica', bold='Helvetica-Bold')
    FONT_DIR = None
REG = 'Deck' if FONT_DIR else 'Helvetica'
BOLD = 'DeckBold' if FONT_DIR else 'Helvetica-Bold'
pdfmetrics.registerFontFamily(REG, normal=REG, bold=BOLD)
W, H = 1280, 720
BG, INK, MUTED, ACCENT, DARK = map(HexColor, ['#FAFAF5','#214A3B','#5D7065','#A27738','#153D30'])
C = canvas.Canvas(str(OUT), pagesize=(W,H))
C.setTitle('RetailAssist - Client X capstone presentation')
C.setAuthor('Admission 109419')
C.setSubject('DSA 8401 Applied Machine Learning - verified results and limitations')


def text(value, x, y, width, size=25, color=INK, bold=False, leading=None):
    style=ParagraphStyle('deck', fontName=BOLD if bold else REG, fontSize=size,
                         leading=leading or size*1.32, textColor=color)
    p=Paragraph(value, style)
    _, height=p.wrap(width, H)
    if y-height < 42:
        raise ValueError(f'Text overflows page at {value[:70]}')
    p.drawOn(C,x,y-height)
    return y-height


def start(number, title, subtitle=None, dark=False):
    C.setFillColor(DARK if dark else BG);C.rect(0,0,W,H,fill=1,stroke=0)
    fg=HexColor('#F6F7EC') if dark else INK
    text(title,64,655,1150,42,fg,True)
    if subtitle:text(subtitle,66,594,1120,20,HexColor('#B9CBBE') if dark else MUTED)
    C.setFillColor(HexColor('#B9CBBE') if dark else MUTED)
    C.setFont(REG,14);C.drawString(64,27,'RetailAssist  /  Client X  /  DSA 8401')
    C.drawRightString(W-64,27,f'{number:02d} / 12')


def bullets(items, x=70,y=545,width=1100,size=27,gap=22):
    for value in items:
        y=text('• '+value,x,y,width,size)-gap
    return y


def foot(value):text(value,66,68,1145,14,MUTED,leading=17)


def image(name,x,y,w,h):
    path=ROOT/'evaluation'/name
    reader=ImageReader(str(path));iw,ih=reader.getSize();scale=min(w/iw,h/ih)
    C.drawImage(reader,x+(w-iw*scale)/2,y+(h-ih*scale)/2,iw*scale,ih*scale,mask='auto')


def end():C.showPage()

# 1. Restrained cover; no synthetic imagery or unsupported claims.
start(1,'RetailAssist',dark=True)
text('Catalogue-grounded<br/>conversations for Client X',64,532,1080,58,HexColor('#F6F7EC'),True,70)
text('Fitted retrieval. Controlled generation. Traceable evidence.',68,330,1080,27,HexColor('#C7D7CA'))
text('MSc Data Science &amp; Analytics<br/>DSA 8401 - Applied Machine Learning<br/>Admission 109419 · 20 November 2026',68,222,1080,22,HexColor('#C7D7CA'))
end()

# 2.
start(2,'Product discovery with incomplete evidence')
text('“Find breakfast oats under KES 2,000.”',68,555,1120,41,INK,True)
text('A natural-language request must become evidence-based product choices.',70,470,1090,27,MUTED)
bullets(['Products and prices must exist in the approved catalogue.',
         'Budgets and unknown attributes must be handled explicitly.',
         'Retail recommendations must remain separate from medical advice.'],y=390,size=27,gap=24)
foot('Scope: anonymous chat, without accounts, storefront browsing, cart or checkout.')
end()

# 3.
start(3,'Research objectives')
for number,title,detail,y in [
 ('01','Reproduce the pipeline','Approved source → preprocessing → fitted index → prediction.',550),
 ('02','Ground every recommendation','Use catalogue IDs, KES prices and supported explanations.',440),
 ('03','Respect constraints and uncertainty','Filter required preferences; abstain when evidence is missing.',330),
 ('04','Evaluate honestly','Separate software diagnostics, relevance evaluation and deployment checks.',220)]:
    text(number,68,y,70,28,ACCENT,True)
    text(title,155,y,1020,28,INK,True)
    text(detail,155,y-44,1010,23,MUTED)
end()

# 4.
start(4,'Client X dataset and data quality','Approved product-only distribution source; no customer or order data')
text(f"{M['accepted_records']:,}",68,535,280,65,INK,True)
text('records retained<br/>zero rejects',71,445,260,24,MUTED)
text('133',68,330,250,47,INK,True)
text('overlapping category labels',71,267,260,23,MUTED)
text('0',68,180,230,47,INK,True)
text('duplicate IDs or<br/>normalized names found',71,123,270,21,MUTED)
image('category_distribution.png',350,106,864,452)
foot('Categories overlap; name uniqueness does not establish the absence of near-duplicate products. Source: current offline_summary.json.')
end()

# 5. Native text flow preserves a simple, inspectable architecture.
start(5,'System architecture','Heavy preparation stays offline; compact artifacts support inference')
text('OFFLINE',68,540,200,18,ACCENT,True)
text('Approved source → clean text → fit TF-IDF → products / index / manifest',68,496,1130,29,INK,True)
text('ONLINE',68,389,200,18,ACCENT,True)
text('Next.js chat → FastAPI controls → constrained retrieval',68,344,1120,30,INK,True)
text('Retrieved records → Groq OR factual fallback → validated CX references',68,286,1130,27,INK)
text('Two containerized services · server-only provider key · shared public quota counters',68,175,1130,23,MUTED)
foot('Both app-root Docker images and the root API image built; a disposable current container passed readiness and fallback checks.')
end()

# 6.
start(6,'Preprocessing and feature engineering')
bullets(['Convert source text to plain text and normalize fields.',
         'Remove client aliases and identifying retailer URLs.',
         'Fit 12,000 TF-IDF features and normalized sparse postings.',
         'Verify artifact hashes and product/index alignment.'],x=68,y=550,width=425,size=25,gap=24)
image('price_distribution.png',510,138,708,414)
foot('All 5,512 records have positive listed KES prices; median KES 1,599. Stock and snapshot freshness are not verified.')
end()

# 7.
start(7,'Retrieval and response generation')
rows=[['Method','Implemented status','Role'],
      ['TF-IDF','Fitted and exercised','Transparent, compact retrieval baseline'],
      ['Groq GPT-OSS','Hosted generation','Constrained response composition'],
      ['Projected semantic / RRF','Source only; not evaluated','Optional offline experiment']]
style=ParagraphStyle('table',fontName=REG,fontSize=22,leading=29,textColor=INK)
data=[[Paragraph(escape(v),style) for v in row] for row in rows]
t=Table(data,colWidths=[295,340,510],rowHeights=[52,90,90,102])
t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'MIDDLE'),('BACKGROUND',(0,0),(-1,0),HexColor('#E2EBDD')),('LINEBELOW',(0,0),(-1,-1),.65,HexColor('#CED9CD')),('LEFTPADDING',(0,0),(-1,-1),12)]))
t.wrapOn(C,1150,400);t.drawOn(C,66,235)
text('GPT-OSS was not trained or fine-tuned. Optional query projection is not native transformer query encoding.',68,184,1125,24,INK,True)
foot('Method references: <link href="https://arxiv.org/abs/1908.10084">Reimers &amp; Gurevych (2019), Sentence-BERT</link>; <link href="https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf">Cormack et al. (2009), RRF</link>; <link href="https://arxiv.org/abs/2005.11401">Lewis et al. (2020), RAG</link>.')
end()

# 8.
start(8,'Evaluation protocol and evidence limits')
text('13 cases × 20 warm repeats = 260 timings',68,555,1120,39,INK,True)
bullets(['Check returned IDs, KES budgets, deterministic ordering and abstention.',
         'Exclude startup, network, hosted generation and UI from retrieval latency.',
         'Keep diagnostic cases separate from independent relevance judgments.'],y=450,size=27,gap=24)
text('Ranking metrics remain blocked',68,203,1120,30,ACCENT,True)
text('Precision@K, Recall@K, MRR and NDCG require independently reviewed relevance labels.',68,151,1110,24,MUTED)
foot('No generated relevance labels were presented as human-reviewed ground truth; no semantic comparison score was fabricated.')
end()

# 9.
start(9,'Measured local retrieval results','Fresh Client X distribution source; fitted TF-IDF only')
text(f"{M['latency_mean_ms']:.2f} ms",68,533,320,53,INK,True)
text('mean warm retrieval',70,462,320,23,MUTED)
text(f"{M['latency_p95_ms']:.2f} ms",68,365,320,53,INK,True)
text('95th percentile',70,294,320,23,MUTED)
text('640',68,198,300,48,INK,True)
text('repeated reference occurrences',70,133,320,21,MUTED)
image('retrieval_latency.png',420,126,795,429)
foot('0 invalid IDs / exercised constraint violations · 5 of 5 expected abstentions passed. Repeated references are not independent relevance labels.')
end()

# 10.
start(10,'Historical public integration checks','Observed at source 7d46aea, before the Client X cleanup')
rows=[['Controlled scenario','Observed mode','References'],
      ['Budget recommendation','groq_grounded','3'],
      ['Dietary uncertainty','clarification','0'],
      ['Urgent medical symptoms','urgent_safety','0'],
      ['Impossible product / budget','no_matches','0'],
      ['Narrower-budget follow-up','groq_grounded','3']]
data=[[Paragraph(escape(v),style) for v in row] for row in rows]
t=Table(data,colWidths=[510,400,235],rowHeights=[45]+[58]*5)
t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'MIDDLE'),('BACKGROUND',(0,0),(-1,0),HexColor('#E2EBDD')),('LINEBELOW',(0,0),(-1,-1),.6,HexColor('#CED9CD')),('LEFTPADDING',(0,0),(-1,-1),12)]))
t.wrapOn(C,1150,400);t.drawOn(C,66,220)
text('All five returned HTTP 200. Two used actual Groq generation.',68,184,1110,25,INK,True)
text('The Client X snapshot is not yet verified in production; original identifying captures are withheld.',68,132,1110,22,MUTED)
foot('Historical references matched source fields and budgets. This small smoke sample is not general relevance or clinical-safety validation.')
end()

# 11.
start(11,'Safety, missing metadata and privacy')
image('missing_data.png',52,141,755,405)
bullets(['Urgent medical requests bypass recommendations.',
         'Unknown ingredients and stock cannot establish suitability.',
         'Public products have null URLs; citations use CX IDs.',
         'Client-name redaction does not erase earlier Git or cloud history.'],x=850,y=547,width=365,size=23,gap=18)
foot('Rule-based safety is not clinical validation. Provider-key rotation, mobile accessibility and load resilience remain unverified.')
end()

# 12.
start(12,'Conclusion and next steps',dark=True)
fg=HexColor('#F6F7EC');muted=HexColor('#C7D7CA')
text('A reproducible lexical / RAG baseline',68,535,1120,42,fg,True)
text('25 API tests and current backend, frontend and Docker CI passed.<br/>The local Client X pipeline and null-URL fallback were verified.',70,450,1090,27,muted)
text('REMAINING RESEARCH',70,328,1050,18,HexColor('#D1B983'),True)
text('Human-reviewed relevance labels · semantic comparison<br/>Fresh anonymized production checks · mobile and accessibility validation',70,285,1100,27,fg)
text('Repository: github.com/afrochic/RetailAssistant<br/>One-page report and reproducibility evidence: reports/final/ · AI disclosure: AI_USE.md',70,164,1100,21,muted)
end()
C.save()
assert len(PdfReader(OUT).pages)==12, 'Presentation must have exactly 12 pages.'
print(f'Created {OUT.name}: 12 landscape slides')
