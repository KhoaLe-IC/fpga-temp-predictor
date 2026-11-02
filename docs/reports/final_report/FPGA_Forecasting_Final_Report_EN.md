# Fixed point temperature and weather forecasting on Cyclone II FPGA

CE436 Discrete Time Signal Processing and Applications  
Technical implementation and verification report  
Prepared on 2 November 2026  
Physical FPGA verification performed on 28 October 2026

## Abstract

This project implements three-hour-ahead forecasting from hourly environmental observations on the DE2 development board with a Cyclone II EP2C35F672C6 FPGA. The first version uses a three-parameter seasonal ordinary least squares model for temperature. The second version extends the system to temperature, surface pressure, relative humidity, wind speed, and wind direction using seven-lag autoregressive models. Each version has a speed-oriented architecture and an architecture that shares a multiplier.

Training and model selection run offline. The FPGA stores fixed coefficients and performs inference using integer arithmetic. Independent C++ reference models check the RTL through SystemVerilog DPI-C testbenches. Verification also includes functional netlist replay, SDF timing simulation, and physical replay through a USB-Blaster JTAG interface.

All four designs passed physical replay with 128 accepted input samples and 104 checked forecasts per design. SignalTap captured a prediction transaction from each instrumented design. The saved captures contain 512 samples at a 50 MHz acquisition clock, and decoded prediction values match the reference vectors. The shared architectures reduce multiplier usage, although total logic usage depends on the implementation. In the temperature JTAG builds, sharing reduces the multiplier count from four to two 9-bit elements while increasing logic usage from 1,130 to 1,541 LEs.

## 1 Project scope

The system predicts environmental conditions three hours after the latest hourly observation. Its inputs are recorded samples supplied by a host computer. The forecast horizon belongs to the data model; hardware processing takes a small number of clock cycles and does not wait three hours to produce a result.

The implementation contains four designs:

| Version | Architecture | Forecast outputs |
| --- | --- | --- |
| Temperature | Pipelined speed design | Temperature |
| Temperature | Shared multiplier design | Temperature |
| Weather | Parallel arithmetic lanes | Temperature, pressure, humidity, wind speed, wind direction |
| Weather | Shared multiplier across channels | The same weather outputs |

The weather arithmetic operates on six channels because direction is represented by cosine and sine. A CORDIC unit converts the predicted direction components into an angle. The current scope does not include precipitation probability, live sensor acquisition, or coefficient training on the FPGA.

The report uses three implementation boundaries. Core measurements describe the prediction logic. JTAG board measurements include the mailbox and vendor debug transport needed to send samples and read results. SignalTap builds add acquisition hardware for waveform capture. These boundaries have different resource totals and must remain separate in comparisons.

## 2 Data preparation and evaluation

### 2.1 Dataset and chronological split

The weather dataset contains NASA POWER hourly T2M, PS, RH2M, WS10M, and WD10M values for Ho Chi Minh City at latitude 10.8231° N and longitude 106.6297° E, covering 2021 through 2025 in UTC. Pressure is expressed in kPa, humidity in percent, wind speed in m/s, and direction in degrees. NASA POWER provides gridded environmental data, so the reported errors should be interpreted for this dataset and location.

The evaluation separates training, validation, and test periods by time. Training target timestamps end before 1 January 2024. Validation uses 2024 inputs with targets before 2025. Test inputs belong to 2025, and examples whose targets fall beyond the available data are excluded. The resulting counts are 26,253 training examples, 8,781 validation examples, and 8,757 test examples. Each example requires 25 consecutive valid history samples. Missing observations are not silently interpolated.

Model candidates are compared on validation error. The selected coefficients are then frozen before test evaluation. This separation prevents the test period from influencing coefficient fitting or model selection. The saved temperature model has the same three hour horizon and a training target cutoff of 1 January 2024.

### 2.2 Baselines and error metrics

