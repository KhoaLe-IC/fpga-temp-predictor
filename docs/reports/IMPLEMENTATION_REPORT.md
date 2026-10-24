# Cyclone II Forecasting Implementation Report

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
\widehat T(t+3)=T(t-21)+a[T(t)-T(t-24)]+b[T(t)-T(t-3)]+c.
$$

The saved coefficients are a=0.7454870438526146, b=0.009149444986888534, c=0.0011295816555433053. Their hardware integers are A_Q=12214, B_Q=150 (14 fractional bits) and C_Q=0 (8 fractional bits). Both checked-in coefficient files were corrected to this common trained configuration. A fresh training-data audit reproduced the saved coefficients using 26,253 training examples.

Inputs and outputs use signed 16-bit values with eight fractional bits. Differences are 17 bits, products 33 bits, and the final accumulator 35 bits. The final arithmetic shift floors negative fractional results; output overflow saturates to signed 16 bits. The first prediction corresponds to accepted sample 25. Invalid cycles and stalled requests do not advance history.

The speed core has five-clock acceptance-to-output latency and a one-clock initiation interval. The resource core has nine-clock latency and a ten-clock initiation interval. At 50 MHz these latencies are 100 ns and 180 ns; the three-hour forecast horizon is a separate property of the data model.

### Reproduced forecast accuracy

| 2025 test model | Samples | MAE (°C) | RMSE (°C) |
| --- | --- | --- | --- |
| OLS_float | 8757 | 0.537973 | 0.785961 |
| OLS_fixed | 8757 | 0.538017 | 0.785955 |
| persistence | 8757 | 2.080369 | 2.732720 |
| diurnal | 8757 | 0.832280 | 1.187346 |

### Fixed-point error decomposition (2025 test)

| Incremental error stage | MAE (°C) | Maximum absolute (°C) | Bias (°C) |
| --- | --- | --- | --- |
| input_quantization | 0.001326787 | 0.004686302 | -0.000004443 |
| coefficient_quantization_given_quantized_inputs | 0.001129571 | 0.001180549 | -0.001129571 |
| final_floor_shift | 0.001932309 | 0.003905773 | -0.001932309 |
| total_fixed_minus_float | 0.003160611 | 0.009091605 | -0.003066323 |

No validation or test prediction saturated the signed 16-bit output. These incremental signed errors add; their absolute-error averages do not. Full details are in `temperature_numerical_error.csv`.

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
\widehat x(t+3)=\beta_x+\sum_{k=0}^{6}w_{x,k}x(t-\ell_k),\qquad \ell=[0,1,3,6,12,21,24].
$$

Direction uses separate cosine and sine channels, with a jointly selected candidate pair based on circular validation error. Its angle is reconstructed as atan2(predicted sine, predicted cosine), wrapped to [0°,360°). Input trigonometric conversion is performed by the host; angle reconstruction is performed in RTL. The zero predicted vector is explicitly marked undefined. Direction metrics use circular angular distance where actual target wind speed is at least 0.5 m/s; this threshold is a declared project choice.

| Channel | Selected candidate | Bias | Weights in lag order |
| --- | --- | --- | --- |
| temperature_C | autoregressive_ridge_1 | 1.2101225 | 1.222816, -0.56978791, 0.098921595, -0.012501398, 0.00092324361, 0.84888763, -0.63368156 |
| pressure_kPa | autoregressive_ridge_0 | 3.213928 | 1.8110484, -1.2388747, 0.31659857, 0.040754064, -0.031326828, 0.70593605, -0.63615631 |
| humidity_pct | autoregressive_ridge_1 | 2.3512285 | 1.0578806, -0.39660592, 0.05510231, -0.020856539, 0.015298748, 0.85217673, -0.592119 |
| wind_speed_mps | autoregressive_ridge_0 | 0.34960471 | 1.4062346, -0.8518117, 0.10270356, 0.011554796, 0.011256045, 0.53842184, -0.34682738 |
| direction_cos | autoregressive_ridge_0 | -0.020163115 | 1.1967025, -0.54354415, -0.014469252, -0.0018030795, 0.069927592, 0.36286861, -0.16259627 |
| direction_sin | autoregressive_ridge_0 | -0.00051809318 | 1.1632619, -0.49500204, -0.0085181309, 0.072203825, 0.083480854, 0.26036472, -0.12223972 |

