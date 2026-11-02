"""Create separate SignalTap builds without changing measurement projects."""
from pathlib import Path
import sys,subprocess,os,re,xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[1]
template=R/'hardware/jtag/signaltap_template.stp'
assert template.exists(), 'Generate the Quartus 13 SignalTap template first'
projects=[('temperature_speed','hardware/quartus/de2_temperature_jtag','temperature'),('temperature_resource','hardware/quartus/de2_temperature_resource_jtag','temperature_resource'),('weather_speed','versions/weather_v2/quartus/de2_jtag_speed','weather_jtag'),('weather_resource','versions/weather_v2/quartus/de2_jtag_resource','weather_jtag')]
for variant,folder,name in projects:
 if len(sys.argv)>1 and variant not in sys.argv[1:]:continue
 src=R/folder; dst=R/'hardware/quartus/signaltap'/variant;dst.mkdir(parents=True,exist_ok=True)
 qsf=(src/f'{name}.qsf').read_text()
 # Relocate all file references and retain original optimization and device settings.
 for kind in ['VERILOG_FILE','SYSTEMVERILOG_FILE','SDC_FILE']:
  qsf=re.sub(r'(-name '+kind+r' )([^\n]+)',lambda m:m[1]+os.path.relpath((src/m[2].strip()).resolve(),dst),qsf)
 top=re.search(r'-name VERILOG_FILE (.*de2_(?:temperature_resource|temperature|weather)_jtag.v)',qsf)
 text=(dst/top[1]).resolve().read_text()
 (dst/'debug_top.v').write_text(re.sub(r'\bwire\b','(* keep = "true" *) wire',text))
 qsf=qsf[:top.start(1)]+'debug_top.v'+qsf[top.end(1):]
 qsf='\n'.join(l for l in qsf.splitlines() if not any(k in l for k in ['SIGNALTAP_FILE','ENABLE_SIGNALTAP','USE_SIGNALTAP_FILE']))+'\n'
 qsf+='set_global_assignment -name ENABLE_SIGNALTAP ON\nset_global_assignment -name USE_SIGNALTAP_FILE capture.stp\nset_global_assignment -name SIGNALTAP_FILE capture.stp\n'
 (dst/'capture.qsf').write_text(qsf);(dst/'capture.qpf').write_text('QUARTUS_VERSION = "13.0"\nPROJECT_REVISION = "capture"\n')
 for coeff in ['coeffs.txt','coefficients.txt']:
  if (src/coeff).exists():(dst/coeff).write_bytes((src/coeff).read_bytes())
 root=ET.fromstring(template.read_text());root.set('sof_file','output_files/capture.sof')
 root.find('display_tree').clear();ET.SubElement(root.find('display_tree'),'display_branch',instance='auto_signaltap_0',signal_set='signal_set_1',trigger='trigger_1')
 inst=root.find('instance');ss=inst.find('signal_set');ss.attrib={'name':'signal_set_1'}
 ss.find('clock').attrib={'name':'CLOCK_50','polarity':'posedge','tap_mode':'classic'}
 ss.find('config').set('sample_depth','512')
 nodes=['core_rst_n','sample_valid','sample_ready','forecast_valid']
 weather=variant.startswith('weather')
 widths=[('sample_data',108 if weather else 16)]
 widths += [(n,18) for n in ['t','p','h','w','c','s','angle']] if weather else [('forecast_out',16)]
 for n,width in widths:nodes += [f'{n}[{i}]' for i in range(width)]
 def probe_name(n):
  if n.startswith('forecast_out['):n=n.replace('forecast_out','forecast_data')
  for field,offset in [('t',0),('p',18),('h',36),('w',54),('c',72),('s',90),('angle',108)]:
   if n.startswith(field+'['):n='forecast_data['+str(offset+int(n.split('[')[1][:-1]))+']';break
  return 'jtag_mailbox:mailbox|'+n
 sv=ss.find('signal_vec');sv.clear()
 for vec in ['trigger_input_vec','data_input_vec','storage_qualifier_input_vec']:
  el=ET.SubElement(sv,vec)
  for n in (['forecast_valid'] if vec!='data_input_vec' else nodes):ET.SubElement(el,'wire',name=probe_name(n),tap_mode='classic')
 pres=ss.find('presentation');pres.clear()
 for view in ['unified_setup_data_view','data_view','setup_view']:
  el=ET.SubElement(pres,view)
  for i,n in enumerate(nodes):
   attrs=dict(name=probe_name(n),tap_mode='classic',type='combinational',is_data_input='true',is_node_valid='true',is_trigger_input=str(n=='forecast_valid').lower(),is_storage_input=str(n=='forecast_valid').lower(),data_index=str(i))
   if n=='forecast_valid':attrs.update(trigger_index='0',storage_index='0')
   ET.SubElement(el,'node' if view=='unified_setup_data_view' else 'net',attrs)
 for view in ['trigger_in_editor','trigger_out_editor']:ET.SubElement(pres,view)
 tr=ss.find('trigger');tr.attrib.pop('global_temp',None);tr.set('name','trigger_1');tr.set('position','center')
 tr.find('events/level').text="'jtag_mailbox:mailbox|forecast_valid' == rising edge\n"
 ET.indent(root);(dst/'capture.stp').write_text(ET.tostring(root,encoding='unicode'))
 subprocess.run(['quartus_stp','capture','--stp_file=capture.stp','--enable'],cwd=dst,check=True,stdout=subprocess.DEVNULL)
 print(variant,dst)
