# Verification and Acceptance Report

Report date: 24 October 2026 (Asia/Ho_Chi_Minh).

All four core SDF timing simulations have passed at 50 MHz. The seven Quartus projects meet the declared static timing constraints. The overall project remains incomplete because no physical-board replay has been performed. This report summarizes the evidence; it does not replace the full [implementation report](IMPLEMENTATION_REPORT.md).

## Verification layers

| Check | Scope | Observed result | Limit |
| --- | --- | --- | --- |
| Temperature C++ DPI-C matrix | Both production RTL cores, five coefficient configurations | PASS; paired replay matches 4,072 outputs per configuration | Finite directed/random traffic, not formal proof |
| Temperature historical replay | Both cores, full 2025 target windows | PASS; 8,781 accepted samples, 8,757 matched forecasts | RTL/DPI-C, not full-year gate-level replay |
| Temperature functional netlists | Two mapped core netlists, strict record reader | PASS; 4,096 inputs, 4,072 forecasts each | No propagation delays |
| Temperature SDF timing netlists | Two fitted cores, original max SDF, 20 ns clock | PASS; 4,096 inputs, 4,072 forecasts each | Core-level replay |
| Temperature UART RTL | Pinned-wrapper logic at 50 MHz / 115200 baud | PASS; 40 inputs, 16 replies | Simulated UART, not electrical board validation |
| Weather C++ DPI-C | Both six-channel architectures | PASS; 1,200 accepted frames, 1,124 forecasts checked each | Reset-aborted work tracked separately |
| Weather independent reference check | C++ integer model against NumPy | PASS; 264 forecast vectors | Selected finite replay |
| Direction conversion | Every integer component pair from −256 through 256 | PASS; 263,169 pairs; max circular error 0.005635° | Conversion only; not weather forecast accuracy |
| Weather functional netlists | Both full forecast cores including CORDIC | PASS; 288 inputs, 264 forecasts each | No propagation delays |
| Weather SDF timing netlists | Both fitted cores, original max SDF, 20 ns clock | PASS; 288 inputs, 264 forecasts each | Observe at 9 ns after clock; no full-board SDF claim |
| Weather UART RTL | Both wrappers at 50 MHz / 115200 baud | PASS; 32 valid frames, 8 replies, corrupt checksum rejected | Simulated transport |
| Quartus compilation/static timing | Two temperature cores, one temperature wrapper, two weather cores, two weather wrappers | PASS; EP2C35F672C6, nonnegative setup/hold, zero unconstrained I/O paths | Declared I/O budgets and CDC exceptions apply |
| Physical board replay | Three pinned board wrappers | NOT RUN | Board unavailable on this computer |

## Evidence-based acceptance checklist

The following is a snapshot of `COMPLETION_AUDIT.json`. Its timestamp and hashes describe the checked state; rerun `python3 scripts/audit_delivery.py` after changing RTL, models, testbenches, or implementation artifacts.

Audit timestamp (UTC): 2026-10-24T05:24:47.217477+00:00