### Quantized weather constants

| Channel | Bias Q8 | Lag 0 | Lag 1 | Lag 3 | Lag 6 | Lag 12 | Lag 21 | Lag 24 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| temperature_C | 310 | 20035 | -9335 | 1621 | -205 | 15 | 13908 | -10382 |
| pressure_kPa | 823 | 29672 | -20298 | 5187 | 668 | -513 | 11566 | -10423 |
| humidity_pct | 602 | 17332 | -6498 | 903 | -342 | 251 | 13962 | -9701 |
| wind_speed_mps | 89 | 23040 | -13956 | 1683 | 189 | 184 | 8822 | -5682 |
| direction_cos | -5 | 19607 | -8905 | -237 | -30 | 1146 | 5945 | -2664 |
| direction_sin | 0 | 19059 | -8110 | -140 | 1183 | 1368 | 4266 | -2003 |

Weights above are raw signed Q14 integers; biases are raw signed Q8 integers.

Exact floating-point and quantized coefficients are in [model.json](../../versions/weather_v2/models/model.json).

### Held-out test accuracy

| Target | Selected fixed MAE | Selected fixed RMSE | Persistence MAE | Diurnal MAE |
| --- | --- | --- | --- | --- |
| temperature_C | 0.507906 | 0.730939 | 2.080369 | 0.832280 |
| pressure_kPa | 0.034600 | 0.044638 | 0.135167 | 0.085775 |
| humidity_pct | 2.614292 | 3.685767 | 8.831186 | 3.804237 |
| wind_speed_mps | 0.566878 | 0.750218 | 0.830494 | 0.891217 |
| direction_deg_wind_ge_0.5mps | 18.084598 | 30.201056 | 21.423810 | 35.292273 |

These software direction scores use floating atan2 of quantized predicted components. The separate RTL angle-conversion check bounds the additional CORDIC approximation error; the table does not claim exact end-to-end CORDIC forecast metrics. A frozen-model numerical diagnostic (`versions/weather_v2/reports/numerical_error.csv`) found no signed 18-bit saturation on validation/test windows. On 8,593 non-calm 2025 targets, fixed-component quantization changed the ideal decoded angle by a circular MAE of 0.128151° and maximum 2.101618° relative to floating-point inference. This component-quantization effect is separate from the smaller CORDIC conversion error. Physical clipping counts are recorded in that CSV.

## 4. Weather hardware and verification

Inputs/outputs are signed 18-bit Q8 values, coefficients signed 18-bit Q14, biases signed 32-bit Q8, products 36 bits, and accumulators 48 bits. A 25-frame history supplies the seven selected lags. Humidity outputs are clipped to 0–100%, wind speed to nonnegative values, and direction components to −1…1; signed 18-bit saturation handles remaining overflow.

The parallel architecture uses six arithmetic lanes. The shared architecture uses one multiplier across all channels. Full-system latencies, including the iterative direction converter, are 40 and 156 clocks (0.80 µs and 3.12 µs). Sustained accepted-frame intervals are 23 and 139 clocks. Both versions also have original-DE2 UART wrappers with explicit four-pin maps and generated programming files. Their RTL serial-path tests passed at 50 MHz / 115200 baud with 32 valid frames, eight checked replies, and rejection of an additional corrupt-checksum frame per architecture. Host replay for these wrappers is provided in `versions/weather_v2/software/replay_board.py`. The output angle is unsigned 18-bit degrees Q8; direction validity is separately signalled for zero vectors. Consumers must capture all valid outputs; no output backpressure exists.

Both architectures passed independent C++ DPI-C comparisons over 1,200 accepted frames each: 1,124 forecasts checked, with four pending forecasts canceled by reset. Tests include signed extremes, physical-range samples, gaps, backpressure, and reset during processing. The C++ model uses 64-bit integer sums and explicit floor division. A separate NumPy implementation cross-checked all 264 forecast vectors in the historical-plus-extreme netlist replay file. Exhaustive CORDIC testing covered all 263,169 integer cosine/sine pairs in the clipped range −256…256; maximum circular conversion error was 0.005635°.

Both final weather functional netlists passed 288 accepted frames and 264 checked forecasts at 50 MHz. The replay covers historical samples and signed extremes. The final netlist manifests record SHA-256 hashes of each simulated netlist and the input/reference vectors; the completion audit checks these against the current files.

