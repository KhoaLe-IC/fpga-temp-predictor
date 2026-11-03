# Weather forecasting on FPGA

## Presentation baseline

Purpose: give the judges a clear account of the finished weather-speed implementation, how it grew from the temperature prototype, and what the saved results establish.

This is a storyboard and design brief for a new final-defense deck. It does not modify the existing proposal PPTX files. The accompanying proposal notes contain planned features and should not be used as the final-defense script.

Audience: DSP and digital-design instructors. Assume familiarity with basic regression, HDL, and FPGA tools; explain the project-specific choices.

Timing assumption: 15 minutes for the talk, with questions afterward. The planned content is 14 minutes 15 seconds, leaving 45 seconds for pauses, speaker changes, or a slow slide transition. A live demonstration is optional and must replace content rather than extend the talk.

### Central argument

We started with a three-parameter temperature predictor, extended the model and arithmetic to forecast five weather quantities, and verified the parallel implementation on a Cyclone II FPGA using recorded inputs.

The talk must answer four questions in order: What does the system predict? What changed from the prototype? How does the hardware execute the model? What evidence supports the results?

Use “weather-speed design” or “parallel weather predictor” consistently. Present only this current implementation. Temperature-only work supplies the development history. The resource-optimized design is outside this talk.

## Professional references and design decisions

Penn State's [assertion–evidence checklist](https://www.writing.engr.psu.edu/AE_checklist.pdf) recommends a short sentence headline supported by visual evidence, with little body text. Its typography guidance gives 28-point headlines, 18–24-point body text, and smaller references. For this projected defense deck, use a larger 32–36-point headline and 24–28-point labels where space allows.

MIT's [Slideshow guidance](https://mitcommlab.mit.edu/broad/commkit/slideshow/) recommends a single message per slide, introducing data before interpreting it, simplifying figures, and preparing technical backup slides. Apply that structure here: explain the comparison and its units before revealing error values; identify the measurement boundary before presenting Quartus numbers. The specific slide order, palette, and timing below are project decisions, not requirements from those sources.

### Visual direction

Use a restrained engineering-defense style: white background, dark charcoal text, one deep-blue accent, and light gray for context. Use amber sparingly to mark a changed feature or one important waveform edge. Retain native screenshot colors.

Build on a 16:9 canvas with approximately 0.55-inch outer margins. Use Aptos or Arial throughout. Headlines sit in the same position, left aligned, at most two lines. Body labels should normally be at least 24 points; equations 28–30 points; source footers 12–14 points. If technical labels become too small, simplify or move the detail to backup.

Let the evidence determine the layout: a timeline for data, a drawing for a datapath, a chart for errors, a screenshot for implementation. Do not force every slide into the same three-box arrangement. Consistent alignment and typography should connect the deck.

Keep most explanatory prose in speaker notes. Use direct titles about this project rather than generic labels such as “Innovative Solution,” “Key Benefits,” or “Future Potential.” Avoid stock clouds, robot artwork, decorative circuit backgrounds, gradients, excessive rounded cards, and ornamental icons. Those assets would compete with the actual engineering work.

Authenticity comes from specific, inspectable material: actual signal names, recorded inputs, real Quartus panels, explained coefficients, and measured results. Do not invent team roles, troubleshooting stories, photographs, or development milestones. A visual style cannot establish authorship or guarantee how someone will perceive AI assistance.

### Screenshot treatment

Use the existing weather_speed screenshots from the saved physical session. Place an enlarged crop of the relevant panel in the main slide, with a small label identifying the build and source. Keep full original screenshots in backup and preserve their files. Add callouts outside the image; never change a displayed value or recreate a screenshot as if it were native output.

Separate uninstrumented Quartus fit results from the instrumented SignalTap capture. Use the saved capture as the planned demonstration; it remains available without a connected board. Use no generated imagery for implementation evidence.

## Timed slide sequence

