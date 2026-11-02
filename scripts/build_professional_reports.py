"""Build the two reviewed report sources with a common engineering report layout."""
from pathlib import Path
import re,json,argparse
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH,WD_BREAK,WD_TAB_ALIGNMENT,WD_TAB_LEADER
from docx.enum.section import WD_SECTION,WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/reports/final_report'
# Reuse the already verified native equation constructors without running a legacy builder.
legacy=(ROOT/'scripts/build_final_report_docx.py').read_text()
mathns={'OxmlElement':OxmlElement,'qn':qn}
exec(legacy[legacy.index('def mr('):legacy.index('eq_index=0')],mathns)
def remove_borders(d):
 for e in list(d.styles.element.xpath('.//w:pBdr')):e.getparent().remove(e)
def runtext(p,text):
 # Bind C++ as one typographic token without changing source text.
 p.add_run(text.replace('C++','C\u2060+\u2060+'))
def inline(p,text,base):
 pat=re.compile(r'\[([^\]]+)\]\(([^)]+)\)|`([^`]+)`|\$([^$]+)\$')
 start=0
 for m in pat.finditer(text):
  runtext(p,text[start:m.start()])
  if m[1]:
   target=m[2];target=target if re.match(r'https?://',target) else (base/target).resolve().as_uri()
   link=OxmlElement('w:hyperlink');link.set(qn('r:id'),p.part.relate_to(target,'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink',is_external=True))
   r=OxmlElement('w:r');pr=OxmlElement('w:rPr');c=OxmlElement('w:color');c.set(qn('w:val'),'000000');pr.append(c);r.append(pr);t=OxmlElement('w:t');t.text=m[1];r.append(t);link.append(r);p._p.append(link)
  else:runtext(p,m[3] or m[4])
  start=m.end()
 runtext(p,text[start:])
def bookmark(p,name,idx):
 b=OxmlElement('w:bookmarkStart');b.set(qn('w:id'),str(idx));b.set(qn('w:name'),name);e=OxmlElement('w:bookmarkEnd');e.set(qn('w:id'),str(idx));p._p.insert(0,b);p._p.append(e)
def anchor(p,label,name):
 h=OxmlElement('w:hyperlink');h.set(qn('w:anchor'),name);r=OxmlElement('w:r');t=OxmlElement('w:t');t.text=label;r.append(t);h.append(r);p._p.append(h)
def footer(section,style,start,label):
 section.footer.is_linked_to_previous=False
 p=section.footer.paragraphs[0];p.alignment=WD_ALIGN_PARAGRAPH.CENTER
 p.paragraph_format.space_before=Pt(4)
 r=OxmlElement('w:fldSimple');r.set(qn('w:instr'),'PAGE');p._p.append(r)
 pg=OxmlElement('w:pgNumType');pg.set(qn('w:fmt'),style);pg.set(qn('w:start'),str(start));section._sectPr.append(pg)
 section.header.is_linked_to_previous=False
 hp=section.header.paragraphs[0];hp.add_run(label).font.size=Pt(8.5);hp.paragraph_format.space_after=Pt(4)
 hp.alignment=WD_ALIGN_PARAGRAPH.RIGHT

