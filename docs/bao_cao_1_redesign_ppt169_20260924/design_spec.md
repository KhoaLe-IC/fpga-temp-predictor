<!-- ppt-master-schema: design-spec/v1 -->
# CE436 Temperature Forecast Proposal - Design Spec

## I. Project Information

| Item | Value |
| --- | --- |
| Project Name | CE436 Temperature Forecast Proposal |
| Canvas Format | ppt169, 1280 × 720 |
| Page Count | 15 |
| Primary Language | vi-VN |
| Target Audience | Giảng viên CE436 và sinh viên trong lớp; nhóm thực hiện gồm 3 người, mới học DSP. |
| Communication Intent | Giải thích đề xuất, mô hình tuyến tính, C++ và FPGA, kiểm chứng và kế hoạch 3 tháng. |
| Desired Audience Outcome | Hiểu hệ thống, cách đánh giá, tính khả thi; thầy góp ý phạm vi, board và demo. |
| Core Message / Ask / Action | Dự báo nhiệt độ +3 giờ bằng hệ số học offline trên C++, hiện thực số cố định trong RTL. |
| Delivery Context | Trình bày tiếng Việt 15–18 phút, có người nói và ghi chú. |
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

#### Slide 04 - Bốn mốc quá khứ, một đích +3 giờ

- **Audience move**: Dễ nhầm chỉ số → đọc đúng các mốc trên trục thời gian.
- **Relationships**: t−24, t−21, t−3, t là quá khứ/hiện tại; t+3 là nhãn tương lai; t+3 cách t−21 đúng 24 giờ.
- **Composition**: 06_title_only.svg; schematic dominant where useful, explanation adjacent.
- **Title**: Bốn mốc quá khứ, một đích +3 giờ
- **Core message**: Mốc t−21 là cùng giờ ngày trước của thời điểm cần dự báo.
- **Page rhythm**: dense
- **Content**:
  - Nguồn dự kiến: NASA POWER, T2M theo giờ; tọa độ và khoảng dữ liệu chưa chốt. Đây là dữ liệu lưới, không phải đo tại đúng một cảm biến.
  - Kiểm tra mốc giờ, giờ thiếu/lặp và đơn vị trước khi tạo mẫu.
  - Dùng t−24, t−21, t−3, t; chỉ dùng giá trị thực t+3 để đánh giá.
  - Giữ 25 mẫu liên tiếp để truy cập các mốc đến t−24.
- **Mathematical content**: t+3-24=t-21
- **Hyperlinks**: NASA POWER → https://power.larc.nasa.gov/docs/services/api/temporal/hourly/

#### Slide 05 - Mô hình tuyến tính từ quá khứ

- **Audience move**: Biết mốc dữ liệu → giải thích được từng thành phần công thức.
- **Relationships**: Mốc cùng giờ ngày trước cộng hiệu chỉnh liên ngày, xu hướng gần và độ lệch hằng.
- **Composition**: 06_title_only.svg; schematic dominant where useful, explanation adjacent.
- **Title**: Mô hình tuyến tính từ quá khứ
- **Core message**: Dùng mốc ngày trước và hai độ lệch để hiệu chỉnh dự báo.
- **Page rhythm**: dense
- **Content**:
  - T(t−21): mốc cùng giờ ngày trước.
  - a[T(t)−T(t−24)]: điều chỉnh chênh lệch so với ngày trước.
  - b[T(t)−T(t−3)]: điều chỉnh biến thiên 3 giờ gần nhất; c: độ lệch hằng.
  - a, b, c học offline trên C++; đây là giả thuyết cần đánh giá, chưa có hệ số thực nghiệm.
- **Mathematical content**: \widehat{T}(t+3)=T(t-21)+a[T(t)-T(t-24)]+b[T(t)-T(t-3)]+c

#### Slide 06 - Một lượt dự báo được tính thế nào?