| Slide | Time | Elapsed end | Main message or title | Main visual |
| --- | --- | --- | --- | --- |
| 1 | 0:30 | 0:30 | Weather forecasting on FPGA | Title and a small native waveform excerpt |
| 2 | 0:45 | 1:15 | Recorded hourly observations produce a three-hour-ahead forecast | Host–JTAG–FPGA–result path |
| 3 | 1:05 | 2:20 | The temperature prototype became a six-channel weather predictor | Before-and-after comparison |
| 4 | 1:00 | 3:20 | Model selection and testing use separate time periods | 2021–2025 timeline |
| 5 | 0:55 | 4:15 | Each channel predicts from seven past values of the same variable | Equation with lag positions |
| 6 | 1:05 | 5:20 | Two component predictions preserve wind direction around zero degrees | Unit-circle drawing and CORDIC path |
| 7 | 1:10 | 6:30 | Fixed-point rules make the software and RTL calculations comparable | Scale-flow diagram and one worked value |
| 8 | 1:00 | 7:30 | Six arithmetic lanes process the weather channels in parallel | Six-lane architecture diagram |
| 9 | 1:05 | 8:35 | A complete forecast takes 40 cycles at 50 MHz | Acceptance and execution schedule |
| 10 | 1:10 | 9:45 | Verification checks arithmetic, transactions, and fitted logic | Verification chain with check counts |
| 11 | 0:55 | 10:40 | The selected weather models beat both simple baselines on the test set | Five small MAE comparisons |
| 12 | 1:05 | 11:45 | The weather-speed JTAG build meets the 50 MHz timing constraint | Native Quartus panels |
| 13 | 1:10 | 12:55 | Physical replay checked 104 forecasts and captured a valid transaction | Native SignalTap waveform and replay excerpt |
| 14 | 0:45 | 13:40 | The demonstrated system uses recorded data and fixed coefficients | Compact scope diagram |
| 15 | 0:35 | 14:15 | The project extends a temperature model into verified weather hardware | Three evidence-backed closing statements |

## Slide instructions and speaker prompts

### 1 Weather forecasting on FPGA

On slide: title, subtitle “From a temperature prototype to parallel weather inference,” course, and actual team names. Use one small waveform excerpt, not a stock weather photograph. Names are to be supplied by the team; do not infer them.

Say: “Our project forecasts temperature, pressure, humidity, wind speed, and wind direction three hours ahead. We will explain the extension from our original temperature model, the parallel hardware, and the evidence from simulation and the DE2 board.”

Transition: identify the system boundary before discussing algorithms.

### 2 Recorded hourly observations produce a three-hour-ahead forecast

Draw a simple left-to-right flow: recorded weather frames on the computer → USB-Blaster/JTAG mailbox → history and weather core → retained result on the computer. Label the input “one frame per recorded hour” and the output “target time t + 3 h.” Keep offline training as a small separate line above the FPGA.

Say: “The timestamps belong to the data. Replaying hourly observations quickly does not change the forecast horizon. The FPGA performs inference with fixed coefficients; it does not wait three hours or train the model. We read the result on the host through JTAG.”

Do not show a sensor, UART cable, LED forecast display, or live dashboard as an implemented feature.

### 3 The temperature prototype became a six-channel weather predictor

Use a two-column comparison with four rows: temperature only → five reported quantities; three-parameter seasonal OLS → seven-lag regressions; one arithmetic channel → six channels; 16-bit Q8 inputs → 18-bit Q8 inputs. Put CORDIC as an added stage under the direction output.

Show the original equation as a small secondary line only if readable:

$$
\widehat T(t+3)=T(t-21)+a[T(t)-T(t-24)]+b[T(t)-T(t-3)]+c.
$$

Say: “The prototype established the training, history, fixed-point, and reference-checking workflow. The extension changed the model as well as the number of outputs. The current temperature coefficients are not the old a, b, and c reused unchanged. We retained the hourly sampling and three-hour horizon.”

Keep the prototype to this slide. The current architecture does not need to be defended through a resource-variant comparison.

### 4 Model selection and testing use separate time periods

Draw three adjacent timeline regions: 2021–2023 training, 2024 validation, 2025 test. Beneath them place 26,253 / 8,781 / 8,757 usable examples. Label the dataset NASA POWER, Ho Chi Minh City, hourly, UTC. Explain in speech that exact eligibility follows target timestamps and valid history, not just calendar membership.

Say: “Training fits coefficients. Validation chooses among candidate models. The selected coefficients are frozen before evaluating the later test period. Each example requires a valid 25-observation history and a target three hours later. This is why the counts differ from the raw number of hours.”

