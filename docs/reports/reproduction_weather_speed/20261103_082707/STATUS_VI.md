# Kết quả tái hiện weather_speed — biến thể reset KEY1

Hoàn tất nạp, replay, kiểm tra CSV và thu SignalTap thực tế bằng CLI. Không phải bản KEY0 nguyên trạng: người dùng đã cho phép chuyển reset vật lý sang KEY1/N23 sau khi KEY0/G26 luôn giữ reset qua nhiều lần nạp, nhấn/thả nút và tắt/bật nguồn. Chưa kết luận riêng nút nhấn hay mạch KEY0 hỏng.

## Môi trường và cấu hình
- Quartus II Web Edition 13.0 SP1, 13.0.1 Build 232; /opt/altera/13.0sp1/quartus/bin.
- USB-Blaster [1-1], @1: EP2C35 (0x020B40DD), TCK 6 MHz.
- EP2C35F672C6; top de2_weather_jtag; SHARED=0; CLOCK_50 N2, 20 ns/50 MHz.
- Reset vật lý KEY1 N23; tên cổng logic vẫn KEY0_N. Revision ordinary weather_jtag; instrumented capture.
- Không có Git metadata để lấy commit. Source snapshot và SHA256 dùng làm dấu vết phiên bản.

## Kết quả mới trên máy zeus
- Ordinary KEY1: biên dịch exit 0, 0 errors, 7 warnings, không Critical Warning. Programming thành công. Replay và CSV PASS: 128 input, 24 warmup, 104 forecast khớp. Đọc lại probe: Accepted=128 Forecasts=104 Reset=0.
- Capture KEY1: sau bật TalkBack theo đồng ý người dùng, biên dịch exit 0, 0 errors, 7 warnings, không Critical Warning 35025; Info 35024 xác nhận kết nối đủ 240 data/trigger/clock/dynamic inputs. Programming thành công.
- Replay instrumented PASS 128/104 và CSV PASS; kiểm tra miền góc [0,360) rồi tính khoảng cách vòng tròn, dung sai giữ 5 Q8 (0.01953125°).
- Acquisition mới 08:46:55 ngày 03/11/2026: PRE quan sát qua PTY trước khi khởi chạy đúng một replay, sau đó DONE. Capture và replay exit 0.
- Validator PASS: 512 mẫu, trigger 256, accept 215, forecast_valid 256; đúng một input accepted và một output valid; reset không tác động trong toàn bộ cửa sổ. Input và sáu output khớp vector thứ 25 từng bit; góc hợp lệ và trong dung sai.
- Chênh lệch 41 mẫu acquisition theo quan sát giá trị tại cạnh lấy mẫu; độ trễ RTL 40 chu kỳ theo quan sát thanh ghi cập nhật sau cạnh nhận. Không đổi hai quy ước này thành cùng một đại lượng.
- Đã giữ bản raw, format bus trên bản live, xác nhận dữ liệu bit không đổi; mở lại bằng Quartus open_session/close_session thành công và validator PASS lần nữa.

## Resource/timing ordinary KEY1
- 6253 logic elements, 4571 registers, 0 memory bits, 12 embedded multiplier 9-bit elements.
- Slow Fmax CLOCK_50 80.89 MHz (tài liệu 79.74 MHz); clock board vẫn 50 MHz.
- Slow setup slack 7.638 ns (tài liệu 7.459 ns); slow hold 0.391 ns; fast hold/minimum across these reported corners 0.215 ns.
- Instrumented giữ riêng: 8077 LE, 6292 registers, 121856 memory bits, 12 multiplier elements; slow setup 7.262 ns, hold slow 0.391 ns/fast 0.215 ns.
- Warnings đã đọc: giới hạn LogicLock/parallel của edition ở ordinary, connectivity của debug hub, NOT gate push-back của SignalTap, node hub receive cố định GND, và Cyclone II không hỗ trợ jitter analysis. Không có lỗi timing hoặc node SignalTap bị ngắt.

## Đọc một dự báo
Khung 25 (sample_index=24), sau 24 khung warmup: 26.445312 °C, 100.531250 kPa, 69.644531% độ ẩm, 3.285156 m/s, cos 0.902344, sin 0.085938, hướng gió 5.437500°. Horizon 3 giờ thuộc mô hình dự báo; không cần chờ 3 giờ để chạy demo. PASS là khớp tham chiếu fixed-point, không phải đo sai số thời tiết tương lai.

## File bằng chứng chính
ordinary_key1_programming.log, ordinary_key1_replay.log, ordinary_replay.csv, ordinary_csv_check.txt, ordinary_retained_probe.log.
capture_programming.log, capture_acquisition_pty.log, capture_ready_evidence.txt, capture_replay.log, capture_replay.csv, capture_csv_check.txt.
weather_speed_live.stp (đã nhóm bus), weather_speed_live_raw.stp, weather_speed_live_decoded.csv, capture_check.txt, capture_check_after_reopen.txt, reopen_capture.log.
ordinary_reports_key1/, capture_reports_key1/, used_files/, source_snapshot/, SHA256SUMS.txt.

## Thay đổi và các lần thử thất bại
Diff weather_jtag_key1.diff, capture_key1.diff; bản QSF trước sửa trong before_key1/. SLD_FILE của capture sửa sang đường tương đối capture_auto_stripped.stp. Không sửa RTL chức năng, model, vectors, expected values hoặc tolerance. TalkBack đã bật, có bản ini trước/sau và log.
Log KEY0 timeout vẫn giữ. Lần compile SignalTap đầu thiếu TalkBack vẫn giữ. Lần capture đầu stdout bị buffer nên không gửi replay, không có DONE; weather_speed_attempt1_no_replay.stp KHÔNG phải bằng chứng đạt. Lần PTY mới là lần nghiệm thu.

## Phần GUI và sao lưu còn lại
Không điều khiển được native GUI trong phiên này; chưa mở cửa sổ hoặc chụp ảnh SignalTap/Programmer. Việc mở lại STP đã làm bằng Quartus CLI. Để xem: Quartus 13.0 SP1 > Tools > SignalTap II Logic Analyzer > Open weather_speed_live.stp ở chính thư mục này > chọn data log live_capture > Data; zoom quanh sample 215–256. Các bus đã nhóm. Chụp ảnh vào screenshots/ nếu cần.
Chưa có đích lưu trữ thứ hai; cần người dùng cung cấp sau khi hồ sơ cục bộ hoàn tất. Board hiện chạy bản SignalTap KEY1. Khi tắt nguồn, phải nạp lại SOF KEY1 tương ứng.
