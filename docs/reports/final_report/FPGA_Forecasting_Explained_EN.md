# Weather forecasting on FPGA

From a temperature prototype to parallel weather inference  
CE436 Technical companion  
2 November 2026

## Preface

This companion explains the current parallel weather forecasting accelerator and the steps that led to it. It begins with the original temperature-only model, then follows the extension to temperature, pressure, humidity, wind speed, and wind direction. The main implementation throughout is weather_system_speed.

Basic algebra is sufficient for the model and fixed-point examples. Hardware terms are introduced when the discussion reaches the datapath and testbench. A worked example uses the actual weather temperature-channel coefficients, so its integer calculation can be checked against the deployed model file.

The [implementation report](FPGA_Forecasting_Final_Report_EN.md) contains the complete measured tables, deployed coefficient list, and physical evidence references. This companion develops the reasoning behind those results. Its numerical examples are teaching calculations, not additional experiments. The appendices provide a source-file reading sequence and questions for defense preparation.

## 1 System overview

### 1.1 Forecast inputs and outputs

The FPGA receives a frame representing one hour of recorded weather. A frame contains six numbers: temperature, pressure, humidity, wind speed, direction cosine, and direction sine. Once the history window is full, the circuit predicts conditions three hours after the latest frame. The two direction components are converted into one angle, giving five reported weather quantities.

Suppose the latest observation is at noon. The forecast target is 15:00. The computer already has earlier observations, while the actual 15:00 values are used later to score the forecast. A hardware result can agree perfectly with the specified equation while differing from the future weather observation. The model evaluation and circuit verification therefore use different comparisons.

Recorded frames are sent from a computer through USB-Blaster and JTAG. The board does not collect these observations from attached sensors. The result is read on the computer and saved in a CSV. The implemented design has no forecast display on LEDs or LCD.

Figure 1 places offline training and the deployed calculation in the same workflow.

![Offline training and deployed weather inference](figures/system_overview.png)

Figure 1. The model is fitted on the computer and deployed as fixed coefficients. The host supplies recorded frames and reads the weather forecast through JTAG.

### 1.2 Sampling and execution time

#### Sampling interval forecast horizon and clock period

An hourly sampling interval means consecutive observations represent conditions one hour apart. A three-hour forecast horizon means the desired target belongs three hours after the latest observation. A 50 MHz hardware clock means the circuit receives 50 million clock ticks each second.

These times belong to different parts of the system. The FPGA does not wait three hours before returning a prediction. After enough history has been loaded, the complete weather speed system calculates a result in 0.80 µs under the documented RTL latency convention.

Recorded observations can be replayed quickly because the timestamps belong to the data. If 25 hourly frames are sent in a short burst, the FPGA still treats them as a sequence of 25 hourly observations. The host must preserve their order and meaning. The arithmetic core has no calendar that can detect an accidentally reversed input file.

### 1.3 History and accepted frames

A signal is a quantity that changes. Outdoor temperature over time is a signal. A sample is one observation of that quantity. Our recorded sequence contains one sample per hour, so it is a discrete-time sequence.

Use T(t) for the latest hourly temperature. Then T(t − 3) is the temperature three sample positions earlier, and T(t − 24) is the temperature 24 sample positions earlier. This notation describes positions in the hourly sequence. It does not mean three or 24 FPGA clock cycles earlier.

Table 1 identifies the observations used for a noon forecast.

Table 1. Hourly observations used by the temperature model

| Symbol | Time relative to noon today | Role |
| --- | --- | --- |
| T(t) | Noon today | Current observation |
| T(t − 3) | 09:00 today | Recent trend reference |
| T(t − 21) | 15:00 yesterday | Previous day at the target hour |
| T(t − 24) | Noon yesterday | Previous day at the current hour |
| T(t + 3) | 15:00 today | Future observation used to evaluate the forecast |

The target is 15:00 today. Its matching hour yesterday is 21 hours before noon today, which explains the lag 21. The matching hour yesterday for the current observation is lag 24.

The history window holds the current value and the preceding 24 values, giving 25 samples. Only four values enter one original-temperature calculation, but the intervening samples must move through history so those lag positions remain correct when the next hourly value arrives. A host that separately supplied all four taps could use a different interface. Our implementation accepts one new temperature at a time and maintains its own history.

After reset, samples 1 through 24 fill history. Sample 25 is the first sample with all required past values available. Each later accepted sample can produce another forecast. For an uninterrupted replay of 128 inputs, the number of forecasts is 128 − 24 = 104. A reset starts the history requirement again.

The same 25-position history principle applies to the current weather design, but every accepted frame carries six channels. Its selected lag positions are 0, 1, 3, 6, 12, 21, and 24. The noon example explains the prototype anchor; the current weather model fits independent weights for all seven selected positions.

