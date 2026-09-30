<!-- ppt-master-schema: design-spec/v1 -->
# CE436 Temperature Forecast Proposal - Design Spec

## I. Project Information

| Item | Value |
| --- | --- |
| Project Name | CE436 Temperature Forecast Proposal |
| Canvas Format | ppt169, 1280 × 720 |
| Page Count | 15 |
| Primary Language | en-US |
| Target Audience | Giảng viên CE436 và sinh viên trong lớp; nhóm thực hiện gồm 3 người, mới học DSP. |
| Communication Intent | Giải thích đề xuất, mô hình tuyến tính, C++ và FPGA, kiểm chứng và kế hoạch 3 tháng. |
| Desired Audience Outcome | Hiểu hệ thống, cách đánh giá, tính khả thi; thầy góp ý phạm vi, board và demo. |
| Core Message / Ask / Action | Dự báo nhiệt độ +3 giờ bằng hệ số học offline trên C++, hiện thực số cố định trong RTL. |
| Delivery Context | English presentation, 15–18 minutes, with speaker notes. |
| Artifact Afterlife | PPTX chỉnh sửa được để luyện nói và cập nhật tiến độ. |
| Reading Mode | balanced |
| Content Strategy | balanced default; giữ toàn bộ ý chính, sắp xếp lại và bổ sung giải thích |
| Design Style | Theo một mẫu nhiệt độ, Technical Deepdive với nhận diện IBM |
| AI Image Acquisition Path | not applicable |
| Generation Mode | continuous |
| Spec Refinement | disabled |
| Speaker Notes | enabled — final Stage-2 proactive policy |
| Custom Animations | disabled — final Stage-2 proactive policy |
| Narration Audio | disabled — final Stage-2 proactive policy |
| Created Date | 2026-09-24 |

- **Template Application**: Áp dụng xanh IBM, trắng/xám và Arial; không logo. Giữ cách giải thích cơ chế và điều kiện của Technical Deepdive. Chọn 01_title_slide.svg cho mở đầu, 05_comparison.svg cho đối chiếu, 06_title_only.svg cho sơ đồ, 12_three_card.svg cho phân công và kiểm chứng, 14_process_timeline.svg cho kế hoạch, 10_hero_statement.svg cho kết luận. Bỏ bố cục ảnh và số liệu mẫu; điều chỉnh nội dung, thứ tự và vùng sơ đồ với Master/Layout và đối tượng chỉnh sửa được. Bổ sung lý do chọn mô hình, trục thời gian, chia dữ liệu, vai trò FPGA và tiêu chí đánh giá, phân biệt đề xuất và kết quả.
- **Confirmed field resolution**: Page Count explicitly edited to 15 takes precedence over the retained 20-page sentence in image_notes. All other image_notes requirements remain: editable diagrams, no invented results or decorative imagery. No appendix quota is retained from the stale page-count sentence.
- **Design Spec Depth**: brief.

- **English revision**: All 15 visible slides and speaker notes are translated from the approved Vietnamese deck; page order, numerical assumptions, model, and visual theme are preserved.

## II. Canvas Specification

| Property | Value |
| --- | --- |
| Format | ppt169 |
| Dimensions | 1280 × 720 |
| viewBox | `0 0 1280 720` |
| Margins | 64 px horizontal, 40 px top, 32 px bottom |
| Content Area | x=64..1216, y=40..680 |

## III. Visual Theme

### Theme Style

- **Mode**: custom
- **Mode References**: instructional
- **Mode Behavior**: Bắt đầu với phạm vi +3 giờ và giới hạn nhóm, theo một mẫu từ quá khứ qua mô hình, số cố định, phần cứng và kiểm chứng; kết thúc bằng kế hoạch và các điểm cần thầy góp ý.
- **Visual style**: custom
- **Visual Style References**: blueprint
- **Visual Style Behavior**: Trục thời gian và các nhánh phép tính chiếm vùng chính; đường dẫn đi từ trái sang phải, mốc đang xét dùng xanh, giải thích sát nhánh tương ứng. Nền trắng, khối xám nhạt, nét chính xác và khoảng trống quanh công thức; vận dụng blueprint trên nền sáng theo IBM.
- **Theme**: Dòng mẫu đi qua phép tính; mốc hiện tại và dự báo nối các trang cơ chế.
- **Tone**: Kỹ thuật, có điều kiện, giải thích rõ cho người mới; nội dung chưa thực nghiệm được ghi rõ.

