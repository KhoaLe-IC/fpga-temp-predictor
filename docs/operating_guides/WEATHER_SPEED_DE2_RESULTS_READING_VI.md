# Hướng dẫn đọc và báo cáo kết quả weather_speed trên kit DE2

Tài liệu này hướng dẫn **đọc kết quả đã chạy thành công**, không yêu cầu chạy lại FPGA. Bằng chứng thuộc phiên `20261103_082707` trên máy `zeus`; SignalTap thu mới lúc **08:46:55 ngày 03/11/2026**, giờ máy tại Việt Nam.

Thiết kế trong phiên nghiệm thu dùng **KEY1 để reset**, theo sự đồng ý của người dùng. Không trình bày đây là bản KEY0 nguyên trạng của hướng dẫn gốc.

## 1. Kết quả chính cần nhớ

| Nội dung | Kết quả thực tế | Ý nghĩa |
| --- | --- | --- |
| Kit và FPGA | DE2, EP2C35F672C6; JTAG ID `020B40DD` | Đúng chip mục tiêu |
| Công cụ | Quartus II Web Edition 13.0 SP1, 13.0.1 Build 232 | Đúng phiên bản kiểm chứng |
| Cáp | USB-Blaster `[1-1]`, TCK 6 MHz | Đường nạp và trao đổi dữ liệu JTAG |
| Clock ứng dụng | CLOCK_50, 50 MHz, chu kỳ 20 ns | Clock tính toán trên FPGA |
| Kiến trúc | `weather_speed`, top `de2_weather_jtag`, `SHARED=0` | Bản tối ưu tốc độ |
| Reset | KEY1 tại N23; tên cổng RTL vẫn `KEY0_N` | KEY0/G26 đã được thay thế trong assignment |
| Nạp FPGA | Thành công với cả ordinary và instrumented | Hai SOF đều đã được nạp thực tế |
| Replay ordinary | 128 đầu vào, 24 warm-up, 104 dự báo khớp | Kiểm tra chức năng bản thông thường |
| Replay instrumented | Cũng PASS 128/104 | Thiết kế có SignalTap vẫn cho kết quả đúng |
| SignalTap | PRE → DONE; 512 mẫu, trigger 256 | Đã có dữ liệu thu trên kit, không chỉ cấu hình trống |
| Giao dịch được thu | Input nhận tại 215, output valid tại 256 | Khớp vector thứ 25 |
| Kiểm tra lưu file | Mở lại bằng Quartus CLI và validator đều đạt | Dữ liệu đã được lưu và đọc lại được |

Câu giới thiệu ngắn:

> Em đã nạp bộ dự báo weather_speed lên FPGA Cyclone II của DE2. Máy tính gửi 128 khung quan sát qua JTAG; sau 24 khung khởi tạo lịch sử, FPGA trả về 104 dự báo khớp tham chiếu fixed-point. Em cũng thu SignalTap trên phần cứng để kiểm tra giao dịch bên trong mạch.

## 2. Mở đúng thư mục bằng chứng

Thư mục tuyệt đối của phiên:

```text
/home/zeus/Study/Subject_in_Uni/Subject_in_Uni/Digital_Signal_Processing/fpga-temp-predictor-main/docs/reports/reproduction_weather_speed/20261103_082707
```

Trong phần còn lại, gọi thư mục này là **RUN_DIR**. Các liên kết bên dưới trỏ tới đúng phiên này.

