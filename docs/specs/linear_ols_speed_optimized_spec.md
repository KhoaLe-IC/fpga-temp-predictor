# Speed-Optimized Linear OLS Temperature Predictor — RTL Specification

**Status:** Proposed implementation specification, 30 September 2026  
**Target:** Original Terasic DE2 board, Cyclone II EP2C35F672C6, 50 MHz system clock. Confirm the label on the physical board before creating pin assignments; DE2-70 and DE2-115 are different targets.  
**Priority:** Maximum inference throughput at the board clock, with a fully pipelined arithmetic path.

## 1. Scope and model

Ordinary least squares (OLS) fitting runs **offline in C++**. The FPGA does not solve the least-squares problem or update coefficients. It performs fixed-coefficient inference on a stream of consecutive hourly temperature samples:

$$
\widehat T(t+3)=T(t-21)+a\,[T(t)-T(t-24)]+b\,[T(t)-T(t-3)]+c.
$$

The three fitted parameters are `a`, `b`, and `c`. The term `T(t-21)` is the same hour on the previous day relative to the `t+3` target. A 25-sample history covers `T(t-24)` through `T(t)`. A forecast is associated with the **latest accepted input sample**, not with the clock cycle when it leaves the pipeline. The future measured value `T(t+3)` is retained by the host for training/scoring and must never enter the inference core.

The host shall send samples in chronological order, with one hour between consecutive samples. A missing hour must be repaired in preprocessing or the stream restarted; `sample_valid` is not a timestamp and cannot signal a gap. FPGA clock cycles measure computation latency, not the three-hour forecast horizon.

## 2. Shared numerical contract

This contract must be identical in the resource-optimized implementation and the C++ bit-exact reference. The listed formats are **provisional** until training-data ranges and fitted coefficients have been checked; a format change requires a versioned update to both specifications and all test vectors.

| Quantity | Representation | Integer interpretation |
|---|---|---|
| Temperature input and output | Signed 16-bit, 8 fractional bits | `Tq = round(T_C × 2^8)` |
| Coefficients `a`, `b` | Signed 16-bit, 14 fractional bits | `A = round(a × 2^14)`, `B = round(b × 2^14)` |
| Offset `c` | Signed 16-bit, 8 fractional bits | `C = round(c_C × 2^8)` |
| Differences `D1`, `D2` | Signed 17-bit integers with 8 fractional bits | `D1 = Tq(t) − Tq(t−24)`; `D2 = Tq(t) − Tq(t−3)` |
| Products | Signed 33-bit integers with 22 fractional bits | `P1 = A × D1`; `P2 = B × D2` |
| Accumulator | Signed 35-bit integer with 22 fractional bits | `S = P1 + P2 + (Tq(t−21) <<< 14) + (C <<< 14)` |

Input and coefficient quantization uses nearest integer, with halfway cases rounded away from zero. The output is `sat16(S >>> 14)`: an **arithmetic** right shift (flooring negative nonintegral values) followed by saturation to `[-32768, 32767]`. No narrowing or rounding is permitted before the 35-bit sum. The C++ reference shall implement signed shifts and saturation explicitly so its result does not depend on implementation-defined C++ behavior. All signed extensions must be explicit in RTL.

If the trained `a` or `b` falls outside the signed Q2.14 range, or input/offset values exceed signed Q8.8, the team must revise the common format rather than silently clip training results. The test report shall distinguish forecast error against real temperatures from fixed-point error against the floating-point model.

## 3. Core interface

The synthesizable module `temp_predictor_speed` exposes:

| Port | Direction | Meaning |
|---|---|---|
| `clk` | input | 50 MHz board clock |
| `rst_n` | input | Active-low **synchronous** reset |
| `sample_valid` | input | `temp_in` is a new hourly sample |
| `sample_ready` | output | Core can accept a sample on this rising edge |
| `temp_in[15:0]` | input | Signed Q8.8 temperature |
| `forecast_valid` | output | `forecast_out` is valid for one cycle |
| `forecast_out[15:0]` | output | Signed Q8.8 prediction |

An input transfer occurs only when `sample_valid && sample_ready` at a rising edge. While out of reset, `sample_ready` shall remain high even after warm-up; this core has no output backpressure. The board wrapper must capture or queue every `forecast_valid` result before serial transmission. Reset discards all in-flight forecasts, clears the accepted-sample count, and makes the 25-sample history invalid; physical clearing of every history register is optional because no result may be emitted before warm-up finishes.

