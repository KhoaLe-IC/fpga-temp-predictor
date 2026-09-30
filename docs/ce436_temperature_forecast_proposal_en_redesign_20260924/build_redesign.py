from pathlib import Path
from lxml import etree as ET

OUT = Path(__file__).parent / 'svg_output'
NS = 'http://www.w3.org/2000/svg'
WHITE, INK, BLUE, DEEP, GRAY, PALE, RULE = '#FFFFFF', '#161616', '#0F62FE', '#002D9C', '#525252', '#F4F4F4', '#DDE1E6'

def E(parent, tag, **attrs):
    return ET.SubElement(parent, f'{{{NS}}}{tag}', {k.replace('_','-'): str(v) for k,v in attrs.items()})

def R(parent,x,y,w,h,fill=PALE,rx=0,stroke=None,sw=1):
    kw=dict(x=x,y=y,width=w,height=h,fill=fill)
    if rx: kw['rx']=rx
    if stroke: kw.update(stroke=stroke,stroke_width=sw)
    return E(parent,'rect',**kw)

def L(parent,x1,y1,x2,y2,color=RULE,sw=2):
    return E(parent,'line',x1=x1,y1=y1,x2=x2,y2=y2,stroke=color,stroke_width=sw)

def C(parent,x,y,r,fill=BLUE,stroke=None,sw=1):
    kw=dict(cx=x,cy=y,r=r,fill=fill)
    if stroke: kw.update(stroke=stroke,stroke_width=sw)
    return E(parent,'circle',**kw)

def T(parent,x,y,s,size=30,color=INK,weight='normal',family='Arial',anchor=None):
    kw=dict(x=x,y=y,font_size=size,fill=color,font_weight=weight,font_family=family)
    if anchor: kw['text_anchor']=anchor
    el=E(parent,'text',**kw); el.text=s; return el

def M(parent,x,y,lines,size=30,color=INK,weight='normal',dy=40,anchor=None):
    kw=dict(x=x,y=y,font_size=size,fill=color,font_weight=weight,font_family='Arial')
    if anchor: kw['text_anchor']=anchor
    el=E(parent,'text',**kw); el.text=lines[0]
    for s in lines[1:]:
        sp=E(el,'tspan',x=x,dy=dy); sp.text=s
    return el

def G(parent,name):
    if name == 'header': bounds = '64 40 1152 100'
    elif name == 'footer': bounds = '1100 655 116 40'
    elif name == 'cover-content': bounds = '64 80 1152 575'
    else: bounds = '64 150 1152 500'
    return E(parent,'g',id=name,data_pptx_bounds=bounds)

def arrow(parent,x1,y,x2,color=BLUE,sw=4):
    L(parent,x1,y,x2-15,y,color,sw)
    E(parent,'polygon',points=f'{x2-15},{y-9} {x2},{y} {x2-15},{y+9}',fill=color)

def page(n,title,role='content'):
    root=ET.Element(f'{{{NS}}}svg',nsmap={None:NS},viewBox='0 0 1280 720',attrib={'font-family':'Arial','data-pptx-page-role':role})
    R(root,0,0,1280,720,WHITE)
    if role!='cover':
        hdr=G(root,'header')
        T(hdr,64,93,title,49,INK,'bold')
        L(hdr,64,127,1216,127,RULE,2)
        R(hdr,64,127,86,5,BLUE)
    foot=G(root,'footer')
    T(foot,1216,682,f'{n:02} / 15',19,GRAY,anchor='end')
    return root

def save(n,name,root):
    OUT.mkdir(exist_ok=True)
    (OUT/f'{n:02}_{name}.svg').write_bytes(ET.tostring(root,encoding='utf-8',xml_declaration=False))

# 01 — one visual hook.
p=page(1,'',role='cover'); a=G(p,'cover-content')
R(a,64,86,10,493,BLUE)
T(a,102,154,'CE436  /  PROJECT PROPOSAL',28,GRAY)
T(a,102,250,'TEMPERATURE',60,INK,'bold')
T(a,102,320,'FORECAST ON FPGA',60,INK,'bold')
T(a,102,415,'+3 h',112,DEEP,'bold')
T(a,385,412,'from past hourly values',35,GRAY)
L(a,112,520,1160,520,RULE,4)
for x in (145,422,720): C(a,x,520,8,GRAY)
C(a,1090,520,17,BLUE)
T(a,112,575,'past',29,GRAY);T(a,684,575,'now',29,GRAY);T(a,1012,575,'forecast',29,DEEP,'bold')
T(a,102,642,'3 students  •  12 weeks  •  C++ + Verilog/SystemVerilog',25,GRAY)
save(1,'cover',p)

