# Resource-Optimized Linear OLS Temperature Predictor — RTL Specification

**Status:** Revision 2 — clarified implementation and evaluation contract, 2 October 2026  
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

## 7. Implementation and evaluation contract — revision 2

### Cycle accounting and tap capture

Number rising edges consecutively. An eligible sample accepted at edge N shall produce an output visible after edge N+L, where L is the declared fixed latency. Observe input transfers using pre-edge ready/valid, and outputs after sequential updates. Latency includes output registration; it does not include UART transmission. Back-to-back valid output cycles are legal in the speed core. When forecast_valid is low, forecast_out is unspecified.

For a new accepted sample at time t, capture the current input as T(t); before shifting history, old history[2], history[20], and history[23] represent T(t−3), T(t−21), and T(t−24). Alternatively use equivalent next-history logic. Reading old history[3]/[21]/[24] on the same nonblocking-update edge is incorrect. Only accepted samples advance history. Reset has priority over acceptance and output, cancels pending results, and requires 25 fresh acceptances. No acceptance is counted on a reset edge.

### Coefficients and safe integer evaluation

Use signed integer module parameters A_Q, B_Q, C_Q, each restricted to [-32768,32767], unless an explicitly documented integration adapter supplies fixed constants. Coefficients are compile-time constants for revision 2; runtime updates are outside scope. Testbench defaults are synthetic verification coefficients, not trained values. The release manifest shall record floating coefficients, raw quantized integers, fractional-bit counts, training-data/split identifiers, model equation/version and actual latency for each variant.

Sign-extend each anchor and offset to 35 bits **before** shifting left by 14; sign-extend 33-bit products to 35 bits before addition. Shifting a 16-bit operand before widening loses significant bits. Differences range from -65535 to 65535. With every legal input/coefficient, a conservative accumulator magnitude bound is 2×32768×65535 + 2×32768×16384 = 5368643584, below the signed 35-bit limit. Thus intermediate wraparound is forbidden and unnecessary. Apply the floor shift and signed saturation once, at the final output. No arithmetic-format change is authorized by this revision.

### Three separate accuracy checks

1. **RTL correctness:** live SystemVerilog DPI-C calls to the shared C++ integer reference; zero mismatches for both variants, correct reset/handshake accounting, configured fixed latency and initiation interval. Use trained coefficients as well as synthetic corner cases. Behavioral DUT checker self-tests do not verify production RTL.
2. **Numerical error:** on identical test windows, compare the original floating model, the floating model evaluated with quantized inputs/coefficients, and the final integer result converted to degrees Celsius. Report MAE, RMSE, maximum absolute difference and saturation count; distinguish coefficient/input quantization from final floor-shift effects. For nonsaturated outputs, the final floor shift alone introduces error below 1/256 °C; this is not a bound on total quantization error.
3. **Forecast quality:** chronological held-out targets, same windows for all models; report MAE/RMSE in °C against actual T(t+3). Include persistence T(t) and previous-day same-target-hour T(t−21) baselines. Fit coefficients on training data only; choose formats/settings on training/validation data before final test evaluation. Record split boundaries and sample counts. Report both variants' results; identical bit-exact arithmetic must give identical forecasts.

Before a board release, profile training/validation ranges, freeze the coefficient manifest and approve a numerical-error budget in °C. Record it as an explicit project decision, not a number borrowed from unrelated paper datasets. No forecast-accuracy superiority is assumed as an RTL acceptance condition. Explain any saturation on the historical test set.

### Reproducible hardware comparison and lessons from papers

Archive core and wrapper compilation boundaries, Quartus version/device/constraints, optimization settings, coefficient manifest and achieved latency/II. Static-coefficient synthesis may optimize multipliers into logic; report actual mapping rather than promise exact DSP counts. For the two variants, use the same coefficients and mapping policy. Report Fmax as timing-analysis evidence, latency in cycles and ns at 50 MHz, and sustained throughput separately. Do not infer initiation interval from latency alone.

[Royer 2011](ols_fpga_literature_review.md) motivates explicit scheduling, width alignment and sharing; [Ferreira 2019](../papers/willian-de-assis-pedrobon-ferreira-fpga-hardware.pdf), PDF pp. 3–5, illustrates the resource cost of spatial parallelism and hardware-versus-software numerical checks; Prediction Techniques 2022 illustrates reporting numerical error separately from hardware throughput. These are design lessons, not instructions to add FPGA coefficient fitting. Our offline OLS/inference partition remains unchanged.

## 8. Acceptance checklist and report fields

This checklist complements Section 6; it does not replace the architectural or timing requirements. A pending item is not a passing result.

| Check | Required evidence / pass condition |
|---|---|
| Frozen configuration | Coefficient manifest, numerical-format version, input-data identifier and chronological split boundaries |
| Production RTL arithmetic | DPI-C scoreboard log: zero mismatches with the C++ integer reference using trained coefficients and directed corner cases |
| Transaction accounting | Exactly one ordered result for every eligible accepted sample, except transactions canceled by reset; no warm-up output |
| Fixed latency and II | Cycle trace with declared L and measured sustained acceptance interval; meet this variant's ceilings |
| Cross-variant equivalence | Match speed/resource results by accepted-sample index, not wall-clock cycle; zero mismatches on identical streams |
| Numerical accuracy | MAE, RMSE and maximum absolute FPGA-versus-floating difference in °C, saturation count, and the numerical-error budget approved before final test evaluation |
| Forecast accuracy | Held-out MAE/RMSE in °C for floating OLS, fixed OLS, persistence and seasonal baseline; same target timestamps and sample count |
| FPGA timing | Completed timing analysis for the actual target and 20 ns clock, with constrained paths and no unexplained unconstrained core paths |
| FPGA resources | Core-only LE/register/multiplier/M4K counts; document constant optimization and sharing; report wrapper totals separately |
| Board function | Input/output replay log matching the integer reference; serial timing reported separately from core throughput |

### Required report tables

The paired architecture table shall contain device, tool version, coefficient identifier, numerical format, compilation boundary, LE count, register count, multiplier count, M4K count, timing-analysis Fmax, operating clock, latency cycles, latency ns, II cycles and sustained forecasts/s. At the 50 MHz operating clock, latency is 20×L ns and ideal sustained core throughput is 50 million/II forecasts/s; label these as calculated from the verified schedule, not measured UART rates.

The accuracy table shall contain model name, dataset/split identifier, target count, MAE and RMSE in °C, maximum absolute numerical deviation where applicable, and saturation count. Baseline errors are forecast errors, not fixed-point numerical errors. Do not copy error values from paper datasets as our acceptance thresholds.

### Release evidence bundle

Include the two RTL source lists, exact per-core schedules, coefficient manifest, C++ floating and integer models, DPI-C bridge, simulator commands/logs, historical vectors, paired accuracy tables, Quartus project/constraints and compilation reports, plus the board replay log. Record simulator/tool versions and the input/output sampling convention so another group can reproduce the results. Until these artifacts exist, retain targets and pending results rather than filling comparison tables with assumed measurements.

## Sources

- [Project model and folder structure](../../README.md).
- [Terasic original DE2 board documentation and pin table](https://www.terasic.com.tw/cgi-bin/page/archive.pl?CategoryNo=53&Language=English&No=30&PartNo=4).
- [Intel Cyclone II device handbook: EP2C35 resources and embedded multipliers](https://cdrdv2-public.intel.com/654376/cyc2_cii5v1.pdf).
- [Intel Quartus II 13.1 release notes: Cyclone II support removed](https://cdrdv2-public.intel.com/682216/rn_qts_131_dev_support.pdf).
