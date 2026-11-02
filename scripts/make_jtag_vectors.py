"""Pack existing independent C++ golden vectors for USB-Blaster mailbox replay."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def make(weather):
 src=R/('versions/weather_v2/build/vectors/vectors.txt' if weather else 'hardware/tb/build/speed_0.txt')
 rows=[list(map(int,line.split())) for line in src.read_text().splitlines() if line.strip()]
 if not weather:rows=rows[1:]
 out=[];toggle=0;fc=0
 for i,row in enumerate(rows[:128]):
  if weather:
   data=sum((row[c]&((1<<18)-1))<<(18*c) for c in range(6));valid=row[6]
   result=sum((row[7+c]&((1<<18)-1))<<(18*c) for c in range(6))|((row[13]&((1<<18)-1))<<108)
  else:data=row[0]&65535;valid=row[1];result=row[2]&65535
  assert valid==int(i>=24)
  fc+=valid;stage=(data<<2)|toggle;toggle^=1;commit=(data<<2)|toggle
  out.append(f'{stage:032x} {commit:032x} {i+1} {fc} {result:032x}')
 assert len(out)==128 and fc==104
 dest=R/'hardware/jtag/vectors'/('weather.txt' if weather else 'temperature.txt');dest.parent.mkdir(exist_ok=True);dest.write_text('\n'.join(out)+'\n');print(dest)
if __name__=='__main__':
 for weather in [False,True]:make(weather)