# 02 — two-item input/output comparison.
p=page(2,'A testable forecasting task'); a=G(p,'input-output')
R(a,64,190,480,335,PALE); R(a,736,190,480,335,PALE)
T(a,94,245,'INPUT',28,DEEP,'bold');T(a,766,245,'OUTPUT',28,DEEP,'bold')
M(a,94,333,['Hourly temperature','at one location'],39,INK,dy=51)
M(a,766,333,['One temperature','3 hours ahead'],39,INK,dy=51)
arrow(a,569,355,710)
T(a,64,603,'Known through t',30,GRAY);T(a,736,603,'Forecast for t + 3 h',30,DEEP,'bold')
save(2,'scope',p)

# 03 — explicit offline/runtime split.
p=page(3,'C++ trains. FPGA forecasts.'); a=G(p,'two-stage-system')
T(a,64,194,'OFFLINE ON PC',28,DEEP,'bold')
for x,w,label in [(64,270,'Temperature CSV'),(405,300,'C++ fitting'),(810,340,'a, b, c')]:
    R(a,x,225,w,116,PALE);T(a,x+24,295,label,34,INK,'bold')
arrow(a,345,283,392);arrow(a,718,283,797)
L(a,64,385,1216,385,RULE,2)
T(a,64,438,'RUNTIME ON FPGA',28,DEEP,'bold')
for x,w,label in [(64,270,'New sample'),(405,300,'FPGA core'),(810,340,'T̂(t+3)')]:
    R(a,x,466,w,116,PALE);T(a,x+24,537,label,34,INK,'bold')
arrow(a,345,524,392);arrow(a,718,524,797)
T(a,64,640,'The coefficients stay fixed while the FPGA runs.',27,GRAY)
save(3,'system',p)

# 04 — time relationship.
p=page(4,'Four past values. One future target.'); a=G(p,'sample-timeline')
L(a,98,340,1182,340,GRAY,4)
for x,label in [(120,'t−24'),(350,'t−21'),(580,'t−3'),(810,'t'),(1090,'t+3')]:
    C(a,x,340,12,BLUE if x>=810 else GRAY)
    T(a,x,405,label,37,DEEP if x>=810 else INK,'bold',anchor='middle')
R(a,64,490,1152,102,PALE)
T(a,93,552,'t + 3 − 24 = t − 21',44,DEEP,'bold')
T(a,64,636,'25 consecutive samples are stored; the future target is never an input.',27,GRAY)
save(4,'samples',p)

# 05 — let the equation carry the page.
p=page(5,'A linear model from past values'); a=G(p,'model-equation')
R(a,64,177,1152,306,PALE)
T(a,96,260,'T̂(t+3) = T(t−21)',43,INK,'bold',family='Consolas')
T(a,96,346,'+ a[T(t)−T(t−24)]',43,DEEP,'bold',family='Consolas')
T(a,96,432,'+ b[T(t)−T(t−3)]',43,DEEP,'bold',family='Consolas')
T(a,760,432,'+ c',43,DEEP,'bold',family='Consolas')
for x,w,top,bottom in [(64,338,'ANCHOR','same hour yesterday'),(466,338,'DAY-TO-DAY','current vs. yesterday'),(868,348,'RECENT CHANGE','latest 3 hours')]:
    R(a,x,523,w,8,BLUE);T(a,x,570,top,26,DEEP,'bold');T(a,x,612,bottom,27,GRAY)
save(5,'model',p)

# 06 — compact arithmetic example.
p=page(6,'How is one forecast computed?'); a=G(p,'worked-example')
R(a,64,177,1152,74,PALE);T(a,91,224,'ILLUSTRATIVE VALUES — NOT A MEASURED RESULT',28,GRAY,'bold')
for x,val,label in [(64,'19°C','t−24'),(240,'21°C','t−21'),(416,'18°C','t−3'),(592,'20°C','t')]:
    T(a,x,318,val,42,INK,'bold'); T(a,x,374,label,27,GRAY)
T(a,64,439,'a = 0.5     b = 0.2',28,GRAY)
for x,value,label in [(64,'21.0','anchor'),(252,'+0.5','day shift'),(440,'+0.4','3 h trend')]:
    T(a,x,521,value,43,INK,'bold'); T(a,x,568,label,25,GRAY)
