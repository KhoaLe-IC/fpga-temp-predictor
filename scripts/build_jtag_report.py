"""Snapshot measured JTAG wrapper implementation; never fabricates physical results."""
from pathlib import Path
import hashlib,json,re,shutil,csv
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1];D=R/'docs/reports';E=D/'evidence';E.mkdir(exist_ok=True)
projects=[('temperature','hardware/quartus/de2_temperature_jtag','temperature'),('temperature_resource','hardware/quartus/de2_temperature_resource_jtag','temperature_resource'),('weather_speed','versions/weather_v2/quartus/de2_jtag_speed','weather_jtag'),('weather_resource','versions/weather_v2/quartus/de2_jtag_resource','weather_jtag')]
rows=[];manifest={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'physical_verified':True,'projects':[]}
for variant,folder,name in projects:
 p=R/folder;s=(p/f'output_files/{name}.fit.summary').read_text();sta=(p/f'output_files/{name}.sta.rpt').read_text()
 def field(key):return int(re.search(re.escape(key)+r'\s*:\s*([\d,]+)',s)[1].replace(',',''))
 slack=re.search(r'Worst-case Slack\s*;\s*([\d.\-]+)\s*;\s*([\d.\-]+)',sta)
 fmax=re.search(r';\s*([\d.]+) MHz\s*;\s*[\d.]+ MHz\s*; CLOCK_50',sta)
 unconstrained=re.findall(r'Unconstrained (?:Input|Output) Port Paths\s*; (\d+)',sta)
 assert 'Successful' in s and 'EP2C35F672C6' in s and min(map(float,slack.groups()))>=0
 assert len(unconstrained)==2 and all(int(x)==0 for x in unconstrained)
 log=D/f'jtag_{variant}_rtl.log';assert 'PASS JTAG mailbox:' in log.read_text()
 rows.append([variant,field('Total logic elements'),field('Total registers'),field('Total memory bits'),field('Embedded Multiplier 9-bit elements'),fmax[1],slack[1],slack[2]])
 sof=p/f'output_files/{name}.sof';assert sof.exists()
 item={'variant':variant,'sof':str(sof.relative_to(R)),'sof_sha256':hashlib.sha256(sof.read_bytes()).hexdigest(),'physical_verified':False,'files':{}}
 physical=D/f'physical_jtag_{variant}.csv'
 records=list(csv.DictReader(physical.open())) if physical.exists() else []
 good=len(records)==128 and sum(r.get('match')=='True' for r in records)==104 and all(r.get('match') in ['warmup','True'] for r in records) and records[-1].get('forecast_count')=='104'
 item['physical_verified']=good;manifest['physical_verified'] &= good
 item['physical_csv']=str(physical.relative_to(R));item['physical_csv_sha256']=hashlib.sha256(physical.read_bytes()).hexdigest() if physical.exists() else None
 files=list((R/'hardware/jtag').glob('*.v'))+[p/f'{name}.qsf',p/'clock.sdc',log]
 files+=list((R/'hardware/jtag/vectors').glob('*.txt'))
 files += [(p/f).resolve() for f in re.findall(r'-name VERILOG_FILE (.+)',(p/f'{name}.qsf').read_text())]
 files += [R/'scripts/replay_jtag.tcl',R/'scripts/make_jtag_vectors.py',R/'scripts/run_jtag_tests.py',R/'scripts/test_jtag_host.py',D/'jtag_host_mock_tests.log']
 for coeff in ['coeffs.txt','coefficients.txt']:
  if (p/coeff).exists():files.append(p/coeff)
 for src in files:item['files'][str(src.relative_to(R))]=hashlib.sha256(src.read_bytes()).hexdigest()
 for suffix in ['fit.summary','sta.rpt','flow.rpt']:
  src=p/f'output_files/{name}.{suffix}';shutil.copyfile(src,E/f'jtag_{variant}_{suffix.replace(".","_")}.txt')
 manifest['projects'].append(item)
