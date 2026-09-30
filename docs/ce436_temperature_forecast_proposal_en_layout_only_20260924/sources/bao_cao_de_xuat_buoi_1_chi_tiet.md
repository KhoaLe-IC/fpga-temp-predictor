# bao_cao_de_xuat_buoi_1_chi_tiet

- Source: `bao_cao_de_xuat_buoi_1_chi_tiet.pptx`
- Total slides: 15

## Slide 1

- DỰ BÁO NHIỆT ĐỘ
- SAU 3 GIỜ TRÊN FPGA

Mô hình tuyến tính từ dữ liệu nhiệt độ quá khứ

CE436 | Báo cáo đề xuất đề tài | Buổi 1

### Speaker Notes

Mở đầu khoảng 25 giây. Nhóm đề xuất một nhánh cụ thể của chủ đề Weather Pattern Forecasting on FPGA using Time Series Analysis. Bài toán là dự báo nhiệt độ sau 3 giờ tại một địa điểm. Đây là buổi đề xuất kế hoạch; chưa báo cáo kết quả thực nghiệm. Trước khi trình bày, thêm tên ba thành viên vào trang này hoặc nói khi giới thiệu.

## Slide 2

Phạm vi đề tài

Chủ đề thầy giao

Bài toán nhóm chọn

- Weather Pattern Forecasting
- on FPGA using Time Series Analysis

- Dự báo nhiệt độ sau 3 giờ
- từ các mẫu nhiệt độ theo giờ

Đầu vào

Đầu ra

Chuỗi T(t) tại một địa điểm

Một giá trị T̂(t+3), đơn vị °C

Cần thầy xác nhận: phạm vi dự báo một đại lượng có đáp ứng yêu cầu của chủ đề.

02

### Speaker Notes

Nói khoảng 45 giây. Đề tài gốc rộng, nên nhóm chọn một mục tiêu có thể đo sai số và trình diễn trên FPGA. Đầu vào ở thời điểm t chỉ gồm các mẫu đã ghi nhận đến t; đầu ra là nhiệt độ tại t+3 giờ. Nhóm cần xác nhận với thầy rằng phạm vi dự báo nhiệt độ ngắn hạn phù hợp với tên chủ đề. Không gọi đây là dự báo toàn bộ tình trạng thời tiết.

## Slide 3

Mục tiêu và sản phẩm cần bàn giao

Câu hỏi nhóm cần trả lời

- 1. Mô hình có giảm sai số so với cách dự báo đơn giản?
- 2. FPGA có cho kết quả đúng như mô hình số cố định?
- 3. Mạch cần bao nhiêu tài nguyên và mất bao lâu để tính?

Sản phẩm cuối kỳ

Chương trình C++ • Mạch RTL • Testbench • Demo trên board • Báo cáo đánh giá

03

### Speaker Notes

Nói khoảng 45 giây. Nhóm sẽ xem kết quả theo hai khía cạnh: chất lượng dự báo và chất lượng hiện thực phần cứng. Chất lượng dự báo phải được so với baseline; kết quả RTL phải trùng mô hình tham chiếu số cố định khi xét đúng độ trễ clock. Tài nguyên và tốc độ sẽ lấy từ báo cáo tổng hợp, không dự đoán trước. Các file mã nguồn hiện trong repo mới là khung thư mục, chưa có kết quả để công bố.

## Slide 4

Nguồn dữ liệu và cách tạo mẫu

Nguồn dự kiến

NASA POWER, nhiệt độ T2M theo giờ tại một tọa độ được chọn.

Tại thời điểm t

T(t−24) T(t−21) T(t−3) T(t)

24 giờ trước 21 giờ trước 3 giờ trước hiện tại

Kiểm tra mốc giờ và dữ liệu thiếu; chia tập theo thời gian để giữ giai đoạn cuối cho kiểm tra.

04

### Speaker Notes

Nói khoảng 50 giây. NASA POWER có API dữ liệu theo giờ, trong đó T2M là nhiệt độ gần mặt đất; đây là nguồn dự kiến. Nguồn: https://power.larc.nasa.gov/docs/services/api/temporal/hourly/. Dữ liệu theo tọa độ là dữ liệu trên lưới, không phải nhiệt độ đo tại đúng một điểm đặt cảm biến. Chốt một tọa độ và cùng một chuẩn thời gian, kiểm tra giờ bị thiếu hoặc lặp. Mỗi mẫu dự báo dùng dữ liệu đã có tới t; nhãn cần dự đoán là T(t+3). Chia theo thứ tự thời gian để tập kiểm tra không xuất hiện trong quá trình tìm hệ số.