## 5. Measured Cyclone II implementation

All projects use the same target device and 20 ns clock. Core projects have provisional 2 ns maximum / 0 ns minimum synchronous I/O delays and default output loading. The pinned UART wrapper instead treats external UART/reset as asynchronous signals with synchronization-path exceptions. These are declared implementation assumptions, not characterized board delays.

| Design | LE | Registers | Logical memory bits | M4K blocks | 9-bit multiplier elements | Slow Fmax (MHz) | Setup slack (ns) | Hold slack (ns) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Temperature speed | 279 | 254 | 288 | 2 | 4 | 113.56 | 11.194 | 0.215 |
| Temperature resource | 645 | 547 | 0 | 0 | 2 | 125.96 | 12.061 | 0.236 |
| Temperature DE2 UART | 516 | 377 | 336 | 3 | 4 | 173.16 | 14.225 | 0.215 |
| Weather parallel | 5,068 | 3563 | 0 | 0 | 12 | 78.38 | 7.242 | 0.215 |
| Weather shared | 6,000 | 3183 | 0 | 0 | 2 | 73.2 | 6.339 | 0.215 |
| Weather DE2 parallel UART | 5,568 | 3941 | 0 | 0 | 12 | 81.84 | 7.781 | 0.215 |
| Weather DE2 shared UART | 6,504 | 3565 | 0 | 0 | 2 | 77.44 | 7.086 | 0.215 |

### SDF timing simulation at 50 MHz

| Design | Acceptance | Inputs / forecasts |
| --- | --- | --- |
| temperature_speed | PASS | 4096 / 4072 |
| temperature_resource | PASS | 4096 / 4072 |
| weather_speed | PASS | 288 / 264 |
| weather_resource | PASS | 288 / 264 |

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

## 8. Interpretation of the forecasting problem

The system estimates conditions three hours after the most recent hourly observation. An hourly sample interval describes the environmental data; the FPGA can process recorded observations much faster than one sample per hour. Similarly, a three-hour prediction horizon is not three hours of hardware latency.

The FPGA implements inference using constants fitted offline. It does not solve the OLS normal equations, train a neural network, acquire measurements from a sensor, or call a weather API. The host prepares data and sends samples over UART. This division is deliberate: training is a software task, while arithmetic, history management, output alignment, and communication form the hardware task.

### Why the temperature model stores a 25-sample window

The equation needs the current temperature and values at offsets 3, 21, and 24. Only selected taps participate in the arithmetic, but a sequential hourly input stream must retain or recover the older observations. A 25-sample window makes the required history available at each accepted sample. Unused cycles do not shift history; a history index represents an accepted observation, not an arbitrary FPGA clock.

The first 24 accepted samples produce no forecast. The 25th provides a complete history window. With 128 accepted samples and no reset, 104 forecasts are expected. Reset discards history eligibility, so another warm-up is required.

### Meaning of the two baselines

For a forecast made at time t with target t+3:

- Persistence predicts the current observation: predicted x(t+3) = x(t).
- Diurnal persistence predicts the observation at the target hour on the previous day: predicted x(t+3) = x(t−21).

These are project evaluation references. They establish whether the trained model improves on simple forecasts using the same time-aligned target windows. They are not requirements attributed to the instructor or numerical results copied from another paper. The temperature OLS equation starts from the diurnal value and adds learned corrections based on recent and previous-day changes.

### Accuracy definitions

MAE is the average absolute difference between prediction and target. RMSE is the square root of the average squared difference and gives greater weight to large errors. Both retain the target's physical unit. Lower values are better on the same dataset, forecast horizon, and target subset.

Direction error uses the shorter distance around the circle: a prediction of 359° against a 1° target has a 2° error. Direction scores exclude targets below the declared 0.5 m/s wind threshold because direction in near-calm conditions is less informative. This evaluation mask does not remove low-speed inputs from the RTL interface.

## 9. Fixed-point implementation decisions

A raw Q8 value represents raw_integer / 256; its resolution is 1/256 = 0.00390625 in the channel's unit. A Q14 coefficient represents raw_integer / 16384. The report states total widths explicitly because Q-format naming conventions can differ over whether the sign bit is counted.

For the temperature core, the 17-bit differences preserve subtraction of two signed 16-bit samples. Multiplication by signed 16-bit coefficients produces 33-bit terms. The widened accumulator combines scaled terms before the final arithmetic right shift and signed saturation. Keeping the intermediate widths avoids overflow that would otherwise occur before the final output check.