| Muốn chứng minh | File cần mở |
| --- | --- |
| Tổng quan, lịch sử xử lý lỗi và giới hạn | [STATUS_VI.md](../reports/reproduction_weather_speed/20261103_082707/STATUS_VI.md) |
| Nạp ordinary thành công | [ordinary_key1_programming.log](../reports/reproduction_weather_speed/20261103_082707/ordinary_key1_programming.log) |
| Replay ordinary thành công | [ordinary_key1_replay.log](../reports/reproduction_weather_speed/20261103_082707/ordinary_key1_replay.log) |
| Từng dự báo trả về | [ordinary_replay.csv](../reports/reproduction_weather_speed/20261103_082707/ordinary_replay.csv) |
| Kiểm tra CSV ordinary | [ordinary_csv_check.txt](../reports/reproduction_weather_speed/20261103_082707/ordinary_csv_check.txt) |
| Kết quả cuối còn giữ trong FPGA | [ordinary_retained_probe.log](../reports/reproduction_weather_speed/20261103_082707/ordinary_retained_probe.log) |
| Nạp bản có SignalTap | [capture_programming.log](../reports/reproduction_weather_speed/20261103_082707/capture_programming.log) |
| Thứ tự arm, PRE và DONE | [capture_acquisition_pty.log](../reports/reproduction_weather_speed/20261103_082707/capture_acquisition_pty.log), [capture_ready_evidence.txt](../reports/reproduction_weather_speed/20261103_082707/capture_ready_evidence.txt) |
| Replay trong lúc thu | [capture_replay.log](../reports/reproduction_weather_speed/20261103_082707/capture_replay.log), [capture_replay.csv](../reports/reproduction_weather_speed/20261103_082707/capture_replay.csv) |
| Kiểm tra CSV instrumented | [capture_csv_check.txt](../reports/reproduction_weather_speed/20261103_082707/capture_csv_check.txt) |
| Waveform đã nhóm bus, nên dùng để trình bày | [weather_speed_live.stp](../reports/reproduction_weather_speed/20261103_082707/weather_speed_live.stp) |
| Bản thu trước khi nhóm bus | [weather_speed_live_raw.stp](../reports/reproduction_weather_speed/20261103_082707/weather_speed_live_raw.stp) |
| Waveform dưới dạng bảng | [weather_speed_live_decoded.csv](../reports/reproduction_weather_speed/20261103_082707/weather_speed_live_decoded.csv) |
| Kết luận validator acquisition | [capture_check.txt](../reports/reproduction_weather_speed/20261103_082707/capture_check.txt) |
| Kiểm tra sau khi mở lại STP | [capture_check_after_reopen.txt](../reports/reproduction_weather_speed/20261103_082707/capture_check_after_reopen.txt), [reopen_capture.log](../reports/reproduction_weather_speed/20261103_082707/reopen_capture.log) |
| Resource và timing bản ordinary KEY1 | [ordinary_reports_key1/](../reports/reproduction_weather_speed/20261103_082707/ordinary_reports_key1/) |
| Resource và timing bản SignalTap KEY1 | [capture_reports_key1/](../reports/reproduction_weather_speed/20261103_082707/capture_reports_key1/) |
| Checksum hồ sơ | [SHA256SUMS.txt](../reports/reproduction_weather_speed/20261103_082707/SHA256SUMS.txt) |

**Tránh chọn nhầm bằng chứng:**

- `archive_restore/`, `ordinary_reports/`, `capture_reports/` chứa dữ liệu lịch sử của archive.
- `ordinary_reports_rebuilt/` là lần biên dịch KEY0 trên máy zeus trước khi chuyển KEY1.
- `ordinary_replay.log`, `ordinary_replay_rebuilt.log` là các lần KEY0 thất bại. Log ordinary thành công có tên **`ordinary_key1_replay.log`**.
- `capture_key1_compile.log` là lần compile thiếu TalkBack. Lần thành công là **`capture_key1_compile_talkback.log`**.
- `capture_acquisition.log` và `weather_speed_attempt1_no_replay.stp` thuộc lần arm đầu, chưa gửi replay do stdout bị buffer; không có DONE để nghiệm thu. Lần thành công dùng **`capture_acquisition_pty.log`**.

Việc giữ log lỗi giúp giải thích quá trình xử lý, không làm mất giá trị của lần chạy đạt sau đó.

## 3. Đọc log nạp và replay

### 3.1 Nạp thành công chứng minh điều gì?

Trong log programming, tìm các thông báo:

```text
Device 1 contains JTAG ID code 0x020B40DD
Configuration succeeded -- 1 device(s) configured
Successfully performed operation(s)
```

Đối chiếu cả đường dẫn SOF. Ordinary dùng `versions/weather_v2/quartus/de2_jtag_speed/output_files/weather_jtag.sof`; instrumented dùng `hardware/quartus/signaltap/weather_speed/output_files/capture.sof`.

Nạp thành công xác nhận FPGA đã nhận cấu hình. Muốn chứng minh tính toán đúng, cần xem tiếp replay và acquisition.

### 3.2 Đọc kết quả replay

Mở `ordinary_key1_replay.log`, tìm:

```text
Variant: weather_speed
Node: {0 128 256 FCST}
PASS PHYSICAL JTAG weather_speed: inputs=128 forecasts=104
```

Node gồm: instance index **0**, Source rộng **128 bit**, Probe rộng **256 bit**, tên **FCST**. Source là dữ liệu/điều khiển máy tính gửi vào; Probe là kết quả/trạng thái đọc ra.

