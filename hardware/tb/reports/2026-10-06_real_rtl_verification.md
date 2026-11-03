> Historical pre-fix report. The reset-ready failure is resolved; see [strict post-fix verification](2026-10-06_fixed_strict.md).

# Real RTL verification — 6 October 2026

Simulator: Verilator 5.052; live DPI-C C++ integer oracle. Production RTL was not modified.

| Run | Result |
|---|---|
| Speed checked-in coefficients A=4096 B=-2048 C=0, L=5 | Strict FAIL: sample_ready low at first active edge after reset (cycle 4) |
| Resource checked-in coefficients A=8192 B=8192 C=0, L=9 | PASS: 8825 checked forecasts; one reset-aborted transaction; 4072 file replay forecasts; replay output interval 10 clocks |
| Paired five-configuration matrix | Resource passed strict checks; speed passed arithmetic/timing checks only with explicitly diagnostic reset-release grace. Both outputs matched for 4072 replay forecasts per configuration |
| Checker regression | Both behavioral stand-ins pass; all 10 injected faults detected; common replay matches |

Matrix: trained (12214,150,0), (0,0,0), (-32768,32767,-32768), (32767,-32768,32767), (1,-1,-1). Each successful core run checked 8825 forecasts, including directed/random traffic, reset and a 4096-input replay. Only the replay is directly paired by sample index; other phases are independently compared against DPI-C.

The speed source says six register stages and labels L_speed=6, but acceptance edge N produces output at N+5 under the spec convention. Measured speed L=5 (100 ns), II=1; resource L=9 (180 ns), sustained II=10 at the simulated 50 MHz. These do not establish synthesized Fmax, multiplier mapping, UART-wrapper correctness or physical board behavior. Verilator is two-state; X/Z checks need a four-state simulator.

The speed strict failure is caused by ready_r being reset low and raised only at the first non-reset rising edge. Pre-edge ready remains low on that edge. Correct the ready behavior to meet the existing spec, or explicitly agree on a revised startup contract before changing the acceptance checker. The diagnostic option is not a strict acceptance pass.

Reproduction commands and file-coefficient integration are documented in [the testbench README](../README.md). Detailed run logs are stored alongside this report. Isolated compile logs/results remain in /tmp/ols-real-paired and /tmp/ols-real-resource for this session.
