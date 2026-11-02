# Tái hiện thiết kế dự báo thời tiết tối ưu tốc độ từ GitHub

Quy trình WS-DE2-02-VI · Bản 1 · Ngày 2 tháng 11 năm 2026

Hướng dẫn này dành cho người bắt đầu từ một thư mục trống trên máy tính cá nhân: tải mã nguồn, lấy tệp cấu hình FPGA đã cung cấp, chạy bộ dự báo trên board DE2 và thu dạng sóng trực tiếp bằng SignalTap. Các lệnh không phụ thuộc tên người dùng hay thư mục cài đặt của tác giả.

Kho mã nguồn: <https://github.com/KhoaLe-IC/fpga-temp-predictor>

Thiết kế đã được kiểm chứng trên phần cứng bằng Quartus II Web Edition 13.0 SP1 trên Linux. Các bước PowerShell dùng cùng tệp và công cụ Quartus, nhưng chưa được chạy thử với board trên Windows trong lần rà soát tài liệu này.

## Chuẩn bị

Cần **board Terasic DE2 nguyên bản, chip EP2C35F672C6**, bộ nguồn của board, kết nối USB-Blaster và máy tính Windows hoặc Linux chạy được Quartus II 13.0 SP1. DE2-70 và DE2-115 dùng chip khác, không sử dụng trực tiếp các tệp cấu hình trong hướng dẫn này. Không cần bộ chuyển đổi UART hoặc cảm biến thời tiết.

Cài các công cụ sau:

| Công cụ | Mục đích |
| --- | --- |
| Git | Tải kho mã nguồn và ghi nhận phiên bản |
| Quartus II Web Edition 13.0 SP1 | Nạp cấu hình Cyclone II và truy cập JTAG |
| Gói hỗ trợ Cyclone II và driver USB-Blaster | Nhận diện và truy cập board |
| Python 3.9 trở lên | Kiểm tra CSV và dữ liệu SignalTap bằng thư viện chuẩn |
| `tar` | Giải nén các tệp cấu hình đã cung cấp |

