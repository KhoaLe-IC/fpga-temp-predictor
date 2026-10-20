# FPGA Forecasting Project — Milestone Plan

## Objective

Deliver a reproducible FPGA temperature forecasting system with two fixed-point RTL architectures: one optimized for throughput and one optimized for resource sharing. Establish a complete, presentation-ready temperature implementation first, then extend the platform to other weather variables where evaluation supports doing so.

**Final defense target:** 6 November 2026.

This document describes planned work. Checkboxes indicate acceptance criteria to be confirmed with saved evidence; they do not claim that results have already been obtained.

## Milestone Overview

| Milestone | Outcome | Dependencies |
| --- | --- | --- |
| M1 — Audit and implementation baseline | Consistent model, verified RTL, and initial Quartus results | Existing temperature implementation |
| M2 — Temperature on FPGA | Reproducible board demonstration and architecture comparison | M1; board and toolchain available |
| M3 — Humidity extension | Evaluated humidity configuration and FPGA demonstration where compatible | M2 for deployment; software evaluation can start earlier |
| M4 — Additional target and refinement | Evaluated wind-speed candidate and improved system evidence | Stable temperature baseline; M3 where relevant |
| M5 — Defense release | Frozen source, reproducible results, report, slides, and demonstration | M2; completed extensions included as supported by evidence |

## M1 — Audit and Implementation Baseline

### Work

- Review both RTL cores for signedness, intermediate widths, coefficient loading, scaling, rounding, overflow, reset, pipeline control, and sample acceptance.
- Review the SystemVerilog testbenches, DPI-C interface, and C++ reference model. Check that expected results follow the mathematical and numeric specification independently of RTL implementation details.
- Resolve coefficient inconsistencies. Generate both architectures' coefficient files from one documented trained model.
- Freeze the temperature equation, feature delays, sampling interval, forecast horizon, units, chronological data split, and fixed-point contract.
- Reproduce forecast metrics for the floating-point model, fixed-point model, persistence baseline, and diurnal baseline. Select changes using training/validation data; reserve test data for final evaluation.
- Start Quartus compilation early to identify device, initialization, synthesis, and timing-constraint issues while the code review proceeds.

### Acceptance Criteria

- [ ] Both architectures use the same documented coefficient set.
- [ ] Relevant regressions pass after fixes, including reset, warm-up, input gaps, consecutive accepted samples, and arithmetic boundaries.
- [ ] Latency and initiation interval are measured using an explicit cycle-count convention.
- [ ] Forecast metrics have recorded data provenance, split boundaries, units, and reproduction commands.
- [ ] The actual DE2 device and supported Quartus version are confirmed; initial compilation results and remaining blockers are recorded.

## M2 — Temperature on FPGA

### Work

- Complete clock constraints, board pin assignments, reset handling, and UART integration.
- Replay historical hourly temperatures over UART at an accelerated rate. Preserve their sample order and explain that sample time and transmission time are different.
- Capture FPGA predictions and compare them automatically with the fixed-point reference for the identical input stream and coefficients.
- Implement both architectures under comparable device, clock, and tool settings.
- Collect resource utilization, timing results, latency, and initiation interval. Identify whether each measurement covers the predictor core or the complete system.
- Record a demonstration and preserve its input, expected outputs, captured outputs, and programming files.

### Acceptance Criteria

- [ ] Each architecture produces bit-exact reference results for the recorded board replay.
- [ ] Initial history fill and UART/sample acceptance behavior are demonstrated without unexplained dropped or duplicated samples.
- [ ] Both implementations meet the declared operating-clock constraint, or any timing failure is explicitly documented.
- [ ] An architecture comparison reports logic, registers, multiplier/DSP use, memory use, timing, latency, and throughput as available from the target tool.
- [ ] Temperature MAE/RMSE and fixed-point error are reported separately from hardware correctness.
- [ ] A repeatable demonstration and backup recording are ready.

