# Linear OLS core testbenches

Two SystemVerilog entry points implement the existing specifications:

- `tb_temp_predictor_speed.sv` verifies `temp_predictor_speed` against [the speed specification](../../docs/specs/linear_ols_speed_optimized_spec.md).
- `tb_temp_predictor_resource.sv` verifies `temp_predictor_resource` against [the resource specification](../../docs/specs/linear_ols_resource_optimized_spec.md).

They share `ols_tb_driver.sv` for stimulus, a black-box scoreboard, live DPI-C calls to the C++ reference model, and failure reporting. The current production RTL files in `../rtl/` are empty placeholders; **the real DUTs have not been simulated**. `support/behavioral_duts.sv` exists solely to exercise the checkers and is never automatically substituted for real RTL.

## Contract and DUT connection

Both DUTs must expose `clk`, `rst_n`, `sample_valid`, `sample_ready`, signed 16-bit `temp_in`, `forecast_valid`, and signed 16-bit `forecast_out`, with the semantics in the specifications. Reset is synchronous and active low. Input transfers are sampled on a rising edge using **pre-edge** `sample_ready`. Outputs are checked 1 ns after that edge so nonblocking assignments have completed. Stimulus changes on falling edges.

| Setting | Speed default | Resource default |
|---|---|---|
| Raw signed coefficient integers | `A_Q=8192`, `B_Q=3277`, `C_Q=0` | Same |
| Exact accepted-input-to-output latency | 5 clocks | 8 clocks |
| Spec latency ceiling | 8 clocks | 10 clocks |
| Sustained acceptance interval ceiling | 1 clock | 10 clocks |

The default coefficients are **test values** (`a=0.5`, `b=3277/16384`, `c=0`), not trained coefficients. The exact latency defaults are **integration assumptions**, since the specs leave the actual schedules to implementation. Override them to the documented RTL latencies; a latency of `L` means acceptance at edge `N` and output visible after edge `N+L`. The testbench does not learn latency from DUT outputs, which would hide timing errors.

By default the wrappers pass signed-integer parameters named `A_Q`, `B_Q`, and `C_Q` into each DUT. These parameter names are an integration convention added by the testbenches; they were not prescribed by the original specs. Adapt the two short DUT instantiations if your modules use other names. For hard-coded coefficients, compile with `--no-dut-parameters` and ensure the supplied `--a`, `--b`, and `--c` match the RTL exactly. Coefficients remain constant throughout each simulation.

## Run against real RTL

Requires a timing-capable Verilator (the flow is tested with 5.052), `make`, Python 3, and `g++`. Icarus is no longer the runner because this flow requires SystemVerilog DPI-C. From the project root (`fpga-temp-predictor/`), once the DUT files exist:

```bash
python3 hardware/tb/run_tests.py --variant speed \
  --rtl hardware/rtl/temp_predictor_speed.sv \
  --a 8192 --b 3277 --c 0 --speed-latency 5

python3 hardware/tb/run_tests.py --variant resource \
  --rtl hardware/rtl/temp_predictor_resource.sv \
  --a 8192 --b 3277 --c 0 --resource-latency 8
```

List all RTL dependencies after `--rtl`. To check both variants together, use `--variant both --rtl <speed sources> <resource sources>`. Add `--matrix` only when DUT coefficients are parameterized; it recompiles for zero coefficients, both signed-extreme combinations, and small fractional coefficients. Missing/empty RTL files cause an error. No command above uses the behavioral stand-ins.

The runner compiles the SV testbench and `dpi/ols_dpi.cpp` into a Verilator executable. Every accepted sample calls C++ **during simulation**, including directed/random cases and file replay. The C++ model owns the 25-sample history and bit-exact prediction arithmetic; SV owns the expected-output queue, timestamps, protocol checks, and output comparison. A reset edge resets both the C++ context and the SV scoreboard.

