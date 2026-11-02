"""Program, acquire and validate actual SignalTap capture plus mailbox replay."""
from pathlib import Path
import subprocess,time,os,sys,xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[1];D=R/'docs/reports/defense_session'
for v in sys.argv[1:]:
 assert v in ['temperature_speed','temperature_resource','weather_speed','weather_resource']
 p=R/'hardware/quartus/signaltap'/v
 report=(p/'output_files/capture.map.rpt').read_text()
 assert 'Succesfully connected in-system debug instance' in report and 'Critical Warning (35025)' not in report, 'Missing SignalTap connections'
 with (D/f'{v}_signaltap_programming.txt').open('w') as f:subprocess.run(['quartus_pgm','-m','jtag','-c','1','-o','p;'+str(p/'output_files/capture.sof')],stdout=f,stderr=subprocess.STDOUT,check=True)
 with (D/f'{v}_signaltap_capture.txt').open('w') as f:
  capture=subprocess.Popen(['quartus_stp','-t',str(R/'scripts/capture_signaltap.tcl'),v],stdout=f,stderr=subprocess.STDOUT,cwd=R)
  time.sleep(2)
  with (D/f'{v}_signaltap_replay.txt').open('w') as g:
   env=dict(os.environ,FPGA_JTAG_CSV=str(D/f'{v}_signaltap_replay.csv'))
   replay=subprocess.run(['quartus_stp','-t',str(R/'scripts/replay_jtag.tcl'),v],stdout=g,stderr=subprocess.STDOUT,cwd=R,env=env)
  code=capture.wait(timeout=40)
 assert replay.returncode==0 and code==0
 stp=D/'signaltap'/f'{v}.stp';root=ET.parse(stp).getroot();data=root.find('.//log/data')
 assert data is not None and int(data.get('trigger_position','-1'))>=0, 'No hardware trigger was captured'
 assert set(data.text.strip()) != {'0'}, 'All-zero capture is not evidence'
 subprocess.run([sys.executable,str(R/'scripts/format_signaltap.py'),str(stp)],check=True)
 print('PASS actual SignalTap trigger and checked replay:',v,flush=True)
