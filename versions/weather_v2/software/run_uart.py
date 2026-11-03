from pathlib import Path
import subprocess,shutil
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1]
for shared in [0,1]:
 variant='resource' if shared else 'speed';b=R/'build'/f'{variant}_uart';b.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/'build/vectors/vectors.txt',b/'vectors.txt')
 rtl=[R/'rtl/de2_weather_uart.v',R/'rtl/wind_direction_cordic.v',R/'rtl'/f'weather_system_{variant}.v',R/'rtl'/f'weather_predictor_{variant}.v']
 if shared==0:rtl.append(R/'rtl/weather_ar_channel.v')
 rtl += [ROOT/'hardware/speed_optimized'/f'{name}.v' for name in ['reset_sync','uart_rx','uart_tx']]
 cmd=['verilator','--binary','--timing','-j','2','-Wno-fatal','--top-module','tb_weather_uart',f'-GSHARED={shared}','--Mdir',str(b/'obj'),'-o','sim',str(R/'tb/tb_weather_uart.sv'),*map(str,rtl)]
 with (b/'compile.log').open('w') as f:subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True)
 with (R/'reports'/f'{variant}_uart.log').open('w') as f:subprocess.run([str(b/'obj/sim')],cwd=b,stdout=f,stderr=subprocess.STDOUT,check=True)
 print(variant,'UART PASS',flush=True)
