"""Check a programmed DE2 weather UART wrapper against C++ generated vectors.
Reset KEY0 before use. The board DB9 requires an RS-232 adapter, not USB-Blaster UART.
"""
from pathlib import Path
import argparse,csv
import serial
R=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--port',required=True);p.add_argument('--vectors',type=Path,default=R/'build/vectors/vectors.txt');p.add_argument('--limit',type=int,default=128);p.add_argument('--output',type=Path,default=R/'reports/physical_board.csv');args=p.parse_args()
 rows=[list(map(int,line.split())) for line in args.vectors.read_text().splitlines()][:args.limit]
 if len(rows)<25 or any(len(row)!=14 for row in rows):raise ValueError('Need >=25 complete chronological reference rows')
 args.output.parent.mkdir(parents=True,exist_ok=True);checked=0
 with serial.Serial(args.port,115200,timeout=5) as uart,args.output.open('w',newline='') as f:
  uart.reset_input_buffer();log=csv.writer(f);log.writerow(['accepted_index','expected_outputs','received_outputs','expected_angle_q8','received_angle_q8','direction_defined','match'])
  for index,row in enumerate(rows):
   inputs,has,expected,angle=row[:6],row[6],row[7:13],row[13]
   if any(v< -131072 or v>131071 for v in inputs):raise ValueError('Input out of range')
   payload=b''.join(v.to_bytes(3,'big',signed=True) for v in inputs);body=bytes([2,18])+payload;check=0
   for byte in body:check^=byte
   uart.write(bytes([170,85])+body+bytes([check]));uart.flush()
   if not has:continue
   reply=uart.read(27)
   if len(reply)!=27:raise RuntimeError(f'Reply timeout at index {index}: {reply.hex()}')
   checksum=0
   for byte in reply[2:-1]:checksum^=byte
   if reply[:4]!=bytes([170,85,130,22]) or checksum!=reply[-1]:raise RuntimeError('Malformed reply')
   received=[int.from_bytes(reply[4+c*3:7+c*3],'big',signed=True) for c in range(6)]
   actual_angle=int.from_bytes(reply[22:25],'big');defined=reply[25];want_defined=int(expected[4]!=0 or expected[5]!=0)
   delta=(actual_angle-angle+46080)%92160-46080
   match=received==expected and defined==want_defined and (abs(delta)<=5 if want_defined else actual_angle==0)
   log.writerow([index,expected,received,angle,actual_angle,defined,match]);f.flush()
   if not match:raise RuntimeError(f'Board mismatch at accepted index {index}')
   checked+=1
 print(f'PASS physical weather board: forecasts={checked}, log={args.output}')
if __name__=='__main__':main()
