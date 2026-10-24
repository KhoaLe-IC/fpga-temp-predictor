"""Replay consecutive hourly samples over the DE2 DB9 RS-232 UART and check every reply.
Hold/release KEY0 after programming and before this command; USB-Blaster is not a UART.
"""
from pathlib import Path
import argparse,csv,json,math
R=Path(__file__).resolve().parents[1]
def q(v,s):return int(math.copysign(math.floor(abs(v)*s+.5),v))
def main():
 p=argparse.ArgumentParser();p.add_argument('--port',required=True);p.add_argument('--samples',type=int,default=128);p.add_argument('--output',type=Path,default=R/'docs/reports/board_temperature.csv');args=p.parse_args()
 if args.samples<25:raise ValueError('At least 25 samples required')
 import serial
 m=json.loads((R/'software/models_cpp/model.json').read_text());a,b,c=q(m['a'],16384),q(m['b'],16384),q(m['c'],256)
 from datetime import datetime,timedelta
 rows=list(csv.DictReader((R/'data/processed/temperature.csv').open()))[:args.samples]
 if len(rows)!=args.samples:raise ValueError('Insufficient input data')
 hist=[];prev=None;checked=0;args.output.parent.mkdir(parents=True,exist_ok=True)
 with serial.Serial(args.port,115200,timeout=5) as uart,args.output.open('w',newline='') as log:
  uart.reset_input_buffer();writer=csv.writer(log);writer.writerow(['timestamp','input_q8','expected_q8','received_q8','match'])
  for row in rows:
   stamp=datetime.fromisoformat(row['timestamp']);temp=q(float(row['temperature']),256)
   if prev is not None and stamp-prev!=timedelta(hours=1):raise ValueError('Input gap requires history reset')
   prev=stamp
   if not -32768<=temp<=32767:raise ValueError('Input outside Q8.8 range')
   raw=temp&65535;hi,lo=raw>>8,raw&255;uart.write(bytes([170,85,1,2,hi,lo,1^2^hi^lo]));uart.flush();hist.append(temp)
   if len(hist)<25:writer.writerow([stamp,temp,'','','warmup']);continue
   expected=max(-32768,min(32767,(hist[-22]*16384+a*(hist[-1]-hist[-25])+b*(hist[-1]-hist[-4])+c*16384)//16384))
   reply=uart.read(7)
   if len(reply)!=7:raise RuntimeError(f'UART timeout: {reply.hex()}')
   if reply[:4]!=bytes([170,85,129,2]) or reply[6]!=(129^2^reply[4]^reply[5]):raise RuntimeError(f'Bad reply: {reply.hex()}')
   received=int.from_bytes(reply[4:6],'big',signed=True);writer.writerow([stamp,temp,expected,received,received==expected]);log.flush()
   if received!=expected:raise RuntimeError(f'Mismatch {stamp}: {received} != {expected}')
   checked+=1
 print(f'PASS physical-board replay: {checked} forecasts; log={args.output}')
if __name__=='__main__':main()
