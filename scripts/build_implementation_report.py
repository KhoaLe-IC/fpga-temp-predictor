"""Collect current measured artifacts into a publishable report and evidence snapshot."""
from pathlib import Path
import csv,json,re,hashlib,shutil
R=Path(__file__).resolve().parents[1];D=R/'docs/reports';E=D/'evidence';E.mkdir(exist_ok=True)
projects=[('Temperature speed','hardware/quartus/speed','predictor'),('Temperature resource','hardware/quartus/resource','predictor'),('Temperature DE2 UART','hardware/quartus/de2_temperature','temperature'),('Weather parallel','versions/weather_v2/quartus/speed','weather'),('Weather shared','versions/weather_v2/quartus/resource','weather'),('Weather DE2 parallel UART','versions/weather_v2/quartus/de2_speed','weather_board'),('Weather DE2 shared UART','versions/weather_v2/quartus/de2_resource','weather_board')]
rows=[];manifest={}
for title,folder,name in projects:
 p=R/folder;summary=(p/f'output_files/{name}.fit.summary').read_text();sta=(p/f'output_files/{name}.sta.rpt').read_text()
 def val(label):
  match=re.search(re.escape(label)+r'\s*:\s*([\d,]+)',summary);return match[1] if match else 'N/A'
 fmax=re.search(r';\s*([\d.]+) MHz\s*;\s*[\d.]+ MHz\s*;',sta);slack=re.search(r'; Worst-case Slack ; ([\d.\-]+) ; ([\d.\-]+)',sta)
 fit_detail=(p/f'output_files/{name}.fit.rpt').read_text(encoding='latin1');m4k=re.search(r'; M4Ks\s*; ([\d,]+) /',fit_detail)
 rows.append([title,val('Total logic elements'),val('Total registers'),val('Total memory bits'),m4k[1] if m4k else 'N/A',val('Embedded Multiplier 9-bit elements'),fmax[1] if fmax else 'N/A',slack[1] if slack else 'N/A',slack[2] if slack else 'N/A'])
 for suffix in ['fit.summary','fit.rpt','sta.rpt','map.rpt','flow.rpt']:
  src=p/f'output_files/{name}.{suffix}';dst=E/(title.lower().replace(' ','_')+'_'+suffix.replace('.','_')+'.txt');shutil.copyfile(src,dst)
 for src in p.glob('*.qsf'):manifest[str(src.relative_to(R))]=hashlib.sha256(src.read_bytes()).hexdigest()
 for src in p.glob('*.sdc'):manifest[str(src.relative_to(R))]=hashlib.sha256(src.read_bytes()).hexdigest()
for pattern in ['hardware/speed_optimized/*.v','hardware/resource_optimized/*.v','versions/weather_v2/rtl/*.v','versions/weather_v2/models/*','hardware/tb/dpi/*']:
 for src in R.glob(pattern):
  if src.is_file():manifest[str(src.relative_to(R))]=hashlib.sha256(src.read_bytes()).hexdigest()
for src,label in [(R/'hardware/tb/regression_current.log','temperature_dpi'),(R/'hardware/quartus/speed/netlist_sim.log','temperature_speed_functional_netlist'),(R/'hardware/quartus/resource/netlist_sim.log','temperature_resource_functional_netlist'),(R/'hardware/quartus/de2_temperature/uart_sim.log','temperature_uart'),(R/'versions/weather_v2/reports/speed_dpi.log','weather_speed_dpi'),(R/'versions/weather_v2/reports/resource_dpi.log','weather_resource_dpi'),(R/'versions/weather_v2/reports/direction_exhaustive.log','direction_exhaustive')]:
 if src.exists():shutil.copyfile(src,E/(label+'.txt'))
for label in ['speed','resource']:
 for suffix in ['uart.log','final_netlist.log','final_netlist_manifest.json']:
  src=R/'versions/weather_v2/reports'/f'{label}_{suffix}'
  if src.exists():shutil.copyfile(src,E/(f'weather_{label}_'+suffix.replace('.','_')+'.txt'))
for variant in ['speed','resource']:
 for suffix in ['txt','json']:
  source=R/'docs/reports'/f'temperature_{variant}_functional_final.{suffix}'
  if source.exists():shutil.copyfile(source,E/source.name)
