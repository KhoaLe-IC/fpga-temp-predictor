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

- **Redesign revision**: Preserve the 15 English slide topics and technical claims; make on-slide copy sparse and readable from a room, use larger type and visual relationships, and move explanation into existing speaker notes. The prototype must be ready early; weeks 4–12 emphasize evaluation and hardware design comparisons. The redesign is flat and keeps IBM blue/white styling without a logo.

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
- **Role rationale**: Code separates timestamps and RTL identifiers; the named lead/display roles keep recurrent diagram labels and equations large enough to read from the room.

### Font Size Hierarchy

| Purpose | Anchor Size (px) |
| --- | ---: |
| Body | 30 |
| Title | 50 |
| Subtitle | 38 |
| Annotation | 24 |
| Lead | 30 |
| Footnote | 18 |
| Code | 26 |
| Display | 72 |
| Technical lead | 34 |
| Visual lead | 35 |
| Metric display | 45 |
| Math display | 47 |
| Step number | 53 |
| Example value | 42 |

## V. Layout Principles

### Deck-wide Direction

- **Hierarchy direction**: Một ý chính, cơ chế lớn, chú thích sát dữ liệu, điều kiện dưới cùng.
- **Composition tendency**: Trục thời gian, nhánh phép tính, đối chiếu, trình tự dự án theo ý nghĩa từng trang.
- **Cross-page continuity**: Cùng chiều luồng mẫu và vị trí các mốc khi cơ chế tiếp tục.
- **Spacing posture**: Thay đổi theo độ sâu, trang ví dụ và kết luận thoáng hơn trang kỹ thuật.
- **Spacing anchors**: page margin 64; block gap 24; column gutter 40; corner radius 4; body leading 38.

The redesign uses flat, fully editable slides. Major labels are 27–60 px; supporting detail is spoken from notes. Each page contains one question or mechanism and a diagram sized for projection.

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

### Part 1: English proposal redesign

#### Slide 01 - TEMPERATURE FORECAST ON FPGA

- **Audience move**: Understand temperature forecast on fpga.
- **Relationships**: past → now → forecast.
- **Composition**: Large-type diagram or single comparison; details move to speaker notes.
- **Title**: TEMPERATURE FORECAST ON FPGA
- **Core message**: +3 h forecast from past hourly values; 3 students, 12 weeks.
- **Page rhythm**: cover
- **Content**:
  - +3 h forecast from past hourly values; 3 students, 12 weeks.

#### Slide 02 - A testable forecasting task

- **Audience move**: Understand a testable forecasting task.
- **Relationships**: input → output.
- **Composition**: Large-type diagram or single comparison; details move to speaker notes.
- **Title**: A testable forecasting task
- **Core message**: Hourly temperature at one location through t → temperature at t+3 h.
- **Page rhythm**: content
- **Content**:
  - Hourly temperature at one location through t → temperature at t+3 h.

#### Slide 03 - C++ trains. FPGA forecasts.

- **Audience move**: Understand c++ trains. fpga forecasts..
- **Relationships**: offline → runtime.
- **Composition**: Large-type diagram or single comparison; details move to speaker notes.
- **Title**: C++ trains. FPGA forecasts.
- **Core message**: PC cleans data and fits a,b,c; FPGA applies fixed coefficients to new samples.
- **Page rhythm**: content
- **Content**:
  - PC cleans data and fits a,b,c; FPGA applies fixed coefficients to new samples.

#### Slide 04 - Four past values. One future target.

- **Audience move**: Understand four past values. one future target..
- **Relationships**: time order.
- **Composition**: Large-type diagram or single comparison; details move to speaker notes.
- **Title**: Four past values. One future target.
- **Core message**: t−24, t−21, t−3, t are inputs; t+3 is the future target; 25 samples are stored.
- **Page rhythm**: content
- **Content**:
  - t−24, t−21, t−3, t are inputs; t+3 is the future target; 25 samples are stored.

#### Slide 05 - A linear model from past values

- **Audience move**: Understand a linear model from past values.
- **Relationships**: anchor + two corrections.
- **Composition**: Large-type diagram or single comparison; details move to speaker notes.
- **Title**: A linear model from past values
- **Core message**: T̂(t+3)=T(t−21)+a[T(t)−T(t−24)]+b[T(t)−T(t−3)]+c.
- **Page rhythm**: content
- **Content**:
  - T̂(t+3)=T(t−21)+a[T(t)−T(t−24)]+b[T(t)−T(t−3)]+c.

#### Slide 06 - How is one forecast computed?

- **Audience move**: Understand how is one forecast computed?.
- **Relationships**: inputs → arithmetic → output.
- **Composition**: Large-type diagram or single comparison; details move to speaker notes.
- **Title**: How is one forecast computed?
- **Core message**: Illustrative arithmetic produces 21.9°C; values are not measured results.
- **Page rhythm**: breathing
- **Content**:
  - Illustrative arithmetic produces 21.9°C; values are not measured results.

#### Slide 07 - Train on the past. Test on the future.

