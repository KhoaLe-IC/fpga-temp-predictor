import os, pty, select, subprocess, time, sys
from pathlib import Path
root = Path.cwd()
run = Path(os.environ['RUN_DIR'])
quartus = '/opt/altera/13.0sp1/quartus/bin/quartus_stp'
master, slave = pty.openpty()
args = [quartus, '-t', str(run/'acquire_weather_speed.tcl'), str(run/'weather_speed_live.stp')]
capture = subprocess.Popen(args, stdout=slave, stderr=slave, stdin=subprocess.DEVNULL, cwd=root, start_new_session=True)
os.close(slave)
replay = None
buffer = ''
start = time.monotonic()
with (run/'capture_acquisition_pty.log').open('w') as log:
    while True:
        ready, _, _ = select.select([master], [], [], 1)
        if ready:
            try: chunk = os.read(master,65536)
            except OSError: break
            if not chunk: break
            text = chunk.decode(errors='replace')
            log.write(text); log.flush()
            print(text,end='',flush=True)
            buffer += text
            # Only the actual analyzer status PRE qualifies; never CAPTURE ARMED.
            import re
            if replay is None and re.search(r'\bPRE\b',buffer):
                print('OBSERVED PRE; launching exactly one checked replay',flush=True)
                (run/'capture_ready_evidence.txt').write_text(buffer+'\nObserved PRE before starting replay.\n')
                env=os.environ.copy(); env['FPGA_JTAG_CSV']=str(run/'capture_replay.csv')
                replay_log=(run/'capture_replay.log').open('w')
                replay=subprocess.Popen([quartus,'-t','scripts/replay_jtag.tcl','weather_speed'],stdout=replay_log,stderr=subprocess.STDOUT,env=env,cwd=root)
        if capture.poll() is not None and not ready: break
        if time.monotonic()-start > 150:
            capture.terminate(); raise RuntimeError('Capture exceeded 150 seconds')
    rc=capture.wait(timeout=10)
os.close(master)
(run/'capture_acquisition.exitcode').write_text(str(rc)+'\n')
if replay is None: raise RuntimeError('No actual PRE observed; replay was not launched')
rr=replay.wait(timeout=60);replay_log.close()
(run/'capture_replay.exitcode').write_text(str(rr)+'\n')
print('Capture exit:',rc,'Replay exit:',rr,flush=True)
if rc or rr: sys.exit(1)
