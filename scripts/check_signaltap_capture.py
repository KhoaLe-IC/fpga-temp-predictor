"""Decode native SignalTap hardware data and check observed transaction evidence."""
from pathlib import Path
import csv,json,hashlib,xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[1];D=R/'docs/reports/defense_session';out=[]
for v in ['temperature_speed','temperature_resource','weather_speed','weather_resource']:
 p=D/'signaltap'/f'{v}.stp';root=ET.parse(p).getroot();ss=root.find('instance/signal_set');data=ss.find('trigger/log/data');assert data is not None
 n=int(data.get('sample_depth'));trigger=int(data.get('trigger_position'));names=[w.get('name') for w in ss.find('signal_vec/data_input_vec')];text=''.join(data.text.split())
 assert n==512 and 0<=trigger<n and len(text)==n*len(names) and set(text)<={'0','1'}
 rows=[list(map(int,text[i*len(names):(i+1)*len(names)])) for i in range(n)];prefix='jtag_mailbox:mailbox|'
 def bit(i,name):return rows[i][names.index(prefix+name)]
 def bus(i,name,width):return sum(bit(i,f'{name}[{b}]')<<b for b in range(width))
 valids=[i for i in range(n) if bit(i,'forecast_valid')];accepts=[i for i in range(n) if bit(i,'sample_valid') and bit(i,'sample_ready')]
 assert len(valids)==1 and len(accepts)==1 and all(bit(i,'core_rst_n') for i in range(n))
 a,f=accepts[0],valids[0];weather=v.startswith('weather');width=108 if weather else 16;result_width=126 if weather else 16
 vectors=(R/'hardware/jtag/vectors'/('weather.txt' if weather else 'temperature.txt')).read_text().splitlines();fields=vectors[24].split();expected_input=(int(fields[1],16)>>2)&((1<<width)-1);expected=int(fields[4],16)
 actual_input=bus(a,'sample_data',width);actual=bus(f,'forecast_data',result_width)
 assert actual_input==expected_input,(v,'input',actual_input,expected_input)
 if weather:
  assert actual&((1<<108)-1)==expected&((1<<108)-1),(v,'component mismatch')
  delta=abs((actual>>108)-(expected>>108));delta=min(delta,92160-delta);assert delta<=5
 else:assert actual==expected,(v,'forecast mismatch',actual,expected)
 # SignalTap samples the pre-edge value of registered results. Relative to the
 # post-edge observation used by RTL scoreboards, valid is visible one sample later.
 latency={'temperature_speed':5,'temperature_resource':9,'weather_speed':40,'weather_resource':156}[v]
 assert f-a==latency+1,(v,'latency',f-a,latency)
 decoded=D/'signaltap'/f'{v}_decoded.csv'
 with decoded.open('w') as fd:
  w=csv.writer(fd);w.writerow(['capture_index','relative_to_trigger','time_ns','core_rst_n','sample_valid','sample_ready','forecast_valid','sample_data_hex','forecast_data_hex'])
  for i in range(n):w.writerow([i,i-trigger,(i-trigger)*20,*[bit(i,k) for k in ['core_rst_n','sample_valid','sample_ready','forecast_valid']],hex(bus(i,'sample_data',width)),hex(bus(i,'forecast_data',result_width))])
 item=dict(variant=v,status='PASS',capture=str(p.relative_to(R)),capture_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),samples=n,clock_period_ns=20,trigger_index=trigger,accepted_index=a,forecast_valid_index=f,observed_pre_edge_sample_separation=f-a,post_edge_core_latency_cycles=latency,input_hex=hex(actual_input),forecast_hex=hex(actual),reference_forecast_hex=hex(expected),decoded_csv=str(decoded.relative_to(R)),decoded_sha256=hashlib.sha256(decoded.read_bytes()).hexdigest())
 out.append(item);print(v,'PASS',a,f,'expected first forecast',hex(actual))
(D/'SIGNALTAP_CAPTURE_CHECK.json').write_text(json.dumps({'status':'PASS','captures':out},indent=2))