## 2 From temperature to weather models

### 2.1 Temperature prototype

The original temperature prototype used:

`forecast = yesterday at the target hour + a × daily change + b × recent change + c`

The quantities are:

`daily change = T(t) − T(t − 24)`

`recent change = T(t) − T(t − 3)`

Therefore:

`T̂(t + 3) = T(t − 21) + a[T(t) − T(t − 24)] + b[T(t) − T(t − 3)] + c`

The hat in T̂ means an estimate. The equation starts from yesterday's temperature at the desired future hour. It then adjusts that starting point using today's difference from yesterday and the recent three-hour change. The constant c is called the bias or intercept. It permits a fixed correction even when both differences are zero.

The coefficients a and b are multipliers learned from the training data. They are not percentages that must add to one. The daily term and recent term can overlap in the information they carry. A small b does not prove that recent changes never matter; it describes the fitted contribution of that term when the other terms are also present.

The prototype floating-point coefficients are a = 0.7454870438526146, b = 0.009149444986888534, and c = 0.0011295816555433053 °C. The first two are dimensionless because they multiply temperature differences. The bias has temperature units.

The model is linear in the learned parameters. Once its inputs are known, the unknowns a, b, and c appear only multiplied by known quantities and added together. A linear model can use delayed values and differences. It does not require the forecast to be a straight line against clock time.

Training means choosing coefficients using examples with known answers. For a past noon in the training period, we already know the temperature measured at 15:00 that day. That future measurement becomes the answer for this historical example.

For each eligible time, define x1 as the daily change, x2 as the recent change, and y as the future observation minus yesterday's target-hour observation. The equation used for fitting becomes:

`predicted y = a × x1 + b × x2 + c`

For one row, the residual is predicted y minus observed y. Ordinary least squares, abbreviated OLS, chooses a, b, and c to minimize the sum of squared residuals over all training rows. Squaring removes the sign and gives larger mistakes more influence.

If three residuals are 1, −2, and 0.5 °C, their squared-error sum is 1 + 4 + 0.25 = 5.25 °C². OLS searches for coefficients that make the training sum small. It does not minimize the later test MAE directly.

#### Least squares example

The invented rows in Table 2 have an exact linear relationship. They illustrate fitting without requiring a large weather file.

Table 2. Illustrative least squares training rows

| Row | x1 | x2 | Observed y |
| --- | --- | --- | --- |
| 1 | 0 | 0 | 1 |
| 2 | 2 | 0 | 2 |
| 3 | 0 | 4 | 2 |
| 4 | 2 | 4 | 3 |

Row 1 gives c = 1. Row 2 then gives 2a + 1 = 2, so a = 0.5. Row 3 gives 4b + 1 = 2, so b = 0.25. Row 4 confirms the result: 0.5 × 2 + 0.25 × 4 + 1 = 3. These teaching coefficients are unrelated to our deployed coefficients.

Real weather rows do not usually agree on one perfect solution. Thousands of equations constrain only three unknown coefficients. Least squares finds a compromise. In matrix notation, stack each row [x1, x2, 1] into a matrix X, and stack the observed y values into a vector y. The parameter vector contains [a, b, c]. The fitting problem is to minimize the squared length of X times the parameter vector minus y.

A matrix is a rectangular table of numbers. Matrix multiplication here is repeated multiply-and-add calculation across rows. A numerical least-squares solver handles the fit. The normal-equation expression involving the inverse of X transpose times X applies when the required inverse exists, but a numerical least-squares solver also handles cases where that expression is unreliable or undefined. We do not implement a matrix inverse on the FPGA.

#### Offline training and deployment

Training runs on the computer. Its result is a small set of coefficients saved to model files. The prototype FPGA uses those coefficients for inference, which means applying the equation to new input samples. The deployed hardware does not update the coefficients after each forecast. Retraining and changing the static coefficient files or generated RTL require a rebuild of the corresponding FPGA design.

### 2.2 Scope of the extension

The prototype confirmed that we could fit a model, quantize its coefficients, implement delayed sample access, and check the result on the FPGA. Extending the project required a larger model and a wider interface. We retained the three-hour horizon and hourly chronology, while adding new targets and a direction conversion path.

The current temperature predictor is also a new seven-lag model. Its coefficients are not the prototype a, b, and c. Each of the six channels has seven lag weights and a bias, giving 42 lag weights and six biases across the selected model. Different variables keep their own units and output limits.

Parallel operation is a hardware choice. It lets the channels calculate together but leaves the selected model unchanged. The recorded temperature MAE changed from 0.538017 °C in the prototype to 0.507906 °C in the weather model because the predictor changed, not because the arithmetic ran in parallel.

### 2.3 Current weather regressions

