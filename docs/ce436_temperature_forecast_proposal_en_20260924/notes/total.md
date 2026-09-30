# 01_cover

Good afternoon, Professor and classmates. Our group proposes a three-hour-ahead temperature forecasting system on FPGA using a linear time-series model built from past values. This is a focused, rigorous realization of the assigned weather forecasting topic. Today we present our proposed algorithmic model, hardware micro-architecture, and upgraded twelve-week execution plan.

---

# 02_scope

We deliberately narrow the broad weather forecasting topic down to hourly temperature at a specific geographic location. At hour t, the model ingests observations available up to t and outputs a forecast for t plus three hours in degrees Celsius. A linear model provides clear, auditable arithmetic that we can reproduce identically in C++ and RTL within three months. FPGA speedup is not our claim for data that arrives only once an hour; our real objective is mastering the complete model-to-hardware workflow.

---

# 03_system

The system separates offline algorithmic training from FPGA runtime inference. Offline in C++, we clean the NASA CSV dataset, establish baseline metrics, solve for model weights using least squares, and generate a bit-exact fixed-point golden reference alongside test vectors. The FPGA accepts sequential samples, buffers the history, and computes predictions with fixed coefficients on-chip. Our tangible deliverables include the C++ reference suite, synthesizable RTL, testbench, board demo, and comprehensive resource report.

---

# 04_samples

This slide consolidates our mathematical model, physical tap meanings, and arithmetic execution. Relative to our forecast target at t plus three hours, the sample at t minus twenty-one hours acts as the diurnal anchor—exactly the same hour yesterday. The difference T(t) minus T(t minus twenty-four) captures the day-to-day trend, while T(t) minus T(t minus three) tracks the recent three-hour temperature gradient. In our numerical walkthrough, past temperatures of nineteen, twenty-one, eighteen, and twenty degrees Celsius with weights zero-point-five and zero-point-two yield a forecast of twenty-one point nine degrees Celsius through subtraction, multiplication, and an adder tree. A twenty-five sample buffer stores samples t minus twenty-four through t, while the future target stays strictly on the host PC.

---

# 05_model

We formulate the model as an Ordinary Least Squares problem: x one is the day-to-day change, x two is the recent three-hour change, and target y is the offset from the diurnal anchor. C++ fits weights a, b, and constant c on historical training data using the Eigen library. To prevent look-ahead data leakage, we enforce a strict chronological split into training, validation, and held-out test periods. Previously observed history crosses split boundaries only as input buffer context, never as future labels.

---

# 06_example

To establish scientific value, we must answer whether our linear model outperforms simple, no-math heuristics. We evaluate all methods using Mean Absolute Error in degrees Celsius across identical test timestamps. We benchmark against two naive baselines: Persistence, which assumes the temperature remains unchanged from t, and Diurnal, which assumes today exactly repeats yesterday at the same hour. If our linear model does not outperform these baselines, we analyze the residuals and report the findings with full academic integrity.

---

# 07_training

Fixed-point hardware implementation begins by profiling dynamic ranges across historical records: capturing sub-zero winter temperatures, peak summer heat, and coefficient magnitudes. We select an optimal signed Q-format, such as Q8.8 or Q10.6, balancing integer headroom against fractional precision. Our C++ fixed-point golden model mirrors every RTL truncation, shift, and saturation rule bit-for-bit. This separates statistical forecasting error against ground truth from quantization noise against floating point, enabling one hundred percent bit-exact RTL verification.

---

# 08_evaluation

To ensure project feasibility while demonstrating substantial engineering depth for three students, we divide our roadmap into two distinct phases. Phase one is our Core MVP, executed during Weeks one through six. It establishes a guaranteed working baseline: a single-variable temperature predictor, a twenty-five stage shift register buffer, and a synthesizable RTL core verified against C++. Phase two, running from Weeks seven to twelve, expands into advanced extensions: multi-variable features including relative humidity and pressure, an architectural trade-off study, and code-coverage verification. This two-phase strategy eliminates semester failure risk early.

---

# 09_fixed_point

Here we map the mathematical taps directly to the hardware datapath. A twenty-five stage shift register receives incoming samples when valid is asserted. Dedicated taps extract the four required indices, feeding two subtraction stages, two fixed-coefficient multipliers, and a pipelined adder tree with saturation logic. A delay of one sample represents one real-world hour in data, whereas hardware latency is only two to four clock cycles. The circuit produces a forecast in nanoseconds, never waiting three real hours.

---

# 10_architecture

Our hardware demonstration replays historical CSV records from a host PC to the FPGA in accelerated time. Samples are transmitted via UART milliseconds apart rather than hours apart, allowing us to demonstrate over one thousand sequential predictions in under two minutes. The FPGA processes each incoming sample, updates its buffer, and streams back the forecast. A host Python dashboard compares the prediction against the held-out target label and plots live error curves without any future data leakage.

---

# 11_verification

Verification proceeds across three hierarchical layers using identical test vectors. In Layer one, C++ compares floating-point against fixed-point arithmetic to measure quantization noise and test boundary conditions. In Layer two, the RTL simulation testbench verifies cycle-by-cycle valid handshakes, reset behavior, and buffer warm-up, requiring zero bit differences against the golden model. In Layer three, physical board tests validate UART timing, packet byte order, and end-to-end scoreboard synchronization.

---

# 12_demo

As part of our Phase two engineering exploration, we conduct an architectural trade-off study comparing two distinct micro-architectures. Architecture A implements a fully parallel pipelined DSP datapath with dedicated multipliers for maximum throughput, targeting high-speed multi-channel sensing. Architecture B implements a resource-shared single-MAC architecture driven by a finite state machine, time-multiplexing multiplications into a single DSP slice or LUT-based multiplier. We will synthesize both architectures on our target FPGA and compare LUTs, DSP slices, and maximum operating frequency.

---

# 13_schedule

Our upgraded twelve-week schedule establishes four concrete milestones, each yielding a working deliverable. Weeks one to three deliver clean NASA data, baselines, and C++ floating-point training. Weeks four to six complete the Phase one Core MVP with a synthesizable RTL core and bit-exact simulation. Weeks seven to nine advance Phase two with multi-variable modeling, the shared-MAC architecture, and UART controller integration. Weeks ten to twelve finalize the live hardware demonstration, code coverage, synthesis resource analysis, and defense report.

---

# 14_team_risks

The workload is evenly distributed across three students across both project phases. Student One leads algorithms and data, delivering the C++ golden model in Phase one and multi-variable modeling in Phase two. Student Two leads RTL design, building the pipelined datapath in Phase one and conducting the architectural trade-off study in Phase two. Student Three leads verification and demo, constructing the bit-exact testbench in Phase one and integrating the UART controller and live PC dashboard in Phase two. All interfaces and arithmetic conventions are agreed upon at kickoff.

---

# 15_conclusion

In summary, our project delivers a three-hour-ahead temperature forecasting system on FPGA, rigorously backed by two distinct proofs: proving forecasting quality against naive baselines on unseen data, and proving hardware correctness bit-for-bit against a golden fixed-point model. Before we proceed, we welcome the professor's feedback on our three-hour prediction scope, recommended FPGA board and toolchain, and minimum demo expectations. Thank you for your time, and we look forward to your guidance.