- **Audience move**: Hiểu công thức → tự tính được một đầu ra.
- **Relationships**: Bốn giá trị giả định sinh hai hiệu, hai tích rồi cộng cùng mốc nền và c.
- **Composition**: 06_title_only.svg; schematic dominant where useful, explanation adjacent.
- **Title**: Một lượt dự báo được tính thế nào?
- **Core message**: Ví dụ số giúp ánh xạ trực tiếp sang các phép trừ, nhân và cộng.
- **Page rhythm**: breathing
- **Content**:
  - MINH HỌA GIẢ ĐỊNH — chưa phải dữ liệu hay hệ số thực nghiệm.
  - T(t−24)=19°C; T(t−21)=21°C; T(t−3)=18°C; T(t)=20°C.
  - a=0,5; b=0,2; c=0°C. Hai hiệu bằng 1°C và 2°C, đóng góp bằng 0,5°C và 0,4°C.
  - Kết quả: 21 + 0,5 + 0,4 = 21,9°C.
- **Mathematical content**: 21+0.5(20-19)+0.2(20-18)=21.9
- **Data class**: scenario — all temperatures and coefficients are illustrative.
- **Motion suggestion**: Formula from slide 5 continues as numerical contributions; potential Morph, motion not activated.

#### Slide 07 - Học trên quá khứ, kiểm tra ở tương lai

- **Audience move**: Chưa biết tìm hệ số → biết luồng huấn luyện không dùng nhãn tương lai sai chỗ.
- **Relationships**: Train có trước validation, validation trước test; chỉ train dùng tìm hệ số, validation dùng chọn cấu hình; test đánh giá cuối.
- **Composition**: 06_title_only.svg; schematic dominant where useful, explanation adjacent.
- **Title**: Học trên quá khứ, kiểm tra ở tương lai
- **Core message**: Chia dữ liệu theo thời gian và giữ giai đoạn test để đánh giá cuối.
- **Page rhythm**: dense
- **Content**:
  - Tạo x1=T(t)−T(t−24), x2=T(t)−T(t−3), y=T(t+3)−T(t−21).
  - Tìm a,b,c bằng bình phương tối thiểu y≈a x1+b x2+c trên tập train.
  - C++ có thể dùng Eigen; chưa chốt tỷ lệ chia và khoảng thời gian.
  - Chia theo timestamp của nhãn; đảm bảo nhãn train không sang giai đoạn validation/test. Lịch sử đã quan sát ở tập trước có thể làm đầu vào.
- **Mathematical content**: y\approx ax_1+bx_2+c
- **Hyperlinks**: Eigen least squares → https://eigen.tuxfamily.org/dox/group__LeastSquares.html

#### Slide 08 - Đánh giá dự báo và phần cứng riêng

- **Audience move**: Nghe nói chính xác → biết phép đo cụ thể, không nhầm khớp bit với dự báo đúng.
- **Relationships**: Mô hình so hai baseline trên cùng test; số thực so số cố định; RTL so reference cố định.
- **Composition**: 05_comparison.svg; schematic dominant where useful, explanation adjacent.
- **Title**: Đánh giá dự báo và phần cứng riêng
- **Core message**: Cần so với baseline và tách sai số mô hình khỏi sai số hiện thực.
- **Page rhythm**: dense
- **Content**:
  - Dự báo: baseline giữ nguyên T(t), baseline cùng giờ ngày trước T(t−21), mô hình đề xuất. Tính MAE (°C) trên cùng tập test; chưa cam kết thắng baseline.
  - Hiện thực: đo chênh lệch float/fixed; yêu cầu RTL khớp bit reference cố định với đúng latency; tài nguyên LUT/FF/DSP và latency lấy từ tổng hợp.
  - Không dùng số MAE/tần số/tài nguyên giả; ngưỡng sai lệch lượng tử hóa chốt sau thử nghiệm.
- **Mathematical content**: \mathrm{MAE}=\frac{1}{N}\sum_{i=1}^{N}|\widehat{T}_i-T_i|
- **Hyperlinks**: Forecasting: simple methods → https://otexts.com/fpp3/simple-methods.html

#### Slide 09 - Chọn số cố định từ miền giá trị