The weather dataset is NASA POWER hourly environmental data for Ho Chi Minh City at latitude 10.8231° N and longitude 106.6297° E, covering 2021 through 2025 in UTC. It provides gridded values. It is not a measurement stream collected by our DE2 board.

The fields are T2M for temperature, PS for surface pressure, RH2M for relative humidity, WS10M for wind speed, and WD10M for wind direction. Their units in this project are °C, kPa, percent, m/s, and degrees. Mixing a pressure unit or time-zone convention would invalidate an otherwise correct calculation.

The extended system considers several candidate models using validation data. The selected scalar models use seven delayed values of the same variable. This is univariate autoregression: auto refers to predicting a variable using its own past values, and regression refers to fitting numerical relationships.

For a scalar variable x, the selected equation has the form:

`x̂(t + 3) = bias + w0×x(t) + w1×x(t−1) + w2×x(t−3) + w3×x(t−6) + w4×x(t−12) + w5×x(t−21) + w6×x(t−24)`

A lag is a delay measured in input sample positions. The lag set is 0, 1, 3, 6, 12, 21, and 24. Each channel has its own coefficients and bias. The saved model uses a larger feature representation for candidate comparisons, but the selected models have nonzero weights only for the same variable's seven lags.

Ridge regression adds a penalty on coefficient size to the squared-error objective. This can discourage large coefficients when past inputs carry overlapping information. In the training script, the inputs are standardized for fitting, and the fitted coefficients are converted back to the original units. Standardization subtracts each training input's mean and divides by its standard deviation. The deployed hardware uses the converted coefficients, so it does not repeat that preprocessing for each sample.

Temperature and humidity select ridge penalty 1. The other selected channels use penalty 0, which removes that regularization penalty. These choices won among the candidates that were evaluated. They are not proof that no other model could perform better.



### 2.4 Forecast evaluation

A model can fit its old examples well and predict new examples badly. We therefore use separate time periods. The weather training targets end before 2024. Validation uses 2024 inputs whose targets remain before 2025. Test inputs belong to 2025, with unavailable future targets excluded.

Training estimates coefficients. Validation compares candidate model choices. Test evaluation measures the selected, frozen model on a later period. If test answers influence coefficient selection, the test loses its role as an independent later-period evaluation.

The weather preparation requires 25 consecutive valid hourly observations and a valid future target. It excludes unusable rows. The recorded example counts are 26,253 for training, 8,781 for validation, and 8,757 for test. These are usable examples after the timing and validity rules, not simply the number of calendar hours in those years.

A baseline is a simple predictor used for comparison. Persistence predicts T(t + 3) = T(t), which assumes the temperature will stay at its current value. The diurnal baseline predicts T(t + 3) = T(t − 21), which assumes the previous day's value at the target hour will repeat. The prototype added learned corrections to that second idea; the current weather model fits seven lag weights per channel.

Mean absolute error, or MAE, averages the sizes of the prediction errors. For errors 1, −2, and 0 °C, MAE is (1 + 2 + 0) / 3 = 1 °C. An MAE of 0.538017 °C means the average absolute difference on the evaluated test set has that value. It does not mean every forecast lies within 0.538017 °C.

Root mean square error, or RMSE, squares the errors, averages the squares, and takes the square root. For the same example, RMSE is square root of 5/3, approximately 1.291 °C. RMSE gives relatively more influence to larger errors. Both metrics have the same unit as the target.

The current weather temperature channel has test MAE 0.507906 °C and RMSE 0.730939 °C. Persistence has MAE 2.080369 °C, and the previous-day baseline has MAE 0.832280 °C. These comparisons support improvement on this particular test set. They do not establish performance for all locations or future years.

Do not convert MAE into an accuracy percentage by dividing by an arbitrary Celsius temperature. Celsius has an arbitrary zero, and such a percentage would change under conversion to another temperature scale.

## 3 Fixed point weather arithmetic

### 3.1 Representation and scaling

The current weather datapath stores each input as a signed 18-bit integer with eight fractional bits. A raw integer q represents q / 256 in that channel's unit. For example, 30 °C is raw 7680, and 2.5 m/s is raw 640. The same scaling factor does not make the physical units interchangeable.

Eighteen signed bits represent raw integers from −131072 through 131071. With eight fractional bits, the represented range is −512 through 511.99609375. One step is 1/256, or 0.00390625 of the channel's unit. The larger range accommodates pressure and the other scalar channels. The prototype used 16 signed bits at the same fractional scale.

The binary point is an agreement between the hardware and host; it is not an extra bit stored in the word. Signed values use two's complement. An 18-bit all-ones word means raw −1 and therefore −0.00390625 in Q8. Reading it as unsigned would give the wrong physical value.

