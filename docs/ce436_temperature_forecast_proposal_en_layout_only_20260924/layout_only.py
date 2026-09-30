from pathlib import Path
from lxml import etree

root = Path(__file__).parent / 'svg_output'
NS='{http://www.w3.org/2000/svg}'
for path in sorted(root.glob('*.svg')):
    tree=etree.parse(str(path))
    svg=tree.getroot()
    svg.set('font-size','30')
    for group in svg.xpath('.//s:g',namespaces={'s':'http://www.w3.org/2000/svg'}):
        gid=group.get('id','')
        if gid in {'page-number','source-link','baseline-source','training-source'}:
            continue
        for node in group.iter():
            if node.tag not in {NS+'text', NS+'tspan'}:
                continue
            old=node.get('font-size')
            if old is None: continue
            try: n=float(old)
            except ValueError: continue
            if n<=16: new=n
            elif n<=20: new=n+3
            elif n<=22: new=n+3
            elif n<=24: new=n+3
            elif n<=26: new=n+2
            elif n<=30: new=n+2
            else: new=n
            if new!=n:node.set('font-size',str(int(new) if new.is_integer() else new))
    # Keep long, low-priority explanatory lines within their current zones.
    if path.name in {'02_scope.svg','04_samples.svg','07_training.svg','09_fixed_point.svg','10_architecture.svg','12_demo.svg'}:
        for gid in {'scope-caveat','causality','split-contract','fixed-boundaries','control-contract','future-boundary'}:
            matches=svg.xpath(f'.//s:g[@id="{gid}"]',namespaces={'s':'http://www.w3.org/2000/svg'})
            if matches:
                for t in matches[0].iter(NS+'text'):
                    size=t.get('font-size')
                    if size and float(size)>24:t.set('font-size','24')
    tree.write(str(path),encoding='utf-8',xml_declaration=False)
print('Adjusted typography on 15 pages; no text nodes edited.')