def table(d,lines,base):
 rows=[[x.strip() for x in l.strip().strip('|').split('|')] for l in lines];rows=[rows[0]]+rows[2:]
 n=len(rows[0]);t=d.add_table(rows=0,cols=n);t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
 if n==2:widths=[2.8,3.5]
 elif n==3:widths=[1.65,2.325,2.325]
 elif n==4:widths=[1.8,1.5,1.5,1.5]
 else:widths=[1.8]+[4.5/(n-1)]*(n-1)
 if rows[0][0] in ['Parameter','Term']:widths=[.7,2.7,1.45,1.45]
 if rows[0][0]=='Quantity':widths=[1.45,3.0,1.85]
 if rows[0][0]=='Verification step':widths=[1.55,2.55,2.2]
 if rows[0][0]=='Row':widths=[.6,1.9,1.9,1.9]
 if rows[0][0]=='Channel':widths=[1.1,4.45,.75]
 if rows[0][0]=='Lag in hours':widths=[.7,1.1,1.1,1.25,2.15]
 for c,w in zip(t.columns,widths):c.width=Inches(w)
 borders=OxmlElement('w:tblBorders')
 for side in ['top','left','bottom','right','insideH','insideV']:
  b=OxmlElement('w:'+side);b.set(qn('w:val'),'single');b.set(qn('w:sz'),'4');b.set(qn('w:color'),'D9D9D9');borders.append(b)
 t._tbl.tblPr.append(borders)
 for ri,row in enumerate(rows):
  tr=t.add_row();pr=tr._tr.get_or_add_trPr();pr.append(OxmlElement('w:cantSplit'))
  if ri==0:pr.append(OxmlElement('w:tblHeader'))
  for ci,(cell,txt) in enumerate(zip(tr.cells,row)):
   cell.width=Inches(widths[ci]);cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
   cp=cell._tc.get_or_add_tcPr();sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'EAEAEA' if ri==0 else 'FFFFFF');cp.append(sh)
   mar=OxmlElement('w:tcMar')
   for side,val in [('top','75'),('bottom','75'),('left','90'),('right','90')]:
    el=OxmlElement('w:'+side);el.set(qn('w:w'),val);el.set(qn('w:type'),'dxa');mar.append(el)
   cp.append(mar)
   p=cell.paragraphs[0];p.paragraph_format.line_spacing=1.0;p.paragraph_format.space_after=Pt(1);p.paragraph_format.space_before=Pt(1)
   p.paragraph_format.keep_with_next=ri<len(rows)-1
   # Text columns read naturally left aligned; short quantitative values center.
   numeric=bool(re.match(r'^[−\-+]?\d',txt)) or txt in ['PASS','Same']
   p.alignment=WD_ALIGN_PARAGRAPH.CENTER if ci>0 and numeric else WD_ALIGN_PARAGRAPH.LEFT
   inline(p,txt,base)
   for r in p.runs:r.font.size=Pt(10);r.bold=ri==0
 d.add_paragraph().paragraph_format.space_after=Pt(1)

def eq(d,latex,num):
 key=0 if '\\mathrm{MAE}' in latex else 1 if '\\mathrm{RMSE}' in latex else 2 if '\\widehat T' in latex else 3
 p=d.add_paragraph(style='Equation');p.paragraph_format.tab_stops.add_tab_stop(Inches(6.3),WD_TAB_ALIGNMENT.RIGHT)
 p.alignment=WD_ALIGN_PARAGRAPH.CENTER
 m=mathns['equation'](key)
 # Explicit size keeps the complete temperature equation within the text column.
 for r in m.iter(qn('m:r')):
  pr=OxmlElement('w:rPr');sz=OxmlElement('w:sz');sz.set(qn('w:val'),'21' if key==2 else '23');pr.append(sz);r.insert(0,pr)
 p._p.append(m);p.add_run(f'    ({num})').font.size=Pt(10)
 if key==3:
  q=d.add_paragraph('ℓ = [0, 1, 3, 6, 12, 21, 24]',style='Equation');q.alignment=WD_ALIGN_PARAGRAPH.CENTER