Replay gửi các vector đã cung cấp, kiểm tra nhận dạng thiết kế, bộ đếm và kết quả. Có 128 đầu vào, trong đó 24 khung đầu dùng để điền lịch sử. Từ khung thứ 25 mới có dự báo, nên `128 − 24 = 104`.

Trong `ordinary_retained_probe.log`, dòng `Accepted=128 Forecasts=104 Reset=0` cho thấy trạng thái đọc lại sau replay phù hợp. Đây là giá trị lưu ở thời điểm kiểm tra; sau khi reset hoặc nạp SOF khác, không mặc định FPGA vẫn giữ giá trị đó.

## 4. Đọc CSV và giải thích một dự báo

### 4.1 Ý nghĩa các cột

| Cột | Cách đọc |
| --- | --- |
| `sample_index` | Chỉ số bắt đầu từ 0; 24 là khung thứ 25 |
| `accepted_count` | Tổng số khung FPGA đã nhận, bằng `sample_index + 1` |
| `forecast_count` | Tổng số dự báo đã tạo; 0 trong 24 khung đầu |
| `forecast_raw` | Bảy giá trị số nguyên fixed-point của dự báo |
| `forecast_physical` | Bảy giá trị sau đổi sang đơn vị vật lý |
| `probe_hex` | Toàn bộ từ trạng thái/kết quả 256 bit, dạng hexadecimal |
| `match` | `warmup` khi chưa có dự báo; `True` khi dự báo đạt so sánh |

Không coi `warmup` là lỗi hoặc là dự báo bằng 0. Hai cột forecast trống ở warm-up vì chưa có output hợp lệ để báo cáo.

Mở CSV bằng trình soạn thảo hoặc bảng tính, chọn dấu phân cách **dấu phẩy**. Các giá trị bên trong `forecast_physical` được ngăn bằng dấu cách và thuộc cùng một ô.

### 4.2 Dòng mẫu đã thu thực tế

Ở `sample_index=24`: `accepted_count=25`, `forecast_count=1`, `match=True`.

| Thành phần | Raw Q8 | Giá trị vật lý |
| --- | ---: | ---: |
| Nhiệt độ | 6770 | 26.4453125 °C |
| Áp suất bề mặt | 25736 | 100.53125 kPa |
| Độ ẩm tương đối | 17829 | 69.64453125 % |
| Tốc độ gió | 841 | 3.28515625 m/s |
| Cos hướng gió | 231 | 0.90234375 |
| Sin hướng gió | 22 | 0.0859375 |
| Góc hướng gió | 1392 | 5.4375° |

CSV in 6 chữ số sau dấu thập phân nên có thể thấy `26.445312`. Bảng trên biểu diễn phép chia chính xác của raw cho 256.

Công thức Q8: **giá trị vật lý = số nguyên raw / 256**. Ví dụ `6770 / 256 = 26.4453125 °C`. Có bảy đầu ra nhưng chỉ năm đại lượng thời tiết; cos và sin là hai thành phần hỗ trợ biểu diễn hướng gió.

Cách nói với giảng viên:

> Ở khung được chấp nhận thứ 25, bộ dự báo bắt đầu xuất kết quả. Nhiệt độ dự báo là khoảng 26,45 °C, áp suất 100,53 kPa, độ ẩm 69,64%, tốc độ gió 3,29 m/s và hướng gió 5,44°. Các giá trị này khớp tham chiếu fixed-point của vector tương ứng.

Horizon dự báo là 3 giờ theo bài toán mô hình; thời gian xử lý trên FPGA không phải 3 giờ.

### 4.3 Phạm vi của chữ PASS

Sáu thành phần nhiệt độ, áp suất, độ ẩm, tốc độ gió, cos và sin được so sánh từng bit. Góc được kiểm tra trong miền `[0, 360°)` trước khi tính sai số vòng tròn:

```text
0 <= actual_angle_raw < 92160
0 <= expected_angle_raw < 92160
error = min(abs(actual - expected), 92160 - abs(actual - expected))
error <= 5
```

Vì `360 × 256 = 92160`, dung sai 5 Q8 tương đương **0.01953125°**. Không gọi đây là dung sai 5 độ.

PASS chứng minh thiết kế phần cứng khớp tham chiếu trên bộ 128 vector đã thử. Nó không chứng minh dự báo thời tiết đúng 100% so với tương lai, không thay cho đánh giá MAE/RMSE trên tập dữ liệu, và không bao phủ mọi đầu vào có thể có.

## 5. Mở bản thu SignalTap đã lưu

Không cần cắm kit hoặc nạp FPGA chỉ để **xem lại dữ liệu STP đã lưu**. Muốn thu một lần mới thì cần board và cấu hình instrumented phù hợp.