## Slide 5

Hai mốc dự báo để so sánh

Giữ nguyên hiện tại

Cùng giờ ngày trước

T̂(t+3) = T(t)

T̂(t+3) = T(t−21)

Nếu nhiệt độ thay đổi ít trong 3 giờ, cách này có thể rất mạnh.

T(t−21) là giá trị 24 giờ trước thời điểm cần dự báo.

Dùng cùng tập kiểm tra và cùng thước đo MAE (°C) cho cả ba phương án.

05

### Speaker Notes

Nói khoảng 45 giây. Đặt hai baseline trước khi huấn luyện mô hình. Cách thứ nhất cho dự báo bằng giá trị hiện tại. Cách thứ hai dùng nhiệt độ cùng giờ của ngày trước: vì cần dự báo t+3, thời điểm ngày trước là t+3−24=t−21. Cả baseline và mô hình nhóm đề xuất sẽ được tính MAE trên đúng cùng tập kiểm tra. Nguồn khái niệm baseline: https://otexts.com/fpp3/simple-methods.html. Mô hình mới không được hứa chắc chắn thắng baseline khi chưa chạy thử.

## Slide 6

Mô hình tuyến tính đề xuất

T̂(t+3) = T(t−21) + a[T(t)−T(t−24)] + b[T(t)−T(t−3)] + c

T(t−21)

T(t)−T(t−24)

T(t)−T(t−3)

- Mốc cùng giờ
- ngày hôm trước

- Nhiệt độ hiện tại lệch
- so với hôm trước bao nhiêu

- Xu hướng trong
- 3 giờ vừa qua

a, b, c được tìm trên C++; FPGA sử dụng các hệ số cố định để tính liên tục theo từng mẫu.

06

### Speaker Notes

Nói khoảng 60 giây. Đây là mô hình tuyến tính theo các mẫu quá khứ, có xét chu kỳ 24 giờ. T(t−21) là nhiệt độ của ngày trước đúng tại giờ t+3 cần dự báo. Chênh lệch t và t−24 phản ánh cả ngày hôm nay nóng hơn hay lạnh hơn cùng giờ hôm qua. Chênh lệch t và t−3 phản ánh xu hướng gần đây. C++ tìm a,b,c từ dữ liệu lịch sử; phần cứng dùng hệ số cố định. Công thức là giả thuyết thiết kế, có thể đổi đặc trưng nếu đánh giá ban đầu cho thấy nó không hợp lý.

## Slide 7

Ví dụ một lượt dự báo

Giá trị minh hoạ, chưa phải dữ liệu hoặc hệ số đã đo

T(t−24) = 19 °C

T(t−21) = 21 °C

T(t−3) = 18 °C

T(t) = 20 °C

Nếu a = 0,5; b = 0,2; c = 0

T̂(t+3) = 21 + 0,5(20−19) + 0,2(20−18) = 21,9 °C

07

### Speaker Notes

Nói khoảng 65 giây. Đây chỉ là ví dụ để người nghe thấy FPGA thực hiện phép tính gì; bốn nhiệt độ và các hệ số đều giả định. Tại t, ta đã biết nhiệt độ t−24, t−21, t−3 và t. Hiệu liên ngày là 20−19=1 độ C; hiệu ba giờ gần nhất là 20−18=2 độ C. Cộng các hiệu đã nhân hệ số vào nhiệt độ cùng giờ ngày trước, ta được 21,9 độ C. Khi làm thật, a,b,c sẽ do C++ tìm trên dữ liệu huấn luyện, còn giá trị thực tại t+3 chỉ được dùng để kiểm tra sau đó.

## Slide 8

Phần việc trên C++

01

Đọc và làm sạch

Kiểm tra thứ tự giờ, giá trị thiếu và đơn vị

02

Tạo mẫu huấn luyện

Tạo các hiệu số đầu vào và nhãn T(t+3)

03

Tìm hệ số

Ước lượng a, b, c bằng bình phương tối thiểu

04

Đánh giá

Tính MAE trên giai đoạn chưa dùng để tìm hệ số

08

### Speaker Notes

