# Resource-Optimized Linear OLS Temperature Predictor — RTL Specification

**Status:** Proposed implementation specification, 30 September 2026  
**Target:** Original Terasic DE2 board, Cyclone II EP2C35F672C6, 50 MHz system clock. Confirm the physical board variant before assigning pins.  
**Priority:** Reduce arithmetic hardware through time-multiplexing while preserving the exact same forecast and numerical behavior as the speed-optimized core.

## 1. Scope and model

OLS training runs **offline in C++** and produces three fixed coefficients `a`, `b`, and `c`. This FPGA design performs inference only:

$$
\widehat T(t+3)=T(t-21)+a\,[T(t)-T(t-24)]+b\,[T(t)-T(t-3)]+c.
$$

The FPGA receives consecutive hourly temperatures up to `t`; it never receives the future measured value `T(t+3)`. A 25-sample history gives `T(t)`, `T(t−3)`, `T(t−21)`, and `T(t−24)`. The host handles missing/duplicate timestamps before streaming samples. The forecast horizon is three **data hours**, while hardware latency is measured in **clock cycles**.

This specification intentionally uses the same model, coefficients, vectors, output representation, and board clock as the [speed-optimized specification](linear_ols_speed_optimized_spec.md). Only the hardware scheduling and resource allocation differ.

## 2. Shared numerical contract

The following provisional formats must be frozen jointly with the speed variant after profiling real data and fitted coefficients. Any necessary format change applies to **both** RTL designs and the C++ reference.

| Quantity | Representation | Exact operation |
|---|---|---|
| `temp_in`, `forecast_out` | Signed 16-bit Q8.8 | `Tq = round(T_C × 2^8)` |
| `a`, `b` | Signed 16-bit Q2.14 | `A = round(a × 2^14)`, `B = round(b × 2^14)` |
| `c` | Signed 16-bit Q8.8 | `C = round(c_C × 2^8)` |
| `D1`, `D2` | Signed 17-bit, 8 fractional bits | `Tq(t)−Tq(t−24)` and `Tq(t)−Tq(t−3)` |
| Products | Signed 33-bit, 22 fractional bits | `P1=A×D1`, `P2=B×D2` |
| Accumulator | Signed 35-bit, 22 fractional bits | `S=P1+P2+(Tq(t−21) <<< 14)+(C <<< 14)` |
| Final output | Signed 16-bit Q8.8 | `sat16(S >>> 14)` |

Quantize real inputs/coefficients to the nearest integer, with halfway cases away from zero. The final `>>> 14` is an arithmetic shift, so negative nonintegral values round toward negative infinity; saturation occurs after that shift. The 35-bit accumulator must be wide enough to avoid intermediate wrap for all legal 16-bit inputs and coefficients. The sequence of additions may differ from the speed core because exact integer addition in this width is associative; truncating either product early is forbidden. C++ must emulate the signed behavior explicitly.

If measured temperature or fitted coefficients do not fit these ranges, update the common contract; do not silently saturate coefficients. Forecasting accuracy versus ground truth and quantization error versus floating point shall be reported separately.

## 3. Core interface and transaction rules

The synthesizable module `temp_predictor_resource` has the same ports and meanings as `temp_predictor_speed`:

| Port | Direction | Meaning |
|---|---|---|
| `clk` | input | 50 MHz clock |
| `rst_n` | input | Active-low synchronous reset |
| `sample_valid` | input | A new signed Q8.8 hourly sample is present |
| `sample_ready` | output | Core can accept it on this rising edge |
| `temp_in[15:0]` | input | Signed 16-bit Q8.8 temperature |
| `forecast_valid` | output | One-cycle pulse for a completed forecast |
| `forecast_out[15:0]` | output | Signed 16-bit Q8.8 result |

Acceptance occurs only on `sample_valid && sample_ready`. The first 24 accepted samples fill history without output. The **25th accepted sample** produces the first forecast after computation completes. Reset clears the accepted-sample count and aborts any active calculation; old history bits need not be physically cleared because they remain invalid until 25 fresh samples arrive.

During an inference operation, `sample_ready=0`. The host or board wrapper must hold a pending sample stable until it is accepted; samples presented while `sample_ready=0` must not be counted or silently dropped. During the initial 24-sample warm-up, the core may accept one sample per clock. Output has no backpressure; the board wrapper shall queue each `forecast_valid` result before UART transmission.

## 4. Resource architecture