- **Audience move**: Understand train on the past. test on the future..
- **Relationships**: train → validate → test.
- **Composition**: Large-type diagram or single comparison; details move to speaker notes.
- **Title**: Train on the past. Test on the future.
- **Core message**: Fit a,b,c by least squares; chronological train, validation, test prevents future-label leakage.
- **Page rhythm**: content
- **Content**:
  - Fit a,b,c by least squares; chronological train, validation, test prevents future-label leakage.

#### Slide 08 - Does the model beat simple forecasts?

- **Audience move**: Understand does the model beat simple forecasts?.
- **Relationships**: three methods → one metric.
- **Composition**: Large-type diagram or single comparison; details move to speaker notes.
- **Title**: Does the model beat simple forecasts?
- **Core message**: Compare T(t), T(t−21), and the proposed model by MAE on identical held-out test timestamps.
- **Page rhythm**: content
- **Content**:
  - Compare T(t), T(t−21), and the proposed model by MAE on identical held-out test timestamps.

#### Slide 09 - Fixed-point needs an explicit contract

- **Audience move**: Understand fixed-point needs an explicit contract.
- **Relationships**: representation → implementation.
- **Composition**: Large-type diagram or single comparison; details move to speaker notes.
- **Title**: Fixed-point needs an explicit contract
- **Core message**: C++ float → C++ fixed → RTL; specify signedness, widths, rounding, overflow.
- **Page rhythm**: content
- **Content**:
  - C++ float → C++ fixed → RTL; specify signedness, widths, rounding, overflow.

#### Slide 10 - From sample history to arithmetic

- **Audience move**: Understand from sample history to arithmetic.
- **Relationships**: buffer → branches → sum.
- **Composition**: Large-type diagram or single comparison; details move to speaker notes.
- **Title**: From sample history to arithmetic
- **Core message**: 25-sample buffer provides taps for two weighted differences and the final sum; valid controls sample acceptance.
- **Page rhythm**: content
- **Content**:
  - 25-sample buffer provides taps for two weighted differences and the final sum; valid controls sample acceptance.

#### Slide 11 - Three verification layers

- **Audience move**: Understand three verification layers.
- **Relationships**: C++ → TB → board.
- **Composition**: Large-type diagram or single comparison; details move to speaker notes.
- **Title**: Three verification layers
- **Core message**: C++ quantization, testbench bit-exactness, board integration use the same vectors.
- **Page rhythm**: content
- **Content**:
  - C++ quantization, testbench bit-exactness, board integration use the same vectors.

#### Slide 12 - Replay historical data for the demo

- **Audience move**: Understand replay historical data for the demo.
- **Relationships**: PC → FPGA → PC.
- **Composition**: Large-type diagram or single comparison; details move to speaker notes.
- **Title**: Replay historical data for the demo
- **Core message**: PC sends samples in order, FPGA forecasts, PC compares; future labels stay on the PC.
- **Page rhythm**: content
- **Content**:
  - PC sends samples in order, FPGA forecasts, PC compares; future labels stay on the PC.

#### Slide 13 - 12 weeks. Prototype early. Evaluate deeply.

- **Audience move**: Understand 12 weeks. prototype early. evaluate deeply..
- **Relationships**: four milestones.
- **Composition**: Large-type diagram or single comparison; details move to speaker notes.
- **Title**: 12 weeks. Prototype early. Evaluate deeply.
- **Core message**: Weeks 1–3 prototype; 4–6 model/fixed-point; 7–9 verification/trade-offs; 10–12 board/report.
- **Page rhythm**: content
- **Content**:
  - Weeks 1–3 prototype; 4–6 model/fixed-point; 7–9 verification/trade-offs; 10–12 board/report.

#### Slide 14 - Three students. Clear ownership.

- **Audience move**: Understand three students. clear ownership..
- **Relationships**: three parallel roles.
- **Composition**: Large-type diagram or single comparison; details move to speaker notes.
- **Title**: Three students. Clear ownership.
- **Core message**: Data/C++, fixed-point/RTL, verification/demo have named owners and a shared arithmetic contract.
- **Page rhythm**: content
- **Content**:
  - Data/C++, fixed-point/RTL, verification/demo have named owners and a shared arithmetic contract.

#### Slide 15 - One forecast. Two things to prove.

- **Audience move**: Understand one forecast. two things to prove..
- **Relationships**: two proofs → three questions.
- **Composition**: Large-type diagram or single comparison; details move to speaker notes.
- **Title**: One forecast. Two things to prove.
- **Core message**: Show forecast quality on unseen data and hardware correctness against C++ fixed; ask for scope, board, demo feedback.
- **Page rhythm**: ending
- **Content**:
  - Show forecast quality on unseen data and hardware correctness against C++ fixed; ask for scope, board, demo feedback.
## X. Speaker Notes Requirements

- **Generation**: enabled
- **Filename**: match each SVG filename under notes/
- **Content**: English natural presenter script, definitions and transitions, source links on relevant slides, no invented measured results. Preserve factual content from source notes and elaborate newly clarified mechanisms.
- **Total duration**: 15–18 minutes, timing guides per page, verify by rehearsal.
- **Notes style**: conversational academic, accessible to a beginner.
- **Presentation purpose**: Explain the proposal, mechanisms, verification and feasible 3-month work plan; obtain scope, board and demo feedback.
