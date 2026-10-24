# Weather forecasting accelerator — version 2

This separate version extends the temperature project to pressure, relative humidity, wind speed, and wind direction. The prediction horizon is three hours at an hourly sampling interval. The FPGA performs inference; training runs offline.

## Data and model selection

`software/fetch_weather.py` fetches NASA POWER T2M, PS, RH2M, WS10M, and WD10M at 10.8231°N, 106.6297°E for 2021–2025, UTC. Raw responses retain API metadata. Missing timestamps/values remain missing; training requires 25 consecutive valid history samples. Pressure units are kPa, humidity %, wind speed m/s, temperature °C, and direction degrees.

Training labels end before 2024; validation inputs are in 2024 with labels before 2025; test inputs are in 2025. Candidate selection uses validation only. Candidates are persistence, diurnal persistence, seasonal three-parameter OLS, and univariate/multivariate autoregression with several ridge penalties. The current selected models are univariate seven-lag autoregressions with lags 0, 1, 3, 6, 12, 21, and 24 hours. “Selected” means best among the tested candidates.

Direction is modelled using cos(θ) and sin(θ), avoiding the 0°/360° discontinuity. The host supplies these components with the other four variables. An iterative RTL CORDIC reconstructs the output angle. The zero predicted vector produces angle zero with `direction_defined=0`. Direction accuracy is reported using circular error for target wind speeds at least 0.5 m/s; this evaluation threshold is an explicit project choice.

## RTL interface and arithmetic

`weather_system_speed` and `weather_system_resource` accept six simultaneous signed 18-bit inputs, each with eight fractional bits: temperature, pressure, humidity, wind speed, direction cosine, and direction sine. History advances only on `sample_valid && sample_ready`. The first 24 accepted frames fill history.

The parallel design has one arithmetic lane per channel; the resource design shares one multiplier across channels. Both use signed 18-bit Q14 coefficients, signed 32-bit Q8 bias, full 36-bit products, and a 48-bit accumulator. Final scaling floors negative fractional values before range limiting. Humidity is limited to 0–100%, wind speed to nonnegative values, and direction components to −1…1. Remaining output overflow saturates to the signed 18-bit range. Coefficients are generated as static RTL constants; re-training requires regeneration and compilation.

Full-system latency, measured from an accepting rising edge to visible valid output, is 40 clocks for speed and 156 clocks for resource. Their sustained acceptance intervals after warm-up are 23 and 139 clocks respectively. The scalar outputs and unsigned 18-bit Q8 direction angle are aligned to `forecast_valid`. No output backpressure is provided; consumers must capture every valid result. Reset is synchronous, active low, and clears validity/history eligibility.

## Reproduction

From the repository root, install `versions/weather_v2/software/requirements.txt` into a Python environment. Then run:

```bash
python versions/weather_v2/software/fetch_weather.py
python versions/weather_v2/software/train_models.py
python versions/weather_v2/software/generate_rtl.py
python versions/weather_v2/software/generate_angle.py
python versions/weather_v2/software/make_vectors.py
python versions/weather_v2/software/run_verification.py
```

Run `quartus_sh --flow compile weather` inside each `quartus/speed` and `quartus/resource` directory, then run `python versions/weather_v2/software/run_netlist.py` from the repository root. The netlist script currently locates vendor simulation libraries under `/home/khoale/altera/13.0sp1/quartus/eda/sim_lib`; adjust this path for another installation.

The Quartus projects target EP2C35F672C6 at 50 MHz with provisional synchronous core I/O budgets. Their automatically assigned core pins are for implementation measurement; these core-only bitstreams are not board pin maps. Physical-board operation is not established by synthesis or simulation.

`models/model.json` contains the selected equations, floating-point and quantized coefficients, split counts, and input-data hash. `reports/metrics.csv` and `reports/validation_candidates.csv` record software evaluation. Verification evidence and implementation status are summarized in the repository's `docs/reports` directory.

## Original-DE2 UART board projects

`quartus/de2_speed` and `quartus/de2_resource` wrap each architecture in the original-DE2 50 MHz / 115200-baud UART interface. Run `quartus_sh --flow compile weather_board` inside the selected directory. The wrapper uses the same four pins as the temperature board project and tri-states unused pins.

Requests are `AA 55 02 12`, six signed 24-bit big-endian Q8 words (the 18-bit core values sign-extended to 24 bits), and an XOR checksum over the type, length, and payload. Input order is temperature, pressure, humidity, wind speed, direction cosine, direction sine.

Replies are `AA 55 82 16`, the six signed 24-bit Q8 forecasts, an unsigned 24-bit Q8 degree angle, a direction-defined byte, and the same checksum convention. Invalid checksums, lengths/types, and noncanonical sign extension are rejected. The first 24 accepted frames produce no reply. After warm-up, wait for each complete reply before sending another frame.

`python versions/weather_v2/software/run_uart.py` runs both complete UART paths at the real clock and baud settings, including a rejected bad-checksum request. After programming and KEY0 reset, `python versions/weather_v2/software/replay_board.py --port /dev/ttyUSB0` performs physical replay against the C++ generated vectors. Use the actual adapter port; no physical replay pass is claimed until this command succeeds on connected hardware.