### Color Scheme

| Role | HEX | Purpose |
| --- | --- | --- |
| Background | #FFFFFF | nền chính |
| Secondary background | #F4F4F4 | vùng nội dung |
| Primary | #0F62FE | nhánh trọng tâm và điểm nhấn |
| Accent | #002D9C | tiêu đề nhấn |
| Secondary accent | #525252 | nhánh phụ |
| Body text | #161616 | chữ chính |
| Secondary text | #525252 | chú thích |
| Divider | #E0E0E0 | đường phân chia |

## IV. Typography System

### Font Plan

| Role | Character (Reference) | Primary | English if non-English | Fallback tail |
| --- | --- | --- | --- | --- |
| Title | technical sans bold | Arial | Arial | sans-serif |
| Body | neutral sans | Arial | Arial | sans-serif |
| Code | monospace for recurring identifiers | Consolas | Consolas | monospace |

- **Title stack**: Arial
- **Body stack**: Arial
- **Code stack**: Consolas
- **Role rationale**: Code separates repeated timestamp and RTL identifiers from prose.

### Font Size Hierarchy

| Purpose | Anchor Size (px) |
| --- | ---: |
| Body | 28 |
| Title | 50 |
| Subtitle | 38 |
| Annotation | 22 |
| Lead | 30 |
| Footnote | 16 |
| Code | 26 |
| Display | 72 |

## V. Layout Principles

### Deck-wide Direction

- **Hierarchy direction**: Một ý chính, cơ chế lớn, chú thích sát dữ liệu, điều kiện dưới cùng.
- **Composition tendency**: Trục thời gian, nhánh phép tính, đối chiếu, trình tự dự án theo ý nghĩa từng trang.
- **Cross-page continuity**: Cùng chiều luồng mẫu và vị trí các mốc khi cơ chế tiếp tục.
- **Spacing posture**: Thay đổi theo độ sâu, trang ví dụ và kết luận thoáng hơn trang kỹ thuật.
- **Spacing anchors**: page margin 64; block gap 24; column gutter 40; corner radius 4; body leading 38.

Adaptive structure definitions: cover-expanded expands title/subtitle zones for Vietnamese copy; schematic-title retains the title-only rule and title zone with a slide-number slot. compare-proof retains paired panels with heading/content slots. three-columns retains three-card panels with their three object slots. four-milestones retains the four milestone axis and content slots. closing-proof adapts the hero panel into title plus two proof lines and a question rail. All add a slide-number slot at 1140 668 76 28; these changes are declared before SVG authoring.

## VI. Icon Usage Specification

- **Primary bundled library**: tabler-outline
- **Stroke Width**: 2

| Icon Path | Suitable Scenarios |
| --- | --- |
| tabler-outline/thermometer | nhiệt độ |
| tabler-outline/cpu | FPGA |
| tabler-outline/database | dữ liệu |
| tabler-outline/checklist | kiểm chứng |

## VIII. Image Resource List

No image resources: confirmed image_usage none. Diagrams remain editable.

| Filename | Dimensions | Ratio | Purpose | Type | Image pattern | Crop Policy | Acquire Via | Status | Reference | text_policy | page_role |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## IX. Content Outline

### Part 1: Đề xuất và cơ chế đến kiểm chứng

#### Slide 01 - DỰ BÁO NHIỆT ĐỘ SAU 3 GIỜ TRÊN FPGA

