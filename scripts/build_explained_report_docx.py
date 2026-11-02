"""Build the English report from its reviewed Markdown source."""
from pathlib import Path
import re
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
R=Path(__file__).resolve().parents[1];P=R/'docs/reports/final_report';md=P/'FPGA_Forecasting_Explained_EN.md'
d=Document();s=d.sections[0];s.page_height=Inches(11.7);s.page_width=Inches(8.3);s.top_margin=Inches(.75);s.bottom_margin=Inches(.75);s.left_margin=Inches(.75);s.right_margin=Inches(.75)
for name in ['Normal','Title','Subtitle','Heading 1','Heading 2','Caption']:
 st=d.styles[name];st.font.name='Arial';st.font.color.rgb=RGBColor(0,0,0)
n=d.styles['Normal'];n.font.size=Pt(11);n.paragraph_format.space_after=Pt(7);n.paragraph_format.line_spacing=1.12
for name,size in [('Title',23),('Heading 1',15),('Heading 2',12),('Caption',9)]:
 st=d.styles[name];st.font.size=Pt(size);st.paragraph_format.space_before=Pt(13 if name!='Caption' else 4);st.paragraph_format.space_after=Pt(6)
d.styles['Title'].paragraph_format.space_after=Pt(12)
d.styles['Caption'].font.bold=False
for border in list(d.styles.element.xpath('.//w:pBdr')):
 border.getparent().remove(border)
# Page numbering is useful for the report and its evidence references.
f=s.footer.paragraphs[0];f.alignment=WD_ALIGN_PARAGRAPH.RIGHT
field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');f._p.append(field)
def inline(p,text):
 pattern=re.compile(r'\[([^\]]+)\]\(([^)]+)\)|`([^`]+)`|\$([^$]+)\$')
 last=0
 for m in pattern.finditer(text):
  p.add_run(text[last:m.start()])
  if m[1]:
   link=OxmlElement('w:hyperlink');target=m[2]
   target=(md.parent/target).resolve().as_uri() if not re.match(r'https?://',target) else target
   rid=p.part.relate_to(target,'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink',is_external=True);link.set(qn('r:id'),rid)
   run=OxmlElement('w:r');props=OxmlElement('w:rPr');color=OxmlElement('w:color');color.set(qn('w:val'),'195B8A');props.append(color);run.append(props);txt=OxmlElement('w:t');txt.text=m[1];run.append(txt);link.append(run);p._p.append(link)
  else:p.add_run(m[3] or m[4])
  last=m.end()
 p.add_run(text[last:])
def table(lines):
 rows=[[x.strip() for x in l.strip().strip('|').split('|')] for l in lines];rows=[rows[0]]+rows[2:]
 t=d.add_table(rows=1,cols=len(rows[0]));t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
 cols=len(rows[0]);widths=([1.65]+[(6.8-1.65)/(cols-1)]*(cols-1)) if cols>2 else [1.5,5.3]
 for i,w in enumerate(widths):t.columns[i].width=Inches(w)
 pr=t._tbl.tblPr;borders=OxmlElement('w:tblBorders')
 for edge in ['top','left','bottom','right','insideH','insideV']:
  b=OxmlElement('w:'+edge);b.set(qn('w:val'),'single');b.set(qn('w:sz'),'4');b.set(qn('w:color'),'D9D9D9');borders.append(b)
 pr.append(borders)
 for ri,row in enumerate(rows):
  cells=t.rows[0].cells if ri==0 else t.add_row().cells
  trpr=t.rows[ri]._tr.get_or_add_trPr();cant=OxmlElement('w:cantSplit');trpr.append(cant)
  if ri==0:
   repeat=OxmlElement('w:tblHeader');trpr.append(repeat)
  for ci,(cell,text) in enumerate(zip(cells,row)):
   cell.width=Inches(widths[ci]);cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
   cp=cell._tc.get_or_add_tcPr();shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'DCE6EF' if ri==0 else ('F4F7FA' if ri%2==0 else 'FFFFFF'));cp.append(shade)
   margins=OxmlElement('w:tcMar')
   for side in ['top','left','bottom','right']:
    el=OxmlElement('w:'+side);el.set(qn('w:w'),'85');el.set(qn('w:type'),'dxa');margins.append(el)
   cp.append(margins);p=cell.paragraphs[0];p.paragraph_format.space_after=Pt(2);p.paragraph_format.space_before=Pt(2);p.paragraph_format.line_spacing=1.05;p.alignment=WD_ALIGN_PARAGRAPH.LEFT if ci==0 or cols==2 else WD_ALIGN_PARAGRAPH.CENTER
   inline(p,text)
   p.paragraph_format.keep_with_next=ri<len(rows)-1
   for run in p.runs:run.font.size=Pt(9);run.bold=ri==0
 d.add_paragraph().paragraph_format.space_after=Pt(1)
