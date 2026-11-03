from pathlib import Path
import subprocess,shutil
R=Path(__file__).resolve().parents[1]
for name,weather,shared in [('temperature',0,0),('temperature_resource',0,1),('weather_speed',1,0),('weather_resource',1,1)]:
 b=R/'hardware/jtag/build'/name;b.mkdir(parents=True,exist_ok=True)
 files=[R/'hardware/jtag/tb_jtag.sv',R/'hardware/jtag/jtag_mailbox.v',R/'hardware/speed_optimized/reset_sync.v']
 top='de2_weather_jtag' if weather else ('de2_temperature_resource_jtag' if shared else 'de2_temperature_jtag');files.append(R/'hardware/jtag'/f'{top}.v')
 if weather:
  variant='resource' if shared else 'speed'
  files.extend(R/'versions/weather_v2/rtl'/f for f in [f'weather_system_{variant}.v',f'weather_predictor_{variant}.v','wind_direction_cordic.v'])
  if not shared:files.append(R/'versions/weather_v2/rtl/weather_ar_channel.v')
 else:
  files.append(R/('hardware/resource_optimized/temp_predictor_resource.v' if shared else 'hardware/speed_optimized/temp_predictor_speed.v'));shutil.copyfile(R/('hardware/resource_optimized/coefficients.txt' if shared else 'hardware/speed_optimized/coeffs.txt'),b/('coefficients.txt' if shared else 'coeffs.txt'))
 if not weather and shared:files.extend([R/'hardware/resource_optimized/temp_history_buffer.v',R/'hardware/resource_optimized/ols_shared_datapath.v'])
 # Propagate the shared selection through the top-level DUT parameter.
 tb=(R/'hardware/jtag/tb_jtag.sv').read_text()
 if weather:tb=tb.replace('`DUT dut(', '`DUT #(.SHARED(SHARED)) dut(')
 (b/'tb.sv').write_text(tb);files[0]=b/'tb.sv'
 cmd=['verilator','--binary','--timing','--assert','-Wno-fatal','-j','2','--top-module','tb_jtag',f'-GWEATHER={weather}',f'-GSHARED={shared}',f'-DDUT={top}','--Mdir',str(b/'obj'),'-o','sim',*map(str,files)]
 with (b/'compile.log').open('w') as f:subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True)
 with (R/'docs/reports'/f'jtag_{name}_rtl.log').open('w') as f:subprocess.run([str(b/'obj/sim'),'+VECTORS='+str(R/'hardware/jtag/vectors'/('weather.txt' if weather else 'temperature.txt'))],cwd=b,stdout=f,stderr=subprocess.STDOUT,check=True)
 print(name,'JTAG RTL PASS',flush=True)