Footnote: gridded environmental data at the retained location; not measurements collected by the DE2. Put precise cutoff rules in backup.

### 5 Each channel predicts from seven past values of the same variable

Center the equation and place seven labeled taps underneath it:

$$
\widehat x(t+3)=\beta_x+\sum_{k=0}^{6}w_{x,k}x(t-\ell_k),
\qquad \ell=[0,1,3,6,12,21,24].
$$

Use one color for samples and another for learned constants. Include a small note: “Temperature and humidity: ridge penalty 1; remaining selected channels: penalty 0.”

Say: “Each output uses its own history. Humidity and pressure do not jointly predict temperature in this selected model. Each arithmetic channel has seven weights and a bias. Ridge regularization penalizes coefficient size during fitting; it does not add an iterative learning algorithm to the FPGA.”

Keep matrix inversion and all 48 deployed constants in backup.

### 6 Two component predictions preserve wind direction around zero degrees

Show 359° and 1° beside one another on a circle. Then show direction → cosine/sine → two regression lanes → CORDIC → angle. Use “2° apart” as the only large numerical annotation.

Say: “Ordinary subtraction makes these nearby directions look far apart. The host encodes each input angle as cosine and sine. The FPGA predicts the two components, then a 16-step iterative CORDIC reconstructs the angle. A zero component pair has an undefined-direction flag.”

Do not describe this numerical encoding as converting meteorological wind direction into an independently measured Cartesian velocity vector.

### 7 Fixed-point rules make the software and RTL calculations comparable

Draw sample Q8 × weight Q14 → full product Q22 → 48-bit accumulator with aligned bias → arithmetic shift by 14 → Q8 and clipping. Label samples and weights signed 18-bit; bias signed 32-bit Q8; product 36-bit.

Use one small conversion: 30 °C → raw 7680. Show the current-model teaching calculation result as a second endpoint only: raw 8059 → 31.48046875 °C. Label it “worked example,” not a physical measurement.

Say: “The binary point is a scaling convention. We preserve product precision and accumulate before shifting. Negative fractions use floor scaling, followed by the specified limits. The C++ reference follows those same rules, so a mismatch indicates an implementation difference rather than a weather forecast error.”

The complete seven-product calculation belongs in backup. It uses the actual deployed temperature-channel weights with illustrative input samples.

### 8 Six arithmetic lanes process the weather channels in parallel

Draw six horizontal lanes labeled temperature, pressure, humidity, wind speed, cosine, and sine. Inside one expanded lane show history → lag selection → multiplier → accumulator. Depict the other lanes with a simple repeated block. Join cosine and sine into CORDIC; delay or hold scalar outputs until the complete frame is valid.

Say: “Parallelism is across the six channels. Each lane reuses one multiplier over its seven terms. The design therefore does not contain 42 simultaneous multipliers. History advances only when a frame is accepted. The wrapper aligns the scalar results with the reconstructed direction.”

Make the six-lane organization the dominant graphic. Avoid a hierarchy dump or a screenshot of the entire RTL file.

### 9 A complete forecast takes 40 cycles at 50 MHz

Use a schedule with accepting edge N, lane output N + 22, earliest next acceptance N + 23, and complete output N + 40 under the documented post-edge convention. A second frame begins while the first frame's direction conversion completes. Add “20 ns per cycle” and “0.80 µs full latency.”

Say: “Latency and acceptance interval are different. A result takes 40 cycles, but eligible frames can enter 23 cycles apart. The first 24 accepted frames fill history. The 25th can generate the first forecast. An idle clock does not represent another hour or shift the stored sequence.”

Do not imply that JTAG host replay attains this core acceptance rate. Keep the detailed three-cycle-per-term lane schedule in backup.

### 10 Verification checks arithmetic, transactions, and fitted logic

Show four stages with short labels: fixed-point C++ reference ↔ RTL/DPI-C; mapped netlist; predictor-core SDF; physical replay. Attach the saved counts to the applicable stages: RTL 1,124 checked forecasts from 1,200 accepted frames; SDF 264 from 288; board replay introduced on slide 13.

Say: “We check output values, order, valid timing, stalls, range limits, and reset cancellation. Resets require fresh history and cancel pending work; the RTL count cannot be explained by subtracting 24 only once. The accepted SDF run covers the predictor core at a 20 ns period. It is not a full timing simulation of the proprietary JTAG transport.”

