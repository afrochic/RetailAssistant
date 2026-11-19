"""Render the editable Markdown report into its submitted PDF; local authoring utility."""
from pathlib import Path
import re
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, Preformatted, KeepTogether

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'RETAILASSIST_FINAL_REPORT.md'
OUTPUT=ROOT/'RETAILASSIST_FINAL_REPORT.pdf'
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='ReportBody',fontName='Helvetica',fontSize=9.3,leading=14,spaceAfter=7,textColor=colors.HexColor('#23352E')))
styles.add(ParagraphStyle(name='ReportTitle',fontName='Helvetica-Bold',fontSize=22,leading=27,spaceAfter=17,textColor=colors.HexColor('#214D3D')))
styles.add(ParagraphStyle(name='ReportH1',fontName='Helvetica-Bold',fontSize=15,leading=19,spaceBefore=16,spaceAfter=9,textColor=colors.HexColor('#214D3D'),keepWithNext=True))
styles.add(ParagraphStyle(name='ReportH2',fontName='Helvetica-Bold',fontSize=11,leading=15,spaceBefore=10,spaceAfter=7,textColor=colors.HexColor('#214D3D'),keepWithNext=True))
styles.add(ParagraphStyle(name='CellSmall',fontName='Helvetica',fontSize=8,leading=11,textColor=colors.HexColor('#23352E')))
styles.add(ParagraphStyle(name='Caption',fontName='Helvetica-Oblique',fontSize=8,leading=11,spaceAfter=12,textColor=colors.HexColor('#52675D')))

def clean(t):
 for a,b in [('—','-'),('–','-'),('’',"'"),('‘',"'"),('“','"'),('”','"'),('→','->'),('×','x'),('≥','>=')]: t=t.replace(a,b)
 return t

def inline(t):
 t=escape(clean(t))
 t=re.sub(r'`([^`]+)`',r'<font name="Courier">\1</font>',t)
 t=re.sub(r'\*\*([^*]+)\*\*',r'<b>\1</b>',t)
 t=re.sub(r'\*([^*]+)\*',r'<i>\1</i>',t)
 return t

def para(t,sty='ReportBody'): return Paragraph(inline(t),styles[sty])
lines=SOURCE.read_text().splitlines();story=[];i=0
while i<len(lines):
 line=lines[i].strip()
 if not line: i+=1;continue
 if line.startswith('```'):
  block=[];i+=1
  while i<len(lines) and not lines[i].startswith('```'):block.append(clean(lines[i]));i+=1
  story.append(Preformatted('\n'.join(block),ParagraphStyle('code',fontName='Courier',fontSize=7,leading=10,spaceAfter=10)))
 elif line.startswith('!['):
  m=re.match(r'!\[([^]]+)\]\(([^)]+)\)',line)
  if m and (ROOT/m[2]).exists():
   img=Image(str(ROOT/m[2]));scale=min(460/img.imageWidth,245/img.imageHeight);img.drawWidth=img.imageWidth*scale;img.drawHeight=img.imageHeight*scale
   story.append(KeepTogether([img,para(m[1],'Caption')]))
 elif line.startswith('|'):
  rows=[]
  while i<len(lines) and lines[i].strip().startswith('|'):
   cells=[x.strip() for x in lines[i].strip().strip('|').split('|')]
   if not all(re.fullmatch(r'[: -]+',x) for x in cells):rows.append([para(x,'CellSmall') for x in cells])
   i+=1
  n=len(rows[0]);widths=[470/n]*n
  if n==2:widths=[245,225]
  if n==3:widths=[110,150,210]
  table=Table(rows,colWidths=widths,repeatRows=1,hAlign='LEFT')
  table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#DFEAE3')),('LINEBELOW',(0,0),(-1,0),.6,colors.HexColor('#517562')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('LINEBELOW',(0,1),(-1,-1),.25,colors.HexColor('#DCE5DF'))]))
  story.extend([table,Spacer(1,12)]);continue
 elif line.startswith('# '):story.append(para(line[2:],'ReportTitle'))
 elif line.startswith('## '):story.append(para(line[3:],'ReportH1'))
 elif line.startswith('### '):story.append(para(line[4:],'ReportH2'))
 elif line.startswith('- '):story.append(para('• '+line[2:]))
 elif re.match(r'^\d+\. ',line):story.append(para(line))
 else:
  chunk=[line];i+=1
  while i<len(lines) and lines[i].strip() and not re.match(r'^(#|\||!\[|```|- |\d+\. )',lines[i].strip()):chunk.append(lines[i].strip());i+=1
  story.append(para(' '.join(chunk)));continue
 i+=1

def page(canvas,doc):
 canvas.saveState();w,h=A4
 canvas.setStrokeColor(colors.HexColor('#CADACF'));canvas.line(42,h-30,w-42,h-30)
 canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#52675D'))
 canvas.drawString(42,h-22,'RETAILASSIST | DSA 8401 | 109419')
 canvas.drawString(42,25,'Evidence cut-off: 20 November 2026 | Controlled local and public production evidence; limitations stated explicitly')
 canvas.drawRightString(w-42,25,str(doc.page));canvas.restoreState()

doc=SimpleDocTemplate(str(OUTPUT),pagesize=A4,rightMargin=42,leftMargin=42,topMargin=48,bottomMargin=44,title='RetailAssist - Final Applied Machine Learning Report',author='Admission 109419',allowSplitting=True)
doc.build(story,onFirstPage=page,onLaterPages=page)
print(OUTPUT)