arrow(a,652,502,840)
T(a,865,529,'21.9°C',78,DEEP,'bold')
T(a,64,640,'subtract  →  multiply  →  add',35,GRAY)
save(6,'example',p)

# 07 — regression and chronological split.
p=page(7,'Train on the past. Test on the future.'); a=G(p,'regression')
R(a,64,176,1152,183,PALE)
T(a,91,235,'x1 = T(t) − T(t−24)',35,INK,family='Consolas')
T(a,91,299,'x2 = T(t) − T(t−3)',35,INK,family='Consolas')
T(a,668,260,'y = a·x1 + b·x2 + c',37,DEEP,'bold')
T(a,668,315,'fit a, b, c by least squares',27,GRAY)
for x,w,label,desc in [(64,338,'01 TRAIN','fit coefficients'),(466,338,'02 VALIDATE','select settings'),(868,348,'03 TEST','evaluate once')]:
    R(a,x,423,w,145,PALE);R(a,x,423,w,7,BLUE if x!=466 else GRAY)
    T(a,x+20,483,label,30,INK,'bold');T(a,x+20,533,desc,28,GRAY)
T(a,64,638,'Split chronologically; training labels must not cross into later periods.',27,GRAY)
save(7,'training',p)

# 08 — three methods, one test set.
p=page(8,'Does the model beat simple forecasts?'); a=G(p,'baseline-comparison')
for x,w,label,formula in [(64,338,'CURRENT VALUE','T(t)'),(466,338,'SAME HOUR YESTERDAY','T(t−21)'),(868,348,'LINEAR MODEL','T̂(t+3)')]:
    R(a,x,190,w,260,PALE);R(a,x,190,w,8,BLUE if x==868 else RULE)
    T(a,x+22,257,label,26,DEEP,'bold')
    T(a,x+22,369,formula,45,INK,'bold',family='Consolas')
R(a,64,505,1152,113,WHITE,stroke=RULE,sw=2)
T(a,91,579,'Compare MAE on the same held-out test timestamps.',35,DEEP,'bold')
save(8,'evaluation',p)

# 09 — three representations and specification decisions.
p=page(9,'Fixed-point needs an explicit contract'); a=G(p,'fixed-point-contract')
for x,w,label in [(64,300,'C++ FLOAT'),(488,300,'C++ FIXED'),(912,304,'RTL')]:
    R(a,x,192,w,145,PALE);T(a,x+25,275,label,32,INK,'bold')
arrow(a,376,264,473);arrow(a,800,264,897)
T(a,64,424,'Define the arithmetic before coding RTL:',34,DEEP,'bold')
for x,w,label in [(64,256,'signedness'),(355,256,'bit widths'),(646,256,'rounding'),(937,279,'overflow')]:
    R(a,x,465,w,94,PALE);T(a,x+20,523,label,30,INK,'bold')
T(a,64,637,'Forecast error and quantization error are different measurements.',28,GRAY)
save(9,'fixed_point',p)

# 10 — legible functional block diagram.
p=page(10,'From sample history to arithmetic'); a=G(p,'rtl-datapath')
R(a,64,187,260,343,PALE);T(a,86,244,'25-SAMPLE',31,DEEP,'bold');T(a,86,284,'BUFFER',31,DEEP,'bold')
for x,y,label in [(86,355,'t−24'),(207,355,'t−21'),(86,410,'t−3'),(207,410,'t')]:
    T(a,x,y,label,26,INK,family='Consolas')
R(a,414,199,347,132,PALE);T(a,437,255,'day-to-day Δ',31,INK,'bold');T(a,437,303,'× a',35,DEEP,'bold')
R(a,414,390,347,132,PALE);T(a,437,446,'recent 3 h Δ',31,INK,'bold');T(a,437,494,'× b',35,DEEP,'bold')
arrow(a,340,355,399);L(a,776,265,860,345,BLUE,3);L(a,776,455,860,355,BLUE,3)
C(a,887,351,52,WHITE,BLUE,4);T(a,887,369,'+',46,DEEP,'bold',anchor='middle')
arrow(a,944,351,1011)
T(a,1024,369,'T̂(t+3)',44,DEEP,'bold',family='Consolas')
T(a,64,619,'Accept a sample on valid; output only after the buffer is ready.',28,GRAY)
save(10,'architecture',p)