Put actual transcript details in backup. Use no decorative green check unless tied to a named saved run.

### 11 The selected weather models beat both simple baselines on the test set

Use five small horizontal bar comparisons with separate axes and clear units. All bars start at zero. Current model in blue; persistence and previous-day baseline in distinct neutral shades. Do not put values with different physical units on one common magnitude axis.

| Target | Selected fixed MAE | Persistence MAE | Previous day MAE |
| --- | --- | --- | --- |
| Temperature, °C | 0.508 | 2.080 | 0.832 |
| Pressure, kPa | 0.0346 | 0.1352 | 0.0858 |
| Humidity, percentage points | 2.614 | 8.831 | 3.804 |
| Wind speed, m/s | 0.567 | 0.830 | 0.891 |
| Direction, degrees | 18.085 | 21.424 | 35.292 |

Introduce persistence as “repeat the latest value” and the diurnal baseline as “repeat yesterday at the target hour.” Say that lower MAE is better before interpreting the bars. Note the temperature change from prototype MAE 0.538 to current 0.508 °C in speech, rather than adding a fourth series across every panel.

Direction footnote: 8,593 non-calm targets, target wind speed at least 0.5 m/s, ideal atan2 decoding of quantized component predictions; CORDIC conversion checked separately. Other targets use 8,757 test examples. These qualifications must remain visible or be clearly stated, not omitted for a stronger claim.

### 12 The weather-speed JTAG build meets the 50 MHz timing constraint

Use enlarged native Quartus Flow Summary and timing/Fmax panels. Highlight 6,253 logic elements, 4,571 registers, 12 nine-bit multiplier elements, setup slack 7.459 ns, and hold slack 0.215 ns. Display at most three large callouts; remaining values can stay in the readable native panels.

Say: “These numbers include the board JTAG wrapper and exclude SignalTap instrumentation. Twelve nine-bit multiplier elements correspond to the six full multipliers allocated here. The board was tested at 50 MHz. The 79.74 MHz figure is a fitted timing estimate, not a physical clock sweep.”

If the native numbers cannot be read at projection size, use two panel crops and move the full application screenshot to backup. Do not replace the screenshot with only a typed summary table.

### 13 Physical replay checked 104 forecasts and captured a valid transaction

Use the native weather_speed SignalTap detail as the main visual. Mark the accepting handshake and final valid event. Add a genuine short excerpt from the saved replay containing “PASS PHYSICAL JTAG weather_speed: inputs=128 forecasts=104.” Label that excerpt as a saved log, not a new live run.

Say: “The first 24 inputs fill history, leaving 104 forecasts from 128 frames. Scalar and component outputs agreed with the fixed-point reference, and the angle passed the permitted tolerance. SignalTap captured a physical prediction transaction. Its raw edge separation is 41 acquisition intervals; the RTL's documented post-edge latency is 40 cycles. We retain the native STP and decoded CSV so this can be inspected.”

Use the temperature bus 01A72 → raw 6770 → 26.4453125 °C as one readable decoding example. Do not attempt to explain every bus in the talk. A full waveform and latency-convention explanation belong in backup.

### 14 The demonstrated system uses recorded data and fixed coefficients

Use a simple system-boundary drawing. Inside the demonstrated boundary: offline-trained models, recorded-frame JTAG input, five forecast quantities, simulation and physical checks. Place one short future-work line below: “Next extension: live acquisition and broader-location evaluation.”

Say: “The current evidence is for recorded inputs at one location. It does not establish live sensor operation or rainfall probability. We have not measured electrical power or the board's maximum operating frequency. Hourly forecasting does not require sub-microsecond execution; this project demonstrates a verified hardware implementation and its scheduling.”

Keep this factual and brief. Do not spend a full minute listing hypothetical applications.

### 15 The project extends a temperature model into verified weather hardware

Show three short statements with small references back to the corresponding evidence: five reported weather quantities; 40-cycle full latency at 50 MHz; 104 forecasts checked on the physical board. Retain the title and these results during questions.

Say: “The extension required new lag models, wider arithmetic, parallel channels, and a direction-conversion path. The statistical evaluation measures forecast quality; the reference comparisons and board replay measure implementation correctness. The saved Quartus and SignalTap records support the reported implementation results.”

