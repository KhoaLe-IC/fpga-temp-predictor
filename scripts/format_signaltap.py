"""Group saved physical SignalTap bits for readable native Quartus waveforms.
Only presentation is changed; data bits and acquisition configuration are preserved.
"""
from pathlib import Path
import xml.etree.ElementTree as ET
import sys
for arg in sys.argv[1:]:
 p=Path(arg);root=ET.parse(p).getroot();ss=root.find('instance/signal_set')
 for view in ['unified_setup_data_view','data_view','setup_view']:
  v=ss.find('presentation/'+view);tag='node' if view=='unified_setup_data_view' else 'net';nets=[n for n in v.iter(tag) if n.get('tap_mode')];v.clear()
  controls=[n for n in nets if '[' not in n.get('name','')]
  for n in controls:v.append(n)
  weather='weather' in p.name
  groups=[('sample_data',0,108 if weather else 16,'input_frame_q8'),('forecast_data',0,126 if weather else 16,'forecast_frame_q8')]
  if weather:groups=[('sample_data',i*18,18,k+'_in_q8') for i,k in enumerate(['temperature','pressure','humidity','wind_speed','direction_cos','direction_sin'])]+[('forecast_data',i*18,18,k+'_out_q8') for i,k in enumerate(['temperature','pressure','humidity','wind_speed','direction_cos','direction_sin','direction_angle'])]
  for stem,start,width,name in groups:
   bus=ET.SubElement(v,'node' if view=='unified_setup_data_view' else 'bus',name=name,order='msb_to_lsb',state='collapse',type='combinatorial')
   for b in reversed(range(start,start+width)):
    n=next(n for n in nets if n.get('name')==f'jtag_mailbox:mailbox|{stem}[{b}]');bus.append(n)
 root.find('.//log/data').set('name',p.stem+'_PHYSICAL')
 ET.indent(root);p.write_text(ET.tostring(root,encoding='unicode'))
 print(p)