Persistence predicts that the future value will equal the latest observation. The diurnal baseline uses the previous day's observation at the target hour. For a forecast at time t + 3, the previous day target hour is t − 21. These baselines test whether the fitted model improves on simple temporal assumptions.

For N predictions, mean absolute error and root mean square error are:

$$
\mathrm{MAE}=\frac{1}{N}\sum_{i=1}^{N}|\widehat y_i-y_i|.
$$

$$
\mathrm{RMSE}=\sqrt{\frac{1}{N}\sum_{i=1}^{N}(\widehat y_i-y_i)^2}.
$$

Both metrics retain the unit of the target variable. Wind direction uses circular angular distance, which treats 359° and 1° as 2° apart. Direction scores include targets whose wind speed is at least 0.5 m/s. This threshold is a project evaluation choice.

Forecast error, fixed point approximation error, and hardware agreement answer different questions. Forecast error compares a prediction with a future observation. Approximation error compares fixed point inference with floating point inference. Hardware agreement compares RTL or FPGA output with the fixed point reference for the same inputs.

## 3 Temperature forecasting model

### 3.1 Seasonal ordinary least squares model

The temperature predictor uses two differences from past observations and a bias:

$$
\widehat T(t+3)=T(t-21)+a[T(t)-T(t-24)]+b[T(t)-T(t-3)]+c.
$$

The term T(t − 21) supplies the previous day's value at the forecast hour. The first difference measures change from the same hour on the previous day. The second difference measures change during the latest three hours. Ordinary least squares fits a, b, and c by minimizing squared residuals against the training targets.

The stored coefficients are:

| Parameter | Floating point value | Hardware integer | Fractional bits |
| --- | --- | --- | --- |
| a | 0.7454870438526146 | 12214 | 14 |
| b | 0.009149444986888534 | 150 | 14 |
| c | 0.0011295816555433053 | 0 | 8 |

The quantized bias is zero because the fitted value is smaller than one half of a Q8 step. It remains a model parameter even though its deployed integer value is zero. Both temperature architectures use the same coefficient values and numerical rules.

### 3.2 Fixed point arithmetic

Temperature inputs and outputs use signed 16-bit integers with eight fractional bits. A stored integer q represents q / 256 °C. The differences require 17 bits, products require 33 bits, and the final accumulator uses 35 bits. Coefficients a and b have 14 fractional bits, so the final scaling uses an arithmetic right shift. Negative fractional values round toward negative infinity. Overflow at the output saturates to the signed 16-bit range.

History advances only when a sample is accepted. The first 24 accepted samples establish the required history, and accepted sample 25 produces the first forecast. A reset cancels pending results and requires a fresh history window. Although the equation reads only selected lags for one prediction, consecutive requests require a history mechanism that supplies the correct delayed observations each time.

### 3.3 Temperature architectures

The speed design pipelines history access, arithmetic, and output generation. It has five cycles of latency under the RTL scoreboard's observation convention and an initiation interval of one cycle. The shared design schedules the products through one full multiplier. Its latency is nine cycles and its initiation interval is ten cycles. At 50 MHz, the corresponding latencies are 100 ns and 180 ns.

An initiation interval describes how often the core can accept a new input during sustained processing. The host JTAG interface sends transactions much more slowly, so its replay rate does not measure the core's maximum throughput.

### 3.4 Temperature test accuracy

The following results use 8,757 test forecasts in 2025. They come from software evaluation of the saved model and baselines.

| Model | MAE in °C | RMSE in °C |
| --- | --- | --- |
| Floating point OLS | 0.537973 | 0.785961 |
| Fixed point OLS | 0.538017 | 0.785955 |
| Persistence | 2.080369 | 2.732720 |
| Previous day target hour | 0.832280 | 1.187346 |

The mean absolute difference between fixed point and floating point predictions is 0.003161 °C, with a maximum absolute difference of 0.009092 °C. No validation or test prediction saturated the signed 16-bit output. These results show that quantization changes this model's predictions only slightly on the evaluated data. They do not establish accuracy at other sites or under untested weather conditions.