End verbally and invite questions. No separate decorative thank-you slide is needed.

## Evidence map

Paths below are relative to this file. These are the authoritative inputs to the final deck, not invitations to type new values from memory.

| Slides | Source |
| --- | --- |
| 2, 8, 9 | [JTAG interface](../../hardware/jtag/README.md), [weather RTL directory](../../versions/weather_v2/rtl), [technical report](../reports/final_report/FPGA_Forecasting_Final_Report_EN.md) |
| 3 | [Prototype model](../../software/models_cpp/model.json), [prototype metrics](../reports/temperature_metrics.csv), [weather model](../../versions/weather_v2/models/model.json) |
| 4, 5 | [Training and selection code](../../versions/weather_v2/software/train_models.py), [selected model](../../versions/weather_v2/models/model.json), [candidate results](../../versions/weather_v2/reports/validation_candidates.csv) |
| 6, 7 | [Weather RTL](../../versions/weather_v2/rtl), [worked calculation](../reports/final_report/FPGA_Forecasting_Explained_EN.md) |
| 10 | [Implementation verification report](../reports/IMPLEMENTATION_REPORT.md), [SDF manifest](../reports/weather_speed_modelsim_timing.json), [weather testbench directory](../../versions/weather_v2/tb) |
| 11 | [Weather test metrics](../../versions/weather_v2/reports/metrics.csv) |
| 12 | [Native flow summary](../reports/defense_session/screenshots/weather_speed_flow_summary.png), [timing summary](../reports/defense_session/screenshots/weather_speed_timing_summary.png), [Fmax](../reports/defense_session/screenshots/weather_speed_fmax.png), [fit report](../reports/JTAG_IMPLEMENTATION_REPORT.md) |
| 13 | [Native waveform](../reports/defense_session/screenshots/weather_speed_signaltap_detail.png), [physical replay log](../reports/defense_session/weather_speed_physical_replay.txt), [replay CSV](../reports/physical_jtag_weather_speed.csv), [STP capture](../reports/defense_session/signaltap/weather_speed.stp), [decoded waveform](../reports/defense_session/signaltap/weather_speed_decoded.csv), [capture checks](../reports/defense_session/SIGNALTAP_CAPTURE_CHECK.json) |

## Backup slides

Keep these after the main 15 slides, excluded from the planned talk time. Give each a direct link from the relevant main slide if possible.

1. Prototype equation and exact original a, b, c; explain why the current predictor changed.
2. Deployed weather integer coefficients in lag order; full worked fixed-point calculation.
3. Data cutoff rules, valid-history requirements, and validation candidate comparison.
4. Full accuracy table with MAE and RMSE, direction subset, and CORDIC approximation results.
5. Full lane schedule, reset behavior, handshake example, and output alignment.
6. Native Quartus screenshots at full context, with project and measurement boundary identified.
7. Native SignalTap buses, sample indices 215 and 256, and the post-edge observation convention.
8. Saved replay and SDF log excerpts with exact scope and counts; JTAG mailbox request/acknowledgement sequence.

## Delivery and review

A possible three-person split is slides 1–5, 6–10, and 11–15, giving approximately 4:15, 5:30, and 4:30. This is a speaking assignment proposal, not a claim about who implemented each part. Choose the actual assignment based on who can explain and defend the material. All members should understand the full path.

Rehearse to 14:15 with actual slide changes. Use the 45-second margin for natural pauses and speaker changes. If questions are included in the 15-minute slot, shorten the talk to about 12 minutes: reduce prototype detail, move the worked arithmetic and detailed timing schedule into backup, and preserve the result and physical-evidence slides.

For a live board demonstration, replace up to 45 seconds of slide 13 with a pre-rehearsed single replay. Keep the saved waveform and log on the slide as the fallback. Do not add GUI navigation, recompilation, or board setup to the scheduled talk.

Before export, verify: each title states the slide's message; every number matches its named source; every chart carries units and dataset scope; all screenshots are readable; simulation and physical results are labeled separately; there are no future-tense proposal promises; the weather-speed scope stays consistent. Read the title sequence by itself to test the story. Rehearse aloud rather than judging duration from slide count.

The baseline is ready for slide production. It has not yet been turned into a new PPTX or tested in a timed team rehearsal.