- **Audience move**: Chưa biết đề tài → nắm mục tiêu +3 giờ và phạm vi buổi đề xuất.
- **Relationships**: Dữ liệu quá khứ dẫn đến dự báo tương lai.
- **Composition**: 01_title_slide.svg; schematic dominant where useful, explanation adjacent.
- **Title**: DỰ BÁO NHIỆT ĐỘ SAU 3 GIỜ TRÊN FPGA
- **Core message**: Một mô hình tuyến tính từ các giá trị quá khứ, hiện thực bằng C++ và RTL.
- **Page rhythm**: anchor
- **Content**:
  - CE436 • Báo cáo đề xuất buổi 1
  - Mô hình tuyến tính từ các giá trị quá khứ
  - 3 thành viên • 12 tuần • C++ + Verilog/SystemVerilog
- **Cover impact**: +3 giờ is the hook; show past samples leading to a forecast.

#### Slide 02 - Chọn một bài toán có thể kiểm chứng

- **Audience move**: Tên đề tài rộng → biết chính xác đầu vào và đầu ra.
- **Relationships**: Chủ đề gốc bao gồm nhánh dự báo nhiệt độ; đầu vào theo giờ đến t dẫn đến một đầu ra t+3.
- **Composition**: 06_title_only.svg; schematic dominant where useful, explanation adjacent.
- **Title**: Chọn một bài toán có thể kiểm chứng
- **Core message**: Thu hẹp chủ đề thời tiết thành dự báo nhiệt độ tại một địa điểm.
- **Page rhythm**: dense
- **Content**:
  - Chủ đề gốc: Weather Pattern Forecasting on FPGA using Time Series Analysis.
  - Đầu vào: chuỗi nhiệt độ theo giờ tại một tọa độ; đầu ra: nhiệt độ sau 3 giờ, đơn vị °C.
  - Lý do: phép tính tuyến tính dễ đối chiếu C++ và RTL, phù hợp giới hạn 3 tháng của nhóm mới học DSP.
  - Mô hình đơn biến, hệ số cố định; độ ẩm/áp suất là mở rộng có điều kiện. FPGA là mục tiêu thực hành số học và kiểm chứng, chưa có bằng chứng lợi ích tốc độ cho dữ liệu theo giờ.

#### Slide 03 - C++ học hệ số, FPGA tính dự báo

- **Audience move**: Biết mục tiêu → hình dung hệ thống và sản phẩm.
- **Relationships**: CSV đi tới C++ để tìm hệ số; hệ số đi tới FPGA; mẫu đầu vào đi qua FPGA để tạo dự báo và đối chiếu.
- **Composition**: 06_title_only.svg; schematic dominant where useful, explanation adjacent.
- **Title**: C++ học hệ số, FPGA tính dự báo
- **Core message**: Huấn luyện offline và suy luận trên FPGA có vai trò tách biệt.
- **Page rhythm**: dense
- **Content**:
  - C++: kiểm dữ liệu → baseline → tìm hệ số → mô hình số cố định và test vector.
  - FPGA: nhận mẫu → lưu lịch sử → tính dự báo; hệ số giữ cố định khi chạy.
  - Sản phẩm: chương trình C++, RTL, testbench, demo board và báo cáo sai số/tài nguyên.

#### Slide 04 - Linear model with diurnal anchor & taps

- **Audience move**: Understand the consolidated formula, tap physical meanings, and numerical computation in one unified view.
- **Relationships**: t−24, t−21, t−3, t are past/present inputs; t+3 is future target; t−21 is the diurnal anchor.
- **Composition**: schematic-title; formula, taps explanation, and arithmetic example side-by-side.
- **Title**: Linear model with diurnal anchor & taps
- **Core message**: Consolidate formula, tap meanings, and numerical example into one clear slide.
- **Page rhythm**: dense
- **Content**:
  - Diurnal anchor: T(t−21), same hour yesterday relative to target t+3.
  - Inter-day trend: a[T(t) − T(t−24)]; short-term gradient: b[T(t) − T(t−3)]; offset c.
  - Numerical walkthrough: 21 + 0.5(1) + 0.2(2) = 21.9°C.
  - 25-sample buffer requirement; target stays on PC.