## 4 Weather forecasting extension

### 4.1 Selected models

The weather version evaluates persistence, the previous day baseline, the seasonal three-parameter model, and seven-lag autoregressions with several ridge penalties. The selected models are univariate autoregressions using lags 0, 1, 3, 6, 12, 21, and 24. Each channel follows:

$$
\widehat x(t+3)=\beta_x+\sum_{k=0}^{6}w_{x,k}x(t-\ell_k),\qquad \ell=[0,1,3,6,12,21,24].
$$

Temperature and humidity select ridge penalty 1. Pressure, wind speed, and the direction component pair select penalty 0. These selections are the best candidates within the evaluated set according to validation error. The exact floating point and integer coefficients are retained in the weather model file.

The host converts direction angles into cosine and sine before transmitting the inputs. The FPGA predicts these components and reconstructs the output angle using CORDIC. Angles are wrapped to the range from 0° inclusive to 360° exclusive. A zero predicted vector has an undefined direction flag.

### 4.2 Numerical representation and scheduling

Weather inputs and channel outputs use signed 18-bit Q8 values. Coefficients use signed 18-bit Q14, biases use signed 32-bit Q8, products use 36 bits, and accumulators use 48 bits. The output angle uses unsigned 18-bit degrees with eight fractional bits. Humidity is clipped to the physical range from 0 to 100%, wind speed to nonnegative values, and direction components to the range from −1 to 1.

The parallel implementation has six arithmetic lanes. The shared implementation schedules all channels through one multiplier. Both use a 25-frame history and the same selected models. Including direction conversion, full-system latency is 40 cycles for the parallel design and 156 cycles for the shared design. Their accepted-frame initiation intervals are 23 and 139 cycles. At 50 MHz, full-system latency is 0.80 µs and 3.12 µs, respectively.

### 4.3 Weather test accuracy

| Target and unit | Fixed point MAE | Fixed point RMSE | Persistence MAE | Previous day MAE |
| --- | --- | --- | --- | --- |
| Temperature in °C | 0.507906 | 0.730939 | 2.080369 | 0.832280 |
| Pressure in kPa | 0.034600 | 0.044638 | 0.135167 | 0.085775 |
| Relative humidity in % | 2.614292 | 3.685767 | 8.831186 | 3.804237 |
| Wind speed in m/s | 0.566878 | 0.750218 | 0.830494 | 0.891217 |
| Wind direction in degrees | 18.084598 | 30.201056 | 21.423810 | 35.292273 |

Direction results use 8,593 non-calm test targets and floating point atan2 applied to the quantized predicted components. They therefore describe the selected fixed point component model with ideal angle decoding. CORDIC approximation is checked separately. Exhaustive conversion testing covered 263,169 integer cosine and sine pairs, with a maximum circular conversion error of 0.005635°. The physical replay permits an angle difference of five Q8 degree units, equivalent to 0.01953125°.

The weather temperature model has a lower test MAE than the original three-parameter model on this evaluation. It also uses more lag coefficients and different hardware. The two versions should be compared as different model and implementation choices.

## 5 Verification method

### 5.1 Independent reference models and RTL tests

SystemVerilog drivers generate inputs, apply valid and ready handshaking, and compare outputs with C++ reference calculations through DPI-C. The reference models implement the deployed fixed point rules, including signed arithmetic, scaling, and overflow handling. Scoreboards associate results with accepted samples and check the required output schedule.

The temperature regression covers five coefficient configurations for both architectures. Each paired replay compares 4,072 outputs by accepted-sample index. A full-year historical replay supplies 8,781 hourly observations including history and checks 8,757 forecasts. Weather DPI-C tests accept 1,200 frames per architecture and check 1,124 forecasts, with four pending results canceled by reset. Test cases include signed extremes, input gaps, backpressure, and reset during processing.

