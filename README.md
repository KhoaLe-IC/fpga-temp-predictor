# Cyclone II Temperature and Weather Forecasting

Three-hour-ahead forecasting from hourly samples, implemented as fixed-point RTL for the original DE2's **Cyclone II EP2C35F672C6 at 50 MHz**. Training runs offline; the FPGA performs inference.

Two separate versions are provided:

| Version | Model and outputs | Location |
| --- | --- | --- |
| Temperature | Three-parameter seasonal OLS; pipelined and multiplier-shared architectures | `hardware/speed_optimized`, `hardware/resource_optimized` |
| Weather | Selected seven-tap autoregressions for temperature, surface pressure, relative humidity, wind speed, and circular wind direction; parallel and shared architectures | [`versions/weather_v2`](versions/weather_v2/README.md) |

The projects compile for the target device and have self-checking C++ DPI-C verification, functional netlist replay, and UART simulation flows. **Physical-board operation remains unverified:** the board is unavailable on this computer. All four core SDF timing simulations passed at 50 MHz. Results and earlier simulator probes are documented in the implementation report.

See the [implementation report](docs/reports/IMPLEMENTATION_REPORT.md) for current measured results and limitations, and [completion audit](docs/reports/COMPLETION_AUDIT.json) for outstanding checks. Do not infer physical deployment from a synthesis or simulation pass.

## Temperature model

$$
\widehat T(t+3)=T(t-21)+a[T(t)-T(t-24)]+b[T(t)-T(t-3)]+c.
$$

The trained coefficients are recorded in [`model.json`](software/models_cpp/model.json). Hardware uses `A_Q=12214`, `B_Q=150`, `C_Q=0`: coefficients a/b have 14 fractional bits, while temperatures and c have eight. Both architectures use the same arithmetic and coefficient configuration. The first 24 accepted samples fill history; the first forecast belongs to sample 25. Reset cancels pending results and requires fresh history.

At 50 MHz, acceptance-to-output latency is five clocks for the pipelined core and nine for the shared core. Sustained acceptance intervals are one and ten clocks respectively. The forecast horizon is three hours of sample time, independent of these hardware latencies.

## Reproduce temperature results

Requirements: Python, g++, Verilator with timing/DPI-C support, Icarus, and Quartus II 13.0 SP1 with Cyclone II device support. Quartus executables must be on PATH. Vendor simulation libraries are located relative to the Quartus installation by the temperature netlist script.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r versions/weather_v2/software/requirements.txt
.venv/bin/python scripts/evaluate_temperature.py
```

The evaluation script audits the saved coefficients against the training data and writes chronological validation/test metrics plus separate input/coefficient/floor-shift error measurements. It does not select a new model using test results.

Run the production RTL coefficient matrix:

```bash
.venv/bin/python hardware/tb/run_tests.py --file-coefficients \
  --model software/models_cpp/model.json --matrix \
  --speed-latency 5 --resource-latency 9 \
  --rtl hardware/speed_optimized/temp_predictor_speed.v \
        hardware/resource_optimized/temp_predictor_resource.v \
        hardware/resource_optimized/temp_history_buffer.v \
        hardware/resource_optimized/ols_shared_datapath.v
```

The live C++ bit-exact oracle is in [`hardware/tb/dpi`](hardware/tb/README.md). The floating-point demonstration in `software/models_cpp/c_model_basic.cpp` is a different artifact; it is not the fixed-point scoreboard. Floating-point CSV targets are used for forecast accuracy, not directly as bit-exact RTL expectations.

Compile `predictor` inside both `hardware/quartus/speed` and `hardware/quartus/resource`, then generate and check fresh functional netlists:

```bash
.venv/bin/python scripts/run_temperature_netlist.py
```

For a full-year historical replay, generate C++ reference vectors with `scripts/make_temperature_historical_vectors.py` and pass `hardware/tb/build/historical/temperature_2025.txt` through the runner's `--vectors` option in place of `--matrix`. Use a separate `--build-dir` to preserve the coefficient-matrix artifacts. Details of the verification interface and traffic checks are in [the testbench guide](hardware/tb/README.md).

## FPGA board builds

Pinned original-DE2 projects are available for all three deployable configurations:

| Configuration | Quartus project directory | Project name |
| --- | --- | --- |
| Temperature UART | `hardware/quartus/de2_temperature` | `temperature` |
| Weather parallel UART | `versions/weather_v2/quartus/de2_speed` | `weather_board` |
| Weather shared UART | `versions/weather_v2/quartus/de2_resource` | `weather_board` |

Run `quartus_sh --flow compile <project name>` in the chosen directory. Programming files and build intermediates are ignored by Git; [programming-file hashes](docs/reports/programming_files_manifest.json) identify the locally built artifacts.

All three use CLOCK_50=N2, KEY0_N=G26, UART_RXD=C25, UART_TXD=B25, based on the original-DE2 manual. **Core-only projects have automatic pin placement for measurement and are not board programming images.** The empty legacy `.xdc` placeholder is not the active constraint source.

Follow [the hardware handoff](docs/reports/HARDWARE_HANDOFF.md) for programming and reference-checked serial replay. The DB9 path uses an RS-232 adapter through the onboard MAX232. USB-Blaster provides JTAG programming, not this UART data link. Reset KEY0 after programming; replay samples in chronological order and use the documented stop-and-wait protocol after warm-up.

## Weather version and evidence

The [weather guide](versions/weather_v2/README.md) documents data acquisition, validation-only model selection, exact coefficients/equations, numeric formats, circular direction handling, RTL/DPI-C tests, netlist tests, and board protocols. Frozen model artifacts live in `versions/weather_v2/models`; software evaluation lives in `versions/weather_v2/reports`.

The report collector and audit are reproducible:

```bash
.venv/bin/python scripts/build_implementation_report.py
.venv/bin/python scripts/audit_delivery.py
```

The audit deliberately reports incomplete acceptance while required evidence is missing. Physical-board logs and an accepted SDF simulation must not be fabricated or substituted with software outputs.