- **Mathematical content**: \widehat{T}(t+3)=T(t-21)+a[T(t)-T(t-24)]+b[T(t)-T(t-3)]+c
- **Hyperlinks**: NASA POWER → https://power.larc.nasa.gov/docs/services/api/temporal/hourly/

#### Slide 05 - Train on the past, test on the future

- **Audience move**: Understand how weights are fitted offline and why chronological splitting prevents data leakage.
- **Relationships**: Train fits weights; validation tunes Q-format; test evaluates final generalization.
- **Composition**: schematic-title; OLS formulation and 3-stage chronological split.
- **Title**: Train on the past, test on the future
- **Core message**: Strict chronological partition prevents future leakage; OLS solved in C++.
- **Page rhythm**: dense
- **Content**:
  - Regression inputs: x1 = T(t)−T(t−24), x2 = T(t)−T(t−3), y = T(t+3)−T(t−21).
  - Least squares solved offline using C++ (Eigen library).
  - Train (weeks 1–3), Validation (weeks 4–6), Test (held-out future).
  - Buffer context crosses split boundaries without label leakage.
- **Mathematical content**: y\approx ax_1+bx_2+c
- **Hyperlinks**: Eigen least squares → https://eigen.tuxfamily.org/dox/group__LeastSquares.html

#### Slide 06 - Algorithmic baseline benchmarking

- **Audience move**: Learn the standard for proving model usefulness against simple alternatives.
- **Relationships**: Proposed model compared directly with Persistence and Diurnal heuristics on the same test set.
- **Composition**: schematic-title; left card defines MAE and question, right card defines baselines.
- **Title**: Algorithmic baseline benchmarking
- **Core message**: Benchmark against Persistence and Diurnal baselines to verify predictive value.
- **Page rhythm**: breathing
- **Content**:
  - Metric: Mean Absolute Error (MAE in °C) on identical test period.
  - Baseline 1: Persistence T(t) — temperature stays constant.
  - Baseline 2: Diurnal T(t−21) — today repeats yesterday at the same hour.
  - Scientific integrity: analyze residuals and report honestly if linear model does not beat baselines.
- **Mathematical content**: \mathrm{MAE}=\frac{1}{N}\sum_{i=1}^{N}|\widehat{T}_i-T_i|
- **Hyperlinks**: Forecasting: simple methods → https://otexts.com/fpp3/simple-methods.html

#### Slide 07 - Fixed-point starts with value ranges

- **Audience move**: Understand how hardware arithmetic format is chosen and how bit-exactness is achieved.
- **Relationships**: Float range profiling leads to Q-format selection and matching C++/RTL arithmetic rules.
- **Composition**: schematic-title; 3-step pipeline and golden verification principle.
- **Title**: Fixed-point starts with value ranges
- **Core message**: Range profiling dictates wordlength; C++ fixed-point golden model guarantees bit-exact RTL.
- **Page rhythm**: dense
- **Content**:
  - Step 1: Profile dataset min/max, negative winter values, weight dynamic ranges.
  - Step 2: Choose signed Q-format (integer guard bits + fractional resolution, e.g. Q8.8/Q10.6).
  - Step 3: Define multiplier bit-growth, shift truncation, and saturation rules.
  - Verification principle: Separate forecast error from quantization noise; achieve 100% bit-exact RTL match.

#### Slide 08 - Core MVP vs. Advanced extensions

