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
