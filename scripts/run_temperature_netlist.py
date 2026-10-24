"""Generate fresh functional Quartus netlists and replay the trained C++ vectors."""
from pathlib import Path
import subprocess,shutil,json,hashlib
R=Path(__file__).resolve().parents[1];LIB=Path(shutil.which('quartus_eda')).resolve().parents[1]/'eda/sim_lib'
for variant in ['speed','resource']:
 p=R/'hardware/quartus'/variant;b=p/'build/functional_final';b.mkdir(parents=True,exist_ok=True)
 with (b/'generate.log').open('w') as f:subprocess.run(['quartus_eda','--simulation','--tool=modelsim','--format=verilog','--functional=on','--output_directory='+str(b),'predictor'],cwd=p,stdout=f,stderr=subprocess.STDOUT,check=True)
 nets=list(b.rglob('predictor.vo'))
 if len(nets)!=1:raise RuntimeError('Expected exactly one functional netlist')
 net=nets[0];vectors=R/'hardware/tb/build'/f'{variant}_0.txt';tb=R/'hardware/quartus/tb_netlist.sv'
 with (b/'compile.log').open('w') as f:subprocess.run(['iverilog','-g2012',f'-DDUT=temp_predictor_{variant}','-s','tb_netlist','-o',str(b/'sim'),str(tb),str(net),str(LIB/'cycloneii_atoms.v'),str(LIB/'altera_primitives.v')],stdout=f,stderr=subprocess.STDOUT,check=True)
 log=R/'docs/reports'/f'temperature_{variant}_functional_final.txt'
 with log.open('w') as f:subprocess.run(['vvp',str(b/'sim'),'+VECTORS='+str(vectors)],cwd=p,stdout=f,stderr=subprocess.STDOUT,check=True)
 if 'PASS netlist at 50 MHz: inputs=4096 forecasts=4072' not in log.read_text():raise RuntimeError('Missing PASS marker')
 manifest={'netlist_sha256':hashlib.sha256(net.read_bytes()).hexdigest(),'vectors_sha256':hashlib.sha256(vectors.read_bytes()).hexdigest(),'testbench_sha256':hashlib.sha256(tb.read_bytes()).hexdigest(),'clock_period_ns':20}
 (R/'docs/reports'/f'temperature_{variant}_functional_final.json').write_text(json.dumps(manifest,indent=2));print(variant,'functional final PASS',flush=True)
