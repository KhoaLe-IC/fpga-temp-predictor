# Demo weather_speed trên DE2 — dùng KEY1

1. Nguồn ngoài, RUN/PROG ở RUN, thả KEY1. Xác nhận USB-Blaster và EP2C35 ID 020B40DD.
2. Nạp used_files/weather_speed_ordinary_key1.sof. Chạy replay_jtag.tcl weather_speed từ gốc repo, đặt FPGA_JTAG_CSV vào thư mục lần demo mới để giữ chứng cứ cũ.
3. Trình bày PASS 128 input/104 forecast, 24 khung warmup. Đọc dòng forecast đầu theo đơn vị vật lý. Đọc ordinary_reports_key1: 6253 LE, 4571 reg, Fmax 80.89 MHz; board chạy 50 MHz.
4. Nạp used_files/weather_speed_signaltap_key1.sof. Dùng STP template matching trong used_files/capture_key1_template.stp; sửa SOF path cho đúng máy nếu di chuyển. Giữ instance auto_signaltap_0, CLOCK_50, depth 512, center và rising edge forecast_valid.
5. Arm qua terminal PTY để log hiển thị tức thì, chỉ chạy một replay sau PRE. capture_live_pty.py của phiên này minh họa đúng thứ tự, nhưng không chạy lại vào cùng RUN_DIR để tránh ghi đè bằng chứng đã nghiệm thu.
6. Đợi DONE và replay PASS, kiểm tra CSV và acquisition. Trình bày accept 215 -> forecast_valid 256: 41 mẫu SignalTap, tương ứng quy ước RTL 40 chu kỳ.
7. Mở STP mới trong SignalTap II và chọn log dữ liệu, chụp ảnh thật. Lưu hồ sơ và checksum trước khi tắt nguồn.

Bản thu đã lưu trong weather_speed_live.stp là dữ liệu thật của lần chạy 03/11/2026, không phải một lần demo mới nếu chỉ mở lại. Dùng bản này làm dự phòng có ghi rõ ngày thu.