- **Audience move**: See how the project is de-risked into a guaranteed Phase 1 MVP and ambitious Phase 2 extensions.
- **Relationships**: Phase 1 provides a safe working baseline; Phase 2 expands feature and architectural scope.
- **Composition**: compare-proof; two balanced columns contrasting Phase 1 vs. Phase 2.
- **Title**: Core MVP vs. Advanced extensions
- **Core message**: Two-phase strategy guarantees baseline success while providing engineering depth for 3 students.
- **Page rhythm**: dense
- **Content**:
  - Phase 1 Core MVP (Weeks 1–6): Single-variable temperature predictor, 25-stage shift register, bit-exact C++ model, synthesizable RTL.
  - Phase 2 Advanced Extensions (Weeks 7–12): Multi-variable inputs (RH + P), hardware trade-off study (Parallel vs Shared MAC), code coverage DV.
  - Deliverable Milestone 2 secures working silicon early; Milestone 4 delivers comprehensive depth.

#### Slide 09 - From sample history to arithmetic core

- **Audience move**: Connect mathematical taps to actual FPGA datapath blocks and control signals.
- **Relationships**: Shift register taps feed subtraction stages, multipliers, and pipelined adder tree.
- **Composition**: schematic-title; shift register buffer and pipelined arithmetic datapath.
- **Title**: From sample history to arithmetic core
- **Core message**: 25-sample buffer feeds parallel subtraction and multiplication with pipelined saturation.
- **Page rhythm**: dense
- **Content**:
  - Buffer stores T(t−24)...T(t); taps at t−24, t−21, t−3, t.
  - Pipelined datapath: 2 subtractors, 2 multipliers (fixed coefficients), adder tree with saturation.
  - Valid handshake: forecast asserted only after 25 valid samples.
  - Sample delay (1 hour in data) vs. hardware latency (2–4 clock cycles).

#### Slide 10 - Demo by replaying historical data

- **Audience move**: Understand how the hardware demo operates without waiting 3 real hours.
- **Relationships**: Host PC streams historical CSV over UART; FPGA computes forecast; PC scoreboard evaluates live.
- **Composition**: schematic-title; three-block diagram showing PC, FPGA board, and scoreboard.
- **Title**: Demo by replaying historical data
- **Core message**: Accelerated replay over UART demonstrates 1,000+ predictions in under 2 minutes.
- **Page rhythm**: dense
- **Content**:
  - Host PC reads CSV chronologically, streams samples up to time t via UART.
  - FPGA processes samples through shift register and arithmetic core, returns forecast via UART.
  - Host scoreboard matches prediction with future label T(t+3) and plots real-time error curve.
  - No data leakage: target label never enters the FPGA.

#### Slide 11 - Three verification layers

- **Audience move**: See how verification progresses systematically from math to simulation to hardware.
- **Relationships**: C++ checks quantization; Testbench checks RTL logic; Board test checks hardware integration.
- **Composition**: three-columns; three structured cards for C++, Simulation, and Board verification.
- **Title**: Three verification layers
- **Core message**: Three distinct verification layers validate quantization, RTL bit-exactness, and physical I/O.
- **Page rhythm**: dense
- **Content**:
  - Layer 1 (C++): Float vs. Fixed comparison, quantization SNR loss, dynamic range stress tests.
  - Layer 2 (Simulation): Testbench vs. RTL core, cycle-by-cycle valid handshake, 100% bit-exact target.
  - Layer 3 (Board): Board vs. Reference, UART timing, packet endianness, live scoreboard verification.
  - Shared test vectors across all three layers.

#### Slide 12 - Hardware micro-architecture trade-off study

- **Audience move**: Understand the engineering trade-off between throughput and area in hardware implementation.
- **Relationships**: Architecture A (Parallel DSP) maximizes throughput; Architecture B (Shared-MAC FSM) minimizes area.
- **Composition**: schematic-title; side-by-side comparison cards for Arch A and Arch B.
- **Title**: Hardware micro-architecture trade-off study
- **Core message**: Compare Parallel DSP datapath vs. Resource-Shared Single-MAC FSM across LUTs, DSPs, and Fmax.
- **Page rhythm**: breathing
- **Content**:
  - Arch A (Parallel DSP): Dedicated multipliers per feature, 2-cycle latency, 1 prediction/cycle throughput, higher DSP/LUT cost. Target: high-speed multi-channel sensing.
  - Arch B (Shared-MAC FSM): Time-multiplexed single MAC, FSM controller, 5–6 cycle latency, minimal area (1 DSP or 0 DSPs via LUTs). Target: ultra-low-power edge IoT.
  - Provides deep RTL/DV exploration justifying 3 team members.