Each coefficient is signed 18-bit Q14, so the raw weight is divided by 16384. A bias is signed 32-bit Q8. A product of an 18-bit input and 18-bit coefficient uses 36 bits, and the sum uses a 48-bit accumulator. The wider sum preserves intermediate precision before the final conversion.

For one channel, the hardware calculation is S = bias_raw × 16384 + the sum of seven weight_raw × sample_raw products. A Q14 weight times a Q8 sample produces a product with 22 fractional bits. Multiplying the bias by 16384 aligns it to that same scale before addition. After the sum, the result is floor(S / 16384), which returns a raw Q8 output.

Arithmetic right shift floors signed negative fractions. For example, an accumulator of −1 becomes raw −1 after the shift, whereas ordinary signed C++ division would truncate toward zero. The reference model must implement the same floor rule. Humidity is then limited to 0 through 100%, wind speed to nonnegative values, and direction components to −1 through 1. Remaining scalar overflow saturates to the signed 18-bit range. These limits prevent invalid numerical ranges; they do not make an inaccurate prediction correct.

### 3.2 Worked temperature channel example

This teaching example uses the actual deployed coefficients for the weather temperature channel. Choose the temperatures in Table 3 at the selected lags. Other channels have their own coefficients and are calculated in parallel; this example follows only one lane.

The raw Q14 weights are [20035, −9335, 1621, −205, 15, 13908, −10382], and the raw Q8 bias is 310. These values come from versions/weather_v2/models/model.json. The real bias represented in hardware is 310 / 256 = 1.2109375 °C.

Table 3. Seven products for the current weather temperature channel

| Lag in hours | Temperature in °C | Raw Q8 input | Raw Q14 weight | Product |
| --- | --- | --- | --- | --- |
| 0 | 30 | 7680 | 20035 | 153868800 |
| 1 | 29.5 | 7552 | −9335 | −70497920 |
| 3 | 28 | 7168 | 1621 | 11619328 |
| 6 | 27 | 6912 | −205 | −1416960 |
| 12 | 26 | 6656 | 15 | 99840 |
| 21 | 31 | 7936 | 13908 | 110373888 |
| 24 | 29 | 7424 | −10382 | −77075968 |

The aligned bias is 310 × 16384 = 5079040. Adding it to the seven products gives S = 132050048. The scaled value is 8059.6953125, so floor scaling produces raw 8059. Temperature has no additional physical-range clip here, and 8059 fits the signed 18-bit output range. The returned forecast is 8059 / 256 = 31.48046875 °C.

Each channel repeats this multiply-and-accumulate procedure with its own seven weights, bias, and lagged samples. An accumulator combines the products by addition; it does not update or train the coefficients. Forecast error for this example would require the actual temperature three hours later, which is not supplied in this teaching calculation.

## 4 Parallel weather datapath

### 4.1 Arithmetic lane and full system schedule

The weather_predictor_speed module instantiates six weather_ar_channel lanes. A lane stores one variable's 25-sample history, the selected coefficient constants, and an accumulator. Six lanes mean temperature, pressure, humidity, wind speed, cosine, and sine can progress together.

A lane uses one multiplier repeatedly. The term counter selects lag 0, then 1, 3, 6, 12, 21, and 24. Table 4 follows an eligible frame from accepting edge N. The acceptance edge shifts history and initializes the aligned bias.

Table 4. Schedule inside one weather arithmetic lane

| Edge relative to acceptance | Operation |
| --- | --- |
| N | Shift history, initialize accumulator from the bias, and select term 0 |
| N + 1 | Capture the lag 0 operand |
| N + 2 | Capture its product with weight 0 |
| N + 3 | Add that product to the accumulator |
| N + 4 through N + 21 | Repeat operand, product, and sum for terms 1 through 6 |
| N + 22 | Scale, limit, and publish the channel result |
| N + 23 | Earliest next acceptance during sustained eligible processing |

The history update uses nonblocking assignments. The channel reads the updated history on later clock edges, so hist[0] supplies the current frame and hist[lag] supplies the required previous frame. A stall must not shift this history.

The six channel results feed the system wrapper. The wrapper holds scalar values while CORDIC converts the direction components. Under the project's post-edge timing definition, all outputs become valid 40 cycles after acceptance. The next frame can enter at a 23-cycle interval because channel arithmetic and the direction path occupy different parts of the processing schedule.

At 50 MHz, one cycle is 20 ns. Full latency is therefore 40 × 20 ns = 800 ns, or 0.80 µs. The initiation interval is 23 cycles, not 40. Parallel means the six channels run together; each channel still performs seven products over time.

### 4.2 Handshake and reset

A handshake specifies when the sender and receiver agree that data has transferred. Our input transfer occurs at a rising edge when sample_valid and sample_ready are both high, while reset is inactive. Valid means the sender is presenting a sample. Ready means the core can accept it.