For the weather cores, each selected channel uses seven signed products plus bias in a 48-bit accumulator. The implementation preserves the selected lag order and coefficient association. The resource design changes the schedule of these operations, not their numerical definition.

Coefficient conversion uses the specified nearest/half-away-from-zero rule. Final output scaling uses floor semantics, including negative values; a C++ integer division that truncates toward zero would not be an equivalent reference. The independent C++ reference handles this distinction explicitly.

There are three different error questions:

1. Forecast error compares a prediction with the observed future environmental value.
2. Quantization error compares fixed-point inference with floating-point inference using the same trained model.
3. RTL implementation error compares hardware arithmetic with the bit-exact integer reference.

A zero RTL mismatch count does not mean perfect weather forecasts. Likewise, a small arithmetic quantization error does not establish that the chosen forecasting model is optimal. The measured forecast and quantization tables answer different questions.

### Circular direction implementation

Angles cross the 0°/360° boundary, so fitting angle values directly can produce poor averages. Version 2 instead predicts cosine and sine separately and reconstructs the angle with iterative vectoring CORDIC. The host computes input components; the RTL computes the output angle.

The reconstructed angle is unsigned degrees with eight fractional bits. A zero predicted vector returns angle zero with the defined flag cleared; zero degrees by itself is a valid north-referenced angle and cannot represent undefined direction without this flag. The CORDIC is separately tested against ideal angle conversion. Its small conversion error must be distinguished from quantization of the predicted components and the much larger forecasting error.

## 10. Architecture and interface comparison

| Property | Temperature speed | Temperature resource | Weather parallel | Weather shared |
| --- | --- | --- | --- | --- |
| Input observation | One temperature | One temperature | Six simultaneous channels | Six simultaneous channels |
| Warm-up | 24 accepted samples | 24 accepted samples | 24 accepted frames | 24 accepted frames |
| Full output latency | 5 clocks | 9 clocks | 40 clocks | 156 clocks |
| Latency at 50 MHz | 100 ns | 180 ns | 0.80 µs | 3.12 µs |
| Initiation interval | 1 clock | 10 clocks | 23 clocks | 139 clocks |
| Arithmetic organization | Parallel correction multipliers | Shared multiplier | Six channel lanes | One shared channel multiplier |
| Output backpressure | Consumer captures valid result | Consumer captures valid result | Consumer captures valid result | Consumer captures valid result |

An input transfer occurs only when both sample_valid and sample_ready are asserted at the accepting clock edge. Latency counts from that edge. The initiation interval describes how frequently the core can accept a new input in sustained operation; it is not the same as latency.

At 50 MHz, the intervals correspond to theoretical input rates of 50 million, 5 million, approximately 2.174 million, and approximately 0.360 million observations/s respectively. These are core-level schedule limits. The serial interface limits practical board traffic to a much lower rate; host software must obey the stop-and-wait protocol.

The shared designs reduce multiplier use, but the fitted tables show higher LE counts than their parallel counterparts. Sharing introduces multiplexing, indexing, control, and different history organization. A defensible comparison therefore reports multipliers, logic, registers, memory, timing, and throughput separately rather than describing the shared implementation as universally smaller.

## 11. UART transport and board integration

The temperature request is `AA 55 01 02 TEMP_H TEMP_L CHK`; its reply is `AA 55 81 02 FORECAST_H FORECAST_L CHK`. The two-byte signed values use eight fractional bits and big-endian byte order. The XOR checksum covers type, length, and payload, excluding the two synchronization bytes. Each request and reply is seven bytes.

The weather request has synchronization bytes `AA 55`, type `02`, length `12` hexadecimal, six signed three-byte values, and checksum: 23 bytes total. The reply uses type `82`, length `16` hexadecimal, six three-byte predictions, a three-byte unsigned direction angle, one direction-defined byte, and checksum: 27 bytes total. The six-channel order is temperature, pressure, humidity, wind speed, cosine, sine. Signed 18-bit values must be canonically sign-extended to 24 bits for transmission.

Both use 115200 baud, 8 data bits, no parity, and one stop bit. After warm-up, the host waits for the complete reply before sending the next observation. Warm-up inputs produce no reply. Sending unrestricted continuous traffic is outside the checked board protocol.

