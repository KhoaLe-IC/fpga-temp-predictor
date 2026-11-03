from pathlib import Path
import json,subprocess
R=Path(__file__).resolve().parents[1]
def main():
 m=json.loads((R/'models/model.json').read_text());coeff=''
 for c in range(6):coeff+=' '.join(str(m['weights_q14'][c][k*6+c]) for k in range(7))+' '+str(m['bias_q8'][c])+'\n'
 for variant,latency in [('speed',40),('resource',156)]:
  build=R/'build'/variant;build.mkdir(parents=True,exist_ok=True);(build/'reference_coefficients.txt').write_text(coeff)
  rtl=[R/'rtl'/f'weather_system_{variant}.v',R/'rtl'/f'weather_predictor_{variant}.v',R/'rtl/wind_direction_cordic.v']
  if variant=='speed':rtl.append(R/'rtl/weather_ar_channel.v')
  cmd=['verilator','--binary','--timing','--assert','-j','2','-Wno-fatal','--top-module','tb_weather',f'-GLATENCY={latency}',f'-DDUT=weather_system_{variant}','--Mdir',str(build/'obj'),'-o','sim',str(R/'tb/tb_weather.sv'),*map(str,rtl),str(R/'tb/weather_reference.cpp')]
  with (build/'compile.log').open('w') as f:subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True)
  with (R/'reports'/f'{variant}_dpi.log').open('w') as f:subprocess.run([str(build/'obj/sim')],cwd=build,stdout=f,stderr=subprocess.STDOUT,check=True)
  print(variant,'DPI-C PASS',flush=True)
if __name__=='__main__':main()