1. Mở Quartus II 13.0 SP1. Có thể mở project `hardware/quartus/signaltap/weather_speed/capture.qpf` để có ngữ cảnh thiết kế.
2. Vào **Tools > SignalTap II Logic Analyzer**, dùng **File > Open** để chọn `RUN_DIR/weather_speed_live.stp`.
3. Chọn instance **`auto_signaltap_0`**, signal set **`signal_set_1`**, trigger **`trigger_1`** nếu giao diện yêu cầu.
4. Chọn dữ liệu acquisition đã lưu. Script thu đặt tên `live_capture`; sau khi nhóm bus, nhãn dữ liệu trong file đã thành **`weather_speed_live_PHYSICAL`**. Tìm nhãn này nếu không thấy `live_capture`.
5. Chọn vùng/tab **Data** hoặc chế độ hiển thị waveform dữ liệu đã thu. Một màn hình chỉ hiện danh sách cấu hình chưa đủ chứng minh đã mở dữ liệu.
6. Zoom toàn cửa sổ trước để thấy 512 mẫu, rồi zoom quanh input accepted và cạnh lên của `forecast_valid`.
7. Đặt hai con trỏ ở sự kiện nhận input và output valid. Đối chiếu bảng ở mục 6 nếu thước đo dùng chỉ số tương đối thay vì chỉ số tuyệt đối.

Tên/vị trí điều khiển có thể khác đôi chút theo bố cục cửa sổ. Không cần bấm **Run Analysis**, **Autorun** hoặc **Program Device** để đọc dữ liệu cũ. Các thao tác đó phục vụ thu/nạp mới.

**Trạng thái thực hiện:** phiên này đã mở lại file bằng Quartus CLI và kiểm tra dữ liệu thành công. Chưa điều khiển GUI hay chụp ảnh màn hình; các bước ở trên dành cho người dùng mở giao diện để trình bày.

## 6. Đọc waveform SignalTap

### 6.1 Cấu hình acquisition

| Thuộc tính | Giá trị |
| --- | --- |
| Clock lấy mẫu | CLOCK_50, cạnh lên |
| Sample depth | 512 mẫu |
| Trigger position | Center, chỉ số tuyệt đối 256 |
| Trigger | Cạnh lên `jtag_mailbox:mailbox|forecast_valid` |
| Khoảng cách hai mẫu liên tiếp | 20 ns |

**PRE** là trạng thái bộ thu đã vào giai đoạn chờ trước trigger. **DONE** là trạng thái acquisition hoàn tất. Dòng tự in `CAPTURE ARMED` xuất hiện trước lệnh `run`, nên chỉ riêng dòng đó chưa chứng minh phần cứng đã sẵn sàng.

Trong lần đạt, chương trình quan sát PRE thật qua PTY rồi mới khởi chạy đúng một replay. Log ghi DONE và STP chứa dữ liệu hợp lệ; đó là chuỗi bằng chứng thu mới.

### 6.2 Các tín hiệu cần chỉ trên màn hình

| Tín hiệu | Ý nghĩa và điều cần quan sát |
| --- | --- |
| `core_rst_n` | Reset active-low: 1 là không reset; phải bằng 1 trong cửa sổ này |
| `sample_valid` | Bên gửi đang cung cấp input hợp lệ |
| `sample_ready` | Bộ dự báo sẵn sàng nhận input |
| `sample_data` / các nhóm `*_in_q8` | Dữ liệu đầu vào được chấp nhận khi valid và ready cùng bằng 1 |
| `forecast_valid` | Output là một dự báo hợp lệ tại mẫu này |
| `forecast_data` / các nhóm `*_out_q8` | Đọc kết quả tại mẫu có forecast_valid=1 |

Điều kiện nhận input là **`sample_valid && sample_ready`**, không chỉ nhìn riêng một trong hai tín hiệu. Thay đổi bus output khi `forecast_valid=0` không được tính thành một dự báo bổ sung.

### 6.3 Các mốc thực tế trong bản thu

| Chỉ số mẫu tuyệt đối | Tương đối trigger | Thời gian tương đối | rst_n | valid | ready | forecast_valid | Cách giải thích |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 214 | −42 | −840 ns | 1 | 0 | 1 | 0 | Đang chờ input |
| **215** | **−41** | **−820 ns** | **1** | **1** | **1** | **0** | **Nhận input vector thứ 25** |
| 216 | −40 | −800 ns | 1 | 0 | 0 | 0 | Đang xử lý |
| 255 | −1 | −20 ns | 1 | 0 | 1 | 0 | Bus đã có một phần kết quả, chưa valid |
| **256** | **0** | **0 ns** | **1** | **0** | **1** | **1** | **Dự báo hợp lệ; trigger ở đây** |
| 257 | +1 | +20 ns | 1 | 0 | 1 | 0 | Xung valid đã kết thúc |