| Board signal | Original-DE2 package pin | Purpose |
| --- | --- | --- |
| CLOCK_50 | N2 | 50 MHz board clock |
| KEY0_N | G26 | Active-low reset button |
| UART_RXD | C25 | Host-to-FPGA serial input |
| UART_TXD | B25 | FPGA-to-host serial output |

The wrapper synchronizes asynchronous inputs and uses timing exceptions for the asynchronous interface paths. These exceptions do not establish the electrical correctness of an arbitrary external connection. The original-DE2 DB9 interface uses RS-232 electrical levels; USB-Blaster provides JTAG programming and is not the UART data link. The physical board revision and pin mapping must be confirmed before programming.

## 12. Files delivered and changes made

The temperature RTL and DPI-C infrastructure already existed at the start of this implementation phase. This work audited and verified those cores, corrected their checked-in coefficient files to the saved trained model, added target-specific Quartus projects and a minimal pinned board wrapper, and extended implementation evidence. It does not claim that the entire temperature design was newly authored in this phase.

| Area | Main artifacts | Purpose |
| --- | --- | --- |
| Temperature coefficients/specification | `hardware/speed_optimized/coeffs.txt`, `hardware/resource_optimized/coefficients.txt`, `docs/specs/` | Align both architectures with the trained constants and describe offline training accurately |
| Temperature fit and board projects | `hardware/quartus/speed`, `resource`, `de2_temperature` | Compile the two cores and the pinned UART system for Cyclone II |
| Temperature evaluation | `scripts/evaluate_temperature.py`, `make_temperature_historical_vectors.py` | Audit saved coefficients; quantify accuracy and quantization; generate full-year C++ reference replay |
| Temperature netlist and physical replay | `scripts/run_temperature_netlist.py`, `replay_temperature_board.py` | Strict functional replay and prepared serial-board checker |
| Weather data/model pipeline | `versions/weather_v2/software/` | Fetch data, train/select candidates, evaluate fixed-point effects, generate RTL and reference vectors |
| Weather saved model | `versions/weather_v2/models/model.json` | Equations, selected candidates, exact weights/biases, quantized constants, split counts, data identity |
| Weather RTL | `versions/weather_v2/rtl/` | Parallel/shared forecasts, iterative direction conversion, output alignment, UART wrapper |
| Weather verification | `versions/weather_v2/tb/` and software runners | C++ DPI-C, exhaustive direction, netlist, and UART checks |
| Weather implementation | `versions/weather_v2/quartus/` | Two core projects and two pinned original-DE2 board projects |
| Vendor timing simulation | `scripts/run_modelsim_timing.py`, `modelsim_env.sh` | Original SDF replay, vendor library mapping, transcript checks, serialization, result hashes |
| Reporting and acceptance | `scripts/build_implementation_report.py`, `audit_delivery.py`, `docs/reports/` | Collect measured evidence, preserve hashes, distinguish completed gates from missing board results |

Three board programming files are recorded in `programming_files_manifest.json`: temperature, weather parallel, and weather shared. Their physical_tested fields remain false. Generated build outputs and downloaded datasets are generally ignored by Git; publishing source files alone does not mean all local binaries and datasets will be uploaded. Reproduction requires the documented toolchain and data pipeline.

## 13. Verification strategy and evidence limits

The verification is layered so a forecasting problem is not confused with an arithmetic, scheduling, communication, or implementation problem:

1. Audit the saved model and chronological dataset windows.
2. Evaluate floating-point forecasts and simple baselines on identical targets.
3. Evaluate fixed-point numerical effects without reselecting the model on test data.
4. Compare RTL with an independent C++ integer model through DPI-C, including reset, stalls, extremes, warm-up, and output ordering.
5. Check the complete UART serialization and framing path at the actual clock and baud settings.
6. Compile for the actual FPGA and inspect resources, setup/hold timing, and unconstrained paths.
7. Replay the functional mapped netlist and the SDF-annotated fitted timing netlist.
8. Program and check the physical board when it becomes available.

Paired architectures are compared by accepted-sample index because their clock latencies differ. Reset-aborted transactions are tracked rather than treated as missing predictions. The strict temperature file reader rejects malformed rows and coefficient-header mismatches; a successful run must consume the intended replay, not silently skip difficult records.