Nói khoảng 50 giây. C++ không chạy thuật toán huấn luyện trên FPGA. C++ tạo những hàng dữ liệu mà tất cả đầu vào ở hoặc trước t, đầu ra đúng là T(t+3). Tìm a,b,c bằng bình phương tối thiểu trên dữ liệu cũ. Giữ một đoạn thời gian mới hơn để kiểm tra; không trộn ngẫu nhiên các thời điểm. Sau đó xuất hệ số và bộ test vector. Có thể dùng thư viện Eigen cho bài toán bình phương tối thiểu, nguồn: https://eigen.tuxfamily.org/dox/group__LeastSquares.html. Chưa có hệ số cụ thể.

## Slide 9

Chuyển từ số thực sang số cố định

C++ số thực

C++ số cố định và RTL

Hệ số và nhiệt độ được tính với độ chính xác cao để làm mốc.

Dùng cùng tỉ lệ, làm tròn, độ rộng bit và cách xử lý tràn số.

Cần kiểm tra trước khi chốt định dạng

Miền nhiệt độ trong dữ liệu • miền giá trị hệ số • độ lớn tổng trung gian

09

### Speaker Notes

Nói khoảng 55 giây. Mạch số không thể dùng số thực một cách tuỳ tiện vì sẽ tăng chi phí phần cứng. Nhóm sẽ xem khoảng giá trị của dữ liệu và các hệ số để chọn số bit và tỉ lệ phù hợp. Phần mềm tham chiếu số cố định phải có cùng quy tắc làm tròn và tràn số với RTL. Chưa chốt Q format vì chưa phân tích dữ liệu. Trong báo cáo cuối, so sai số do mô hình với sai số thêm do lượng tử hoá. Đây là lựa chọn hiện thực, không thay đổi định nghĩa bài toán dự báo.

## Slide 10

Kiến trúc mạch FPGA dự kiến

Mẫu T(t)

Bộ đệm 25 mẫu

Khối tính hiệu

Nhân và cộng

→

→

→

Nhận mẫu mới

Giữ T(t−24)…T(t)

Tạo 2 độ lệch

Xuất T̂(t+3)

Hệ số a, b, c lưu trong mạch. Mỗi mẫu giờ mới tạo một dự báo sau khi bộ đệm đủ dữ liệu.

10

### Speaker Notes

Nói khoảng 60 giây. Đây là kiến trúc đề xuất, chưa tổng hợp. PC hoặc một nguồn phát dữ liệu sẽ đưa lần lượt các mẫu nhiệt độ vào FPGA. Bộ đệm cần 25 mẫu để truy cập từ t−24 đến t. Chọn bốn mốc t, t−3, t−21, t−24; khối số học tạo hai hiệu số, hai tích rồi cộng cùng mốc ngày trước và hệ số c. Hệ số được nạp cố định sau khi huấn luyện. Tín hiệu clock/handshake và cách kết nối board sẽ được thiết kế khi biết phần cứng cụ thể.

## Slide 11

Kế hoạch kiểm chứng

Tầng 1

C++ số thực và số cố định

Đo tác động của lượng tử hoá

Tầng 2

Testbench và RTL

So từng mẫu với C++ số cố định

Tầng 3

Chạy trên board

Kiểm tra giao tiếp và kết quả thực

Trường hợp biên: nhiệt độ âm, thay đổi đột ngột, reset, dữ liệu chưa đủ 25 mẫu.

11

### Speaker Notes

Nói khoảng 55 giây. Ba tầng kiểm chứng được tách rõ. Tầng 1 xem chênh lệch giữa tính toán số thực và số cố định. Tầng 2 dùng testbench đưa test vector vào RTL, so với C++ số cố định và tính đến latency. Tầng 3 đưa cùng dữ liệu qua đường giao tiếp của board để kiểm tra tích hợp. Cần test cả nhiệt độ âm, tràn số, reset, dữ liệu chưa đủ bộ đệm và đoạn dữ liệu biến đổi nhanh. Kết quả mong muốn là RTL khớp bit với reference cố định; sai số dự báo với thời tiết thật là chỉ tiêu riêng.

## Slide 12

Kịch bản demo cuối kỳ

Máy tính

FPGA

Đối chiếu

→

→

- Phát lại chuỗi nhiệt độ
- theo giờ từ dữ liệu cũ

- Nhận từng mẫu và tạo
- dự báo T̂(t+3)

- Hiển thị dự báo và
- T(t+3) thực trong CSV

Dữ liệu được phát lại nhanh để demo. FPGA vẫn chỉ thấy các mẫu tới thời điểm t khi tính dự báo.

12

### Speaker Notes

