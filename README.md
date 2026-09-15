# FPGA-Based 3-Hour Temperature Predictor (Dự Án Dự Báo Nhiệt Độ Sau 3 Giờ Trên FPGA)

## 1. Giới thiệu Đề tài
Dự án thực hiện dự báo nhiệt độ tại thời điểm \(t+3\) giờ dựa trên chuỗi dữ liệu nhiệt độ quá khứ bằng mô hình tuyến tính có xét tính chu kỳ ngày đêm:

$$\widehat T_{t+3} = T_{t-21} + a(T_t - T_{t-24}) + b(T_t - T_{t-3}) + c$$

Trong đó:
- $T_{t-21}$: Nhiệt độ cùng giờ của ngày hôm trước so với giờ cần dự báo ($t+3 - 24 = t-21$).
- $(T_t - T_{t-24})$: Sai lệch nhiệt độ hiện tại so với cùng giờ ngày hôm trước (xu hướng chênh lệch liên ngày).
- $(T_t - T_{t-3})$: Sai lệch nhiệt độ trong 3 giờ gần nhất (xu hướng biến thiên ngắn hạn).
- $a, b, c$: Các hệ số được huấn luyện từ dữ liệu lịch sử bằng C++.

---

## 2. Cấu trúc Thư mục Dự án

```text
fpga-temp-predictor/
├── data/
│   ├── raw/                # Dữ liệu gốc tải về (CSV)
│   ├── processed/          # Dữ liệu đã xử lý và làm sạch (train.csv, test.csv)
│   └── testvectors/        # Vector kiểm thử (đầu vào & nhãn mẫu) cho FPGA Testbench
├── software/
│   ├── Makefile            # Lệnh biên dịch C++
│   ├── include/            # Header files (fixed_point.h...)
│   ├── src/
│   │   ├── train_float.cpp   # Huấn luyện tìm hệ số a, b, c bằng số thực
│   │   └── predict_fixed.cpp # Mô phỏng số cố định (fixed-point) & sinh testvector
│   ├── scripts/            # Script tiền xử lý dữ liệu và vẽ biểu đồ
│   └── bin/                # Thư mục chứa file thực thi
├── hardware/
│   ├── rtl/                # Mã nguồn phần cứng Verilog/SystemVerilog
│   │   └── temp_predictor_core.v
│   ├── tb/                 # Testbench mô phỏng kiểm thử RTL
│   │   └── tb_temp_predictor_core.v
│   └── constrs/            # File gán chân FPGA (XDC / QSF)
├── docs/                   # Báo cáo, slide và biểu đồ kết quả
└── .vscode/                # Cấu hình VS Code (tasks, settings, extensions)
```

---

## 3. Quy trình Thực hiện (5 Giai đoạn)

### Bước 1: Chuẩn bị Dữ liệu & Huấn luyện C++ (Floating-point)
1. Sinh dữ liệu mẫu:
   ```bash
   python3 software/scripts/generate_sample_data.py
   ```
2. Biên dịch và huấn luyện:
   ```bash
   cd software
   make
   ./bin/train_float ../data/processed/train.csv
   ```
   Chương trình sẽ in ra các hệ số tối ưu $a, b, c$ cùng sai số MAE/RMSE so với các baseline.

### Bước 2: Mô phỏng Số Cố Định (Fixed-point)
1. Chạy mô hình số cố định (định dạng Q8.8 hoặc Q10.6):
   ```bash
   ./bin/predict_fixed ../data/processed/test.csv ../data/testvectors/testvectors.txt
   ```
   Chương trình sẽ tạo ra file `testvectors.txt` chứa cả đầu vào và kết quả mẫu để nạp cho FPGA testbench.

### Bước 3: Thiết kế & Mô phỏng Phần cứng (Verilog)
Mô phỏng bằng **Icarus Verilog**:
```bash
iverilog -o hardware/tb/sim.vvp hardware/rtl/temp_predictor_core.v hardware/tb/tb_temp_predictor_core.v
vvp hardware/tb/sim.vvp
```
Testbench sẽ đọc `testvectors.txt`, đưa vào mạch `temp_predictor_core` và tự động đối chiếu từng bit kết quả.

### Bước 4: Triển khai lên Board FPGA
- Tạo project trong Vivado / Quartus.
- Thêm file RTL trong `hardware/rtl/` và gán chân board trong `hardware/constrs/`.
- Tích hợp giao tiếp UART để truyền nhận dữ liệu với máy tính.

### Bước 5: Báo cáo & Đánh giá
- Thống kê tài nguyên FPGA (LUT, FF, DSP slices).
- Đánh giá độ chênh lệch sai số giữa C++ Floating-point, C++ Fixed-point và FPGA RTL.