If valid is high while ready is low, the sender must hold that pending frame and valid assertion until acceptance. If valid is low, changes on the input bus are ignored. History advances only for accepted samples. Counting every clock as another hour would corrupt all delayed taps.

Table 5 illustrates acceptance and backpressure over five clock edges.

Table 5. Illustrative input handshake

| Clock edge | valid | ready | Input action |
| --- | --- | --- | --- |
| 10 | 1 | 1 | Accept frame A |
| 11 | 1 | 0 | Hold frame B pending |
| 12 | 1 | 0 | Continue holding the same B |
| 13 | 1 | 1 | Accept B once |
| 14 | 0 | 1 | Accept nothing |

The core has no output ready signal. A consumer must capture every result when forecast_valid is high. It cannot ask the core to repeat a result later. The JTAG mailbox provides persistent storage so that a slow computer can still read the last completed result.

Reset is synchronous and active low. The RTL performs its reset behavior at a rising edge when rst_n is zero. Reset clears validity and history eligibility and cancels pending predictions. Not every physical history bit needs clearing because no prediction is allowed until enough new samples overwrite the required window. The board wrapper handles the external reset path before it reaches the synchronous core.

Reset priority matters. Input values presented during reset must not count as new valid history. Tests deliberately exercise this case and reset while a forecast is in flight.

### 4.3 Direction representation and CORDIC

Angles wrap around. Directions 359° and 1° are two degrees apart around the circle, even though ordinary subtraction gives 358°. Directly averaging or fitting raw angle values near that boundary can produce misleading results.

The host represents an angle theta by two components, cos(theta) and sin(theta). In ordinary coordinate terms, these locate a point on the unit circle. For teaching examples, 0° corresponds to (1, 0), 90° to (0, 1), and 180° to (−1, 0). This is a numerical angle encoding; a wind direction value retains the dataset's meteorological meaning.

The system predicts the cosine and sine channels separately. It then recovers an angle using atan2(sine, cosine), which identifies the correct quadrant. The predicted pair does not have to lie exactly on the unit circle for its nonzero direction to be calculated.

A zero pair has no direction. Our hardware emits angle zero and sets direction_defined to zero for that pair. A zero-degree output with direction_defined equal to one has a different meaning and must not be confused with the undefined case.

CORDIC calculates the angle in RTL using repeated shifts, additions, and a table of small rotation angles. The vectoring process reduces the vertical component toward zero while accumulating the corresponding angle. The implemented unit performs 16 iterative steps and handles quadrants and wrapping. Reading its source reveals how the numerical iterations are scheduled; there is no general floating-point atan2 unit in the FPGA.

Direction therefore needs six arithmetic channels in total: temperature, pressure, humidity, wind speed, cosine, and sine. The final human-readable outputs still describe five weather quantities because the last two channels describe one direction.

Direction forecast scoring uses circular angular distance and includes target wind speeds of at least 0.5 m/s. That threshold is an evaluation policy. It is separate from the zero-vector validity rule.

The reported 18.084598° direction test MAE uses ideal floating-point atan2 applied to quantized predicted components. CORDIC conversion is tested separately: 263,169 integer pairs were checked, with maximum circular error 0.005635°. The board angle checker permits five raw Q8 degree counts, or 0.01953125°. The conversion tolerance is not the weather prediction MAE.

## 5 Verification

### 5.1 Reference model and scoreboard

The testbench sends six-channel frames to the real weather_system_speed RTL. It drives the clock and reset and changes stimulus away from the active sampling edge. Only a valid/ready handshake advances the expected input history.

DPI-C lets SystemVerilog call a C-compatible bridge to the C++ weather reference. The reference uses the deployed integer coefficients and numerical rules to calculate expected outputs. It runs in the simulator on the computer and is not part of the synthesized FPGA. The reference history, counters, and pending expectations are reset with the DUT.

The scoreboard stores expected results in accepted-frame order and checks the corresponding RTL transaction. It verifies the six component values, direction validity, and permitted angle error, as well as the documented output schedule. A correct number delivered for the wrong input frame is still a failure. Missing, duplicated, or reordered results must also fail.

Weather speed verification accepted 1,200 frames and checked 1,124 forecasts. Repeated resets require new warm-up windows, and four pending results were canceled by reset. The number 1,124 therefore cannot be derived simply by subtracting 24 once from 1,200. The reset accounting is part of the test.

Directed tests exercise known corner cases such as signed extremes and physical clips. Pseudorandom traffic explores changing values and input gaps. Netlist replay and predictor-core SDF timing simulation check later stages of implementation. The accepted timing run sent 288 frames and checked 264 forecasts. The whole JTAG transport does not have a claimed full SDF replay.