Các hàng trên lấy từ `weather_speed_live_decoded.csv`. Nếu GUI đặt trigger làm gốc, bạn sẽ thấy vị trí −41 và 0 thay cho 215 và 256; đó là cùng hai sự kiện.

Input tại 215:

```text
0x40010000a9852f31921416b8
```

Output hợp lệ tại 256:

```text
0x5700005800e700d2445a5192201a72
```

Các số hexadecimal có thể được thêm số 0 ở đầu khi GUI hiển thị đủ độ rộng. Thêm số 0 đầu không làm thay đổi giá trị.

### 6.4 Giải thích 41 mẫu và 40 chu kỳ

Trong bản thu: `256 − 215 = 41` khoảng lấy mẫu, tức **820 ns trên thước thời gian acquisition**. Đây là số đo trực tiếp từ hai vị trí trong dữ liệu SignalTap.

Tài liệu RTL quy định độ trễ **40 chu kỳ**, tương đương 800 ns ở 50 MHz, theo cách quan sát giá trị thanh ghi **sau cạnh chấp nhận input**. SignalTap lấy mẫu tại cạnh acquisition; khác biệt về thời điểm quan sát trước/sau cập nhật thanh ghi tạo ra độ lệch một mẫu trong cấu hình này.

Cách trình bày chính xác:

> Trên waveform SignalTap, hai sự kiện cách nhau 41 mẫu acquisition. Theo quy ước đo sau cập nhật thanh ghi của RTL, độ trễ thiết kế là 40 chu kỳ. Hai con số dùng hai quy ước quan sát khác nhau; em giữ nguyên số đo và quy ước thay vì sửa chỉ số để chúng bằng nhau.

Không dùng thời gian chạy replay trên máy tính để đo độ trễ RTL hoặc initiation interval: quá trình JTAG có độ trễ giao tiếp và phần mềm. Bản thu này cũng không phải phép thử throughput liên tục ở tốc độ tối đa.

### 6.5 Đọc các bus Q8 trong SignalTap

Các bus đã được nhóm thành `temperature_in_q8`, `pressure_in_q8`, … và `temperature_out_q8`, …, `direction_angle_out_q8`.

- Chọn radix **Signed Decimal** cho sáu trường 18-bit đầu; chia số đọc được cho 256.
- Chọn **Unsigned Decimal** cho `direction_angle_out_q8`; chia cho 256 để được độ.
- Nếu tự giải mã trường signed 18-bit từ hex: nếu raw >= 131072 thì trừ 262144, sau đó chia 256.
- Không đọc toàn bộ bus forecast 126-bit như một số nhiệt độ; phải tách thành bảy trường 18-bit.

| Bits của forecast_data | Trường |
| --- | --- |
| 17:0 | Nhiệt độ |
| 35:18 | Áp suất |
| 53:36 | Độ ẩm |
| 71:54 | Tốc độ gió |
| 89:72 | Cos hướng gió |
| 107:90 | Sin hướng gió |
| 125:108 | Góc hướng gió, unsigned |

Khi trình bày, chọn sample 256 rồi đối chiếu output Q8 với bảng dự báo đầu tiên ở mục 4.2. Dữ liệu input ở sample 215 được validator đối chiếu với vector 25. Chỉ có một giao dịch dự báo trong cửa sổ 512 mẫu; toàn bộ 104 dự báo được kiểm tra bởi replay CSV, không phải đều xuất hiện trong một cửa sổ waveform này.

## 7. Đọc kết luận của bộ kiểm tra acquisition

Mở `capture_check.txt`:

```text
PASS CAPTURE: 512 samples; input and forecast match the reference
Accepted input index: 215
Forecast-valid index: 256
Raw sample separation: 41
Forecast word: 0x5700005800e700d2445a5192201a72
```

Bộ kiểm tra đã xác nhận: đủ 512 mẫu nhị phân, trigger tại 256; đúng một lần nhận input và một xung output valid; reset không tác động; input khớp vector 25; sáu thành phần output khớp từng bit; góc trong miền hợp lệ và sai số vòng tròn không quá 5 Q8.