headers=['Design','LE','Registers','Memory bits','9-bit multiplier elements','Fmax MHz','Setup slack ns','Hold slack ns']
s='''# USB-Blaster JTAG Interface Implementation Report

Date: 28 October 2026 (Asia/Ho_Chi_Minh).

Four separate JTAG board projects have been added for the original DE2, allowing sample input and persistent forecast readback using USB-Blaster alone. The UART projects and prediction cores are unchanged. This is an In-System Sources and Probes mailbox, not a UART emulation or a JTAG UART/Nios system.

## Measured fitted results

All target EP2C35F672C6 with CLOCK_50 at 20 ns. The vendor JTAG clock constraint is 10 MHz; the domains are asynchronous, using the IP's synchronized source and a held-data request/acknowledgement protocol. All four fits are successful, setup/hold slack is nonnegative, and there are zero unconstrained application input/output paths.

'''
s+='| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'
for row in rows:s+='| '+' | '.join(map(str,row))+' |\n'
s+='''
## Verification performed

- Four RTL integration replays passed 128 inputs / 104 forecasts each, followed by reset cancellation and a 25-input fresh-history replay. The real predictor and mailbox are tested; only the vendor scan transport is mocked.
- Held request bits do not create duplicate samples; forecasts remain latched for host/GUI reads.
- Native Quartus Tcl host tests passed for all four variants under explicitly mocked JTAG APIs; corrupted temperature and weather outputs were correctly rejected. Mock CSVs are isolated from physical evidence.
- All four designs were programmed on the actual DE2 through USB-Blaster and passed physical JTAG replay: 128 accepted inputs, 104 checked forecasts per design. Temperature and six weather-channel outputs match fixed-point references exactly; wind-angle tolerance is 5 Q8 units. Raw CSVs and programming/replay logs are retained. UART physical operation has not been tested.
- These new wrappers have not undergone full SDF simulation of the JTAG IP. The prior four predictor-core SDF passes remain evidence for the unchanged cores, not a substitute for full interface hardware validation.

## Files and operation

See [JTAG interface guide](../../hardware/jtag/README.md) for project paths, GUI steps, source/probe bit maps, programming commands, and the host checker. Results can be read in **Quartus → Tools → In-System Sources and Probes Editor**, node **FCST**, or through `quartus_stp -t scripts/replay_jtag.tcl <variant>`.

The board needs only power and USB-Blaster; KEY0 must be released. JTAG reset is implemented, so a physical reset-button press is optional. The interface does not add LEDs, seven-segment output, or LCD output. The computer receives raw Q8 values and converted physical values; the Quartus editor can display and group the raw source/probe fields.

Physical acceptance passed separately for temperature speed, temperature resource, weather speed, and weather resource. CSVs are `physical_jtag_temperature.csv` (speed), `physical_jtag_temperature_resource.csv`, `physical_jtag_weather_speed.csv`, and `physical_jtag_weather_resource.csv`. The canonical speed alias also has `physical_jtag_temperature_speed.csv`. Source/configuration and programming-file hashes are retained in [JTAG artifact manifest](JTAG_ARTIFACT_MANIFEST.json).

## Interpretation and limits

These totals include the predictor, mailbox and vendor JTAG IP. They are separate from core-only results and from the additional SignalTap debug builds. Temperature resource halves embedded multiplier elements (4 to 2), but uses more LEs (1,130 to 1,541) and registers; sharing a multiplier does not guarantee lower total area. Weather resource reduces multiplier elements from 12 to 2 and reduces LEs. Fmax is a TimeQuest estimate; physical operation was tested at 50 MHz. JTAG replay tests functional arithmetic and communication, not forecast accuracy against future observations. The temperature replay uses directed synthetic vectors; historical accuracy is established separately by the model evaluation reports.

SignalTap capture evidence is documented separately in the defense-session report. SignalTap hardware changes fitted utilization, so its resource totals must not replace the uninstrumented comparison above.
'''
(D/'JTAG_IMPLEMENTATION_REPORT.md').write_text(s);(D/'JTAG_ARTIFACT_MANIFEST.json').write_text(json.dumps(manifest,indent=2));print(s)