A physical replay then checks the programmed board. Its uninstrumented weather speed run accepted 128 frames and checked 104 forecasts after one 24-frame warm-up. A separately instrumented build passed the same counts. Mocked JTAG API tests check the host checker and do not count as physical board evidence.

### 5.2 Meaning of the evidence

There are three different comparisons in this project. Forecast evaluation compares a prediction with the future recorded observation. Numerical evaluation compares fixed-point output with floating-point output. Implementation verification compares RTL or physical output with the fixed-point reference for identical inputs.

The current temperature-channel test MAE of 0.507906 °C measures prediction against future observations. Bit-exact agreement between RTL and the integer reference measures implementation correctness. These comparisons use different answers and must be reported separately.

An implementation PASS means all checks in that particular test completed without a detected mismatch. It needs its scope and sample count. A 104-forecast board replay is physical evidence for those transactions; it is not evidence of a year-long live deployment.

Table 6 summarizes the scope of each verification stage.

Table 6. Scope of each verification stage

| Verification step | What it checks | Important boundary |
| --- | --- | --- |
| Software forecast evaluation | Predictions against later observations | Dataset and chosen time split |
| RTL with DPI-C | Arithmetic, protocol, reset, order, and cycle timing | Simulated production RTL |
| Functional netlist replay | Logic after synthesis or mapping | Simulator and vendor atoms |
| Static timing analysis | Estimated setup and hold constraints | Declared clocks and constraints |
| SDF timing simulation | Netlist operation with annotated path delays | Predictor core timing netlist |
| Physical JTAG replay | Actual programmed FPGA responses | Recorded replay at 50 MHz |
| SignalTap capture | Selected internal signals on the FPGA | Saved acquisition window |

Synthesis converts RTL into a netlist, a description of components and connections. Fitting places those components in the chosen device and routes the wires. A design can simulate correctly in RTL and still fail a timing constraint after routing.

SDF stands for Standard Delay Format. It supplies delay values to a timing simulation of the fitted netlist. The accepted core timing runs use maximum SDF delays and a 20 ns clock. A run with missing annotation would not provide the same evidence even if it printed PASS elsewhere, so the stored timing manifests record the relevant files and statuses.

Static timing analysis checks paths without enumerating input vectors. Setup slack measures the margin for data arriving early enough before capture. Hold slack measures the margin for data remaining stable long enough after capture. Positive reported slack means the analyzed check has margin under the declared model. Constraint coverage still matters; a positive number is meaningful within its stated timing assumptions.

## 6 FPGA integration and results

### 6.1 JTAG communication

USB-Blaster provides access to the FPGA's JTAG infrastructure. It is not a normal USB serial adapter. We use a Quartus In-System Sources and Probes IP block, abbreviated ISSP, to expose a source word that the computer writes and a probe word that it reads.

The source word has 128 bits. It carries payload data, a request toggle, and a reset bit. The probe word has 256 bits. It carries the last result, counters, status flags, an acknowledgement toggle, and a signature identifying the design.

A mailbox is the control circuit between that debug transport and the forecasting core. The computer first stages the payload while keeping the old request bit, then changes the request bit to commit the transaction. A toggle means the bit changes from its previous value; successive requests can alternate 0 to 1 and 1 to 0.

The mailbox waits for synchronized source values and additional settling cycles before capturing the payload. It holds the core input until the core accepts it. During warm-up, it can acknowledge without a forecast. After warm-up, it captures the completed prediction before acknowledging completion.

The computer holds payload and request unchanged until acknowledgement. It then reads a stable completed probe word. Only one transaction may be outstanding. This protocol prevents a slow computer from overwriting a pending request or missing a one-clock forecast_valid pulse.

The last-result-valid bit stays set until reset. It means the mailbox contains a result. Core forecast_valid is a transient event. These flags have different jobs, so a screenshot of a persistent result flag is not a direct waveform measurement of the core pulse.

The counters make a replay easier to audit. After 128 accepted inputs without reset, a forecast count of 104 matches the 24-input warm-up rule. Counters are 16 bits and wrap modulo 65536; their finite width should be considered in longer sessions.

In the deployed design, the result appears in the host replay output, saved CSV, or Quartus In-System Sources and Probes Editor. There is no result display on LEDs, seven-segment displays, or LCD. UART wrappers exist, but physical UART operation has not been verified.

### 6.2 Timing resources and waveform interpretation

The uninstrumented weather speed board build uses 6,253 logic elements, 4,571 registers, and 12 nine-bit multiplier elements. Two nine-bit elements correspond to one full 18 by 18 multiplier on this device, so the arithmetic allocation is consistent with six channel multipliers. The fit reports zero mapped memory bits; the design still stores history in its mapped registers and logic.

