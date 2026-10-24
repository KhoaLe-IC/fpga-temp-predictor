from pathlib import Path
import subprocess, argparse, hashlib, json, shutil
a=argparse.ArgumentParser();a.add_argument("--variant",choices=["speed","resource","both"],default="both");a.add_argument("--tag",default="final");args=a.parse_args()
R=Path(__file__).resolve().parents[1]
LIB=Path('/home/khoale/altera/13.0sp1/quartus/eda/sim_lib')
for variant,latency in [('speed',40),('resource',156)]:
 if args.variant not in ['both',variant]:continue
 p=R/'quartus'/variant;b=R/'build'/f'{variant}_{args.tag}_netlist';b.mkdir(parents=True,exist_ok=True)
 source=p/'simulation/modelsim/weather.vo';snapshot=b/'weather.vo';shutil.copyfile(source,snapshot)
 digest=hashlib.sha256(snapshot.read_bytes()).hexdigest()
 with (b/'compile.log').open('w') as f:subprocess.run(['iverilog','-g2012',f'-DDUT=weather_system_{variant}','-s','tb_weather_netlist',f'-Ptb_weather_netlist.LATENCY={latency}','-o',str(b/'sim'),str(R/'tb/tb_weather_netlist.sv'),str(snapshot),str(LIB/'cycloneii_atoms.v'),str(LIB/'altera_primitives.v')],stdout=f,stderr=subprocess.STDOUT,check=True)
 with (R/'reports'/f'{variant}_{args.tag}_netlist.log').open('w') as f:subprocess.run(['vvp',str(b/'sim'),'+VECTORS='+str(R/'build/vectors/vectors.txt')],cwd=p,stdout=f,stderr=subprocess.STDOUT,check=True)
 if 'PASS weather netlist 50 MHz: inputs=288 forecasts=264' not in (R/'reports'/f'{variant}_{args.tag}_netlist.log').read_text():raise RuntimeError('Simulation ended without the required scoreboard PASS marker')
 (R/'reports'/f'{variant}_{args.tag}_netlist_manifest.json').write_text(json.dumps({'netlist_sha256':digest,'source_netlist':str(source.relative_to(R)), 'clock_period_ns':20,'vectors_sha256':hashlib.sha256((R/'build/vectors/vectors.txt').read_bytes()).hexdigest()},indent=2))
 print(variant,'netlist PASS',flush=True)