**Checkpoint:** Completion of M2 establishes the core project that can be reported even if extensions remain unfinished. If hardware access is blocked, document the blocker and retain a clearly labeled simulation demonstration; physical-board confirmation remains pending.

## M3 — Humidity Extension

### Work

- Obtain and document humidity data, units, missing-data handling, and chronological evaluation splits.
- Evaluate whether the existing feature structure is suitable; train a separate coefficient set and compare against relevant persistence and seasonal baselines.
- Check coefficient range, intermediate arithmetic range, quantization error, and behavior near the physical 0–100% range.
- Document any clipping or saturation policy and include it in both reference and hardware evaluation.
- Reuse the accelerator where the numeric contract permits. If arithmetic changes are required, update the specification and verification before deployment.

### Acceptance Criteria

- [ ] Humidity results include baseline comparisons and floating-point/fixed-point metrics.
- [ ] Physical-range violations and their handling are reported.
- [ ] The coefficient/configuration loading procedure is documented.
- [ ] Any deployed humidity configuration passes reference comparison on RTL and FPGA.

Retraining the same equation for humidity is a new target configuration. Describe it separately from introducing a different model architecture.

## M4 — Additional Target and System Refinement

### Work

- Evaluate wind-speed forecasting in software, including baseline performance, nonnegative output behavior, and numeric range.
- Deploy wind speed only if the evaluated model is useful and compatible with the available implementation effort.
- Investigate forecast errors, quantization effects, and architecture tradeoffs; prioritize improvements supported by measured evidence.
- Automate the workflow from training and coefficient export through reference generation, RTL verification, board replay, and result summaries.
- Optionally investigate rain probability in software: define the rain event and horizon, select a suitable probability model, and evaluate probability quality before proposing hardware implementation.

### Acceptance Criteria

- [ ] Wind-speed evaluation produces either a validated extension or a documented reason for rejection.
- [ ] Any deployed extension has its own coefficients, data provenance, numeric checks, and verification evidence.
- [ ] Improvements include before/after measurements under comparable conditions.
- [ ] Rain probability, if explored, uses appropriate probability evaluation; clipping an OLS output alone is not treated as proof of a calibrated forecast.

## M5 — Defense Release

### Work

- Freeze a reproducible source revision and record tool versions, model configurations, and commands.
- Assemble the final comparison: forecast accuracy, quantization error, hardware correctness, resource utilization, latency, and throughput.
- Prepare slides covering the problem, equation and training, fixed-point arithmetic, two architectures, verification, FPGA demonstration, measured results, and limitations.
- Label simulation, software evaluation, synthesis, and physical-board evidence explicitly.
- Rehearse the presentation and prepare answers about model selection, history depth, coefficient generation, arithmetic behavior, handshaking, and architecture tradeoffs.
- Preserve a backup demonstration recording and all files needed to reproduce the live demonstration.

### Acceptance Criteria

- [ ] Every numerical claim in the presentation can be traced to a saved artifact.
- [ ] Report and slides match the final implementation and actual training workflow.
- [ ] Source, coefficients, input data references, logs, programming files, and reproduction instructions are organized.
- [ ] The team can explain the key design decisions and limitations without relying on generated text.
- [ ] A complete rehearsal and demonstration recovery procedure are finished.

## Execution and Review

AI assistance may be used for implementation, review, regression execution, report analysis, and documentation. Team reviews occur at milestone checkpoints to confirm assumptions, inspect evidence, and accept results.

Independent tasks can proceed concurrently: RTL/reference review, Quartus integration, and software evaluation. Extensions must not delay completion of the temperature demonstration or the defense release.

Recommended review responsibilities for the three team members:

| Responsibility | Review focus |
| --- | --- |
| RTL and verification | Arithmetic contract, protocol behavior, reference independence, regression evidence |
| FPGA integration | Toolchain, constraints, UART, board outputs, resource and timing reports |
| Modelling and communication | Data splits, forecasting metrics, baselines, reproducibility, report and slides |

Maintain a short evidence record for each accepted milestone: source revision, configuration, commands, artifact locations, result summary, and unresolved limitations.
