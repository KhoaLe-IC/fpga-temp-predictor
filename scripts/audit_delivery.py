"""Evidence-based completion audit. Pending physical/SDF checks are never inferred from synthesis."""
from pathlib import Path
import csv,hashlib,json,re,math
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1];checks=[]
def record(name,status,evidence):checks.append(dict(requirement=name,status=status,evidence=evidence))
def logcheck(name,path,marker):
 p=R/path
 record(name,'PASS' if p.exists() and marker in p.read_text() else 'PENDING',path)
model=json.loads((R/'software/models_cpp/model.json').read_text());coeff=[int(math.copysign(math.floor(abs(model[k])*scale+.5),model[k])) for k,scale in [('a',16384),('b',16384),('c',256)]]
for path in ['hardware/speed_optimized/coeffs.txt','hardware/resource_optimized/coefficients.txt','hardware/quartus/de2_temperature/coeffs.txt']:
 actual=[int(x,16) for x in (R/path).read_text().split()];expected=[x&65535 for x in coeff];record('Temperature coefficients: '+path,'PASS' if actual==expected else 'FAIL',path)
for title,path,project in [('temperature speed','hardware/quartus/speed','predictor'),('temperature shared','hardware/quartus/resource','predictor'),('temperature board','hardware/quartus/de2_temperature','temperature'),('weather parallel','versions/weather_v2/quartus/speed','weather'),('weather shared','versions/weather_v2/quartus/resource','weather'),('weather parallel board','versions/weather_v2/quartus/de2_speed','weather_board'),('weather shared board','versions/weather_v2/quartus/de2_resource','weather_board')]:
 p=R/path;fit=p/f'output_files/{project}.fit.summary';sta=p/f'output_files/{project}.sta.rpt'
 if not fit.exists() or not sta.exists():record(title+' fit/timing','PENDING',path);continue
 s=sta.read_text();slack=re.search(r'Worst-case Slack ; ([\d.\-]+) ; ([\d.\-]+)',s)
 unconstrained=re.findall(r'Unconstrained (?:Input|Output) Port Paths\s*; (\d+)',s)
 clean=len(unconstrained)==2 and all(int(v)==0 for v in unconstrained)
 passed='Successful' in fit.read_text() and 'EP2C35F672C6' in fit.read_text() and slack and min(map(float,slack.groups()))>=0 and clean and '50.0 MHz' in s
 record(title+' fit/timing at 50 MHz','PASS' if passed else 'FAIL',str(sta.relative_to(R)))
logcheck('Temperature DPI-C coefficient matrix','hardware/tb/regression_current.log','All requested DUT simulations passed.')
logcheck('Temperature full-year historical DPI-C replay','docs/reports/temperature_historical_dpi.txt','EQUIVALENCE PASS: 8757 forecasts matched by accepted-sample index')
for v in ['speed','resource']:
 logcheck('Temperature '+v+' strict-reader final netlist','docs/reports/temperature_'+v+'_functional_final.txt','PASS netlist at 50 MHz: inputs=4096 forecasts=4072')
 logcheck('Temperature '+v+' functional netlist','hardware/quartus/'+v+'/netlist_sim.log','PASS netlist at 50 MHz: inputs=4096 forecasts=4072')
 logcheck('Weather '+v+' DPI-C','versions/weather_v2/reports/'+v+'_dpi.log','PASS weather DPI-C: accepted=1200 checked=1124')
 logcheck('Weather '+v+' UART','versions/weather_v2/reports/'+v+'_uart.log','PASS weather UART 50 MHz / 115200 baud')
 logcheck('Weather '+v+' final functional netlist','versions/weather_v2/reports/'+v+'_final_netlist.log','PASS weather netlist 50 MHz: inputs=288 forecasts=264')
 path=R/f'versions/weather_v2/reports/{v}_final_netlist_manifest.json'
 if path.exists():
  m=json.loads(path.read_text());w=R/'versions/weather_v2';same=hashlib.sha256((w/m['source_netlist']).read_bytes()).hexdigest()==m['netlist_sha256'] and hashlib.sha256((w/'build/vectors/vectors.txt').read_bytes()).hexdigest()==m['vectors_sha256'];record(v+' netlist snapshot identity','PASS' if same else 'FAIL',str(path.relative_to(R)))
 else:record(v+' netlist snapshot identity','PENDING',str(path.relative_to(R)))
logcheck('Temperature full UART','hardware/quartus/de2_temperature/uart_sim.log','PASS UART at 50 MHz / 115200 baud')
logcheck('Wind direction exhaustive conversion','versions/weather_v2/reports/direction_exhaustive.log','PASS exhaustive direction: vectors=263169')
logcheck('Temperature saved-model training audit','docs/reports/temperature_evaluation.log','Saved coefficient / training-data audit PASS')
logcheck('Weather C++ / NumPy reference cross-check','versions/weather_v2/reports/reference_crosscheck.log','C++/NumPy cross-check PASS: 264 forecasts')
for target in ['temperature_speed','temperature_resource','weather_speed','weather_resource']:
 p=R/'docs/reports'/f'{target}_modelsim_timing.json';status='PENDING'
 if p.exists():
  m=json.loads(p.read_text());same=m.get('status')=='PASS' and m.get('clock_period_ns')==20
  for field in ['netlist','sdf','vectors','testbench','transcript']:
   f=R/m.get(field,'missing');same=same and f.is_file() and hashlib.sha256(f.read_bytes()).hexdigest()==m.get(field+'_sha256')
  t=R/m.get('transcript','missing');text=t.read_text() if t.is_file() else ''
  same=same and 'SDF Backannotation Successfully Completed' in text and ('PASS weather netlist 50 MHz: inputs=288 forecasts=264' if target.startswith('weather') else 'PASS netlist at 50 MHz: inputs=4096 forecasts=4072') in text and not re.search(r'(?i)(timing violation|\*\* fatal|\*\* error)',text)
  status='PASS' if same else 'FAIL'
 record(target+' accepted SDF timing simulation',status,str(p.relative_to(R)))
for name,path in [('temperature','docs/reports/board_temperature.csv'),('weather parallel','versions/weather_v2/reports/physical_parallel.csv'),('weather shared','versions/weather_v2/reports/physical_shared.csv')]:
 p=R/path;status='PENDING'
 if p.exists():
  rows=list(csv.DictReader(p.open()));scored=[r for r in rows if r.get('match') not in ['warmup','']];status='PASS' if len(scored)>=104 and all(r['match']=='True' for r in scored) else 'FAIL'
 record(name+' physical board replay',status,path+'; user confirmed board unavailable on this computer')
for path in ['docs/reports/IMPLEMENTATION_REPORT.md','docs/reports/HARDWARE_HANDOFF.md','versions/weather_v2/models/model.json','versions/weather_v2/reports/metrics.csv','versions/weather_v2/reports/validation_candidates.csv']:
 record('Deliverable '+path,'PASS' if (R/path).is_file() else 'PENDING',path)
result={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'status':'COMPLETE' if all(c['status']=='PASS' for c in checks) else 'INCOMPLETE','checks':checks}
(R/'docs/reports/COMPLETION_AUDIT.json').write_text(json.dumps(result,indent=2));print(result['status'])
for c in checks:
 if c['status']!='PASS':print(c['status'],c['requirement'])