The runner also generates a 4,096-sample offline replay using the same C++ model. This replay exercises the file path and checks consistency with live DPI calls; it is not a second independent arithmetic oracle. The behavioral stand-ins retain a separate bounded-width SV arithmetic implementation. The C++ model has hand-calculated self-checks for warm-up, reset, negative floor division, saturation, and the 21.9 °C example. These tests verify fixed-point implementation behavior, not weather forecast quality.

## Optional external C++ or historical vectors

Pass `--vectors path/to/vectors.txt` to replace the generated replay. The text format is:

```text
8192 3277 0
4864 0 0
5000 0 0
...
5120 1 5606
```

The first row contains decimal raw `A_Q B_Q C_Q`. Each subsequent row is `temperature_raw has_forecast expected_raw`, where the first 24 rows have `has_forecast=0` and every later row has `has_forecast=1`. All raw sample and result values must be within signed 16-bit range. There are no headers/comments or literal `...` lines in a real file. A file represents one uninterrupted chronological stream after reset. The testbench checks the vector-file result against its live DPI-C result and then checks the DUT output against that expected result.

The 25th row's taps are current row, 3 rows earlier, 21 rows earlier, and 24 rows earlier. Future measured `T(t+3)` values are not part of this input format. They belong in an accuracy evaluation, not in the RTL oracle. Quantize real temperatures before writing the raw integers, according to the common spec.

## DPI-C interface and manual builds

The shared driver imports the following C functions. Each testbench creates its own opaque `chandle` context, so the two systems can use separate histories and coefficients even when embedded in a larger verification environment.

| Function | Purpose |
|---|---|
| `ols_ref_selftest()` | Validate C++ arithmetic/history anchors before stimulus |
| `ols_ref_create(a,b,c)` | Allocate one model with raw signed coefficient integers |
| `ols_ref_reset(handle)` | Clear accepted-sample history on synchronous reset |
| `ols_ref_push(handle,temp,prediction,sum,scaled)` | Advance by one **accepted** sample; return 0 during warm-up, 1 when forecast is valid, or -1 on invalid arguments |
| `ols_ref_destroy(handle)` | Release the context in the SV `final` block |

Only the `valid && ready` handshake calls `ols_ref_push`; stalled/invalid input cycles never reach the model. It returns a signed 32-bit `int` prediction (restricted to the signed 16-bit result range) and signed `longint` accumulator/scaled values for arithmetic coverage. SV checks the C++ warm-up flag against its own acceptance counter. No future target temperature is passed through DPI.

`dpi/ols_dpi.h` declares the C ABI (`extern "C"`), while `dpi/ols_reference.hpp` contains the reusable C++ model. The bridge catches errors and returns status/null instead of allowing C++ exceptions to cross the simulator boundary. All DPI arguments are scalars; there are no vendor-dependent array layouts. The runner also checks API error handling and isolation between two model contexts using `support/test_dpi_bridge.cpp`. DPI-C and the C++ model are simulation components; they are not included in the FPGA synthesis sources.

For a manual Verilator build from the project root, after supplying real RTL:

```bash
verilator --binary --timing --assert --trace \
  --top-module tb_temp_predictor_speed --Mdir hardware/tb/build/manual_speed \
  -o sim -CFLAGS "-std=c++17" \
  hardware/tb/ols_tb_driver.sv hardware/tb/tb_temp_predictor_speed.sv \
  hardware/rtl/temp_predictor_speed.sv \
  "$(pwd)/hardware/tb/dpi/ols_dpi.cpp"
hardware/tb/build/manual_speed/sim +VECTORS=path/to/vectors.txt +VCD=speed.vcd
```

Use `-GA_Q=<integer> -GB_Q=<integer> -GC_Q=<integer> -GLATENCY=<cycles>` for top-level parameter overrides. Change top/file names for the resource variant. `+VCD` is optional; the runner enables tracing at build time but does not dump waveforms by default.