for target in ['temperature_speed','temperature_resource','weather_speed','weather_resource']:
 result=D/f'{target}_modelsim_timing.json'
 if result.exists():
  timing=json.loads(result.read_text());transcript=R/timing['transcript']
  shutil.copyfile(transcript,E/f'{target}_modelsim_timing.txt')
  manifest[str(result.relative_to(R))]=hashlib.sha256(result.read_bytes()).hexdigest()
m=json.loads((R/'versions/weather_v2/models/model.json').read_text())
def table(headers,values):return '| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+''.join('| '+' | '.join(map(str,row))+' |\n' for row in values)
s='''# Cyclone II Forecasting Implementation Report

**Target:** EP2C35F672C6, confirmed from the supplied device image.  
**Clock:** 50 MHz (20 ns).  
**Tools:** Quartus II 13.0 SP1 Web Edition; Verilator 5.052 for DPI-C RTL tests; Icarus for functional vendor-atom netlist simulations.  
**Report date:** 24 October 2026 (Asia/Ho_Chi_Minh).  
**Status:** Local implementation and simulation are verified for both versions. All four cores passed SDF timing simulation at 50 MHz, and all seven projects met static timing. Physical-board operation remains unverified: `jtagconfig` reported no JTAG hardware, and the user confirmed that the board is not available on this computer.

The deliverables include two temperature cores, a pinned temperature UART board project, six-channel weather forecasting in two architectures, two weather UART board projects, trained models, independent reference models, verification utilities, and implementation evidence. The board projects have compiled programming files, but deployment is not claimed.

## 1. Delivered scope and version separation

Version 1 preserves the three-parameter temperature OLS model and its two RTL architectures. Version 2 is separate under `versions/weather_v2`, with independently trained pressure, humidity, wind-speed, and circular wind-direction forecasts, as well as temperature. Neither FPGA version trains or updates coefficients on the device.

## 2. Temperature version

The model predicts three hours ahead from consecutive hourly samples:

$$
\\widehat T(t+3)=T(t-21)+a[T(t)-T(t-24)]+b[T(t)-T(t-3)]+c.
$$

The saved coefficients are a=0.7454870438526146, b=0.009149444986888534, c=0.0011295816555433053. Their hardware integers are A_Q=12214, B_Q=150 (14 fractional bits) and C_Q=0 (8 fractional bits). Both checked-in coefficient files were corrected to this common trained configuration. A fresh training-data audit reproduced the saved coefficients using 26,253 training examples.

Inputs and outputs use signed 16-bit values with eight fractional bits. Differences are 17 bits, products 33 bits, and the final accumulator 35 bits. The final arithmetic shift floors negative fractional results; output overflow saturates to signed 16 bits. The first prediction corresponds to accepted sample 25. Invalid cycles and stalled requests do not advance history.

The speed core has five-clock acceptance-to-output latency and a one-clock initiation interval. The resource core has nine-clock latency and a ten-clock initiation interval. At 50 MHz these latencies are 100 ns and 180 ns; the three-hour forecast horizon is a separate property of the data model.

### Reproduced forecast accuracy

'''
temp=list(csv.DictReader((D/'temperature_metrics.csv').open()));s+=table(['2025 test model','Samples','MAE (°C)','RMSE (°C)'],[[r['model'],r['samples'],f"{float(r['MAE_C']):.6f}",f"{float(r['RMSE_C']):.6f}"] for r in temp if r['split']=='test' and r['model']!='fixed_minus_float'])
numerical=list(csv.DictReader((D/'temperature_numerical_error.csv').open()))
s+='\n### Fixed-point error decomposition (2025 test)\n\n'
s+=table(['Incremental error stage','MAE (°C)','Maximum absolute (°C)','Bias (°C)'],[[r['stage'],f"{float(r['MAE_C']):.9f}",f"{float(r['max_abs_C']):.9f}",f"{float(r['bias_C']):.9f}"] for r in numerical if r['split']=='test'])
s+='\nNo validation or test prediction saturated the signed 16-bit output. These incremental signed errors add; their absolute-error averages do not. Full details are in `temperature_numerical_error.csv`.\n'
s+='''
Maximum fixed-point deviation from the floating-point temperature predictor on the test set is approximately 0.009092°C. Forecast error and arithmetic implementation error are different measurements. At nominal 115200 baud with 8-N-1 framing and stop-and-wait, the temperature protocol has a theoretical ceiling of about 823 forecasts/s after warm-up (7 request + 7 reply bytes); the weather protocol ceiling is about 230 frames/s (23 request + 27 reply bytes), before host overhead and turnarounds. These calculated serial budgets are distinct from core throughput and are not physical-board measurements.

### Verification and board integration

The production RTL passed a five-configuration coefficient matrix for both architectures through the existing C++ DPI-C reference. Each paired replay compared 4,072 outputs by accepted-sample index. Functional Quartus atom-netlist replays at 50 MHz passed 4,096 inputs / 4,072 forecasts for each core. A separate full-year historical DPI-C replay also passed for both architectures: 8,781 accepted hourly samples (including initial history), yielding 8,757 matched forecasts for the 2025 test windows. A separate UART RTL test at 50 MHz / 115200 baud passed 40 inputs and 16 checked replies, including packet framing and checksum.

The minimal original-DE2 wrapper exposes CLOCK_50, KEY0_N, UART_RXD, and UART_TXD. It has explicit pin assignments and tri-states unused pins. Its compiled programming file is under `hardware/quartus/de2_temperature/output_files/temperature.sof`. Core-only projects have automatic pin placement for measurement and must not be programmed as board designs.

The host replay utility is `scripts/replay_temperature_board.py`. It requires a connected RS-232 adapter, a programmed board, and KEY0 reset before replay. It checks each board response and saves a CSV. It has not been run against physical hardware here.

## 3. Weather data and model selection

NASA POWER hourly T2M, PS, RH2M, WS10M, and WD10M were downloaded for Ho Chi Minh City (10.8231°N, 106.6297°E), 2021–2025, UTC. API responses retain units and metadata. Pressure is kPa, humidity percent, wind speed m/s, and direction degrees. These are gridded environmental data; performance is not evidence of station-level operational forecasting accuracy.

Training labels end before 2024. Validation uses 2024 inputs with target timestamps before 2025. Test uses 2025 inputs, excluding targets outside the available dataset. Selection is based on validation MAE, with circular MAE for direction. Counts: 26,253 training, 8,781 validation, and 8,757 test examples. All require 25 consecutive valid history samples. Missing samples are not silently interpolated.

Candidates include persistence, previous-day target-hour persistence, seasonal three-parameter OLS, and univariate/multivariate seven-lag autoregression with ridge penalties 0, 0.001, 0.1, 1, 10, and 100. The selected models are best among this evaluated candidate set. No claim of globally optimal forecasting is made. The generated RTL currently supports the selected univariate models and explicitly rejects selected cross-channel weights.

### Selected equations and coefficients

For each channel x, the selected equation is:

$$
\\widehat x(t+3)=\\beta_x+\\sum_{k=0}^{6}w_{x,k}x(t-\\ell_k),\\qquad \\ell=[0,1,3,6,12,21,24].
$$

Direction uses separate cosine and sine channels, with a jointly selected candidate pair based on circular validation error. Its angle is reconstructed as atan2(predicted sine, predicted cosine), wrapped to [0°,360°). Input trigonometric conversion is performed by the host; angle reconstruction is performed in RTL. The zero predicted vector is explicitly marked undefined. Direction metrics use circular angular distance where actual target wind speed is at least 0.5 m/s; this threshold is a declared project choice.

'''
coefrows=[]
for c,name in enumerate(m['channels']):coefrows.append([name,m['selected_candidates'][c],f"{m['bias'][c]:.8g}",', '.join(f"{m['weights'][c][k*6+c]:.8g}" for k in range(7))])
s+=table(['Channel','Selected candidate','Bias','Weights in lag order'],coefrows)
s+='\n### Quantized weather constants\n\n'
s+=table(['Channel','Bias Q8','Lag 0','Lag 1','Lag 3','Lag 6','Lag 12','Lag 21','Lag 24'],[[name,m['bias_q8'][c],*[m['weights_q14'][c][k*6+c] for k in range(7)]] for c,name in enumerate(m['channels'])])
s+='\nWeights above are raw signed Q14 integers; biases are raw signed Q8 integers.\n'
s+='\nExact floating-point and quantized coefficients are in [model.json](../../versions/weather_v2/models/model.json).\n\n### Held-out test accuracy\n\n'
metrics=list(csv.DictReader((R/'versions/weather_v2/reports/metrics.csv').open()));s+=table(['Target','Selected fixed MAE','Selected fixed RMSE','Persistence MAE','Diurnal MAE'],[[name,next(f"{float(r['MAE']):.6f}" for r in metrics if r['split']=='test' and r['target']==name and r['model']=='selected_fixed'),next(f"{float(r['RMSE']):.6f}" for r in metrics if r['split']=='test' and r['target']==name and r['model']=='selected_fixed'),next(f"{float(r['MAE']):.6f}" for r in metrics if r['split']=='test' and r['target']==name and r['model']=='persistence'),next(f"{float(r['MAE']):.6f}" for r in metrics if r['split']=='test' and r['target']==name and r['model']=='diurnal')] for name in dict.fromkeys(r['target'] for r in metrics)])
s+='''
These software direction scores use floating atan2 of quantized predicted components. The separate RTL angle-conversion check bounds the additional CORDIC approximation error; the table does not claim exact end-to-end CORDIC forecast metrics. A frozen-model numerical diagnostic (`versions/weather_v2/reports/numerical_error.csv`) found no signed 18-bit saturation on validation/test windows. On 8,593 non-calm 2025 targets, fixed-component quantization changed the ideal decoded angle by a circular MAE of 0.128151° and maximum 2.101618° relative to floating-point inference. This component-quantization effect is separate from the smaller CORDIC conversion error. Physical clipping counts are recorded in that CSV.

## 4. Weather hardware and verification

Inputs/outputs are signed 18-bit Q8 values, coefficients signed 18-bit Q14, biases signed 32-bit Q8, products 36 bits, and accumulators 48 bits. A 25-frame history supplies the seven selected lags. Humidity outputs are clipped to 0–100%, wind speed to nonnegative values, and direction components to −1…1; signed 18-bit saturation handles remaining overflow.

The parallel architecture uses six arithmetic lanes. The shared architecture uses one multiplier across all channels. Full-system latencies, including the iterative direction converter, are 40 and 156 clocks (0.80 µs and 3.12 µs). Sustained accepted-frame intervals are 23 and 139 clocks. Both versions also have original-DE2 UART wrappers with explicit four-pin maps and generated programming files. Their RTL serial-path tests passed at 50 MHz / 115200 baud with 32 valid frames, eight checked replies, and rejection of an additional corrupt-checksum frame per architecture. Host replay for these wrappers is provided in `versions/weather_v2/software/replay_board.py`. The output angle is unsigned 18-bit degrees Q8; direction validity is separately signalled for zero vectors. Consumers must capture all valid outputs; no output backpressure exists.

Both architectures passed independent C++ DPI-C comparisons over 1,200 accepted frames each: 1,124 forecasts checked, with four pending forecasts canceled by reset. Tests include signed extremes, physical-range samples, gaps, backpressure, and reset during processing. The C++ model uses 64-bit integer sums and explicit floor division. A separate NumPy implementation cross-checked all 264 forecast vectors in the historical-plus-extreme netlist replay file. Exhaustive CORDIC testing covered all 263,169 integer cosine/sine pairs in the clipped range −256…256; maximum circular conversion error was 0.005635°.

Both final weather functional netlists passed 288 accepted frames and 264 checked forecasts at 50 MHz. The replay covers historical samples and signed extremes. The final netlist manifests record SHA-256 hashes of each simulated netlist and the input/reference vectors; the completion audit checks these against the current files.

## 5. Measured Cyclone II implementation

All projects use the same target device and 20 ns clock. Core projects have provisional 2 ns maximum / 0 ns minimum synchronous I/O delays and default output loading. The pinned UART wrapper instead treats external UART/reset as asynchronous signals with synchronization-path exceptions. These are declared implementation assumptions, not characterized board delays.

'''
s+=table(['Design','LE','Registers','Logical memory bits','M4K blocks','9-bit multiplier elements','Slow Fmax (MHz)','Setup slack (ns)','Hold slack (ns)'],rows)
timingrows=[]
for target in ['temperature_speed','temperature_resource','weather_speed','weather_resource']:
 result=D/f'{target}_modelsim_timing.json'
 status=json.loads(result.read_text()).get('status','PENDING') if result.exists() else 'PENDING'
 timingrows.append([target,status,('4096 / 4072' if target.startswith('temperature') else '288 / 264') if status=='PASS' else 'Not accepted'])