The completion audit verifies accepted SDF artifacts against their recorded hashes and checks both successful annotation and the full scoreboard marker. It deliberately remains INCOMPLETE while physical replay logs are missing. The evidence snapshot preserves Quartus reports and simulation transcripts; it is not a formal proof of all possible input sequences.

The SDF weather replays use 288 frames and 264 forecasts, including historical values and signed extremes. They do not replay the complete 2025 weather test set in gate-level simulation. The temperature full-year check is an RTL/DPI-C replay; the temperature gate-level timing check uses the separate 4,096-input replay. Those coverage scopes must not be interchanged in a presentation.

## 14. Reproduction sequence

Run commands from the repository root unless stated otherwise. The commands below describe rebuilding the work; the reported results come from the saved, inspected evidence. Regeneration after changing software dependencies or model-selection settings can change coefficients and requires rebuilding and verifying the affected RTL.

### Software and model checks

```bash
.venv/bin/python scripts/evaluate_temperature.py
.venv/bin/python scripts/make_temperature_historical_vectors.py
.venv/bin/python versions/weather_v2/software/fetch_weather.py
.venv/bin/python versions/weather_v2/software/train_models.py
.venv/bin/python versions/weather_v2/software/generate_rtl.py
.venv/bin/python versions/weather_v2/software/generate_angle.py
.venv/bin/python versions/weather_v2/software/make_vectors.py
.venv/bin/python versions/weather_v2/software/evaluate_numerics.py
```

Use `versions/weather_v2/software/requirements.txt` for the recorded Python dependencies. Training is offline; the board uses the generated constants. Fetching NASA data requires network access or the retained local cache.

### RTL verification

```bash
.venv/bin/python hardware/tb/run_tests.py --file-coefficients \
  --model software/models_cpp/model.json --matrix \
  --speed-latency 5 --resource-latency 9 \
  --rtl hardware/speed_optimized/temp_predictor_speed.v \
        hardware/resource_optimized/temp_predictor_resource.v
.venv/bin/python versions/weather_v2/software/run_verification.py
.venv/bin/python versions/weather_v2/software/run_uart.py
```

The exact additional historical replay arguments are described in `hardware/tb/README.md`; use the generated `hardware/tb/build/historical/temperature_2025.txt` as the `--vectors` file in a separate build directory. Do not use the behavioral selftest option as evidence for the production RTL.

### Quartus and netlist verification

Compile `predictor` in each temperature core directory and `temperature` in the temperature board directory. Compile `weather` in each weather core directory and `weather_board` in each weather board directory:

```bash
quartus_sh --flow compile predictor
```

That command is an example to run inside a temperature core project directory; select the project name appropriate to the directory as stated above. Then, from the repository root:

```bash
.venv/bin/python scripts/run_temperature_netlist.py
.venv/bin/python versions/weather_v2/software/run_netlist.py
source scripts/modelsim_env.sh
.venv/bin/python scripts/run_modelsim_timing.py --design temperature_speed
.venv/bin/python scripts/run_modelsim_timing.py --design temperature_resource
.venv/bin/python scripts/run_modelsim_timing.py --design weather_speed
.venv/bin/python scripts/run_modelsim_timing.py --design weather_resource
.venv/bin/python scripts/build_implementation_report.py
.venv/bin/python scripts/audit_delivery.py
```

The timing runner serializes sessions and rejects timing violations or a missing scoreboard PASS. Simulator exit status alone is insufficient. The detailed [hardware handoff](HARDWARE_HANDOFF.md) gives programming and serial replay commands; those require hardware access and have not been executed successfully on a physical board here.

## 15. Conclusions supported by the evidence

Both versions are implemented for EP2C35F672C6, fit on that device, meet the declared 50 MHz static timing constraints, and pass their functional and SDF timing replays. The trained models improve on the evaluated simple baselines on the specified held-out dataset. Fixed-point effects are measured separately, and the two architecture families expose a quantified multiplier/logic/throughput tradeoff.

The available evidence does not yet establish that a physical DE2 has been programmed and operated successfully. It also does not establish optimal forecasting over all possible models, accuracy at other locations or seasons, power consumption, live sensor integration, or measured physical-board maximum frequency. Those claims would require additional evidence.

The next acceptance step is concrete: confirm the board revision, program each pinned board wrapper, reset it, replay 128 observations, capture 104 matching replies per wrapper, and retain the resulting CSV logs. The supplied host tools and programming-file manifest are prepared for that step.