The design is constrained and physically tested at 50 MHz. Static timing estimates Fmax as 79.74 MHz and reports setup slack 7.459 ns and hold slack 0.215 ns. These estimates describe the fitted design under its constraints. They are not a measured board-frequency sweep.

SignalTap adds an embedded acquisition circuit. The weather speed capture contains 512 samples at 20 ns spacing. The accepting input is recorded at index 215, and the rising forecast-valid trigger is at 256, a raw separation of 41 samples. The RTL latency is defined by observing registers after their update, giving 40 cycles. Preserve the raw capture indices and explain the observation convention when presenting the waveform.

Read valid and ready together to locate acceptance. Then locate forecast_valid and decode the six values, angle, and direction-defined flag at that event. A changing output bus while valid is low does not indicate a new completed forecast. The mailbox's retained result-valid bit is persistent and has a different purpose from the core's one-cycle event.

The native screenshot and STP file are the original physical records. The clean control plot in Figure 2 of the implementation report is decoded from their saved CSV. The forecast accuracy table comes from historical software evaluation, and the board replay compares the same integer implementation against reference vectors.

## Appendix A Source files and reproduction

Paths are relative to fpga-temp-predictor. Read the files in the following order to follow the current weather design from training to physical evidence.

1. versions/weather_v2/software/train_models.py prepares lagged examples, separates time periods, fits candidates, and selects coefficients using validation data.
2. versions/weather_v2/models/model.json stores the selected models, weights_q14, bias_q8, formats, and data hash. Its temperature row supplies the worked example in Section 3.2.
3. versions/weather_v2/rtl/weather_ar_channel.v implements the per-channel history and seven-term schedule. weather_predictor_speed.v instantiates the six lanes.
4. versions/weather_v2/rtl/weather_system_speed.v aligns the scalar results with wind_direction_cordic.v, which reconstructs the angle.
5. versions/weather_v2/tb/tb_weather.sv and weather_reference.cpp implement simulation checking. software/run_verification.py in that version runs the verification flow.
6. versions/weather_v2/quartus/de2_jtag_speed/weather_jtag.qpf is the board project. Use its output_files/weather_jtag.sof for the live demonstration.
7. scripts/replay_jtag.tcl selects weather_speed, resets the design, sends reference frames, and saves physical results.
8. docs/reports/physical_jtag_weather_speed.csv contains the checked board replay. docs/reports/defense_session/signaltap contains weather_speed.stp and its decoded CSV; the implementation report links the native screenshot.

For the development starting point, software/models_cpp/model.json and hardware/speed_optimized/temp_predictor_speed.v retain the original temperature coefficients and pipeline. They document the prototype. The current weather datapath uses the weather model and sources listed above.

Offline model inspection, simulation, report review, and saved waveform viewing can be performed without the board. A live demonstration requires a powered DE2 and USB-Blaster. Program the weather speed SOF and run the matching weather_speed replay. Power cycling clears the SRAM configuration, so programming must be repeated for a later live demonstration. The current demonstration reads results through JTAG; an additional serial adapter is not required.

## Appendix B Defense discussion

#### Project contribution

The project extends a temperature-only OLS prototype into a six-channel parallel weather predictor. The extension includes selected seven-lag models, wider fixed-point arithmetic, an angular representation for wind direction, CORDIC reconstruction, and a verified board interface. Temperature, pressure, humidity, wind speed, and direction are the reported quantities.

#### Relationship to the prototype

The prototype established the history, arithmetic, and reference-checking approach with a smaller equation. The current weather temperature channel uses new coefficients and seven lags. Additional channels run their own univariate models. We should explain both the reused engineering method and the parts that were redesigned.

#### Meaning of speed optimization

There is one arithmetic lane per channel, so six channels progress in parallel. Each lane reuses its multiplier over seven lag terms. The full system has latency 40 cycles and sustained acceptance interval 23 cycles. This is not a 42-multiplier single-cycle datapath.

#### Interpretation of the temperature improvement

The original test MAE is 0.538017 °C and the current temperature-channel MAE is 0.507906 °C. The predictor changed after validation-based model selection. Parallel execution does not explain that accuracy improvement. The comparison is limited to the recorded evaluation.

#### Why direction uses two channels

Angles wrap around at 360°. Predicting cosine and sine avoids treating 359° and 1° as widely separated raw numbers. CORDIC reconstructs the angle from the predicted pair. A zero pair has an undefined-direction flag.

#### Meaning of a board PASS

The physical replay checked 104 forecasts from 128 accepted frames at 50 MHz. It establishes agreement with the reference for those inputs. Forecast accuracy comes from the separate chronological test against future observations. Neither result substitutes for the other.

#### Scope and remaining limits

The implementation uses recorded observations and fixed coefficients. It does not train on the FPGA, collect live sensor data, or output precipitation probability. Reported Fmax is a timing estimate, while physical replay used 50 MHz. Direction model scores use ideal angle decoding of quantized components, with CORDIC conversion checked separately.

