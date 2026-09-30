from pathlib import Path
from lxml import etree

ROOT = Path(__file__).parent / "svg_output"

M = {
1: {
"DỰ BÁO NHIỆT ĐỘ":"TEMPERATURE FORECAST",
"SAU 3 GIỜ TRÊN FPGA":"3 HOURS AHEAD ON FPGA",
"Mô hình tuyến tính từ các giá trị quá khứ":"A linear model from past values",
"CE436  /  BÁO CÁO ĐỀ XUẤT  /  BUỔI 1":"CE436  /  PROJECT PROPOSAL  /  SESSION 1",
"Dữ liệu quá khứ":"Past data", "Hiện tại":"Now", "+3 giờ":"+3 hours",
"3 thành viên  ·  12 tuần  ·  C++ + Verilog/SystemVerilog":"3 students  ·  12 weeks  ·  C++ + Verilog/SystemVerilog",
},
2: {
"Một bài toán có thể kiểm chứng":"A testable forecasting task",
"CHỦ ĐỀ THẦY GIAO":"ASSIGNED TOPIC", "ĐẦU VÀO":"INPUT", "ĐẦU RA":"OUTPUT",
"Nhiệt độ theo giờ":"Hourly temperature", "tại một địa điểm, đến thời điểm t":"at one location, up to time t",
"Một dự báo nhiệt độ tại t + 3 giờ":"One temperature forecast at t + 3 h", "Đơn vị: °C":"Unit: °C",
"Vì sao chọn mô hình tuyến tính?":"Why a linear model?",
"Phép tính rõ ràng, dễ đối chiếu C++ ↔ RTL trong kế hoạch 3 tháng.":"Clear arithmetic; C++ and RTL can be compared within 3 months.",
"Phạm vi lõi: một biến, hệ số cố định. Độ ẩm/áp suất chỉ mở rộng khi còn thời gian.":"Core: one variable, fixed coefficients. Add humidity/pressure only if time allows.",
"FPGA phục vụ thực hành DSP và RTL; chưa khẳng định lợi ích tốc độ cho dữ liệu theo giờ.":"FPGA is for DSP/RTL practice; no speedup claim for hourly data.",
},
3: {
"C++ học hệ số, FPGA tính dự báo":"C++ trains; FPGA forecasts",
"OFFLINE  /  MÁY TÍNH":"OFFLINE  /  PC", "CSV nhiệt độ":"Temperature CSV",
"C++ huấn luyện":"C++ training", "Hệ số a, b, c":"Coefficients a, b, c",
"Làm sạch  →  baseline  →  tìm hệ số  →  reference số cố định + test vector":"Clean  →  baselines  →  fit coefficients  →  fixed-point reference + test vectors",
"KHI CHẠY  /  HỆ SỐ GIỮ CỐ ĐỊNH":"RUNTIME  /  COEFFICIENTS FIXED",
"Mẫu T(t)":"Sample T(t)", "Dự báo T̂(t+3)":"Forecast T̂(t+3)",
"Lưu lịch sử · tính toán · xuất kết quả":"Store history · compute · output",
"BÀN GIAO: C++  ·  RTL  ·  Testbench  ·  Demo board  ·  Báo cáo sai số và tài nguyên":"DELIVERABLES: C++  ·  RTL  ·  testbench  ·  board demo  ·  error/resource report",
},
4: {
"Bốn mốc quá khứ, một đích +3 giờ":"Four past values, one +3 h target",
"Nguồn dự kiến: ":"Planned source: ", "NASA POWER • T2M theo giờ":"NASA POWER • hourly T2M",
"Dữ liệu lưới; tọa độ và khoảng dữ liệu chưa chốt. Kiểm tra giờ thiếu/lặp, mốc giờ và đơn vị.":"Gridded data; location and date range TBD. Check missing/duplicate hours, time zone, and units.",
"Mốc t−21 là cùng giờ ngày trước của thời điểm cần dự báo.":"t−21 is the same hour on the day before the target.",
"Giữ 25 mẫu liên tiếp. FPGA chỉ thấy dữ liệu đến t; T(t+3) dùng để đánh giá.":"Keep 25 consecutive samples. FPGA sees data through t; T(t+3) is for evaluation.",
"Sơ đồ thể hiện thứ tự mốc, không theo tỷ lệ khoảng cách thời gian.":"Timeline shows order, not time intervals to scale.",
"Nguồn dự kiến: NASA POWER — tài liệu API theo giờ":"Planned source: NASA POWER — hourly API documentation",
},
5: {
"Mô hình tuyến tính từ quá khứ":"A linear model from past values",
"Mốc cùng giờ":"Same-hour anchor", "ngày hôm trước":"on the previous day",
"Hiệu chỉnh chênh lệch":"Correction for day-to-day", "so với ngày trước":"difference",
"Hiệu chỉnh biến thiên":"Correction for recent", "trong 3 giờ gần nhất":"3-hour change",
"c: độ lệch hằng. a, b, c được tìm offline trên C++ và giữ cố định khi FPGA chạy.":"c is a constant offset. C++ fits a, b, c offline; FPGA uses them unchanged.",
"Đây là mô hình đề xuất cần đánh giá; chưa có hệ số hoặc kết quả thực nghiệm.":"Proposed model only; no fitted coefficients or measured results yet.",
},
6: {
"Một lượt dự báo được tính thế nào?":"How is one forecast computed?",
"MINH HỌA GIẢ ĐỊNH — nhiệt độ và hệ số dưới đây chưa phải kết quả thực nghiệm.":"ILLUSTRATIVE EXAMPLE — values below are not measured results.",
"Hệ số minh họa: a = 0,5; b = 0,2; c = 0°C":"Example coefficients: a = 0.5; b = 0.2; c = 0°C",
"21 + 0,5 × (20−19) + 0,2 × (20−18)":"21 + 0.5 × (20−19) + 0.2 × (20−18)",
"= 21 + 0,5 + 0,4":"= 21 + 0.5 + 0.4", "21,9°C":"21.9°C",
"Mạch cần thực hiện: ":"Hardware operations: ", "trừ → nhân hệ số → cộng":"subtract → multiply → add",
},
7: {
"Học quá khứ, kiểm tra tương lai":"Train on the past, test on the future",
"C++ tìm a, b, c bằng bình phương tối thiểu.":"C++ fits a, b, c by least squares.",
"Tìm hệ số":"Fit coefficients", "trên dữ liệu cũ":"on earlier data",
"Chọn đặc trưng":"Select features", "và cấu hình":"and settings",
"Đánh giá cuối":"Final evaluation", "trên giai đoạn mới":"on later data",
"Nhãn train không vượt sang validation/test; vẫn dùng được lịch sử đã quan sát.":"Training labels cannot cross into validation/test; observed history remains usable.",
"Chia theo thời gian; tỷ lệ chưa chốt. C++ có thể dùng Eigen để giải least squares.":"Split chronologically; ratios TBD. C++ may use Eigen for least squares.",
"Tài liệu triển khai: Eigen — Solving linear least squares systems":"Implementation reference: Eigen — Solving linear least squares systems",
},
8: {
"Hai thước đo, hai câu hỏi riêng":"Two evaluations, two questions",
"DỰ BÁO CÓ ÍCH KHÔNG?":"IS THE FORECAST USEFUL?", "MẠCH CÓ TÍNH ĐÚNG?":"IS THE HARDWARE CORRECT?",
"So cùng tập test:":"Compare on the same test set:", "Giữ nguyên hiện tại: T(t)":"Current value: T(t)",
"Cùng giờ ngày trước: T(t−21)":"Same hour yesterday: T(t−21)", "Mô hình nhóm đề xuất":"Proposed model",
"Sai số dự báo trung bình":"Mean absolute forecast", "(giá trị tuyệt đối).":"error.",
"Chưa có kết quả để kết luận.":"No results yet.", "Đo sai lệch do lượng tử hóa.":"Measure quantization error.",
"RTL ↔ reference fixed":"RTL ↔ fixed reference", "Khớp bit với đúng valid và latency.":"Bit-exact with valid and latency.",
"Lấy từ kết quả tổng hợp mạch.":"From synthesis results.",
"Ngưỡng sai lệch sẽ":"Error limits will be", "chốt sau thử nghiệm.":"set after experiments.",
"Nguồn baseline: Forecasting: Principles and Practice — Simple forecasting methods":"Baseline reference: Forecasting: Principles and Practice — Simple forecasting methods",
},
9: {
"Số cố định bắt đầu từ miền giá trị":"Fixed-point starts with value ranges",
"C++ SỐ THỰC":"C++ FLOAT", "Mốc đối chiếu":"Model's", "của mô hình":"reference",
"PHÂN TÍCH TRƯỚC KHI CHỌN BIT":"ANALYZE BEFORE CHOOSING BITS",
"Miền nhiệt độ · miền hệ số · tổng trung gian":"Temperature · coefficient · intermediate ranges",
"Chưa chốt Q format khi chưa có dữ liệu và hệ số.":"Q format TBD until data and coefficients are known.",
"C++ FIXED VÀ RTL DÙNG CÙNG QUY TẮC":"C++ FIXED AND RTL FOLLOW ONE SPEC",
"Số có dấu · số bit phần lẻ · độ rộng tích và tổng":"Signedness · fractional bits · product and sum widths",
"Vị trí dịch bit · làm tròn · xử lý tràn: saturation hoặc wrap":"Shifts · rounding · overflow: saturation or wrap",
"Reference C++ mô phỏng từng bước số học mà RTL thực hiện.":"C++ reference mirrors each RTL arithmetic step.",
"Kiểm tra nhiệt độ âm, biên biểu diễn và tràn số.":"Test negative temperatures, numeric limits, and overflow.",
"Sai số dự báo so với thực tế và sai lệch fixed so với float là hai đại lượng khác nhau.":"Forecast error vs. truth and fixed-vs-float error are separate.",
},
10: {
"Từ lịch sử mẫu đến lõi số học":"From sample history to arithmetic",
"Nhận mẫu T(t)":"Receive T(t)", "BUFFER 25 MẪU":"25-SAMPLE BUFFER",
"Các tap cần đọc:":"Required taps:", "a × Δngày":"a × Δday", "b × Δ3giờ":"b × Δ3h",
"Sơ đồ chức năng; cách bố trí bộ nhân chưa chốt.":"Functional diagram; multiplier layout TBD.",
"Clock + valid điều khiển nhận mẫu. Chỉ tạo dự báo khi đủ 25 mẫu hợp lệ.":"Clock + valid accept samples. Forecast only after 25 valid samples.",
"Hệ số cố định; chọn dùng chung hay song song bộ nhân sau khi biết board.":"Coefficients stay fixed; choose shared or parallel multipliers after board selection.",
"Trễ 1 mẫu = 1 giờ dữ liệu. Latency mạch tính bằng chu kỳ clock, không phải chờ 3 giờ.":"One sample delay = 1 data hour. Hardware latency is in clock cycles, not 3 hours.",
},
11: {
"Ba tầng kiểm chứng":"Three verification layers",
"Đo phần sai lệch":"Measure error", "do lượng tử hóa":"from quantization",
"Kiểm tra:":"Test:", "nhiệt độ âm, biên số,":"negative temps, limits,", "giá trị biến đổi nhanh.":"rapid changes.",
"So từng đầu ra":"Compare each output", "theo valid và latency":"with valid and latency",
"Mục tiêu: khớp bit.":"Target: bit-exact.", "Test reset, tràn, thiếu":"Test reset, overflow,", "mẫu, gián đoạn valid.":"warm-up, valid gaps.",
"Kiểm tra giao tiếp":"Check interfaces", "và kết quả tích hợp":"and integrated output",
"Dùng cùng test vector;":"Use the same vectors;", "kiểm thứ tự mẫu, dữ liệu":"check sample order,",
"nhận và log đầu ra.":"input and output logs.",
"Cùng dữ liệu và quy tắc số học, mỗi tầng trả lời một câu hỏi riêng.":"Same data and arithmetic rules; each layer answers a different question.",
},
12: {
"Demo bằng cách phát lại dữ liệu":"Demo by replaying historical data",
"Phát nhanh chuỗi lịch sử, vẫn giữ thứ tự thời gian.":"Replay quickly while preserving time order.",
"Kịch bản đề xuất; chưa có kết quả chạy board hoặc giao diện demo thực.":"Proposed demo; no board run or live interface yet.",
"Gửi lần lượt":"Send samples", "các mẫu đến t":"through t",
"UART nếu board phù hợp":"UART if board permits", "Nhận mẫu":"Receive samples",
"Tính T̂(t+3)":"Compute T̂(t+3)", "Gửi kết quả về PC":"Return result to PC",
"PC / ĐỐI CHIẾU":"PC / COMPARE", "So kết quả":"Compare results", "theo giờ":"by hour",
"Ghi log và hiển thị":"Log and display",
"PC có nhãn T(t+3) trong CSV để đánh giá; nhãn tương lai không được gửi vào FPGA.":"PC holds T(t+3) for evaluation; future labels never enter FPGA.",
"Board, giao tiếp và mức demo tối thiểu cần chốt với thầy.":"Board, interface, and minimum demo scope need instructor input.",
},
13: {
"12 tuần, bốn mốc bàn giao":"12 weeks, four milestones",
"TUẦN 1–3":"WEEKS 1–3", "Dữ liệu":"Data", "Học nền tảng":"Learn basics",
"CSV sạch":"Clean CSV", "Hai baseline":"Two baselines",
"TUẦN 4–6":"WEEKS 4–6", "Mô hình C++":"C++ model",
"Hệ số, validation":"Coefficients, validation", "Chọn đặc trưng":"Select features", "Bắt đầu fixed":"Start fixed-point",
"TUẦN 7–9":"WEEKS 7–9", "Lõi tính toán":"Arithmetic core", "Đối chiếu bit":"Bit comparison",
"Chuẩn bị tích hợp":"Prepare integration", "TUẦN 10–12":"WEEKS 10–12",
"Board + báo cáo":"Board + report", "Demo, đánh giá cuối":"Demo, final evaluation",
"Tài nguyên mạch":"Hardware resources", "Giới hạn và kết luận":"Limits and conclusions",
"Mỗi giai đoạn có sản phẩm chạy được; lịch báo cáo buổi 2 theo thông báo của thầy.":"Each phase has a working deliverable; session 2 follows the instructor's schedule.",
},
14: {
"Ba người, ba đầu ra phối hợp":"Three students, coordinated outputs",
"NGƯỜI 1":"STUDENT 1", "Dữ liệu + C++":"Data + C++",
"CSV · baseline":"CSV · baselines", "Hệ số · MAE · reference":"Coefficients · MAE · reference",
"RỦI RO: THIẾU / LỆCH GIỜ":"RISK: MISSING / MISALIGNED HOURS",
"Kiểm và sửa chuỗi giờ":"Validate and repair hours", "trước khi tạo mẫu.":"before building samples.",
"NGƯỜI 2":"STUDENT 2", "Số cố định + RTL":"Fixed-point + RTL",
"Buffer · lõi số học":"Buffer · arithmetic core", "Tổng hợp · tích hợp board":"Synthesis · board integration",
"RỦI RO: BOARD CHƯA RÕ":"RISK: BOARD NOT CONFIRMED",
"Hoàn thiện lõi độc lập":"Build a standalone core", "và mô phỏng trước.":"and simulate it first.",
"NGƯỜI 3":"STUDENT 3", "Kiểm chứng + demo":"Verification + demo",
"Vector · so bit":"Vectors · bit checking", "Truyền nhận · log kết quả":"I/O · result logs",
"RỦI RO: SAI SỐ CAO":"RISK: HIGH FORECAST ERROR",
"Cả nhóm xét lại validation;":"Revisit validation together;", "báo cáo đúng kết quả test.":"report test results honestly.",
"Cùng chốt: dữ liệu, hệ số, signedness, rounding/overflow, valid và latency.":"Agree on data, coefficients, signedness, rounding/overflow, valid, and latency.",
},
15: {
"Một dự báo, hai điều cần chứng minh":"One forecast, two claims to verify",
"Mô hình tuyến tính → nhiệt độ +3 giờ":"Linear model → temperature +3 h",
"01  Chất lượng dự báo":"01  Forecast quality",
"So với baseline trên dữ liệu chưa dùng để huấn luyện.":"Compare with baselines on unseen data.",
"02  Độ đúng phần cứng":"02  Hardware correctness",
"RTL khớp mô hình tham chiếu số cố định.":"RTL matches the fixed-point reference.",
"Xin thầy góp ý: phạm vi +3 giờ · board và công cụ · demo tối thiểu.":"Instructor input: +3 h scope · board/tools · minimum demo.",
"Mở rộng độ ẩm/áp suất sau khi hoàn thành phần lõi.":"Add humidity/pressure only after the core is complete.",
},
}

def main():
    changed = 0
    for p in sorted(ROOT.glob('*.svg')):
        i = int(p.name[:2]); mapping = M[i]
        tree = etree.parse(str(p))
        seen = set()
        for e in tree.xpath('//*[local-name()="text" or local-name()="tspan"]'):
            if e.text in mapping:
                seen.add(e.text)
                e.text = mapping[e.text]
                changed += 1
        missing = set(mapping) - seen
        if missing:
            raise ValueError(f'{p.name}: mappings not found: {missing}')
        tree.write(str(p), encoding='utf-8', xml_declaration=False)
    print(f'Translated {changed} text runs on 15 slides')

if __name__ == '__main__':
    main()