The first prediction is generated for the **25th accepted sample** (`t = 24` when the first is indexed 0). Every accepted sample thereafter produces exactly one prediction, in acceptance order. `forecast_valid` must never assert for the first 24 accepted samples.

## 4. Speed architecture

1. Store the most recent 25 accepted samples in a 25 × 16-bit shift register. After an acceptance, logical taps are `history[0]=T(t)`, `history[3]=T(t−3)`, `history[21]=T(t−21)`, and `history[24]=T(t−24)`.
2. Snapshot the four taps for each accepted sample so later shifts cannot change an in-flight calculation.
3. Compute `D1` and `D2` in **two parallel 17-bit subtractors**.
4. Compute `P1` and `P2` in **two parallel signed 17 × 16-bit multipliers** intended to map to two Cyclone II 18 × 18 embedded multipliers.
5. Register intermediate values and use a balanced, registered addition path for the 35-bit `S` expression. Perform the final shift and saturation in the output stage.
6. Delay the valid bit through the same pipeline. The latency `L_speed` is fixed by RTL, documented in cycles, and checked by the testbench; the design target is **at most 8 clock cycles** from an accepted post-warm-up sample to its output pulse.

The arithmetic pipeline has a target **initiation interval of one clock**: after warm-up it accepts one sample on every clock edge and, once filled, can emit one forecast per clock. This is a **core-only throughput target**. A 115200-baud UART replay is much slower and cannot demonstrate one-forecast-per-clock performance; use simulation or a direct clocked test source for that measurement.

## 5. DE2 integration and build constraints

- Compile for the actual EP2C35F672C6 device in **Quartus II 13.0 SP1**. Later Quartus II 13.1 removed Cyclone II support. Use a 20 ns clock constraint on the board's 50 MHz input. Record the actual board pin map in a `.qsf` file derived from the correct DE2 pin table; the repository's empty `.xdc` placeholder is not a DE2 constraint file.
- Use only one board clock domain for the core. Synchronize the physical reset button before it reaches `rst_n`. The UART receiver/transmitter and host packet framing belong to the board wrapper, not to the forecasting arithmetic contract.
- Hard-coded coefficient constants are permitted for a first implementation. The exact bit patterns and source training run must be saved alongside the bitstream and test vectors. No coefficient change may occur during an in-flight forecast.
- Report **core-only** and **whole-board** synthesis results separately. The core report must state Fmax/critical path, logic elements, registers, embedded multipliers, and M4K blocks. Inspect actual multiplier mapping; source-code `*` operators alone do not prove DSP-block use.

## 6. Verification and acceptance

The C++ fixed-point model is the bit-exact oracle. A self-checking SystemVerilog/Verilog testbench shall compare every valid output, in order, against that model using the same coefficient file and chronological vectors. Required cases: fewer than 25 samples; the 25th sample; continuous one-sample-per-clock traffic; bubbles in `sample_valid`; reset during warm-up and during pipeline operation; negative temperatures; coefficient and temperature limits; intermediate values near output saturation; and at least one long replay across thousands of samples.

This variant is accepted when all of the following are shown, not merely asserted:

- Zero output mismatches, correct output count/order, and correct `forecast_valid` latency.
- One accepted post-warm-up sample per clock and one forecast per clock after pipeline fill in a core-level simulation.
- Quartus timing analysis meets the **50 MHz board clock** (`Fmax ≥ 50 MHz`, or nonnegative worst-case slack under the equivalent 20 ns constraint) for the implemented board build.
- A synthesis report shows no more than two embedded 18 × 18 multipliers for the arithmetic core, or documents any deliberate soft-multiplier mapping and its logic cost.
- A programmed DE2 board replays a host sample sequence and returns predictions that match the bit-exact reference. Board/UART throughput is reported separately.

**Deliverables:** Verilog RTL, coefficient manifest, C++ reference and vectors, self-checking testbench, DE2 `.qsf`/timing constraints, synthesis/timing reports, and a board-demo log. These are requirements; no performance or resource figures are claimed as measured yet.

## Sources

- [Project model and folder structure](../README.md).
- [Terasic original DE2 board documentation and pin table](https://www.terasic.com.tw/cgi-bin/page/archive.pl?CategoryNo=53&Language=English&No=30&PartNo=4).
- [Intel Cyclone II device handbook: EP2C35 resources and embedded multipliers](https://cdrdv2-public.intel.com/654376/cyc2_cii5v1.pdf).
- [Intel Quartus II 13.1 release notes: Cyclone II support removed](https://cdrdv2-public.intel.com/682216/rn_qts_131_dev_support.pdf).