Tải Quartus từ trang chính thức cho [Windows](https://www.altera.com/downloads/fpga-development-tools/quartus-ii-web-edition-design-software-version-13-0sp1-windows) hoặc [Linux](https://www.altera.com/downloads/fpga-development-tools/quartus-ii-web-edition-design-software-version-13-0sp1-linux). Cài cả phần mềm và gói hỗ trợ Cyclone II tương ứng. Phiên bản đã dùng để kiểm chứng là 13.0.1 Build 232. Không cần ModelSim cho quy trình chạy lại trên board này.

Cài [Git](https://git-scm.com/downloads) và [Python](https://www.python.org/downloads/) nếu chưa có. **Không cần cài các gói trong `requirements.txt`**: mô hình và bộ dữ liệu kiểm tra đã được chuẩn bị sẵn.

Trên Windows, dùng **PowerShell**, không dùng Command Prompt, Git Bash hay WSL cho các khối lệnh Windows. Trên Linux, dùng **Bash**. Chỉ làm theo nhánh phù hợp với hệ điều hành của mình. Hướng dẫn chưa xác nhận khả năng chạy trực tiếp trên macOS hoặc chuyển tiếp USB qua máy ảo.

Làm lần lượt mục 1–8 để chạy cấu hình có sẵn. Mục 9 dành cho biên dịch lại từ mã nguồn. Giữ nguyên tên tệp, tên tín hiệu và lệnh tiếng Anh để có thể sao chép chính xác. Các thông báo PASS và mục trình đơn Quartus cũng được giữ nguyên để dễ đối chiếu.

## 1 Tải kho mã nguồn

1. Mở PowerShell trên Windows hoặc Bash trên Linux. Chọn một thư mục có quyền ghi để chứa dự án; khi tập thử, nên tránh thư mục mạng hoặc thư mục đang đồng bộ.
2. Kiểm tra Git:

   ```text
   git --version
   ```

3. Tải bằng HTTPS rồi chuyển vào thư mục dự án. Hai lệnh sau dùng được trong cả PowerShell và Bash:

   ```text
   git clone https://github.com/KhoaLe-IC/fpga-temp-predictor.git
   cd fpga-temp-predictor
   ```

   Đường dẫn này không cần khóa SSH của tác giả hay quyền truy cập máy tính của tác giả.

4. Kiểm tra phiên bản mã nguồn và thư mục gốc:

   ```text
   git rev-parse HEAD
   git rev-parse --show-toplevel
   ```

   Lệnh thứ hai in ra vị trí dự án **trên máy của bạn**. Phiên bản dùng khi kiểm tra hướng dẫn là `a476b32e42db90a7c68c94c941427b44cd9a65a2`. Những commit sau có thể bổ sung tài liệu mà không thay đổi mô hình hay tệp FPGA.

5. Giữ cửa sổ này mở. Các lệnh phía sau bắt đầu tại thư mục gốc dự án, trừ khi bước đó yêu cầu chuyển thư mục.

Nếu tải ZIP từ GitHub, hãy giải nén rồi mở terminal tại thư mục có `hardware`, `scripts` và `versions`. Bản ZIP không chạy được `git rev-parse`; hãy ghi lại nhánh hoặc commit đã tải bằng cách khác. Các thao tác với tệp vẫn thực hiện được.

## 2 Thiết lập công cụ trên máy của bạn

Chỉ thực hiện mục 2.1 hoặc 2.2. Đường dẫn dự án được lấy từ thư mục hiện tại; nếu Quartus chưa có trên PATH, bạn cần cung cấp vị trí cài đặt **trên máy mình**.

### 2.1 Windows PowerShell

1. Xác nhận đang đứng trong thư mục dự án vừa tải:

   ```powershell
   if (-not (Test-Path 'scripts/replay_jtag.tcl')) {
       throw 'Open PowerShell inside the cloned fpga-temp-predictor folder.'
   }
   $ProjectRoot = (Get-Location).Path
   ```

2. Tìm Quartus. Nếu `quartus_sh.exe` đã có trên PATH, đoạn lệnh tự sử dụng vị trí đó. Nếu chưa, chương trình sẽ hỏi đường dẫn đầy đủ đến tệp thực thi:

   ```powershell
   $QuartusCommand = Get-Command quartus_sh.exe -ErrorAction SilentlyContinue
   if ($null -eq $QuartusCommand) {
       $QuartusExe = Read-Host 'Paste the full path to quartus_sh.exe without quotation marks'
       if (-not (Test-Path -LiteralPath $QuartusExe -PathType Leaf)) {
           throw 'That executable does not exist. Locate quartus_sh.exe in your Quartus installation.'
       }
       $QuartusBin = Split-Path -LiteralPath $QuartusExe
   } else {
       $QuartusBin = Split-Path -LiteralPath $QuartusCommand.Source
   }
   $env:Path = "$QuartusBin;$env:Path"
   ```

   Mở File Explorer, tìm thư mục cài Quartus rồi vào `bin` hoặc `bin64` để tìm `quartus_sh.exe`. Sao chép đường dẫn đầy đủ của tệp này. `C:\altera\13.0sp1` chỉ là ví dụ thư mục cài đặt; không nhập ví dụ nếu máy bạn không có thư mục đó.

3. Kiểm tra công cụ và phiên bản:

   ```powershell
   Get-Command quartus_sh, quartus_pgm, quartus_stp, jtagconfig, tar -ErrorAction Stop
   quartus_sh --version
   py -3 --version
   ```

   Cần Quartus 13.0 SP1 và Python từ 3.9. Nếu thiếu trình khởi chạy `py`, sửa cài đặt Python trước khi dùng các lệnh `py -3` bên dưới.

4. Tạo thư mục kết quả mới và ghi nhận vị trí:

   ```powershell
   $RunDir = Join-Path $ProjectRoot ('build/reproduction/weather_speed_' + (Get-Date -Format 'yyyyMMdd_HHmmss'))
   New-Item -ItemType Directory -Path $RunDir -Force | Out-Null
   Write-Output $RunDir
   git rev-parse HEAD | Set-Content (Join-Path $RunDir 'commit.txt')
   quartus_sh --version 2>&1 | Out-File (Join-Path $RunDir 'quartus_version.txt')
   ```

Chuyển đến mục 3. Các biến chỉ tồn tại trong cửa sổ PowerShell hiện tại; cửa sổ mới không tự nhận các biến này.

### 2.2 Linux Bash

1. Xác nhận đang đứng trong thư mục dự án vừa tải:

   ```bash
   test -f scripts/replay_jtag.tcl || {
     printf '%s\n' 'Open Bash inside the cloned fpga-temp-predictor folder.'
     exit 1
   }
   ProjectRoot="$PWD"
   ```

2. Tìm Quartus. Đoạn lệnh dùng vị trí có sẵn trên PATH hoặc hỏi thư mục chứa `quartus_sh`:

   ```bash
   if command -v quartus_sh >/dev/null 2>&1; then
     QuartusBin="$(dirname "$(command -v quartus_sh)")"
   else
     read -r -p 'Paste the full directory containing quartus_sh: ' QuartusBin
   fi
   test -x "$QuartusBin/quartus_sh" || {
     printf '%s\n' 'quartus_sh was not found in that directory.'
     exit 1
   }
   export PATH="$QuartusBin:$PATH"
   ```

   Có thể dùng trình quản lý tệp để tìm thư mục cài đặt. Dán đường dẫn tuyệt đối đến `quartus/bin`, không thêm dấu nháy. Không sao chép đường dẫn chứa tên người dùng của máy khác.

3. Kiểm tra công cụ và phiên bản:

   ```bash
   command -v quartus_sh quartus_pgm quartus_stp jtagconfig tar python3
   quartus_sh --version
   python3 --version
   ```

   Xác nhận tất cả lệnh đều được tìm thấy, Quartus là 13.0 SP1 và Python từ 3.9. Xử lý lỗi khởi động hoặc thiếu thư viện trước khi kết nối board.

4. Tạo thư mục kết quả mới và ghi nhận vị trí:

   ```bash
   RunDir="$ProjectRoot/build/reproduction/weather_speed_$(date +%Y%m%d_%H%M%S)"
   mkdir -p "$RunDir"
   printf '%s\n' "$RunDir"
   git rev-parse HEAD > "$RunDir/commit.txt"
   quartus_sh --version > "$RunDir/quartus_version.txt" 2>&1
   set -o pipefail
   ```

Chuyển đến mục 3 trong cùng terminal để tiếp tục dùng các biến `ProjectRoot` và `RunDir`.

## 3 Giải nén tệp cấu hình FPGA

Bản clone mới thường **không có tệp SOF riêng lẻ** vì đầu ra biên dịch bị Git bỏ qua. Kho mã nguồn có lưu một tệp nén chứa các cấu hình đã kiểm chứng. Bước này giải nén vào thư mục kết quả mới, không ghi đè mã nguồn.

### 3.1 Giải nén trên Windows

Chạy trong cửa sổ PowerShell đã thiết lập:

```powershell
$PackageDir = Join-Path $RunDir 'packaged'
New-Item -ItemType Directory -Path $PackageDir -Force | Out-Null
tar -xzf docs/reports/defense_evidence_2026-10-28.tar.gz -C "$PackageDir"
if ($LASTEXITCODE -ne 0) { throw 'Archive extraction failed.' }
$OrdinarySof = Join-Path $PackageDir 'versions/weather_v2/quartus/de2_jtag_speed/output_files/weather_jtag.sof'
$CaptureSof = Join-Path $PackageDir 'hardware/quartus/signaltap/weather_speed/output_files/capture.sof'
$CaptureSetup = Join-Path $PackageDir 'hardware/quartus/signaltap/weather_speed/capture.stp'
Get-Item $OrdinarySof, $CaptureSof, $CaptureSetup, 'hardware/jtag/vectors/weather.txt' -ErrorAction Stop
Get-FileHash -Algorithm SHA256 $OrdinarySof, $CaptureSof
```

### 3.2 Giải nén trên Linux

Chạy trong cửa sổ Bash đã thiết lập:

```bash
PackageDir="$RunDir/packaged"
mkdir -p "$PackageDir"
tar -xzf docs/reports/defense_evidence_2026-10-28.tar.gz -C "$PackageDir"
OrdinarySof="$PackageDir/versions/weather_v2/quartus/de2_jtag_speed/output_files/weather_jtag.sof"
CaptureSof="$PackageDir/hardware/quartus/signaltap/weather_speed/output_files/capture.sof"
CaptureSetup="$PackageDir/hardware/quartus/signaltap/weather_speed/capture.stp"
ls -l "$OrdinarySof" "$CaptureSof" "$CaptureSetup" hardware/jtag/vectors/weather.txt
sha256sum "$OrdinarySof" "$CaptureSof"
```

### 3.3 Đối chiếu tệp cấu hình

Hai tệp trong gói đã được kiểm tra có SHA-256 như sau:

| Cấu hình | SHA-256 |
| --- | --- |
| Weather speed thông thường | `6983677cd3563baaa6f7b06cdc5ddacb70f3843e729ea46484f09897e7752f96` |
| Weather speed có SignalTap | `aec8714829982c4a139070690d5997693d20b050e928850e031f523202880027` |

Cấu hình thông thường dùng để chạy lại và đối chiếu kết quả. Cấu hình có SignalTap bổ sung mạch thu dạng sóng. Cả hai đều là hệ thống dự báo thời tiết tối ưu tốc độ.

Trong gói còn có báo cáo và trạng thái từ lần chạy trước. Những tệp đó không chứng minh board của bạn vừa chạy thành công. Kết quả mới được lưu cạnh `packaged/` trong thư mục của lần chạy hiện tại.

Nếu không có tệp nén, kiểm tra đã tải đủ kho mã nguồn và đang ở đúng thư mục. Có thể biên dịch từ mã nguồn theo mục 9. Không thay bằng SOF của `de2_jtag_resource`, dự án UART hay lõi xử lý riêng vì thấy tên gần giống.

## 4 Kết nối và nạp DE2

### 4.1 Kiểm tra kết nối JTAG

1. Tắt nguồn board. Tìm **công tắc vật lý RUN/PROG ở cạnh trái của DE2 nguyên bản** và gạt về **RUN**. Đây là công tắc trên board, không phải tùy chọn trong Quartus. Nếu board hoặc nhãn khác mô tả này, đối chiếu sách hướng dẫn đúng phiên bản board trước khi tiếp tục.
2. Cắm bộ nguồn ngoài cho board và nối cổng lập trình USB-Blaster với máy tính.
3. Bật nguồn board; nhả KEY0 vì đây là nút reset của ứng dụng.
4. Trong terminal đã chuẩn bị, chạy:

   ```text
   jtagconfig
   ```

5. Phải thấy chip EP2C35 với ID `020B40DD` bên dưới USB-Blaster, ví dụ:

   ```text
   1) USB-Blaster [1-1]
     020B40DD   EP2C35 (IR=10)
   ```

   Địa chỉ cáp có thể khác. Ghi lại số thứ tự cáp; lệnh nạp bên dưới giả sử cáp số **1**.

Nếu Windows nhận thiết bị USB chưa rõ loại, dùng Device Manager cài driver USB-Blaster từ thư mục driver của Quartus theo [hướng dẫn của hãng](https://www.altera.com/developers/software/cables-and-adapter-drivers-installation-guide). Trên Linux, kiểm tra quyền truy cập thiết bị theo tài liệu của hãng. Chỉ tiếp tục khi `jtagconfig` nhìn thấy FPGA, không chỉ tên cáp.

### 4.2 Nạp cấu hình thông thường

Lệnh sau dùng được trong cả hai terminal đã thiết lập vì đều có biến `OrdinarySof`:

```text
quartus_pgm -m jtag -c 1 -o "p;$OrdinarySof"
```

Thay `1` bằng số cáp thực tế. Chờ thông báo `Configuration succeeded` hoặc trạng thái hoàn tất thành công trong Programmer.

Để thao tác bằng giao diện, mở Quartus > Tools > Programmer, chọn USB-Blaster trong Hardware Setup, chọn chế độ JTAG, thêm tệp được biến `OrdinarySof` trỏ tới, đánh dấu Program/Configure rồi bấm Start. Để xem đường dẫn tệp, nhập:

```text
echo $OrdinarySof
```

Chụp màn hình có thiết bị, tệp đã chọn và trạng thái thành công. Cấu hình nằm trong SRAM; sau khi tắt nguồn board, phải nạp lại.

## 5 Chạy lại dữ liệu và kiểm tra dự báo

Script reset lõi qua JTAG, gửi 128 khung dữ liệu đã ghi sẵn rồi kiểm tra 104 dự báo sau 24 khung khởi tạo lịch sử. Bộ dữ liệu là `hardware/jtag/vectors/weather.txt`, có sẵn trong kho.

Đóng các công cụ đang ghi Sources/Probes thủ công để chúng không thay đổi mailbox khi script truyền dữ liệu.

### 5.1 Chạy trên Windows

```powershell
$env:FPGA_JTAG_CSV = Join-Path $RunDir 'ordinary_replay.csv'
quartus_stp -t scripts/replay_jtag.tcl weather_speed 2>&1 |
    Tee-Object -FilePath (Join-Path $RunDir 'ordinary_replay.log')
if ($LASTEXITCODE -ne 0) { throw 'Replay failed. Read ordinary_replay.log.' }
```

### 5.2 Chạy trên Linux

```bash
FPGA_JTAG_CSV="$RunDir/ordinary_replay.csv" \
  quartus_stp -t scripts/replay_jtag.tcl weather_speed \
  2>&1 | tee "$RunDir/ordinary_replay.log"
```

### 5.3 Kiểm tra chạy hoàn tất

Đầu ra phải nhận diện `Variant: weather_speed`, nút Sources/Probes `{0 128 256 FCST}` và kết thúc bằng:

```text
PASS PHYSICAL JTAG weather_speed: inputs=128 forecasts=104; CSV=...
```

Đường dẫn CSV phải nằm trong thư mục kết quả mới. Nếu bỏ thiết lập đầu ra ở trên, script sẽ ghi đè tệp cũ `docs/reports/physical_jtag_weather_speed.csv` trong kho.

Mỗi dòng dự báo lần lượt gồm: nhiệt độ (°C), áp suất (kPa), độ ẩm tương đối (%), tốc độ gió (m/s), cos hướng gió, sin hướng gió và góc hướng gió (độ). Kết quả đầu tiên là `sample=24`, tức khung thứ 25 vì chỉ số bắt đầu từ 0.

Với bộ dữ liệu cung cấp không thay đổi, kết quả đầu tiên đã lưu là:

```text
sample=24 forecast=26.445312 100.531250 69.644531 3.285156 0.902344 0.085938 5.437500 match=True
```

FPGA tính dự báo; máy tính gửi quan trắc và so sánh giá trị nhận về với mô hình tham chiếu. Phép chạy này kiểm tra phần cứng tính đúng theo tham chiếu. Độ chính xác dự báo so với thời tiết quan sát về sau là một phép đánh giá riêng.

### 5.4 Kiểm tra tệp CSV đã lưu

Sao chép mã ở Phụ lục B vào trình soạn thảo và lưu thành `verify_weather_run.py` trong thư mục kết quả. Trên Windows, chọn All files khi lưu để tránh tên `verify_weather_run.py.txt`.

**Cần chạy cả bước kiểm tra này.** Script JTAG hiện có chưa kiểm tra đầy đủ miền giá trị góc trước khi tính sai số vòng tròn. Bộ kiểm tra ở bản hướng dẫn này bổ sung điều kiện góc từ 0 đến dưới 360° cho CSV và SignalTap; thông báo PASS của replay một mình chưa đủ để nghiệm thu.

Trên Windows:

```powershell
py -3 "$RunDir/verify_weather_run.py" "$RunDir/ordinary_replay.csv"
if ($LASTEXITCODE -ne 0) { throw 'CSV validation failed.' }
```

Trên Linux:

```bash
python3 "$RunDir/verify_weather_run.py" "$RunDir/ordinary_replay.csv"
```

Kết quả cần có: `PASS CSV: 128 inputs, 24 warm-up rows, 104 matching forecasts`.

## 6 Thu dạng sóng trực tiếp

Hoàn tất chạy cấu hình thông thường và lưu log trước khi đổi cấu hình.

### 6.1 Nạp cấu hình có SignalTap

1. Trong terminal đã thiết lập, nạp SOF có mạch thu:

   ```text
   quartus_pgm -m jtag -c 1 -o "p;$CaptureSof"
   ```

2. Sao chép STP tương ứng vào thư mục kết quả.

   Windows:

   ```powershell
   Copy-Item -LiteralPath $CaptureSetup -Destination (Join-Path $RunDir 'weather_speed_live.stp')
   ```

   Linux:

   ```bash
   cp "$CaptureSetup" "$RunDir/weather_speed_live.stp"
   ```

3. Mở Quartus > Tools > SignalTap II Logic Analyzer. Mở bản sao `weather_speed_live.stp` vừa tạo.
4. Trong JTAG Chain Configuration, chọn USB-Blaster và EP2C35 đang kết nối. Tệp lưu sẵn chứa tên cáp của máy cũ; phải kiểm tra lại khi đổi máy.
5. Nếu ô SOF đang trỏ sai do đường dẫn tương đối cũ, duyệt đến tệp được biến `CaptureSof` chỉ ra.
6. Xác nhận instance `auto_signaltap_0`, clock `CLOCK_50`, độ sâu thu 512 mẫu, vị trí trigger ở giữa và trigger cạnh lên của `jtag_mailbox:mailbox|forecast_valid`. Lưu bản sao STP rồi đóng cửa sổ SignalTap.

Đổi cáp không thay đổi mô hình dự báo. Đổi tín hiệu quan sát hoặc cấu hình trigger có thể cần biên dịch lại. Khi tái hiện kết quả, giữ nguyên cấu hình thu đã cung cấp.

### 6.2 Tạo tệp lệnh thu

Dùng trình soạn thảo lưu đoạn dưới thành `acquire_weather_speed.tcl` trong thư mục kết quả. Tệp dùng được trên cả hai hệ điều hành và không ghi vào thư mục bằng chứng cũ.

```tcl
package require ::quartus::stp
set args $quartus(args)
if {[llength $args] != 1} {
    error "Supply the full path to weather_speed_live.stp"
}
set capture_file [file normalize [lindex $args 0]]
open_session -name $capture_file
puts "CAPTURE ARMED: run weather_speed replay in the other terminal"
flush stdout
run -instance auto_signaltap_0 \
    -signal_set signal_set_1 \
    -trigger trigger_1 \
    -data_log live_capture \
    -timeout 120
close_session
puts "CAPTURE SAVED: $capture_file"
```

Trên Windows, kiểm tra phần mở rộng là `.tcl`, không phải `.tcl.txt`.

### 6.3 Chuẩn bị terminal thứ hai

1. Mở terminal **cùng loại** với terminal đầu.
2. Chuyển đến đúng thư mục dự án vừa clone. Trên Windows có thể mở File Explorer tại thư mục rồi chọn Open in Terminal; trên Linux dùng Open Terminal Here nếu có.
3. Lấy giá trị thực tế của `RunDir` và `QuartusBin` từ terminal đầu bằng:

   ```text
   echo $RunDir
   echo $QuartusBin
   ```

4. Nhập lại đúng hai đường dẫn vừa in vào terminal thứ hai khi được hỏi.

   Windows:

   ```powershell
   $RunDir = Read-Host 'Paste the existing run directory without quotation marks'
   $QuartusBin = Read-Host 'Paste the Quartus executable directory without quotation marks'
   $env:Path = "$QuartusBin;$env:Path"
   if (-not (Test-Path 'scripts/replay_jtag.tcl')) { throw 'Enter the clone root first.' }
   ```

   Linux:

   ```bash
   read -r -p 'Paste the existing run directory: ' RunDir
   read -r -p 'Paste the Quartus executable directory: ' QuartusBin
   export PATH="$QuartusBin:$PATH"
   test -f scripts/replay_jtag.tcl || exit 1
   set -o pipefail
   ```

Terminal đầu thu dạng sóng; terminal thứ hai gửi dữ liệu. Cả hai phải dùng cùng FPGA và cùng thư mục kết quả.

### 6.4 Thu và gửi dữ liệu

1. Trong **terminal đầu**, chạy:

   ```text
   quartus_stp -t "$RunDir/acquire_weather_speed.tcl" "$RunDir/weather_speed_live.stp"
   ```

2. Chờ `CAPTURE ARMED` và trạng thái chờ dữ liệu trước trigger của SignalTap (`PRE` trong log đã lưu). Lệnh tiếp tục chờ trong lúc thu. Riêng dòng `CAPTURE ARMED` được in trước khi gọi lệnh thu nên chưa đủ để xác nhận thiết bị đã sẵn sàng.
3. Trong **terminal thứ hai**, chạy replay với cấu hình có SignalTap.

   Windows:

   ```powershell
   $env:FPGA_JTAG_CSV = Join-Path $RunDir 'capture_replay.csv'
   quartus_stp -t scripts/replay_jtag.tcl weather_speed 2>&1 |
       Tee-Object -FilePath (Join-Path $RunDir 'capture_replay.log')
   if ($LASTEXITCODE -ne 0) { throw 'Instrumented replay failed.' }
   ```

   Linux:

   ```bash
   FPGA_JTAG_CSV="$RunDir/capture_replay.csv" \
     quartus_stp -t scripts/replay_jtag.tcl weather_speed \
     2>&1 | tee "$RunDir/capture_replay.log"
   ```

4. Xác nhận replay báo PASS với 128 đầu vào và 104 dự báo.
5. Trở về terminal đầu, kiểm tra `CAPTURE SAVED` và trạng thái SignalTap `DONE`.
6. Tại thư mục gốc dự án, kiểm tra cả hai tệp mới.

   Windows:

   ```powershell
   py -3 "$RunDir/verify_weather_run.py" "$RunDir/capture_replay.csv" --stp "$RunDir/weather_speed_live.stp" --vectors hardware/jtag/vectors/weather.txt
   if ($LASTEXITCODE -ne 0) { throw 'Capture validation failed.' }
   ```

   Linux:

   ```bash
   python3 "$RunDir/verify_weather_run.py" "$RunDir/capture_replay.csv" \
     --stp "$RunDir/weather_speed_live.stp" \
     --vectors hardware/jtag/vectors/weather.txt
   ```

Cần thấy cả `PASS CSV` và `PASS CAPTURE`. Trong bản thu gốc, khung được nhận ở chỉ số 215 và `forecast_valid` lên ở 256, cách nhau 41 mẫu. Độ trễ RTL được tài liệu hóa là 40 chu kỳ theo cách quan sát sau cạnh clock; SignalTap lấy mẫu trước lần cập nhật thanh ghi mà scoreboard RTL quan sát. Không dùng hai quy ước này lẫn nhau khi giải thích kết quả.

Nếu hết thời gian chờ, giữ nguyên bản thu lỗi, kiểm tra SOF, STP tương ứng, thiết bị và trigger. Làm lại mục 6.4 với bộ thu sẵn sàng trước khi chạy replay.

## 7 Hiển thị kết quả trong Quartus

1. Sau khi hai tiến trình terminal kết thúc, mở `weather_speed_live.stp` trong SignalTap.
2. Chọn data log vừa thu và hiển thị dạng sóng.
3. Tìm `core_rst_n`, `sample_valid`, `sample_ready`, `forecast_valid`. Chỉ ra thời điểm nhận dữ liệu khi valid và ready cùng bằng 1, sau đó là thời điểm dự báo hợp lệ.
4. Chụp màn hình thấy rõ tên tín hiệu, thang thời gian và giao dịch. Lưu ảnh vào thư mục kết quả của lần chạy này.
5. Nếu muốn gom các bit thành bus cho dễ đọc, đóng STP rồi chạy:

   Windows:

   ```powershell
   py -3 scripts/format_signaltap.py "$RunDir/weather_speed_live.stp"
   ```

   Linux:

   ```bash
   python3 scripts/format_signaltap.py "$RunDir/weather_speed_live.stp"
   ```

6. Mở lại STP và chụp thêm ảnh các bus thời tiết đã gom. Công cụ định dạng cần dữ liệu thu hoàn tất; nó chỉ đổi cách trình bày, không đổi các bit đã ghi.

Các giá trị có dấu và thành phần hướng gió dùng 8 bit phần lẻ: giải mã số nguyên có dấu rồi chia 256. Góc hướng gió là số không dấu Q8 theo đơn vị độ. Dữ liệu ở chu kỳ `forecast_valid = 0` không phải dự báo mới.

Có thể đọc dự báo cuối trong Tools > In-System Sources and Probes Editor, instance FCST, sau khi replay xong. Không ghi Sources trong lúc replay đang chạy. Bản triển khai này không hiển thị dự báo lên LED, LED 7 đoạn hay LCD của DE2.

## 8 Lưu hồ sơ chạy thử

Giữ các tệp sau trong thư mục kết quả mới:

- `commit.txt`, `quartus_version.txt`.
- `ordinary_replay.log`, `ordinary_replay.csv`.
- `capture_replay.log`, `capture_replay.csv`.
- `weather_speed_live.stp` có dữ liệu đã thu.
- Ảnh Programmer và dạng sóng của chính lần chạy này.
- Hai SOF đã dùng hoặc bản ghi mã băm của chúng.

Có thể lưu đầu ra bộ kiểm tra bằng cách thêm `| Tee-Object -FilePath "$RunDir/validation.txt"` vào cuối lệnh PowerShell, hoặc `| tee "$RunDir/validation.txt"` với Bash. Khi dùng pipeline, vẫn phải kiểm tra lỗi của lệnh Python, không chỉ lệnh ghi tệp.

Sao lưu cả thư mục sang nơi khác. Sau khi thu và lưu xong có thể tắt board; lần chạy trực tiếp tiếp theo cần nạp lại SOF vì mất nguồn sẽ xóa cấu hình FPGA.

`build/` bị Git bỏ qua. Sao chép thư mục để giữ bằng chứng; `git push` thông thường không tự đưa các kết quả sinh ra lên GitHub.

## 9 Biên dịch lại từ mã nguồn

Nhánh này tạo lại cấu hình FPGA. Không cần huấn luyện lại, tải dữ liệu hay cài gói Python. Các hệ số thời tiết được chọn đã có trong RTL.

### 9.1 Biên dịch dự án thông thường

1. Trong Quartus, chọn File > Open Project rồi mở tệp sau **trong bản clone của bạn**:

   ```text
   versions/weather_v2/quartus/de2_jtag_speed/weather_jtag.qpf
   ```

2. Xác nhận chip EP2C35F672C6, top-level entity `de2_weather_jtag`, revision `weather_jtag`, tham số `SHARED = 0`.
3. Xác nhận `CLOCK_50 = PIN_N2`, `KEY0_N = PIN_G26`, ràng buộc clock ứng dụng 20 ns.
4. Chọn Processing > Start Compilation. Chờ hoàn tất; đọc lỗi và cảnh báo nghiêm trọng.
5. Dùng `output_files/weather_jtag.sof` vừa tạo thay cho SOF thông thường đã giải nén.

Hoặc biên dịch bằng terminal, bắt đầu tại thư mục gốc:

```text
cd versions/weather_v2/quartus/de2_jtag_speed
quartus_sh --flow compile weather_jtag
cd ../../../..
```

Sau các lệnh trên, terminal trở lại thư mục gốc. Cập nhật biến trỏ đến tệp mới.

Windows:

```powershell
$OrdinarySof = Join-Path $ProjectRoot 'versions/weather_v2/quartus/de2_jtag_speed/output_files/weather_jtag.sof'
```

Linux:

```bash
OrdinarySof="$ProjectRoot/versions/weather_v2/quartus/de2_jtag_speed/output_files/weather_jtag.sof"
```

### 9.2 Biên dịch dự án có SignalTap

1. Mở `hardware/quartus/signaltap/weather_speed/capture.qpf` trong bản clone.
2. Xác nhận revision `capture` và tệp `capture.stp` được bật.
3. Biên dịch. Xem báo cáo map để xác nhận các nút SignalTap được kết nối. Kiểm tra cảnh báo nút không kết nối, gồm Critical Warning 35025.
4. Dùng `output_files/capture.sof` mới **cùng `capture.stp` của chính dự án này**. Không ghép SOF mới với cấu hình thu lưu trữ không tương ứng.

Hoặc chạy từ thư mục gốc:

```text
cd hardware/quartus/signaltap/weather_speed
quartus_sh --flow compile capture
cd ../../../..
```

Cập nhật hai biến rồi làm lại mục 6.

Windows:

```powershell
$CaptureSof = Join-Path $ProjectRoot 'hardware/quartus/signaltap/weather_speed/output_files/capture.sof'
$CaptureSetup = Join-Path $ProjectRoot 'hardware/quartus/signaltap/weather_speed/capture.stp'
```

Linux:

```bash
CaptureSof="$ProjectRoot/hardware/quartus/signaltap/weather_speed/output_files/capture.sof"
CaptureSetup="$ProjectRoot/hardware/quartus/signaltap/weather_speed/capture.stp"
```

Các tham chiếu mã nguồn và ràng buộc clock của hai dự án đã được đối chiếu với tệp do Git quản lý. Đường dẫn tương đối với tệp dự án cho phép chuyển cả thư mục clone sang máy khác.

### 9.3 Đọc kết quả triển khai

Dùng Compilation Report của dự án thông thường để so sánh tài nguyên. Bản JTAG thông thường đã lưu báo cáo:

| Đại lượng | Kết quả đã lưu |
| --- | --- |
| Logic elements | 6.253 |
| Registers | 4.571 |
| Memory bits | 0 |
| Embedded multiplier 9-bit elements | 12 |
| Fmax của CLOCK_50 theo slow model | 79,74 MHz |
| Clock dùng khi chạy trên board | 50 MHz |

Fmax là ước lượng của công cụ phân tích timing; replay trên board không đo tần số cực đại thực tế. Bản SignalTap có thêm mạch thu nên dùng tài nguyên khác. Kết quả biên dịch mới có thể thay đổi theo mã nguồn, thiết lập, phiên bản công cụ và lựa chọn của fitter; hãy lưu báo cáo thực tế của lần biên dịch.

## 10 Xử lý sự cố

| Hiện tượng | Cách xử lý |
| --- | --- |
| Không nhận lệnh `git` | Cài Git, mở terminal mới rồi kiểm tra phiên bản. |
| Không nhận `quartus_sh` | Làm lại bước tìm công cụ, dùng đúng thư mục trên máy hiện tại. |
| Vừa clone nhưng không có SOF | Làm mục 3; SOF nằm trong tệp nén do Git quản lý. |
| Windows báo lỗi với `export` | Dùng khối PowerShell, không dùng cú pháp Bash. |
| Thấy USB-Blaster nhưng không thấy EP2C35 | Kiểm tra nguồn, công tắc RUN và dây lập trình. |
| `jtagconfig` không thấy phần cứng | Kiểm tra driver, quyền truy cập, cáp và bản Quartus đang dùng. |
| Không tìm thấy FCST | Nạp cấu hình weather JTAG, không dùng SOF lõi riêng hoặc UART. |
| Identity mismatch | Xác nhận đang dùng weather speed và đối số `weather_speed`. |
| Hết thời gian chờ acknowledgement | Nhả KEY0, kiểm tra chân clock/reset và đóng công cụ ghi Sources cạnh tranh. |
| SignalTap báo cấu hình không khớp | Dùng SOF và STP từ cùng một bản biên dịch có SignalTap. |
| Bộ thu chờ mãi | Bật chờ thu trước replay; kiểm tra trigger forecast-valid, clock thu, thiết bị và SOF. |
| Bộ kiểm tra báo lỗi | Giữ log; thử lại với bộ vectors, mô hình và SOF tương ứng không đổi. Không sửa giá trị mong đợi để che lỗi. |
| Terminal mới thiếu biến | Làm mục 6.3 với thư mục kết quả đã có, không tạo mốc thời gian mới. |

Khi có nhiều cáp hoặc thiết bị JTAG, replay yêu cầu chỉ định rõ theo cú pháp:

```text
quartus_stp -t scripts/replay_jtag.tcl weather_speed "HARDWARE_NAME" "DEVICE_NAME"
```

Thay hai chỗ viết hoa bằng đúng tên cáp và EP2C35 mà Quartus báo. SignalTap cũng phải chọn cùng thiết bị; số cáp của lệnh nạp phải tương ứng.

## Phụ lục A Phạm vi chứng minh của bản demo

FPGA dự báo từ quan trắc theo giờ đã ghi sẵn. Máy tính không lấy dữ liệu thời tiết trực tiếp từ DE2. 24 khung đầu tạo lịch sử; mỗi khung sau tạo dự báo cho thời điểm sau quan trắc mới nhất 3 giờ.

Một lượt đầy đủ kiểm tra 128 đầu vào và 104 dự báo. Các thành phần được đối chiếu từng bit với mô hình số cố định; góc cho phép sai lệch tối đa 5 đơn vị Q8 độ, tức 0,01953125°, theo khoảng cách vòng tròn. Script replay hiện có kiểm tra cờ hướng của vector không.

Thiết kế tốc độ của toàn hệ thống có độ trễ sau cạnh clock là 40 chu kỳ và khoảng cách khởi động giữa hai đầu vào (initiation interval) là 23 chu kỳ sau khởi tạo lịch sử. Sáu nhánh số học chạy song song; mỗi nhánh dùng lại một bộ nhân cho bảy giá trị trễ. Truyền JTAG chậm hơn lịch xử lý nội bộ này.

Các chỉ số dự báo bằng phần mềm và bản thu cũ nằm trong `docs/reports/`. Khi trình bày phải nói rõ đó là kết quả trước đây. CSV và STP mới chứng minh lần tái hiện trên board đang kết nối.

## Phụ lục B Bộ kiểm tra kết quả đã lưu

Lưu mã sau thành `verify_weather_run.py` trong thư mục kết quả. Chương trình chỉ dùng thư viện chuẩn Python và đọc dữ liệu, không sửa mã nguồn hay bản thu. Chạy bằng Python bình thường; không dùng tùy chọn `-O` vì nó bỏ qua các lệnh `assert`.

```python
import argparse
import csv
import xml.etree.ElementTree as ET
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('csv_file', type=Path)
parser.add_argument('--stp', type=Path)
parser.add_argument('--vectors', type=Path,
                    default=Path('hardware/jtag/vectors/weather.txt'))
args = parser.parse_args()

vector_lines = [line.split() for line in args.vectors.read_text().splitlines()
                if line.strip()]
assert len(vector_lines) == 128, 'Expected 128 reference vectors'

def check_angle(actual, expected):
    assert 0 <= actual < 92160, ('Angle outside [0, 360) degrees', actual)
    assert 0 <= expected < 92160, ('Invalid reference angle', expected)
    delta = abs(actual - expected)
    delta = min(delta, 92160 - delta)
    assert delta <= 5, ('Direction difference', delta)

with args.csv_file.open(newline='') as stream:
    records = list(csv.DictReader(stream))
assert len(records) == 128, f'Expected 128 rows, got {len(records)}'
for index, row in enumerate(records):
    assert int(row['sample_index']) == index
    assert int(row['accepted_count']) == index + 1
    assert int(row['forecast_count']) == max(0, index - 23)
    expected = 'warmup' if index < 24 else 'True'
    assert row['match'] == expected, (index, row['match'])
    if index >= 24:
        raw = [int(value) for value in row['forecast_raw'].split()]
        assert len(raw) == 7, ('Invalid forecast field count', index)
        reference = int(vector_lines[index][4], 16)
        for lane in range(6):
            value = (reference >> (18 * lane)) & ((1 << 18) - 1)
            if value & (1 << 17):
                value -= 1 << 18
            assert raw[lane] == value, ('CSV component mismatch', index, lane)
        check_angle(raw[6], reference >> 108)
print('PASS CSV: 128 inputs, 24 warm-up rows, 104 matching forecasts')
print('First forecast:', records[24]['forecast_physical'])
print('Last forecast: ', records[-1]['forecast_physical'])

if args.stp is not None:
    root = ET.parse(args.stp).getroot()
    signal_set = root.find('instance/signal_set')
    assert signal_set is not None, 'Missing SignalTap signal set'
    data = signal_set.find('trigger/log/data')
    assert data is not None, 'No acquired data saved in this STP'
    count = int(data.get('sample_depth', '-1'))
    trigger = int(data.get('trigger_position', '-1'))
    names = [wire.get('name') for wire in
             signal_set.find('signal_vec/data_input_vec')]
    bits = ''.join((data.text or '').split())
    assert count == 512 and trigger == 256, (count, trigger)
    assert len(bits) == count * len(names), 'Incorrect data length'
    assert set(bits) <= {'0', '1'}, 'Nonbinary acquisition data'
    samples = [bits[i * len(names):(i + 1) * len(names)]
               for i in range(count)]
    positions = {name: index for index, name in enumerate(names)}
    prefix = 'jtag_mailbox:mailbox|'

    def bit(index, name):
        return int(samples[index][positions[prefix + name]])

    def bus(index, name, width):
        return sum(bit(index, f'{name}[{b}]') << b
                   for b in range(width))

    accepts = [i for i in range(count)
               if bit(i, 'sample_valid') and bit(i, 'sample_ready')]
    valids = [i for i in range(count) if bit(i, 'forecast_valid')]
    assert len(accepts) == 1 and len(valids) == 1, (accepts, valids)
    assert all(bit(i, 'core_rst_n') for i in range(count))
    accept, valid = accepts[0], valids[0]
    assert valid - accept == 41, (accept, valid)
    fields = vector_lines[24]
    expected_input = (int(fields[1], 16) >> 2) & ((1 << 108) - 1)
    expected_output = int(fields[4], 16)
    actual_input = bus(accept, 'sample_data', 108)
    actual_output = bus(valid, 'forecast_data', 126)
    mask = (1 << 108) - 1
    assert actual_input == expected_input, 'Captured input mismatch'
    assert (actual_output & mask) == (expected_output & mask), \
        'Captured component mismatch'
    check_angle(actual_output >> 108, expected_output >> 108)
    print('PASS CAPTURE: 512 samples; input and output match reference')
    print('Accepted index:', accept, 'Forecast-valid index:', valid)
    print('Raw sample separation:', valid - accept)
    print('Forecast word:', hex(actual_output))
```

Nếu thay mô hình, bộ vectors, lịch RTL, trigger hoặc tín hiệu quan sát thì đó là thí nghiệm khác. Bộ kiểm tra này dành riêng cho cấu hình tái hiện được cung cấp.

## Phụ lục C Tài liệu tham khảo và cập nhật

- [Quartus II Web Edition 13.0 SP1 cho Windows](https://www.altera.com/downloads/fpga-development-tools/quartus-ii-web-edition-design-software-version-13-0sp1-windows).
- [Quartus II Web Edition 13.0 SP1 cho Linux](https://www.altera.com/downloads/fpga-development-tools/quartus-ii-web-edition-design-software-version-13-0sp1-linux).
- [Hướng dẫn driver cáp lập trình của hãng](https://www.altera.com/developers/software/cables-and-adapter-drivers-installation-guide).
- [Sách hướng dẫn DE2 nguyên bản](https://www-ug.eecg.toronto.edu/msl/manuals/DE2_User_Manual.pdf).
- [Giao thức JTAG và dự án board](../../hardware/jtag/README.md).
- [Script replay](../../scripts/replay_jtag.tcl).
- [Kết quả kiểm tra bản thu phần cứng đã lưu](../reports/defense_session/SIGNALTAP_CAPTURE_CHECK.json).

Cách tổ chức theo [hướng dẫn viết quy trình của Microsoft](https://learn.microsoft.com/en-us/style-guide/procedures-instructions/writing-step-by-step-instructions) và [Google](https://developers.google.com/style/procedures): nêu vị trí bắt đầu, thao tác cần làm và kết quả cần kiểm tra.

Lưu tài liệu cùng mã nguồn trong Git. Khi thay giao diện replay hoặc bitstream đóng gói, cập nhật đồng thời đường dẫn, mã băm và kết quả mong đợi. Không đưa đường dẫn cá nhân của người phát triển vào lệnh bắt buộc.

Bản tiếng Việt giữ nguyên các khối lệnh của bản tiếng Anh, ngoại trừ bộ kiểm tra Python được bổ sung kiểm tra miền góc và đối chiếu CSV với vectors. Việc rà soát tài liệu không thay thế chạy thử trực tiếp trên FPGA. Chưa thực hiện lượt chạy Windows hoặc lượt chạy phần cứng mới trong lần chỉnh tài liệu này.

### Kết quả rà soát bản tiếng Việt — 02/11/2026

- Đối chiếu đủ 46 khối mã với bản tiếng Anh; các lệnh thao tác được giữ nguyên, chỉ bộ kiểm tra Python được bổ sung.
- Kiểm tra cú pháp các khối Bash và Python; xác nhận các liên kết tệp nội bộ tồn tại và không có đường dẫn bắt buộc mang tên người dùng của tác giả.
- Đối chiếu SHA-256 của cả hai SOF trong gói lưu trữ: khớp bảng ở mục 3.3.
- Chạy bộ kiểm tra với CSV và STP phần cứng đã lưu: đạt 128 đầu vào, 104 dự báo và bản thu 512 mẫu; chỉ số nhận 215, chỉ số dự báo hợp lệ 256.
- Thử dữ liệu cố tình sai: phát hiện cờ match sai, thành phần CSV sai, góc CSV vượt 360° và góc bản thu vượt miền. Sai lệch góc 5 đơn vị Q8 được chấp nhận; 6 đơn vị bị từ chối.

Các kiểm tra trên dùng dữ liệu đã lưu. Lệnh PowerShell chưa được chạy trên Windows và chưa thực hiện một lượt FPGA mới. Script `scripts/replay_jtag.tcl` không được sửa trong lần chỉnh tài liệu này; hãy chạy thêm bộ kiểm tra Python như mục 5.4 và 6.4.