- **Audience move**: Biết phép tính thực → biết các quyết định bắt buộc cho số học phần cứng.
- **Relationships**: C++ số thực là mốc; phân tích miền giá trị dẫn tới định dạng; C++ fixed và RTL dùng cùng quy tắc.
- **Composition**: 06_title_only.svg; schematic dominant where useful, explanation adjacent.
- **Title**: Chọn số cố định từ miền giá trị
- **Core message**: Quy tắc số học phải được đặc tả trước khi viết RTL.
- **Page rhythm**: dense
- **Content**:
  - Xem miền nhiệt độ, hệ số và tổng trung gian để chọn số bit có dấu và số bit phần lẻ.
  - Quy định độ rộng tích/tổng, vị trí dịch bit, làm tròn và saturation/wrap. Chưa chốt Q format.
  - C++ fixed mô phỏng đúng từng bước RTL; thử nhiệt độ âm, biên biểu diễn và tràn số.
  - Phân biệt sai số dự báo so với giá trị thật và sai lệch do lượng tử hóa so với mô hình float.

#### Slide 10 - Từ lịch sử mẫu đến lõi số học

- **Audience move**: Biết công thức → nhận diện phần cứng cần xây.
- **Relationships**: Mẫu mới vào buffer; các tap tới khối trừ; hai hiệu nhân a,b rồi cộng với T(t−21),c để ra dự báo.
- **Composition**: 06_title_only.svg; schematic dominant where useful, explanation adjacent.
- **Title**: Từ lịch sử mẫu đến lõi số học
- **Core message**: Bộ đệm 25 mẫu cấp dữ liệu cho hai nhánh hiệu chỉnh.
- **Page rhythm**: dense
- **Content**:
  - Buffer giữ T(t−24)…T(t), tap tại t−24, t−21, t−3, t.
  - Hai phép trừ, hai phép nhân và phép cộng; hệ số cố định. Kiến trúc dùng chung hay song song bộ nhân sẽ chốt sau biết board.
  - Chỉ xuất dự báo khi đủ 25 mẫu hợp lệ. Clock và tín hiệu valid điều khiển việc nhận mẫu.
  - Trễ 1 mẫu tương ứng 1 giờ dữ liệu; latency mạch tính bằng chu kỳ clock, không phải 3 giờ chờ.

#### Slide 11 - Ba tầng kiểm chứng cùng một dữ liệu

- **Audience move**: Có kiến trúc → biết cách phát hiện lỗi và điều kiện nghiệm thu.
- **Relationships**: C++ float/fixed kiểm lượng tử hóa; testbench/RTL kiểm số học và điều khiển; board/reference kiểm tích hợp.
- **Composition**: 12_three_card.svg; schematic dominant where useful, explanation adjacent.
- **Title**: Ba tầng kiểm chứng cùng một dữ liệu
- **Core message**: Mỗi tầng kiểm chứng trả lời một câu hỏi khác nhau.
- **Page rhythm**: dense
- **Content**:
  - Tầng 1: C++ float ↔ fixed; đo sai lệch thêm do lượng tử hóa.
  - Tầng 2: testbench ↔ RTL; so từng đầu ra theo valid và latency, mục tiêu khớp bit.
  - Tầng 3: board ↔ reference; kiểm giao tiếp, thứ tự mẫu và kết quả.
  - Test biên: âm, tăng/giảm nhanh, tràn số, reset, chưa đủ buffer, gián đoạn valid; cùng quy tắc số học.

#### Slide 12 - Demo bằng cách phát lại dữ liệu

- **Audience move**: Lo phải chờ 3 giờ → hiểu demo hợp lệ với dữ liệu tuần tự.
- **Relationships**: PC gửi lần lượt mẫu đến t; FPGA dự báo t+3; PC đối chiếu nhãn đã có trong CSV nhưng không gửi tương lai vào FPGA.
- **Composition**: 06_title_only.svg; schematic dominant where useful, explanation adjacent.
- **Title**: Demo bằng cách phát lại dữ liệu
- **Core message**: Phát nhanh chuỗi lịch sử để quan sát kết quả ngay trong buổi báo cáo.
- **Page rhythm**: dense
- **Content**:
  - PC đọc CSV, truyền tuần tự các mẫu lịch sử; UART là phương án dự kiến tùy board.
  - FPGA nhận mẫu, tính và gửi đầu ra; PC ghi log và hiển thị kết quả.
  - Đối chiếu dự báo và giá trị thực theo timestamp. Chưa có giao diện hay kết quả demo thực.
  - Giữ nguyên thứ tự thời gian dù phát lại nhanh; board và giao tiếp cần chốt với thầy.