## Appendix C Review calculations

The following questions use teaching values and the actual deployed temperature-channel constants where stated. Each member should attempt them before reading the answer.

#### Raw value decoding

An 18-bit signed Q8 temperature result is raw 8059. Its value is 8059 / 256 = 31.48046875 °C. An 18-bit all-ones result is raw −1, or −0.00390625 °C. Width and signedness are interpreted before scaling.

#### History accounting

An uninterrupted stream of 50 accepted weather frames after reset produces 50 − 24 = 26 eligible forecasts. Reset clears eligibility, so another 20 accepted frames after reset do not yet produce a forecast. Any in-flight prediction canceled by reset must be accounted for separately.

#### Latency and acceptance interval

At 50 MHz, each period is 20 ns. Forty cycles equal 800 ns, or 0.80 µs. The sustained accepted-frame interval is 23 cycles, so it differs from full output latency. The direction conversion path can run while channel arithmetic begins a later frame.

#### Worked arithmetic check

Using Table 3, the seven products plus bias_raw × 16384 must sum to 132050048. Dividing by 16384 gives 8059.6953125; floor scaling yields raw 8059. A different sum points to a coefficient, lag, sign, or scale mismatch. A final value of 8060 would violate the specified floor operation for this example.

#### Circular direction error

A prediction of 359° and an observation of 1° differ by 2° on the circle. Ordinary subtraction gives the wrong distance. An output angle of zero must also be interpreted with direction_defined to distinguish an undefined vector from a valid zero-degree direction.

#### Evidence interpretation

A fitted Fmax of 79.74 MHz and a passing 50 MHz replay support two statements: the timing tool estimated 79.74 MHz under its constraints, and the board passed the tested transactions at 50 MHz. They do not establish a measured maximum clock on the physical board.

Before the defense, every member should be able to explain the progression in Table 1 of the implementation report, reproduce the arithmetic in Table 3 of this companion, trace a six-channel handshake, and locate the actual weather speed waveform and replay CSV.

## Appendix D Native implementation screenshots

#### Quartus compilation and fitted resources

![Native Quartus weather speed compilation summary](../defense_session/screenshots/weather_speed_flow_summary.png)

Figure D1. Native Quartus compilation report for the weather speed JTAG build. The enlarged view shows the successful flow, Cyclone II EP2C35F672C6 target, weather speed source files, 6,253 logic elements, 4,571 registers, and 12 nine-bit multiplier elements. The screenshot records the uninstrumented build and supports the implementation resource figures.

The image is a detail view of the saved application screenshot. The original remains at docs/reports/defense_session/screenshots/weather_speed_flow_summary.png. Its compilation timestamp is 27 October 2026; physical verification followed on 28 October. These are separate stages of the implementation.

#### Quartus timing analysis

![Native Quartus weather speed timing summary](../defense_session/screenshots/weather_speed_timing_summary.png)

Figure D2. Native TimeQuest multicorner timing summary. CLOCK_50 has positive setup slack of 7.459 ns and hold slack of 0.215 ns, with zero reported total negative slack for those checks. The image is an enlarged detail of the saved application screenshot.

![Native Quartus weather speed Fmax summary](../defense_session/screenshots/weather_speed_fmax.png)

Figure D3. Native slow-model Fmax summary for the same weather speed JTAG build. The estimated Fmax is 79.74 MHz for CLOCK_50. Physical replay used 50 MHz; this timing estimate is not a measured maximum board frequency. Both original screenshots remain in docs/reports/defense_session/screenshots.

#### Physical SignalTap waveform

![Native physical weather speed SignalTap waveform](../defense_session/screenshots/weather_speed_signaltap_detail.png)

Figure D4. Saved native SignalTap waveform from the instrumented weather speed design, acquired during the physical FPGA session. The screenshot shows the input valid and ready signals, the final forecast_valid event at the trigger, and the input and output buses. This is an application capture, with the original signal names and bus values visible.

The complete physical capture is retained as docs/reports/defense_session/signaltap/weather_speed.stp. At the forecast-valid event, the temperature bus reads hexadecimal 01A72, which is raw 6770, or 26.4453125 °C in Q8. The angle bus reads hexadecimal 00570, or 5.4375° in unsigned Q8 degrees. These decoded values explain how to read the screenshot; their agreement with the reference is checked by the saved replay and capture checks.

The input acceptance and final forecast-valid event are separated by 41 recorded acquisition intervals. The documented RTL latency is 40 cycles under its post-edge observation convention. The native waveform preserves the acquisition convention and must be read together with that explanation. SignalTap instrumentation changes the fitted design, so the resource and Fmax screenshots above describe the separate uninstrumented build.