`capture_check_after_reopen.txt` chứng minh các điều kiện vẫn đạt sau khi nhóm bus và mở lại STP bằng Quartus. `format_data_preserved.txt` xác nhận việc nhóm bus không đổi các bit acquisition.

Nếu chỉ cần xem bảng mà không mở Quartus, mở `weather_speed_live_decoded.csv`. Cột `capture_index` là chỉ số tuyệt đối, `relative_to_trigger` là độ lệch so với mẫu 256, `time_ns` bằng độ lệch nhân 20 ns.

## 8. Đọc tài nguyên và timing

### 8.1 Dùng đúng báo cáo

Dùng **ordinary KEY1** để báo cáo chi phí tài nguyên của thiết kế chạy bình thường. Bản instrumented có thêm phần cứng thu SignalTap nên tiêu tốn tài nguyên hơn.

| Chỉ tiêu | Ordinary KEY1 | Có SignalTap KEY1 |
| --- | ---: | ---: |
| Logic elements | 6.253 / 33.216 | 8.077 / 33.216 |
| Registers | 4.571 | 6.292 |
| Memory bits | 0 | 121.856 |
| Embedded multiplier 9-bit elements | 12 | 12 |
| Slow Fmax CLOCK_50 | 80,89 MHz | 78,51 MHz |
| Slow setup slack | 7,638 ns | 7,262 ns |
| Slow hold slack | 0,391 ns | 0,391 ns |
| Fast hold slack | 0,215 ns | 0,215 ns |
| Clock vận hành | 50 MHz | 50 MHz |

Số 12 ở đây là **phần tử multiplier 9-bit theo cách Quartus báo cáo**, không nên tự đổi cách gọi thành 12 khối nhân 18-bit độc lập.

`Memory bits = 0` của ordinary không có nghĩa thiết kế không lưu lịch sử; lịch sử có thể nằm trong registers. Memory của instrumented chủ yếu phục vụ phần cứng debug/buffer acquisition.

### 8.2 File và panel cần tìm

Trong `ordinary_reports_key1/`:

- `weather_jtag.fit.summary`: device, revision, tổng LE, register, memory và multiplier.
- `weather_jtag.sta.rpt`: tìm `Clocks`, `Slow Model Fmax Summary`, `Slow Model Setup Summary`, `Slow Model Hold Summary`, `Fast Model Hold Summary`.
- `weather_jtag.flow.rpt`: trạng thái các bước compilation.
- `weather_jtag.pin`: xác nhận CLOCK_50 ở N2 và cổng KEY0_N hiện được đặt ở N23.

Có thể mở các file `.rpt` trực tiếp bằng trình soạn thảo. Nếu mở Compilation Report trong Quartus, chọn đúng project ordinary và revision `weather_jtag`, tránh lấy nhầm report của project `capture`.

**Fmax 80,89 MHz** là ước lượng static timing của công cụ cho các đường clock tương ứng, không phải tần số đã tăng clock và chạy thử trên kit. Clock board trong phiên là **50 MHz**. Slack setup dương cho thấy còn dư thời gian theo ràng buộc và mô hình timing đang xét; không phải bằng chứng cho mọi điều kiện vật lý ngoài phạm vi mô hình.

Slow hold là 0,391 ns; fast hold là 0,215 ns. Khi nói minimum của các corner đã báo cáo, dùng 0,215 ns và giữ rõ tên corner, không gán số này cho panel slow hold.

Tài liệu gốc ghi Fmax 79,74 MHz và setup slack 7,459 ns. Bản KEY1 hiện tại có Fmax 80,89 MHz và slack 7,638 ns. Assignment reset đã đổi và fitting được chạy lại; báo cáo số mới đúng với SOF hiện tại, không kết luận KEY1 làm thuật toán tính toán nhanh hơn.

## 9. Giải thích các thay đổi và lỗi trước khi chạy đạt

| Vấn đề gặp trong phiên | Xử lý | Cách báo cáo trung thực |
| --- | --- | --- |
| KEY0 luôn giữ reset dù nhấn/thả, nạp lại và bật lại nguồn | Theo đồng ý người dùng, đổi reset G26 → N23/KEY1 trong hai QSF | Đường KEY0 có vấn đề quan sát được; chưa xác định riêng nút hay mạch nối hỏng |
| Tên cổng vẫn là KEY0_N | Giữ RTL, chỉ đổi pin assignment | Tên logic không quyết định nút vật lý; assignment N23 mới quyết định KEY1 |
| SLD_FILE trỏ máy tác giả | Đổi thành `capture_auto_stripped.stp` tương đối | Sửa đường dẫn khi chuyển máy |
| Error 265013 khi compile SignalTap | Bật TalkBack sau khi người dùng đồng ý | Điều kiện sử dụng SignalTap của Web Edition, không phải lỗi thuật toán |
| Lần arm đầu không thấy PRE kịp thời do buffer stdout | Giữ log cũ, thu lại bằng PTY; chỉ gửi replay sau PRE thật | Chọn lần DONE và validator PASS làm bằng chứng |