#### Slide 13 - 12 weeks, upgraded two-phase milestones

- **Audience move**: Review the detailed 12-week schedule with concrete deliverables at every 3-week milestone.
- **Relationships**: Chronological progression from data foundations to Phase 1 MVP, Phase 2 expansion, and final demo.
- **Composition**: four-milestones; horizontal timeline with four milestone nodes and summary banner.
- **Title**: 12 weeks, upgraded two-phase milestones
- **Core message**: Four clear 3-week milestones guarantee baseline delivery by Week 6 and advanced scope by Week 12.
- **Page rhythm**: dense
- **Content**:
  - Weeks 1–3 (M1): Data cleaning, baseline models, C++ floating-point OLS training.
  - Weeks 4–6 (M2): Fixed-point profiling, synthesizable RTL core, bit-exact TB, Phase 1 MVP complete.
  - Weeks 7–9 (M3): Multi-variable data (RH, P), Shared-MAC FSM, architectural trade-off study, UART RTL.
  - Weeks 10–12 (M4): Live UART PC demo, DV code coverage, synthesis resource reports, final defense.

#### Slide 14 - Three students, two-phase workload

- **Audience move**: See how tasks are distributed across 3 students in both Phase 1 and Phase 2.
- **Relationships**: Student 1 (Algorithms/Data), Student 2 (RTL/Architecture), Student 3 (DV/Demo).
- **Composition**: three-columns; three role cards showing Phase 1 and Phase 2 duties for each student.
- **Title**: Three students, two-phase workload
- **Core message**: Clear role ownership across both phases justifies 3 students and ensures accountability.
- **Page rhythm**: dense
- **Content**:
  - Student 1: Data & Algorithms — Phase 1: CSV, baselines, OLS, C++ golden model; Phase 2: Multi-var features, ARX, SNR.
  - Student 2: RTL & Architecture — Phase 1: 25-stage buffer, pipelined core, saturation; Phase 2: Shared-MAC FSM, trade-off synthesis.
  - Student 3: DV & Demo — Phase 1: Test vector suite, bit-exact TB; Phase 2: UART controller, live GUI scoreboard, code coverage.
  - Shared arithmetic contract agreed at project kickoff.

#### Slide 15 - One forecast, two claims to verify

- **Audience move**: Understand the core commitments and the concrete feedback requested from the instructor.
- **Relationships**: Two rigorous verification claims (forecast quality and RTL correctness) lead to three instructor questions.
- **Composition**: closing-proof; hero statement card with two verification pillars and question footer.
- **Title**: One forecast, two claims to verify
- **Core message**: Prove forecast value against baselines and prove hardware bit-exactness against golden model.
- **Page rhythm**: anchor
- **Content**:
  - Phased Linear Model predicting temperature 3 hours ahead.
  - Claim 1 (Forecast Quality): Outperform naive baselines on unseen future test data.
  - Claim 2 (Hardware Correctness): RTL matches C++ fixed-point golden model bit-for-bit.
  - Questions for instructor: Confirm 3-hour scope, FPGA board/tools, and minimum demo expectations.
- **Closing impact**: Two distinct proofs and three concrete questions for the teacher.

## X. Speaker Notes Requirements

- **Generation**: enabled
- **Filename**: match each SVG filename under notes/
- **Content**: Vietnamese natural presenter script, definitions and transitions, source links on relevant slides, no invented measured results. Preserve factual content from source notes and elaborate newly clarified mechanisms.
- **Total duration**: 15–18 minutes, timing guides per page, verify by rehearsal.
- **Notes style**: conversational academic, accessible to a beginner.
- **Presentation purpose**: Explain the proposal, mechanisms, verification and feasible 3-month work plan; obtain scope, board and demo feedback.