s+='\n### SDF timing simulation at 50 MHz\n\n'+table(['Design','Acceptance','Inputs / forecasts'],timingrows)
s+='''
Two 9-bit multiplier elements correspond to one full 18×18 multiplier resource on this target; therefore the raw multiplier counts represent two versus one temperature multipliers, and six versus one weather multipliers. Logical memory bits and allocated M4K blocks are shown separately. Resource sharing saves multiplier elements but does not guarantee fewer logic elements. Dynamic selection, control, and register/history organization contribute to the shared designs' logic use. Report core and full-system measurements separately.

### What the passing timing checks establish

Functional netlist simulation verifies the mapped logic without propagation delays. TimeQuest analyzes fitted setup/hold timing. ModelSim then replayed the fitted timing netlists with original Quartus SDF max delays at a 20 ns clock, using the bundled precompiled Cyclone II libraries. All four timing scoreboards passed with no reported timing violations. These are core-level timing replays; the UART board wrappers have RTL serial-path tests and fitted static timing, but no full-board SDF replay is claimed.

### Simulator issues resolved during the work

- Icarus could run functional vendor-atom netlists but could not elaborate the vendor timing-check constructs needed for SDF. This was a tool limitation, not a passing timing result.
- XSim probes produced timing violations/mismatches. A separate parser probe also exposed conversion failures for some valid signed decimal records. A lossless hexadecimal replay passed without SDF, while the XSim SDF probe still failed. These attempts are retained as diagnostics and are not accepted timing evidence.
- ModelSim-Altera Starter Edition 10.1d was downloaded from Altera after user sign-in and explicit approval of the download agreement. Its SHA-1 matched the published value. A local 32-bit ncurses ABI-5 build resolved the missing library; platform-specific launchers resolved legacy Linux detection. No system library was replaced.
- Starter Edition requires its bundled precompiled Altera libraries for SDF. Mapping `cycloneii_ver` and `altera_ver` resolved the initial primitive-library rejection.
- An initial shared-weather angle mismatch came from sampling at 8 ns, before the fitted 8.070 ns maximum clock-to-output delay. The parallel weather maximum is 8.485 ns. Moving the scoreboard observation to 9 ns resolved the premature sampling; the RTL, 20 ns clock, SDF delays, and timing checks were retained.
- One overlapping ModelSim session terminated on a license-lock error. The parallel weather replay was retried alone after the shared run finished and passed. Future timing-runner invocations are serialized as a precaution.

See [ModelSim setup](MODELSIM_SETUP.md), the four timing result manifests, and the copied transcripts in `evidence/`. Earlier simulator-specific failures do not invalidate the subsequent accepted vendor-simulator runs; they remain documented for traceability.

## 6. Remaining acceptance items

- Program the connected physical DE2 board and run the checked UART replay. No JTAG hardware was available during inspection.
- Confirm the physical board revision matches the original-DE2 pin map before programming.

## 7. Reproduction and evidence

See [Quartus project instructions](../../hardware/quartus/README.md) and [weather version instructions](../../versions/weather_v2/README.md). Temperature evaluation is reproduced with `python scripts/evaluate_temperature.py`. The report collector is `python scripts/build_implementation_report.py`; it copies current Quartus reports and verification logs into `evidence/` and records source/configuration hashes in `evidence_manifest.json`.

Source references: [NASA POWER hourly API](https://power.larc.nasa.gov/docs/services/api/temporal/hourly/) and [Altera DE2 User Manual v1.6](https://www-ug.eecg.toronto.edu/msl/manuals/DE2_User_Manual.pdf), Tables 4.2, 4.5, and 4.10. The provided image identifies the FPGA device; the manual supplies the original-DE2 pin assumptions.
'''
s+='\n'+(R/'scripts/implementation_report_details.md').read_text()
(D/'IMPLEMENTATION_REPORT.md').write_text(s);(D/'evidence_manifest.json').write_text(json.dumps(manifest,indent=2));print('Report and evidence snapshot updated')