Các thay đổi có bản sao/diff trong RUN_DIR. Không sửa mô hình, hệ số, RTL chức năng, vectors, expected values hoặc tăng tolerance để lấy PASS.

Cả hai lần compile KEY1 thành công đều có 7 warnings, không phải “không có cảnh báo”. Không có Critical Warning 35025; bản capture có Info 35024 xác nhận kết nối đủ 240 đầu vào/clock/pin debug cần thiết. Các warnings đã được đọc và ghi trong `STATUS_VI.md`.

## 10. Trình tự trình bày với giảng viên trong 5–7 phút

| Thời lượng gợi ý | Mở gì | Nói gì |
| --- | --- | --- |
| 30–45 giây | Bảng cấu hình ở mục 1 | Kit, chip, công cụ, weather_speed, clock 50 MHz; chủ động nói dùng KEY1 |
| 45 giây | Log programming và cuối ordinary replay | FPGA đã được nạp; chạy đủ 128 input và 104 forecast |
| 1 phút | CSV tại sample_index 24 | Giải thích 24 warm-up, Q8 và một dự báo bằng đơn vị vật lý |
| 2 phút | SignalTap STP, vùng 215–256 | Reset không tác động; handshake nhận input; output valid; đối chiếu bus với CSV |
| 1 phút | Fitter và TimeQuest ordinary KEY1 | 6253 LE, 4571 registers; 50 MHz thực tế, Fmax 80,89 MHz ước lượng |
| 30–45 giây | capture_check, checksum, kết luận | Xác nhận saved data PASS; nêu phạm vi kiểm chứng và thay đổi KEY1 |

Đoạn thuyết trình mẫu:

> Em kiểm chứng thiết kế weather_speed trên kit DE2 dùng Cyclone II EP2C35. Máy tính gửi dữ liệu quan sát có sẵn qua JTAG, FPGA thực hiện tính toán và trả kết quả. Do đường KEY0 giữ reset, em chuyển chân reset sang KEY1 theo assignment N23, giữ nguyên thuật toán và vector kiểm tra.
>
> Bản thông thường đã nạp thành công và xử lý 128 khung. Sau 24 khung warm-up, cả 104 dự báo đều khớp tham chiếu. Đây là một dòng đầu tiên: nhiệt độ 26,45 °C và hướng gió 5,44°.
>
> Với bản có SignalTap, em arm bộ thu trước rồi chạy replay. Tại mẫu 215, sample_valid và sample_ready cùng bằng 1 nên input được nhận. Tại mẫu 256, forecast_valid lên 1 và bus output khớp cùng vector. Reset không tác động trong cửa sổ này. Khoảng cách trên acquisition là 41 mẫu; tài liệu RTL dùng quy ước sau cạnh nên ghi 40 chu kỳ.
>
> Bản ordinary dùng 6253 LE và 4571 registers, chạy ở 50 MHz. TimeQuest ước lượng Fmax 80,89 MHz. Kết quả chứng minh phần cứng khớp tham chiếu fixed-point trên bộ vector thử; em không dùng PASS này để khẳng định độ chính xác dự báo thời tiết tương lai.

## 11. Chuẩn bị hình và nội dung đưa vào báo cáo

Phiên này **chưa chụp GUI thực tế**. Nếu cần hình trong báo cáo, tự mở dữ liệu đã lưu theo mục 5 và chụp màn hình thật; không dùng ảnh lịch sử trong archive như ảnh của phiên này.

Nên có bốn hình:

1. Log ordinary có Variant, node và dòng PASS 128/104; chú thích “Replay JTAG trên DE2, phiên 03/11/2026, reset KEY1”.
2. Waveform có tên `core_rst_n`, `sample_valid`, `sample_ready`, `forecast_valid`, thước mẫu và hai vị trí −41/0 hoặc 215/256.
3. Bus output tại valid, thấy các giá trị Q8; kèm bảng đổi đơn vị như mục 4.2.
4. Fitter/TimeQuest ordinary KEY1, nhìn rõ revision, device, clock name và corner timing.