### 5.2 Mapped logic and timing checks

Functional netlist simulation checks the mapped logic using vendor atoms. TimeQuest analyzes fitted setup and hold timing under the declared constraints. ModelSim-Altera Starter Edition 10.1d runs the original Quartus timing netlists with maximum SDF delays at a 20 ns clock. These methods cover different failure mechanisms, so their results are recorded separately.

| Predictor core | SDF timing replay inputs | Checked forecasts | Result |
| --- | --- | --- | --- |
| Temperature speed | 4096 | 4072 | PASS |
| Temperature shared | 4096 | 4072 | PASS |
| Weather parallel | 288 | 264 | PASS |
| Weather shared | 288 | 264 | PASS |

Accepted timing runs completed SDF back-annotation, passed their scoreboards, and reported no timing violations. The stored timing manifests identify the netlist, SDF file, vectors, testbench, and transcript using hashes. These runs cover predictor cores. A full SDF replay of the JTAG board interface is not claimed.

### 5.3 JTAG interface verification

A mailbox connects the forecasting core to Quartus In-System Sources and Probes. The source word has 128 bits and the probe word has 256 bits. The host stages input data, toggles a request bit, and waits for an acknowledgement. The mailbox accepts one transaction at a time, preserves the latest forecast for readback, and exposes accepted-input and forecast counters.

The vendor IP synchronizes source outputs to CLOCK_50. The mailbox adds settling cycles before sampling the held payload. Its RTL tests replay 128 inputs and 104 forecasts for every design, then exercise reset cancellation and a fresh 25-input history. Separate host tests use mocked JTAG APIs and deliberately corrupt outputs to check that the host detects mismatches. Mocked tests are kept separate from physical evidence.

## 6 FPGA implementation results

All four JTAG board projects target EP2C35F672C6 with CLOCK_50 constrained to 20 ns. CLOCK_50 uses pin N2 and KEY0_N uses pin G26. The JTAG path uses dedicated device infrastructure. The following fitted results include the predictor, mailbox, and JTAG IP, but exclude SignalTap acquisition hardware.

| Design | LEs | Registers | Memory bits | 9-bit multiplier elements |
| --- | --- | --- | --- | --- |
| Temperature speed | 1130 | 1016 | 336 | 4 |
| Temperature shared | 1541 | 1352 | 0 | 2 |
| Weather parallel | 6253 | 4571 | 0 | 12 |
| Weather shared | 5598 | 4192 | 0 | 2 |

| Design | Fmax in MHz | Setup slack in ns | Hold slack in ns | Operating clock |
| --- | --- | --- | --- | --- |
| Temperature speed | 190.48 | 14.750 | 0.215 | 50 MHz |
| Temperature shared | 139.37 | 12.825 | 0.215 | 50 MHz |
| Weather parallel | 79.74 | 7.459 | 0.215 | 50 MHz |
| Weather shared | 79.23 | 7.378 | 0.215 | 50 MHz |

All four fits completed successfully with nonnegative setup and hold slack. Fmax is a static timing estimate from the fitted design. Physical functional tests operated at 50 MHz; they did not sweep the board clock to measure the maximum operating frequency.

Two 9-bit multiplier elements correspond to one full 18 × 18 multiplier resource on this target. Temperature sharing reduces this resource from two full multipliers to one, but its control and history implementation increase the LE and register totals. Weather sharing reduces the multiplier element count from 12 to 2, and the JTAG wrapper fit also uses fewer LEs and registers. These outcomes support reporting each resource separately instead of assigning a single area label to the shared designs.

SignalTap instrumentation adds acquisition memory, trigger logic, and routing load. Its builds are used for waveform evidence. The table above retains the uninstrumented JTAG results used to compare the architectures.

## 7 Physical verification on DE2

### 7.1 Programming and checked replay

