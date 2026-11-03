# Strict RTL verification after reset-ready fix

6 October 2026; Verilator 5.052, live DPI-C C++ integer reference.

The speed core now drives sample_ready from rst_n and gates acceptance with sample_ready. This removes the reset-release bubble and prevents history writes on reset edges. The pipeline comment now correctly states L=5, distinguishing latency from its six register stages. Resource RTL is unchanged.

Strict simulation passed for both production cores with five coefficient configurations: (12214,150,0), (0,0,0), (-32768,32767,-32768), (32767,-32768,32767), (1,-1,-1). No diagnostic reset exception was used. Each run checked 8825 forecasts, including warm-up, continuous/random traffic, signed extremes, reset during pending inference and a 4096-input replay. All 4072 replay outputs matched between variants in each configuration. Speed L=5/II=1; resource L=9/II=10 at simulated 50 MHz.

See [strict log](2026-10-06_fixed_strict.log) and [runner instructions](../README.md). The earlier failure report describes pre-fix RTL. This verifies finite simulation behavior, not synthesized Fmax/resources, UART wrappers or physical board operation.