The same scalar DPI sources can be used in a DPI-capable Questa/ModelSim configuration on Linux. The following is an integration example, **not tested on this host**; simulator installation/license support and compiler ABI must be checked:

```bash
g++ -std=c++17 -fPIC -shared hardware/tb/dpi/ols_dpi.cpp -o libols_ref.so
vlog -sv hardware/tb/ols_tb_driver.sv hardware/tb/tb_temp_predictor_speed.sv \
  hardware/rtl/temp_predictor_speed.sv
vsim -c -sv_lib ./libols_ref tb_temp_predictor_speed -do "run -all; quit -f"
```

Verilator's usual simulation is two-state. The SV code retains unknown-value checks for four-state simulators, but the Verilator self-tests do not prove X/Z detection.

## What is checked

- A 50 MHz clock; no output during the first 24 accepted samples; the first output belongs to sample 25.
- History advances only for `sample_valid && sample_ready`; invalid-bus changes and valid gaps must not alter it.
- Exact signed arithmetic: 17-bit differences, full products, aligned anchor/offset, final floor shift, and signed saturation. The live C++ oracle uses 64-bit integers and explicit floor division, rather than copying RTL truncation/slicing.
- Exact output data, order, count, and configured latency. Missing, extra, early, unknown, or corrupt outputs fail with `$fatal` and a nonzero simulator status.
- Long continuous requests, random input bubbles, isolated requests, positive/negative temperatures, extrema, saturation, and negative fractional accumulators. Arithmetic-bin counts are reported. The default-coefficient run requires both saturation directions and negative fractional results to be exercised.
- Speed `sample_ready` stays high. Under continuous requests, speed acceptance interval is one clock. Consecutive valid output cycles are legal for a full pipeline.
- Resource input remains stable across stalls; the core stays not-ready while a forecast remains unfinished. Its sustained acceptance interval is at most 10 clocks. The driver has a bounded handshake timeout.
- Reset during warm-up and with an in-flight forecast; pending results are canceled, and a fresh 25 accepted samples are required. Accounting checks `eligible = checked + reset_aborted`.

Finite simulation cannot prove all input sequences. Synthesis resource counts, achieved Fmax, and board behavior require separate Quartus/DE2 checks and cannot be established by these testbenches.

## Validate the testbench itself

```bash
python3 hardware/tb/run_tests.py --selftest --matrix
```

This explicit mode compiles `support/behavioral_duts.sv` instead of production RTL. Its timed models use bounded-width shift arithmetic, while live DPI-C computes the reference with floor division. The matrix runs five coefficient configurations for each core and injects five faults per core: corrupt result, early result, missing result, stale valid on reset, and incorrect ready/busy behavior. A fault run passes the checker self-test only if it exits nonzero with the intended diagnostic. The runner prints **“Real DUTs remain unverified”** on success.

Generated executables, vector files, and waveforms belong in `build/`, which is ignored locally.

## Revision 2 checks

Both-variant runs now write `<variant>_<configuration>_results.csv` and compare every replay prediction by its accepted-sample index. Output cycles are recorded but not compared because the architectures have different schedules. Each simulation still independently checks exact latency and live DPI-C predictions. A mismatch, reordered/missing index or empty replay fails the comparison. This comparison covers the common uninterrupted file replay; reset and interrupted traffic remain checked independently against DPI-C in each core.

Reset stimulus now deliberately presents valid data during reset to verify reset priority. The driver also checks that its pending input stays stable across backpressure.

Use trained coefficients directly:

```bash
python3 hardware/tb/run_tests.py --selftest --matrix --model software/models_cpp/model.json
```

`--model` loads floating `a,b,c`, quantizes them using the spec's nearest/half-away-from-zero rule, and rejects values outside the signed 16-bit format. It overrides `--a/--b/--c`. For real RTL, replace `--selftest` with `--rtl <sources>` and provide the actual per-core latency. The model option does not train coefficients or measure forecast MAE/RMSE. CSV predictions are raw Q8.8 values, not ground-truth errors.