# 11 — verification ladder.
p=page(11,'Three verification layers'); a=G(p,'verification-layers')
for x,w,num,title,desc,check in [
    (64,338,'01','C++','float vs. fixed','quantization'),
    (466,338,'02','TESTBENCH','RTL vs. reference','bit-exact output'),
    (868,348,'03','BOARD','integrated run','I/O and sample order')]:
    R(a,x,188,w,383,PALE);T(a,x+22,259,num,53,BLUE,'bold')
    T(a,x+22,325,title,30,INK,'bold');T(a,x+22,386,desc,30,INK)
    L(a,x+22,427,x+w-22,427,RULE,2);T(a,x+22,490,check,27,GRAY)
T(a,64,636,'All layers use the same input vectors and arithmetic specification.',28,GRAY)
save(11,'verification',p)

# 12 — demo loop.
p=page(12,'Replay historical data for the demo'); a=G(p,'demo-flow')
for x,w,title,desc in [(64,300,'PC / CSV','send past samples'),(488,300,'FPGA','compute forecast'),(912,304,'PC / CHECK','compare with truth')]:
    R(a,x,211,w,241,PALE);T(a,x+20,289,title,32,INK,'bold');T(a,x+20,362,desc,29,GRAY)
arrow(a,376,330,473);arrow(a,800,330,897)
R(a,64,520,1152,96,WHITE,stroke=BLUE,sw=3)
T(a,92,581,'Only samples through t enter the FPGA.',37,DEEP,'bold')
save(12,'demo',p)

# 13 — schedule with an early prototype milestone.
p=page(13,'12 weeks. Prototype early. Evaluate deeply.'); a=G(p,'milestones')
for x,w,week,title,lines in [
    (64,256,'W1–3','PROTOTYPE',['data + C++','working RTL core']),
    (355,256,'W4–6','VALIDATE',['model vs. baselines','fixed-point sweep']),
    (646,256,'W7–9','HARDEN',['bit-exact tests','resource trade-offs']),
    (937,279,'W10–12','DEMO',['board integration','final test + report'])]:
    R(a,x,200,w,337,PALE);R(a,x,200,w,9,BLUE)
    T(a,x+18,269,week,31,DEEP,'bold');T(a,x+18,340,title,28,INK,'bold')
    M(a,x+18,414,lines,26,GRAY,dy=46)
T(a,64,627,'Each phase ends with a measurable deliverable.',30,DEEP,'bold')
save(13,'schedule',p)

# 14 — ownership and one risk per person.
p=page(14,'Three students. Clear ownership.'); a=G(p,'team-roles')
for x,w,name,role,out,risk in [
    (64,338,'STUDENT 1','DATA + C++','dataset + MAE, coefficients','missing hours'),
    (466,338,'STUDENT 2','FIXED + RTL','RTL core, synthesis','board TBD'),
    (868,348,'STUDENT 3','VERIFY + DEMO','test vectors, interface + logs','high error')]:
    R(a,x,191,w,381,PALE);T(a,x+20,250,name,28,DEEP,'bold');T(a,x+20,317,role,30,INK,'bold')
    M(a,x+20,380,out.split(', '),27,GRAY,dy=42)
    L(a,x+20,472,x+w-20,472,RULE,2);T(a,x+20,526,risk,27,GRAY)
T(a,64,635,'One shared contract: data, coefficients, rounding, valid, and latency.',27,DEEP,'bold')
save(14,'team_risks',p)

# 15 — conclusion and explicit asks.
p=page(15,'One forecast. Two things to prove.',role='ending'); a=G(p,'closing-proof')
R(a,64,179,548,255,PALE);R(a,668,179,548,255,PALE)
T(a,94,251,'01  FORECAST',32,DEEP,'bold');T(a,94,303,'QUALITY',32,DEEP,'bold')
M(a,94,370,['Beat the baselines','on unseen data'],31,INK,dy=43)
T(a,698,251,'02  HARDWARE',32,DEEP,'bold');T(a,698,303,'CORRECTNESS',32,DEEP,'bold')
M(a,698,370,['Match the C++ fixed-','point reference'],31,INK,dy=43)
R(a,64,496,1152,119,WHITE,stroke=BLUE,sw=3)
T(a,92,549,'Feedback needed:',29,DEEP,'bold')
T(a,92,591,'scope  •  FPGA board/tools  •  minimum demo',31,INK)
save(15,'conclusion',p)

print(f'Wrote {len(list(OUT.glob("*.svg")))} redesigned SVG slides')