The USB-Blaster chain identified an EP2C35 device with JTAG ID 0x020B40DD. Each JTAG programming file was loaded separately, and the host checker verified the design identity before sending samples. A JTAG reset clears counters and history, so replay does not depend on a manual reset-button sequence.

| Design | Accepted inputs | Checked forecasts | Physical JTAG replay |
| --- | --- | --- | --- |
| Temperature speed | 128 | 104 | PASS |
| Temperature shared | 128 | 104 | PASS |
| Weather parallel | 128 | 104 | PASS |
| Weather shared | 128 | 104 | PASS |

The first 24 accepted inputs fill history. Every subsequent input in this replay produces one forecast, giving 128 − 24 = 104 checked forecasts. Temperature and six weather component outputs agree bit for bit with the fixed point reference. Weather angle output is checked using the stated tolerance and the direction-defined flag.

Temperature replay vectors include directed synthetic values and arithmetic corner cases. The physical replay establishes correct hardware inference for those inputs. The historical software evaluation in Sections 3 and 4 establishes forecast accuracy against future observations. The instrumented SignalTap builds also passed a separate 128-input and 104-forecast physical replay for every architecture.

### 7.2 SignalTap capture checks

Each capture uses CLOCK_50 at 50 MHz, a depth of 512 samples, and a rising forecast-valid trigger at capture index 256. The saved native STP files contain actual acquisition data. A decoder checks that the input matches the first forecast-producing reference transaction, that a valid output occurs, and that its prediction matches the reference value.

| Design | Input acceptance index | Forecast-valid index | Sample separation | RTL post-edge latency |
| --- | --- | --- | --- | --- |
| Temperature speed | 250 | 256 | 6 | 5 cycles |
| Temperature shared | 246 | 256 | 10 | 9 cycles |
| Weather parallel | 215 | 256 | 41 | 40 cycles |
| Weather shared | 99 | 256 | 157 | 156 cycles |

The raw capture samples signal values at the acquisition edge. RTL scoreboards observe registered results after the edge updates. The capture separation is one sample greater than the documented post-edge latency under these observation conventions. Both the raw indices and the RTL latency definition are retained so the waveform is not presented as a different latency measurement.

For the captured temperature transaction, the valid result is hexadecimal 7FFF, which is the signed 16-bit positive saturation limit. This directed case checks arithmetic behavior. It is not a typical ambient temperature forecast. Output bus changes during cycles with forecast_valid equal to zero do not represent additional valid predictions.

### 7.3 Saved waveform figures

The following plots decode the control signals directly from the saved physical SignalTap CSVs. They preserve the acquisition sample indices. Native Quartus screenshots with the complete input and output buses are linked in Appendix A.

![Temperature speed SignalTap waveform](figures/temperature_speed.png)

Figure 1. Temperature speed capture with sample-valid, ready, and forecast-valid signals. Time-axis labels are samples relative to the trigger; one sample represents 20 ns.

![Temperature shared SignalTap waveform](figures/temperature_resource.png)

Figure 2. Temperature shared capture. The longer input-to-valid interval is visible in the same trigger-centered view.

![Weather parallel SignalTap waveform](figures/weather_speed.png)

Figure 3. Weather parallel control capture. The full prediction, including direction angle, becomes valid at the trigger.

![Weather shared SignalTap waveform](figures/weather_resource.png)

Figure 4. Weather shared capture over a wider sample range. The shared arithmetic schedule extends the interval before the full forecast becomes valid.

## 8 Reproduction and evidence files

The repository retains source code, trained coefficients, simulation scripts, native acquisition files, physical CSV results, and screenshots. The evidence archive created on 28 October 2026 contains 122 verified files and is approximately 5.4 MB. It preserves the physical session independently of the board's volatile configuration. Some status files inside that historical archive describe earlier stages of the same session; the programming logs, checked replay results, and decoded captures provide the final hardware evidence.

The four board projects are:

