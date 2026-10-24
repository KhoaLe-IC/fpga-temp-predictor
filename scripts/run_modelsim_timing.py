"""Reproducible vendor-format post-fit SDF gate; requires ModelSim/Questa on PATH.
Never treats simulator exit status alone as a pass: validates transcript and PASS marker.
"""
from pathlib import Path
import argparse,subprocess,shutil,re,json,hashlib,fcntl
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--design',choices=['temperature_speed','temperature_resource','weather_speed','weather_resource'],required=True);args=p.parse_args()
 # Starter Edition sessions share license-lock state; serialize complete runs.
 lockpath=Path.home()/'.cache/fpga-weather-modelsim.lock';lockpath.parent.mkdir(exist_ok=True)
 lock=lockpath.open('a');fcntl.flock(lock,fcntl.LOCK_EX)
 (ROOT/'docs/reports'/f'{args.design}_modelsim_timing.json').unlink(missing_ok=True)
 for tool in ['quartus_eda','vlib','vlog','vsim']:
  if not shutil.which(tool):raise SystemExit(f'Required tool unavailable: {tool}. No timing-simulation pass is claimed.')
 weather=args.design.startswith('weather');variant=args.design.split('_')[-1];project=ROOT/('versions/weather_v2/quartus' if weather else 'hardware/quartus')/variant
 name='weather' if weather else 'predictor';build=project/'build/modelsim_timing';build.mkdir(parents=True,exist_ok=True)
 lib=Path(shutil.which('quartus_eda')).resolve().parents[1]/'eda/sim_lib'
 if not (lib/'cycloneii_atoms.v').exists():lib=Path('/home/khoale/altera/13.0sp1/quartus/eda/sim_lib')
 with (build/'generate.log').open('w') as f:subprocess.run(['quartus_eda','--simulation','--tool=modelsim','--format=verilog','--functional=off','--output_directory='+str(build),name],cwd=project,stdout=f,stderr=subprocess.STDOUT,check=True)
 files=list(build.rglob(name+'.vo'));sdfs=list(build.rglob(name+'_v.sdo'))
 if len(files)!=1 or len(sdfs)!=1:raise RuntimeError('Ambiguous/missing timing netlist or SDF')
 netlist=files[0];sdf=sdfs[0]
 # Suppress only the redundant automatic SDF task; vsim explicitly applies original max SDF.
 copy=build/'timing_netlist.v';copy.write_text(re.sub(r'initial\s+\$sdf_annotate\([^;]+;','// SDF applied explicitly by vsim.',netlist.read_text()))
 tbsource=ROOT/('versions/weather_v2/tb/tb_weather_netlist.sv' if weather else 'hardware/quartus/tb_netlist.sv');tb=build/'tb_timing.sv';tb.write_text(tbsource.read_text().replace('#2;','#9;'))
 top='tb_weather_netlist' if weather else 'tb_netlist';dut=('weather_system_' if weather else 'temp_predictor_')+variant
 vectors=ROOT/('versions/weather_v2/build/vectors/vectors.txt' if weather else f'hardware/tb/build/{variant}_0.txt')
 shutil.rmtree(build/'work',ignore_errors=True)
 subprocess.run(['vlib','work'],cwd=build,check=True)
 vendor=Path(shutil.which('vsim')).resolve().parents[1]/'altera/verilog'
 if not (vendor/'cycloneii').is_dir():vendor=Path.home()/'altera/13.0sp1/modelsim_ase/altera/verilog'
 if not (vendor/'cycloneii').is_dir():raise SystemExit('Precompiled Altera Cyclone II library required for SDF simulation')
 for logical,folder in [('cycloneii_ver','cycloneii'),('altera_ver','altera')]:
  subprocess.run(['vmap',logical,str(vendor/folder)],cwd=build,check=True)
 with (build/'compile.log').open('w') as f:subprocess.run(['vlog','-sv','+define+DUT='+dut,str(tb),str(copy)],cwd=build,stdout=f,stderr=subprocess.STDOUT,check=True)
 command=['vsim','-c','-L','cycloneii_ver','-L','altera_ver','-t','1ps','-sdfmax',f'/{top}/dut={sdf}',f'work.{top}','+VECTORS='+str(vectors)]
 if weather:command.append('-gLATENCY='+str(40 if variant=='speed' else 156))
 command+=['-do','onerror {quit -code 1}; run -all; quit -f']
 transcript=build/'simulation.log'
 with transcript.open('w') as f:subprocess.run(command,cwd=build,stdout=f,stderr=subprocess.STDOUT,check=True)
 text=transcript.read_text();bad=re.search(r'(?i)(timing violation|\$hold.*violation|\$setup.*violation|\*\* error|\*\* fatal|unable to.*annotat|failed to.*annotat|annotation.*skipped)',text)
 if bad or 'SDF Backannotation Successfully Completed' not in text or ('PASS weather netlist 50 MHz' if weather else 'PASS netlist at 50 MHz') not in text:raise RuntimeError('Timing simulation not accepted; inspect transcript')
 (ROOT/'docs/reports'/f'{args.design}_modelsim_timing.json').write_text(json.dumps({'status':'PASS','clock_period_ns':20,'observation_delay_ns':9,'sdf_sha256':hashlib.sha256(sdf.read_bytes()).hexdigest(),'netlist_sha256':hashlib.sha256(netlist.read_bytes()).hexdigest(),'transcript':str(transcript.relative_to(ROOT)),'transcript_sha256':hashlib.sha256(transcript.read_bytes()).hexdigest(),'netlist':str(netlist.relative_to(ROOT)),'sdf':str(sdf.relative_to(ROOT)),'vectors':str(vectors.relative_to(ROOT)),'vectors_sha256':hashlib.sha256(vectors.read_bytes()).hexdigest(),'testbench':str(tb.relative_to(ROOT)),'testbench_sha256':hashlib.sha256(tb.read_bytes()).hexdigest()},indent=2))
 print('PASS SDF timing simulation:',args.design)
if __name__=='__main__':main()