Nói khoảng 55 giây. Dữ liệu thời tiết thay đổi theo giờ, nên buổi demo không thể chờ ba giờ thực. Nhóm sẽ phát lại dữ liệu lịch sử nhanh hơn thời gian thật. FPGA nhận chuỗi từng mẫu, tính dự báo sau 3 giờ tại mỗi bước khi đã đủ 25 mẫu. Máy tính biết dữ liệu thực trong file nên có thể vẽ đồ thị dự báo và thực tế sau đó; dữ liệu thực tương lai tuyệt đối không được đưa vào FPGA tại bước dự báo. Giao tiếp dùng UART nếu board hỗ trợ thuận tiện, hoặc phương án nạp dữ liệu khác phù hợp với board.

## Slide 13

Kế hoạch 12 tuần và mốc bàn giao

Tuần 1–3

Tuần 4–6

Tuần 7–9

Tuần 10–12

Dữ liệu

Mô hình C++

RTL và testbench

Board và báo cáo

CSV sạch; baseline

Hệ số; MAE trên dữ liệu mới

Đối chiếu số cố định

Demo; tài nguyên; giới hạn

Giữa kỳ: chứng minh mô hình và RTL mô phỏng. Cuối kỳ: FPGA chạy demo và có số liệu đánh giá.

13

### Speaker Notes

Nói khoảng 50 giây. Đây là lịch dự kiến tính từ khi nhóm bắt đầu; ngày của buổi báo cáo 2 cần đối chiếu với lịch thầy công bố. Ba tuần đầu lấy và kiểm dữ liệu, xây baseline. Ba tuần kế tìm hệ số và kiểm tra trên giai đoạn mới. Tuần 7 đến 9 chuyển số cố định, viết RTL và testbench. Ba tuần cuối tích hợp board, đo kết quả và viết báo cáo. Đầu ra mỗi giai đoạn là một thứ có thể chạy hoặc kiểm tra, không chỉ là phần đọc tài liệu.

## Slide 14

Rủi ro chính và cách xử lý

Dữ liệu

Thiếu giờ hoặc khác múi giờ

Kiểm tra chuỗi thời gian trước khi tạo mẫu

Mô hình

Sai số không hơn mốc đơn giản

Thử lại đặc trưng; báo cáo đúng kết quả

Board

Chưa biết giao tiếp, thời điểm nhận board

Hoàn thiện lõi RTL và testbench trước

14

### Speaker Notes

Nói khoảng 65 giây. Rủi ro thứ nhất là dữ liệu có giờ thiếu hoặc không cùng múi giờ; nếu bỏ qua sẽ lấy nhầm t−24 hoặc nhãn t+3. Nhóm sẽ xác thực chuỗi thời gian ngay trước khi học mô hình. Rủi ro thứ hai là mô hình tuyến tính chưa chắc đánh bại dự báo giữ nguyên nhiệt độ; nhóm sẽ so baseline, thử điều chỉnh đặc trưng dựa trên tập validation và công bố trung thực kết quả tập test. Rủi ro thứ ba là board và cổng giao tiếp chưa rõ; lõi tính dự báo và testbench có thể làm độc lập trước khi tích hợp. Độ ẩm/áp suất là mở rộng có điều kiện, không làm ảnh hưởng mốc lõi.

## Slide 15

Phân công nhóm và điểm cần xác nhận

Người 1

Người 2

Người 3

Dữ liệu và C++

Mạch FPGA

Kiểm chứng và demo

Chuỗi thời gian, hệ số, MAE

Số cố định, bộ đệm, phép tính

Testbench, giao tiếp, biểu đồ

Cần chốt với thầy sau buổi 1

Phạm vi dự báo nhiệt độ sau 3 giờ • board FPGA và công cụ • yêu cầu demo tối thiểu

15

### Speaker Notes

Nói khoảng 45 giây. Chia việc theo mảng để cả ba có đầu ra rõ; mỗi người vẫn phải hiểu bài toán chung. Thành viên 1 xử lý dữ liệu và C++; thành viên 2 thiết kế lõi FPGA; thành viên 3 xây testbench và kịch bản demo, cùng người 2 tích hợp board. Thay nhãn Người 1/2/3 bằng tên. Cần hỏi thầy: phạm vi chỉ dự báo nhiệt độ có được chấp nhận không, board nào được cấp, và mức demo phần cứng tối thiểu. Nếu có thời gian sau khi hoàn thành lõi, nhóm mới thử thêm độ ẩm hoặc áp suất để so sai số.