| Design | Project path from the repository root |
| --- | --- |
| Temperature speed | hardware/quartus/de2_temperature_jtag/temperature.qpf |
| Temperature shared | hardware/quartus/de2_temperature_resource_jtag/temperature_resource.qpf |
| Weather parallel | versions/weather_v2/quartus/de2_jtag_speed/weather_jtag.qpf |
| Weather shared | versions/weather_v2/quartus/de2_jtag_resource/weather_jtag.qpf |

For a live demonstration, power the original DE2, connect USB-Blaster, select the correct SOF file, and run the matching host replay variant. Power cycling clears the FPGA's SRAM configuration, so the SOF must be loaded again. Saved STP captures and screenshots remain available offline.

The deployment uses JTAG for sample transfer and readback. The current design has no forecast display on LEDs, seven-segment displays, or LCD. The repository also contains UART wrappers and serial-path simulations, but physical UART operation has not been verified.

## 9 Conclusions and limitations

The project produced four working implementations of fixed point forecasting on Cyclone II. Independent reference checking, mapped-logic tests, SDF timing simulation, and physical JTAG replay provide evidence at successive stages of implementation. SignalTap captures show real input and prediction transactions for both versions and both architectures.

The three parameter temperature model achieves a test MAE of 0.538017 °C in fixed point. The weather extension reduces temperature MAE to 0.507906 °C on its evaluated test set and adds forecasts for pressure, humidity, wind speed, and direction. The shared designs reduce dedicated multiplier usage at the cost of a longer processing schedule. Total logic savings depend on the version and implementation boundary.

The present evidence covers recorded data and fixed coefficients. It does not measure electrical power, live sensor behavior, maximum board frequency, or operational forecasting at other locations. Precipitation probability is outside the implemented outputs. Further work can evaluate other sites and periods, investigate power consumption, and improve the shared design's history and control logic while preserving the existing numerical contract.

## Appendix A Evidence sources

The following repository files support the numerical results and hardware claims in this report. Paths are relative to this Markdown report unless stated otherwise.

1. [Implementation report and core verification results](../IMPLEMENTATION_REPORT.md).
2. [Temperature floating point model](../../../software/models_cpp/model.json), [test metrics](../temperature_metrics.csv), and [fixed point numerical errors](../temperature_numerical_error.csv).
3. [Weather selected model](../../../versions/weather_v2/models/model.json) and [validation and test metrics](../../../versions/weather_v2/reports/metrics.csv).
4. [JTAG implementation results](../JTAG_IMPLEMENTATION_REPORT.md) and [interface protocol](../../../hardware/jtag/README.md).
5. [Temperature speed physical replay](../physical_jtag_temperature.csv), [temperature shared replay](../physical_jtag_temperature_resource.csv), [weather parallel replay](../physical_jtag_weather_speed.csv), and [weather shared replay](../physical_jtag_weather_resource.csv).
6. [Decoded SignalTap checks](../defense_session/SIGNALTAP_CAPTURE_CHECK.json) and [native captures and decoded CSV files](../defense_session/signaltap/).
7. [Temperature speed SDF manifest](../temperature_speed_modelsim_timing.json), [temperature shared SDF manifest](../temperature_resource_modelsim_timing.json), [weather parallel SDF manifest](../weather_speed_modelsim_timing.json), and [weather shared SDF manifest](../weather_resource_modelsim_timing.json).
8. [Native temperature speed screenshot](../defense_session/screenshots/temperature_speed_signaltap_detail.png), [temperature shared screenshot](../defense_session/screenshots/temperature_resource_signaltap_detail.png), [weather parallel screenshot](../defense_session/screenshots/weather_speed_signaltap_detail.png), and [weather shared screenshot](../defense_session/screenshots/weather_resource_signaltap_detail.png).
9. [Physical-session evidence archive](../defense_evidence_2026-10-28.tar.gz) and [saved evidence checksums](../defense_session/SAVED_EVIDENCE_SHA256.json).