# Construct fractions, summation limits and subscripts as native editable OMML.
def mr(text):
 r=OxmlElement('m:r');t=OxmlElement('m:t');t.text=text;r.append(t);return r
def slot(tag,*children):
 e=OxmlElement('m:'+tag)
 for c in children:e.append(c)
 return e
def sub(base,idx):return slot('sSub',slot('e',mr(base)),slot('sub',mr(idx)))
def fraction():return slot('f',slot('num',mr('1')),slot('den',mr('N')))
def summation(index,upper,*body):
 n=OxmlElement('m:nary');pr=OxmlElement('m:naryPr');ch=OxmlElement('m:chr');ch.set(qn('m:val'),'∑');pr.append(ch);loc=OxmlElement('m:limLoc');loc.set(qn('m:val'),'undOvr');pr.append(loc);n.append(pr);n.append(slot('sub',mr(index)));n.append(slot('sup',mr(upper)));n.append(slot('e',*body));return n
def equation(index):
 m=OxmlElement('m:oMath')
 if index in [0,1]:
  m.append(mr('MAE = ' if index==0 else 'RMSE = '))
  body=[mr('|'),sub('ŷ','i'),mr(' − '),sub('y','i'),mr('|')]
  if index==1:body=[slot('sSup',slot('e',mr('('),sub('ŷ','i'),mr(' − '),sub('y','i'),mr(')')),slot('sup',mr('2')))]
  terms=[fraction(),summation('i = 1','N',*body)]
  if index==0:
   for t in terms:m.append(t)
  else:
   rad=OxmlElement('m:rad');pr=OxmlElement('m:radPr');hide=OxmlElement('m:degHide');hide.set(qn('m:val'),'1');pr.append(hide);rad.append(pr);rad.append(slot('deg'));rad.append(slot('e',*terms));m.append(rad)
 elif index==2:m.append(mr('T̂(t + 3) = T(t − 21) + a[T(t) − T(t − 24)] + b[T(t) − T(t − 3)] + c'))
 else:
  m.append(mr('x̂(t + 3) = '));m.append(sub('β','x'));m.append(mr(' + '));m.append(summation('k = 0','6',sub('w','x,k'),mr(' x(t − '),sub('ℓ','k'),mr(')')))
 return m
eq_index=0
lines=md.read_text().splitlines();i=0
while i<len(lines):
 line=lines[i]
 if not line.strip():i+=1;continue
 if line=='$$':
  i+=1
  while i<len(lines) and lines[i]!='$$':i+=1
  p=d.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER
  p._p.append(equation(eq_index))
  if eq_index==3:
   p2=d.add_paragraph('ℓ = [0, 1, 3, 6, 12, 21, 24]');p2.alignment=WD_ALIGN_PARAGRAPH.CENTER
  eq_index+=1;i+=1;continue
 if line.startswith('|'):
  start=i
  while i<len(lines) and lines[i].startswith('|'):i+=1
  table(lines[start:i]);continue
 if line.startswith('!['):
  m=re.match(r'!\[([^\]]*)\]\(([^)]+)\)',line);p=d.add_paragraph();p.paragraph_format.keep_with_next=True;p.add_run().add_picture(str((md.parent/m[2]).resolve()),width=Inches(6.8));p.paragraph_format.space_before=Pt(8)
  docpr=p.runs[0]._r.xpath('.//wp:docPr')[0];docpr.set('descr',m[1]);i+=1;continue
 if line.startswith('# '):d.add_paragraph(line[2:],'Title');i+=1;continue
 if line.startswith('## '):
  title=line[3:];p=d.add_paragraph(title,'Heading 1')
  if title.startswith('Part '):p.paragraph_format.page_break_before=True
  if title=='Abstract':p.paragraph_format.space_before=Pt(16)
  i+=1;continue
 if line.startswith('### '):d.add_paragraph(line[4:],'Heading 2');i+=1;continue
 p=d.add_paragraph(style='Caption' if line.startswith('Figure ') else 'Normal');inline(p,line.rstrip());i+=1
 if line.endswith('  '):p.paragraph_format.space_after=Pt(2)
d.core_properties.title='Understanding our FPGA forecasting project from the beginning';d.core_properties.subject='CE436 implementation and verification report';d.core_properties.author='';d.core_properties.keywords='FPGA, OLS, fixed point, JTAG, SignalTap, verification'
out=P/'FPGA_Forecasting_Explained_EN.docx';d.save(out);print(out)