def build(stem,page_map=None):
 md=OUT/(stem+'.md');lines=md.read_text().splitlines();title=lines[0][2:]
 guide='Explained' in stem
 label='CE436  Technical companion' if guide else 'CE436  Implementation report'
 d=Document();s=d.sections[0]
 s.page_width=Inches(8.2677);s.page_height=Inches(11.6929);s.top_margin=Inches(.85);s.bottom_margin=Inches(.8);s.left_margin=Inches(.984);s.right_margin=Inches(.984)
 s.header_distance=Inches(.38);s.footer_distance=Inches(.38)
 for st in d.styles:
  if st.type==1:
   st.font.name='Liberation Serif';st.font.color.rgb=RGBColor(0,0,0)
   rf=st.element.get_or_add_rPr().find(qn('w:rFonts'))
   if rf is not None:
    for a in list(rf.attrib):
     if a.endswith('Theme'):del rf.attrib[a]
    for a in ['ascii','hAnsi','eastAsia','cs']:rf.set(qn('w:'+a),'Liberation Serif')
 n=d.styles['Normal'];n.font.size=Pt(11.5);n.paragraph_format.line_spacing=1.08;n.paragraph_format.space_after=Pt(6)
 n.paragraph_format.widow_control=True
 for name,size,bold in [('Title',24,False),('Subtitle',13,False),('Heading 1',14,True),('Heading 2',12,True),('Heading 3',11.5,True),('Caption',10,False)]:
  st=d.styles[name];st.font.size=Pt(size);st.font.bold=bold;st.font.italic=False;st.paragraph_format.space_before=Pt(14 if 'Heading' in name else 0);st.paragraph_format.space_after=Pt(6)
  if 'Heading' in name:st.paragraph_format.keep_with_next=True
 d.styles['Caption'].font.italic=True
 for name in ['Equation','Contents','Small']:
  if name not in d.styles:d.styles.add_style(name,1)
  st=d.styles[name];st.font.name='Times New Roman';st.font.color.rgb=RGBColor(0,0,0);st.font.size=Pt(10.5 if name!='Equation' else 11)
  st.paragraph_format.space_after=Pt(4)
 d.styles['Equation'].paragraph_format.space_before=Pt(4)
 d.styles['Small'].font.size=Pt(9.5)
 remove_borders(d)
 # Cover uses whitespace and the document subject rather than decorative graphics.
 p=d.add_paragraph('CE436',style='Subtitle');p.paragraph_format.space_before=Pt(44)
 p=d.add_paragraph('Discrete Time Signal Processing and Applications');p.paragraph_format.space_after=Pt(70)
 p=d.add_paragraph(title,style='Title');p.paragraph_format.space_after=Pt(18)
 subtitle=next(x.strip() for x in lines[1:] if x.strip())
 d.add_paragraph(subtitle,style='Subtitle')
 p=d.add_paragraph('Technical companion' if guide else 'Technical report');p.paragraph_format.space_before=Pt(80)
 d.add_paragraph('2 November 2026')
 if not guide:d.add_paragraph('Hardware verification  28 October 2026',style='Small')
 cs=d.add_section(WD_SECTION.NEW_PAGE);footer(cs,'lowerRoman',1,'')
 d.add_paragraph('Contents',style='Heading 1')
 # Keep a one-page contents list; page numbers are filled from the first render.
 headings=[]
 for l in lines:
  if re.match(r'^##? ',l):
   if l.startswith('## '):headings.append((1,l[3:]))
  elif l.startswith('### '):headings.append((2,l[4:]))
 for idx,(level,h) in enumerate(headings):
  p=d.add_paragraph(style='Contents');p.paragraph_format.left_indent=Inches(.15 if level==2 else 0);p.paragraph_format.space_after=Pt(3)
  p.paragraph_format.tab_stops.add_tab_stop(Inches(6.3),WD_TAB_ALIGNMENT.RIGHT,WD_TAB_LEADER.DOTS)
  anchor(p,h,'sec_'+str(idx));p.add_run('\t'+str((page_map or {}).get(h,'00')))
 bs=d.add_section(WD_SECTION.NEW_PAGE);footer(bs,'decimal',1,label)
 i=1;eqno=0;hidx=0;tabno=0;evidence=False;exhibit=0
 # Skip source cover metadata; the DOCX cover above represents it.
 while i<len(lines) and not lines[i].startswith('## '):i+=1
 while i<len(lines):
  l=lines[i]
  if not l.strip():i+=1;continue
  if l=='$$':
   a=i+1;i+=1
   while lines[i]!='$$':i+=1
   eqno+=1;eq(d,'\n'.join(lines[a:i]),eqno);i+=1;continue
  if l.startswith('|'):
   a=i
   while i<len(lines) and lines[i].startswith('|'):i+=1
   if guide and not any(x.startswith("Table ") for x in lines[max(0,a-3):a]):
    tabno+=1
    head=lines[a].split('|')[1].strip()
    names={'Symbol':'Hourly observations used by the temperature model','Row':'Illustrative least squares training rows','Quantity':'Integer calculation using the deployed temperature coefficients','Edge':'Clock schedule for one eligible input','Clock edge':'Illustrative input handshake','Verification step':'Scope of each verification stage'}
    p=d.add_paragraph(f'Table {tabno}. '+names.get(head,'Implementation values'),style='Caption');p.paragraph_format.keep_with_next=True
   table(d,lines[a:i],md.parent);continue
  if l.startswith('!['):
   m=re.match(r'!\[([^\]]*)\]\(([^)]+)\)',l);p=d.add_paragraph();
   if not guide and 'weather_speed.png' in l and any('Appendix B Physical waveform' in x for x in lines[:i]):p.paragraph_format.page_break_before=True
   p.paragraph_format.keep_with_next=True;p.paragraph_format.space_before=Pt(5);p.paragraph_format.space_after=Pt(3)
   picture=p.add_run().add_picture(str((md.parent/m[2]).resolve()),width=Inches(9.72 if evidence else 6.3))
   # Display a detail viewport while retaining the original screenshot pixels in DOCX.
   crops={'weather_speed_flow_summary.png':(0,0,1600,650),'weather_speed_timing_summary.png':(0,0,1550,385),'weather_speed_fmax.png':(0,0,1180,280)}
   name=Path(m[2]).name
   if evidence and name in crops:
    from PIL import Image
    iw,ih=Image.open((md.parent/m[2]).resolve()).size;x,y,cw,ch=crops[name]
    src=OxmlElement('a:srcRect')
    for key,value in [('l',x/iw),('t',y/ih),('r',(iw-x-cw)/iw),('b',(ih-y-ch)/ih)]:src.set(key,str(round(value*100000)))
    fill=picture._inline.xpath('.//pic:blipFill')[0];fill.insert(1,src)
    picture.height=Inches(9.72*ch/cw)
   p.runs[0]._r.xpath('.//wp:docPr')[0].set('descr',m[1]);i+=1;continue
  match=re.match(r'^(#{2,4}) (.+)',l)
  if match:
   level=len(match[1])-1;h=match[2]
   if 'Native implementation screenshots' in h:
    es=d.add_section(WD_SECTION.NEW_PAGE);pn=es._sectPr.find(qn('w:pgNumType'));pn=pn if pn is not None else OxmlElement('w:pgNumType');pn.set(qn('w:start'),str((page_map or {}).get(h,1)));pn.set(qn('w:fmt'),'decimal');es._sectPr.append(pn);es.orientation=WD_ORIENT.LANDSCAPE;es.page_width=Inches(11.6929);es.page_height=Inches(8.2677);es.top_margin=Inches(.55);es.bottom_margin=Inches(.55);evidence=True
   p=d.add_paragraph(h,style='Heading '+str(level))
   if evidence and level==3:
    if exhibit:p.paragraph_format.page_break_before=True
    exhibit+=1
   if level<=2:bookmark(p,'sec_'+str(hidx),hidx);hidx+=1
   if level==1 and (h.startswith('References') or (h.startswith('Appendix') and (not guide or h.startswith('Appendix A')))):p.paragraph_format.page_break_before=True
   i+=1;continue
  cap=l.startswith(('Table ','Figure ')) and bool(re.match(r'^(Table|Figure) [A-Z]?\d+\.',l))
  if re.match(r'^`[^`]+`$',l):
   text=l[1:-1]
   # Expanded seven-term equation is split at a meaningful sum boundary.
   if text.startswith('x̂(t + 3)'):
    text=text.replace(' + w4','\n+ w4')
   p=d.add_paragraph(style='Equation');p.alignment=WD_ALIGN_PARAGRAPH.CENTER
   for j,ln in enumerate(text.splitlines()):
    if j:p.add_run().add_break()
    p.add_run(ln).italic=True
  else:
   p=d.add_paragraph(style='Caption' if cap else 'Normal');inline(p,l.rstrip(),md.parent)
   if cap:p.paragraph_format.keep_with_next=l.startswith('Table ')
   # Keep a table lead-in or exercise question attached to its following item.
   if l.endswith(':') or (guide and l.endswith('?')):p.paragraph_format.keep_with_next=True
  i+=1
 d.core_properties.title=title;d.core_properties.subject=subtitle;d.core_properties.author='';d.core_properties.keywords='CE436 FPGA forecasting verification'
 out=OUT/(stem+'.docx');d.save(out)
 return {'file':str(out),'headings':[h for _,h in headings]}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--page-map');args=ap.parse_args();maps=json.loads(Path(args.page_map).read_text()) if args.page_map else {}
 result=[]
 for stem in ['FPGA_Forecasting_Final_Report_EN','FPGA_Forecasting_Explained_EN']:result.append(build(stem,maps.get(stem)))
 print(json.dumps(result,indent=2))