Ảnh mở lại waveform nên ghi: **“Dữ liệu thu trên kit ngày 03/11/2026; ảnh hiển thị lại từ STP đã lưu.”** Ngày chụp ảnh có thể khác ngày thu dữ liệu.

Bố cục báo cáo viết:

- Mục tiêu và cấu hình kiểm chứng.
- Phương pháp: nạp ordinary, replay, nạp instrumented, arm trước replay và thu SignalTap.
- Bảng kết quả chức năng: 128 input, 24 warm-up, 104 match; kiểm tra góc; kết quả acquisition.
- Phân tích waveform tại input/output, diễn giải 41 mẫu và 40 chu kỳ.
- Bảng tài nguyên và timing; tách ordinary với instrumented.
- Khác biệt so với quy trình gốc: KEY1, đường dẫn, TalkBack; giới hạn của PASS.
- Phụ lục đường dẫn log, CSV, STP, reports và checksum.

## 12. Câu hỏi thường gặp khi bảo vệ

**Tại sao có 128 đầu vào nhưng chỉ 104 dự báo?**
24 khung đầu điền lịch sử; khung thứ 25 tạo dự báo đầu tiên. 128 − 24 = 104.

**Tại sao có 7 đầu ra nhưng nói 5 đại lượng thời tiết?**
Nhiệt độ, áp suất, độ ẩm, tốc độ gió và góc hướng gió là năm đại lượng. Cos/sin là hai đầu ra hỗ trợ biểu diễn hướng.

**Có dùng cảm biến thời tiết trực tiếp không?**
Không. Phiên này replay quan sát đã đóng gói trong vector qua JTAG. FPGA thực hiện tính toán thật trên dữ liệu đó.

**Mở lại STP có được gọi là chạy live không?**
Không. STP chứa dữ liệu thu thật trong phiên đã ghi ngày giờ, nhưng mở lại chỉ là xem bằng chứng đã lưu. Một demo live mới phải nạp, arm và replay mới.

**Tại sao không hiển thị dự báo trên LED/LCD?**
Thiết kế demo này trả kết quả qua JTAG và CSV, không ánh xạ dự báo ra LED, seven-segment hoặc LCD.

**512 mẫu có phải 512 khung thời tiết không?**
Không. Đó là 512 lần lấy mẫu tín hiệu nội bộ ở clock 50 MHz. Chỉ một input accepted và một output valid nằm trong cửa sổ này.

**Đây có phải chứng minh KEY0 bị hỏng không?**
Chỉ đủ kết luận đường reset qua KEY0/G26 gây giữ reset trong các phép thử, còn KEY1 hoạt động. Muốn xác định linh kiện hỏng cần kiểm tra điện phần cứng riêng.

**Tắt nguồn rồi có mất kết quả không?**
Log, CSV và STP trên máy vẫn còn. FPGA mất cấu hình SRAM nên muốn chạy lại phải nạp SOF KEY1 thích hợp. Không cần nạp lại để chỉ xem file đã lưu.

## 13. Kiểm tra hồ sơ trước khi nộp

- Đường dẫn dẫn tới phiên `20261103_082707`, không phải `defense_session` của tác giả.
- Chọn log replay KEY1 thành công và acquisition PTY có PRE/DONE.
- Bảng tài nguyên lấy từ `ordinary_reports_key1/`.
- Ghi reset KEY1/N23, clock 50 MHz và phiên bản Quartus.
- Ghi rõ ảnh là xem lại bản thu nếu chưa thực hiện một lần live mới.
- Giữ bản gốc raw STP, CSV, logs, báo cáo và `SHA256SUMS.txt`; ảnh bổ sung có thể lưu riêng để không nhầm phạm vi checksum cũ.
- Hồ sơ tại thời điểm bàn giao đã kiểm tra SHA256 của 279 file. Tài liệu hướng dẫn này được tạo sau đó, nằm ngoài RUN_DIR và không thuộc danh sách 279 file ấy.
- Bản sao lưu ở thiết bị/thư mục thứ hai chưa được thực hiện trong phiên; nên bổ sung trước buổi báo cáo.

Nếu cần chạy lại toàn bộ thay vì đọc kết quả, xem [quy trình tái hiện gốc](WEATHER_SPEED_DE2_REPRODUCTION.md) và [ghi chú demo KEY1 của phiên](../reports/reproduction_weather_speed/20261103_082707/DEMO_VI.md). Nhớ áp dụng khác biệt KEY1; không chạy script thu/replay ghi đè vào hồ sơ đã nghiệm thu.