1. Use the same **25 × 16-bit register history** and tap ordering as the speed core: after acceptance, `history[0]=T(t)`, `history[3]=T(t−3)`, `history[21]=T(t−21)`, `history[24]=T(t−24)`. Keeping storage identical isolates arithmetic architecture in the comparison. A separate M4K ring-buffer experiment may be added later, but must be reported as a third variant.
2. A finite-state machine performs one forecast at a time. It reuses **one 17-bit subtractor** to form `D1` and `D2`, and **one signed 17 × 16-bit multiplier** first for `A×D1`, then for `B×D2`.
3. Use one signed **35-bit accumulator/addition path**. Sign-extend each product, add the two products and the aligned anchor/offset in any cycle order, then shift and saturate once at the end. Latch operands or hold the history stationary throughout the transaction so a later input cannot alter the calculation.
4. The controller must explicitly separate `IDLE/WARMUP`, difference, multiply, accumulate, output, and reset behavior. No combinational path may span both multiplications in one cycle; no latches or gated clocks are allowed.
5. Publish the exact RTL schedule and fixed latency `L_resource` after implementation. The design target is **no more than 10 clocks** from accepting a post-warm-up sample to `forecast_valid`, with an **initiation interval no greater than 10 clocks** in sustained core-level traffic. These are target ceilings, not measured results.

The resource goal is at most **one** Cyclone II 18 × 18 embedded multiplier in the core. The single multiplier replaces the speed core's intended two parallel multipliers. This may increase control multiplexers and reduce throughput; therefore the resource claim must be supported by the actual Quartus report, not by counting `*` operators in RTL. Logic elements, registers, and M4K use must also be reported. The design should show at least one additional reduction (logic elements or registers) versus the speed core; otherwise the report must accurately describe the saving as **multiplier-only** and identify the control overhead.

## 5. DE2 integration and fair comparison

- Build for the actual EP2C35F672C6 in **Quartus II 13.0 SP1** with a 20 ns clock constraint. Quartus II 13.1 removed Cyclone II support. Use a DE2 `.qsf` pin map, not the repository's empty `.xdc` placeholder. Synchronize the board reset button before the synchronous core reset.
- Use the **same** coefficient bit patterns, 50 MHz clock, history implementation, test vectors, synthesis options, top-level UART wrapper, and tool version for both variants. Produce separate **core-only** reports to avoid UART resources hiding the arithmetic difference, and whole-board reports for the demo.
- Replaying hourly samples over the board's serial link is sufficient for functional demonstration but is not a throughput benchmark. For the comparison, a core-level driver must saturate `sample_valid`, respect `sample_ready`, and count accepted samples and outputs.
- Static coefficients are acceptable for the first bitstream. Save their exact signed 16-bit values, training-data identifier, and quantization version. No coefficient updates are allowed during a transaction.

## 6. Verification and acceptance

Use the **same C++ bit-exact oracle and chronological vectors** as the speed core. The self-checking RTL testbench must compare every forecast bit-for-bit, in order, with accepted-sample indexing. Required cases: warm-up boundary; a continuous input request stream with `sample_ready` stalls; single isolated samples; reset while busy; negative temperatures; maximum/minimum encoded values; accumulator and output-saturation cases; and a long historical replay. Assertions/checks shall prove that no sample is accepted while `sample_ready=0`, no output is produced before 25 accepted samples, and every later accepted sample eventually yields exactly one output.

This variant is accepted when all of the following are demonstrated:

- Zero C++/RTL output mismatches and correct ready/valid/output ordering under stalls and reset.
- The documented fixed latency and a sustained initiation interval **≤10 clock cycles** in simulation.
- Quartus timing analysis meets the **50 MHz board clock** (`Fmax ≥ 50 MHz`, or equivalent nonnegative slack under the 20 ns constraint).
- Core synthesis uses **no more than one** embedded 18 × 18 multiplier, or explicitly documents a soft-multiplier implementation and its logic cost; the same mapping policy is used for the speed-core comparison.
- The comparative report gives logic elements, registers, embedded multipliers, M4K blocks, Fmax, latency, and initiation interval for both cores, and states which resource categories actually decreased.
- A programmed DE2 board replays samples and returns predictions matching the fixed-point reference; serial-link throughput is reported separately.

**Deliverables:** Verilog RTL and FSM schedule, coefficient manifest, shared C++ reference/vectors, self-checking testbench, DE2 `.qsf`/timing constraints, paired synthesis/timing comparison, and a board-demo log. These are proposed requirements; no timing or resource outcome is claimed as already measured.

## Sources

- [Project model and folder structure](../README.md).
- [Terasic original DE2 board documentation and pin table](https://www.terasic.com.tw/cgi-bin/page/archive.pl?CategoryNo=53&Language=English&No=30&PartNo=4).
- [Intel Cyclone II device handbook: EP2C35 resources and embedded multipliers](https://cdrdv2-public.intel.com/654376/cyc2_cii5v1.pdf).
- [Intel Quartus II 13.1 release notes: Cyclone II support removed](https://cdrdv2-public.intel.com/682216/rn_qts_131_dev_support.pdf).