#### Slide 13 - 12 tuần, bốn mốc bàn giao

- **Audience move**: Biết khối lượng → thấy kế hoạch thực hiện trong ba tháng.
- **Relationships**: Dữ liệu đi trước mô hình; mô hình dẫn đến fixed/RTL; kiểm chứng dẫn đến demo board.
- **Composition**: 14_process_timeline.svg; schematic dominant where useful, explanation adjacent.
- **Title**: 12 tuần, bốn mốc bàn giao
- **Core message**: Mỗi giai đoạn có đầu ra có thể chạy hoặc đối chiếu.
- **Page rhythm**: dense
- **Content**:
  - Tuần 1–3: học nền tảng cần dùng, CSV sạch và hai baseline.
  - Tuần 4–6: huấn luyện C++, chọn đặc trưng, hệ số, đánh giá trên validation; bắt đầu fixed.
  - Tuần 7–9: RTL và testbench, đối chiếu bit, chuẩn bị tích hợp.
  - Tuần 10–12: board, đánh giá cuối, tài nguyên và báo cáo. Lịch buổi 2 cần theo thông báo thầy.

#### Slide 14 - Ba người, ba đầu ra phối hợp

- **Audience move**: Biết lịch → biết người phụ trách và cách xử lý rủi ro.
- **Relationships**: Dữ liệu/C++ cung cấp reference và vector cho RTL/DV; DV/demo phối hợp với RTL để tích hợp.
- **Composition**: 12_three_card.svg; schematic dominant where useful, explanation adjacent.
- **Title**: Ba người, ba đầu ra phối hợp
- **Core message**: Chia việc theo mảng và thống nhất giao diện ngay từ đầu.
- **Page rhythm**: dense
- **Content**:
  - Người 1: dữ liệu và C++; CSV, baseline, hệ số, MAE. Nếu dữ liệu thiếu/lệch giờ: sửa trước tạo mẫu.
  - Người 2: fixed và RTL; buffer, khối số học, tổng hợp. Board chưa rõ: làm lõi độc lập trước.
  - Người 3: testbench và demo; vector, so bit, truyền nhận và log. Nếu mô hình kém baseline: đánh giá lại trên validation, báo cáo trung thực.
  - Cả nhóm cùng chốt định dạng dữ liệu, hệ số, signedness, rounding/overflow, valid và latency.

#### Slide 15 - Một dự báo, hai điều cần chứng minh

- **Audience move**: Nghe kế hoạch → hiểu cam kết và các quyết định cần thầy xác nhận.
- **Relationships**: Baseline đối chiếu chất lượng; reference đối chiếu RTL; phạm vi/board/demo là các quyết định còn mở.
- **Composition**: 10_hero_statement.svg; schematic dominant where useful, explanation adjacent.
- **Title**: Một dự báo, hai điều cần chứng minh
- **Core message**: Chất lượng dự báo và độ đúng phần cứng đều phải có bằng chứng.
- **Page rhythm**: anchor
- **Content**:
  - Mô hình tuyến tính từ giá trị quá khứ → dự báo nhiệt độ +3 giờ.
  - Chứng minh 1: dự báo được đánh giá với baseline trên dữ liệu chưa dùng huấn luyện. Chứng minh 2: RTL khớp reference số cố định.
  - Xin xác nhận: phạm vi nhiệt độ +3 giờ; board và công cụ; mức demo tối thiểu.
  - Mở rộng độ ẩm/áp suất chỉ sau khi hoàn thành phần lõi.
- **Closing impact**: Two distinct proofs and three concrete questions for the teacher.

## X. Speaker Notes Requirements

- **Generation**: enabled
- **Filename**: match each SVG filename under notes/
- **Content**: Vietnamese natural presenter script, definitions and transitions, source links on relevant slides, no invented measured results. Preserve factual content from source notes and elaborate newly clarified mechanisms.
- **Total duration**: 15–18 minutes, timing guides per page, verify by rehearsal.
- **Notes style**: conversational academic, accessible to a beginner.
- **Presentation purpose**: Explain the proposal, mechanisms, verification and feasible 3-month work plan; obtain scope, board and demo feedback.