| Requirement | Status | Evidence path relative to repository |
| --- | --- | --- |
| Temperature coefficients: hardware/speed_optimized/coeffs.txt | PASS | `hardware/speed_optimized/coeffs.txt` |
| Temperature coefficients: hardware/resource_optimized/coefficients.txt | PASS | `hardware/resource_optimized/coefficients.txt` |
| Temperature coefficients: hardware/quartus/de2_temperature/coeffs.txt | PASS | `hardware/quartus/de2_temperature/coeffs.txt` |
| temperature speed fit/timing at 50 MHz | PASS | `hardware/quartus/speed/output_files/predictor.sta.rpt` |
| temperature shared fit/timing at 50 MHz | PASS | `hardware/quartus/resource/output_files/predictor.sta.rpt` |
| temperature board fit/timing at 50 MHz | PASS | `hardware/quartus/de2_temperature/output_files/temperature.sta.rpt` |
| weather parallel fit/timing at 50 MHz | PASS | `versions/weather_v2/quartus/speed/output_files/weather.sta.rpt` |
| weather shared fit/timing at 50 MHz | PASS | `versions/weather_v2/quartus/resource/output_files/weather.sta.rpt` |
| weather parallel board fit/timing at 50 MHz | PASS | `versions/weather_v2/quartus/de2_speed/output_files/weather_board.sta.rpt` |
| weather shared board fit/timing at 50 MHz | PASS | `versions/weather_v2/quartus/de2_resource/output_files/weather_board.sta.rpt` |
| Temperature DPI-C coefficient matrix | PASS | `hardware/tb/regression_current.log` |
| Temperature full-year historical DPI-C replay | PASS | `docs/reports/temperature_historical_dpi.txt` |
| Temperature speed strict-reader final netlist | PASS | `docs/reports/temperature_speed_functional_final.txt` |
| Temperature speed functional netlist | PASS | `hardware/quartus/speed/netlist_sim.log` |
| Weather speed DPI-C | PASS | `versions/weather_v2/reports/speed_dpi.log` |
| Weather speed UART | PASS | `versions/weather_v2/reports/speed_uart.log` |
| Weather speed final functional netlist | PASS | `versions/weather_v2/reports/speed_final_netlist.log` |
| speed netlist snapshot identity | PASS | `versions/weather_v2/reports/speed_final_netlist_manifest.json` |
| Temperature resource strict-reader final netlist | PASS | `docs/reports/temperature_resource_functional_final.txt` |
| Temperature resource functional netlist | PASS | `hardware/quartus/resource/netlist_sim.log` |
| Weather resource DPI-C | PASS | `versions/weather_v2/reports/resource_dpi.log` |
| Weather resource UART | PASS | `versions/weather_v2/reports/resource_uart.log` |
| Weather resource final functional netlist | PASS | `versions/weather_v2/reports/resource_final_netlist.log` |
| resource netlist snapshot identity | PASS | `versions/weather_v2/reports/resource_final_netlist_manifest.json` |
| Temperature full UART | PASS | `hardware/quartus/de2_temperature/uart_sim.log` |
| Wind direction exhaustive conversion | PASS | `versions/weather_v2/reports/direction_exhaustive.log` |
| Temperature saved-model training audit | PASS | `docs/reports/temperature_evaluation.log` |
| Weather C++ / NumPy reference cross-check | PASS | `versions/weather_v2/reports/reference_crosscheck.log` |
| temperature_speed accepted SDF timing simulation | PASS | `docs/reports/temperature_speed_modelsim_timing.json` |
| temperature_resource accepted SDF timing simulation | PASS | `docs/reports/temperature_resource_modelsim_timing.json` |
| weather_speed accepted SDF timing simulation | PASS | `docs/reports/weather_speed_modelsim_timing.json` |
| weather_resource accepted SDF timing simulation | PASS | `docs/reports/weather_resource_modelsim_timing.json` |
| temperature physical board replay | PENDING | `docs/reports/board_temperature.csv; user confirmed board unavailable on this computer` |
| weather parallel physical board replay | PENDING | `versions/weather_v2/reports/physical_parallel.csv; user confirmed board unavailable on this computer` |
| weather shared physical board replay | PENDING | `versions/weather_v2/reports/physical_shared.csv; user confirmed board unavailable on this computer` |
| Deliverable docs/reports/IMPLEMENTATION_REPORT.md | PASS | `docs/reports/IMPLEMENTATION_REPORT.md` |
| Deliverable docs/reports/HARDWARE_HANDOFF.md | PASS | `docs/reports/HARDWARE_HANDOFF.md` |
| Deliverable versions/weather_v2/models/model.json | PASS | `versions/weather_v2/models/model.json` |
| Deliverable versions/weather_v2/reports/metrics.csv | PASS | `versions/weather_v2/reports/metrics.csv` |
| Deliverable versions/weather_v2/reports/validation_candidates.csv | PASS | `versions/weather_v2/reports/validation_candidates.csv` |

## Accepted SDF evidence

The four `*_modelsim_timing.json` files record the SDF/netlist hashes, actual testbench, reference vectors, and transcript. The audit rehashes these files and checks successful annotation and the complete scoreboard PASS, rather than trusting a manifest label or simulator exit code alone.

The collected transcripts are:

- [Temperature speed](evidence/temperature_speed_modelsim_timing.txt)
- [Temperature resource](evidence/temperature_resource_modelsim_timing.txt)
- [Weather parallel](evidence/weather_speed_modelsim_timing.txt)
- [Weather shared](evidence/weather_resource_modelsim_timing.txt)

The earlier Icarus/XSim timing attempts were not accepted. The initial ModelSim shared-weather mismatch was caused by premature testbench observation, corrected using fitted clock-to-output timing. The final weather runs use the same 20 ns clock, enabled timing checks, and original SDF max delays. A separate ModelSim lock-file failure led to a standalone parallel retry and serialized future runner execution.

## Remaining physical acceptance

For each board wrapper: confirm the original-DE2 revision/pins, program its recorded `.sof`, reset KEY0, replay 128 observations, and retain a CSV containing 104 matching forecasts without timeouts or packet errors. Use the commands in [HARDWARE_HANDOFF.md](HARDWARE_HANDOFF.md). Software-generated values or UART simulation logs cannot substitute for captured board responses.
