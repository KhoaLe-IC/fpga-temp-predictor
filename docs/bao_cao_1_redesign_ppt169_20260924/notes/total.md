# 01_cover

Em xin chào thầy và các bạn. Nhóm em đề xuất đồ án dự báo nhiệt độ sau ba giờ trên FPGA, sử dụng mô hình tuyến tính từ các giá trị quá khứ. Đây là một hướng cụ thể trong chủ đề Weather Pattern Forecasting on FPGA using Time Series Analysis mà thầy giao. Nhóm gồm ba thành viên và dự kiến thực hiện trong mười hai tuần, với hai phần chính là chương trình C++ và mạch viết bằng Verilog hoặc SystemVerilog.

Ở buổi đầu, nhóm trình bày bài toán sẽ giải quyết, nguyên lý tính dự báo, cách chuyển phép tính thành mạch và kế hoạch kiểm chứng. Những công thức, kiến trúc và mốc công việc sau đây đang ở mức đề xuất. Nhóm chưa có hệ số huấn luyện, số liệu độ chính xác hay kết quả chạy board để công bố. Sau phần trình bày, nhóm mong nhận góp ý về phạm vi, board và mức demo cần đạt.

---

# 02_scope

Chủ đề dự báo thời tiết khá rộng vì có nhiều đại lượng như nhiệt độ, độ ẩm, áp suất và lượng mưa. Với thời gian ba tháng, trong đó nhóm còn phải học kiến thức DSP, nhóm chọn trước một đại lượng là nhiệt độ tại một địa điểm. Đầu vào là chuỗi nhiệt độ được ghi theo giờ, tính đến thời điểm hiện tại t. Đầu ra là một giá trị ước lượng nhiệt độ tại thời điểm ba giờ sau đó, có đơn vị độ C.

Nhóm chọn mô hình tuyến tính vì từng phép tính có thể giải thích, viết lại trong C++ và đối chiếu với RTL. Đây là lựa chọn về phạm vi thực hiện; nhóm chưa khẳng định mô hình tuyến tính là mô hình dự báo tốt nhất. Phần lõi chỉ dùng nhiệt độ và các hệ số cố định. Nếu hoàn thành sớm, nhóm mới cân nhắc bổ sung độ ẩm hoặc áp suất để kiểm tra có giảm sai số hay không.

Dữ liệu đầu vào chỉ thay đổi theo giờ nên nhóm cũng chưa có cơ sở nói rằng bài toán này cần FPGA để tăng tốc. Giá trị của đồ án là thực hành chuỗi xử lý từ mô hình số đến hiện thực số cố định và kiểm chứng trên phần cứng.

---

# 03_system

Toàn bộ hệ thống có thể chia thành giai đoạn chuẩn bị trên máy tính và giai đoạn tính dự báo trên FPGA. Trong giai đoạn offline, chương trình C++ đọc dữ liệu CSV, kiểm tra và làm sạch chuỗi thời gian. Từ dữ liệu này, chương trình tạo các cách dự báo đơn giản làm mốc so sánh, sau đó tìm ba hệ số a, b và c của mô hình đề xuất.

C++ còn có một nhiệm vụ quan trọng là tạo mô hình tham chiếu số cố định và bộ dữ liệu kiểm tra. Mô hình tham chiếu sẽ mô phỏng cùng quy tắc số học mà RTL sử dụng. Khi chạy trên FPGA, các hệ số đã được xác định và giữ cố định. Mạch nhận từng mẫu nhiệt độ, lưu lịch sử cần thiết, tính dự báo và xuất kết quả. Việc học hệ số không nằm trong phạm vi lõi FPGA của phương án này.

Đầu ra cuối kỳ vì vậy gồm chương trình C++, mạch RTL, testbench, demo trên board và báo cáo đánh giá. Báo cáo sẽ trình bày riêng sai số dự báo, sai lệch số cố định và tài nguyên phần cứng, để mỗi kết quả đều có phép đối chiếu phù hợp.

---

# 04_samples

Nguồn dữ liệu nhóm dự kiến sử dụng là NASA POWER, với biến nhiệt độ T2M theo giờ. Đây là dữ liệu trên lưới gắn với tọa độ được chọn, không phải nhiệt độ đo bởi một cảm biến đúng tại điểm đó. Nhóm chưa chốt tọa độ và khoảng thời gian lấy dữ liệu. Trước khi tạo mẫu, cần thống nhất mốc thời gian, kiểm tra giờ thiếu hoặc bị lặp và kiểm tra đơn vị nhiệt độ. Tài liệu API theo giờ đã được liên kết ngay trên slide.

Sơ đồ này biểu diễn thứ tự các mốc, không biểu diễn khoảng cách theo tỷ lệ. Ở thời điểm t, nhóm dùng nhiệt độ hiện tại, ba giờ trước, hai mươi mốt giờ trước và hai mươi bốn giờ trước. Mốc dễ nhầm nhất là t trừ hai mươi mốt. Vì mục tiêu nằm ở t cộng ba, thời điểm cùng giờ của ngày hôm trước sẽ là t cộng ba trừ hai mươi bốn, tức t trừ hai mươi mốt.

Để truy cập được đến t trừ hai mươi bốn, bộ đệm cần giữ hai mươi lăm mẫu liên tiếp, tính cả mẫu hiện tại. Nhiệt độ thực tại t cộng ba chỉ dùng làm nhãn huấn luyện hoặc đánh giá; nó không được đưa vào đầu vào dự báo tại thời điểm t.

---

# 05_model

Mô hình đề xuất bắt đầu từ nhiệt độ cùng giờ ngày hôm trước, tức T tại t trừ hai mươi mốt. Nhóm dùng giá trị này làm mốc nền, rồi cộng hai phần hiệu chỉnh và một độ lệch hằng c. Dấu mũ trên T biểu thị đây là giá trị dự báo, chưa phải nhiệt độ thực.

Phần hiệu chỉnh thứ nhất lấy nhiệt độ hiện tại trừ nhiệt độ cùng giờ hôm trước, rồi nhân với hệ số a. Nếu hôm nay nóng hoặc lạnh hơn hôm trước tại giờ hiện tại, đại lượng này thể hiện sự chênh lệch đó. Phần thứ hai lấy nhiệt độ hiện tại trừ nhiệt độ ba giờ trước, rồi nhân với b. Đại lượng này mô tả biến thiên gần đây. Hệ số c cho phép mô hình có thêm một mức dịch cố định, có cùng đơn vị nhiệt độ; a và b không có đơn vị.

Ba hệ số được ước lượng trên dữ liệu lịch sử bằng C++. Các giải thích trực quan giúp hình thành giả thuyết mô hình, nhưng không bảo đảm các đặc trưng này sẽ dự báo tốt. Nhóm phải kiểm tra trên dữ liệu mới và so với baseline trước khi kết luận. Trong phạm vi hiện tại, FPGA chỉ thực hiện công thức với những hệ số đã học.

---

# 06_example

Để minh họa một lần tính, giả sử nhiệt độ hai mươi bốn giờ trước là mười chín độ, hai mươi mốt giờ trước là hai mươi mốt độ, ba giờ trước là mười tám độ và hiện tại là hai mươi độ. Giả sử a bằng không phẩy năm, b bằng không phẩy hai và c bằng không. Tất cả các giá trị này được chọn để giải thích phép tính, chưa phải dữ liệu hay hệ số đo được.

Hiệu liên ngày là hai mươi trừ mười chín, bằng một độ. Nhân với a, phần hiệu chỉnh thứ nhất bằng không phẩy năm độ. Hiệu ba giờ gần nhất là hai mươi trừ mười tám, bằng hai độ; nhân với b cho không phẩy bốn độ. Cộng hai phần này vào mốc nền hai mươi mốt độ, ta được dự báo hai mươi mốt phẩy chín độ C.

Ví dụ này cho thấy lõi phần cứng cần thực hiện các phép trừ, nhân hệ số rồi cộng. Giá trị dự báo không được xem là đúng chỉ vì phép tính đúng. Muốn biết dự báo tốt đến đâu, sau đó vẫn phải so với nhiệt độ thực tại thời điểm mục tiêu.

---

# 07_training

Để tìm hệ số, nhóm chuyển công thức dự báo về bài toán hồi quy đơn giản hơn. Đặc trưng x một là chênh lệch nhiệt độ hiện tại với cùng giờ hôm trước; x hai là chênh lệch với ba giờ trước. Nhãn y là nhiệt độ thực ba giờ sau trừ đi nhiệt độ cùng giờ ngày trước của thời điểm mục tiêu. Khi đó cần tìm a, b và c để biểu thức a nhân x một cộng b nhân x hai cộng c gần y nhất trên tập huấn luyện, theo tiêu chuẩn bình phương tối thiểu.

Dữ liệu được chia thành ba giai đoạn theo thời gian. Train dùng tìm hệ số. Validation dùng xem đặc trưng và cấu hình nào phù hợp. Test là giai đoạn mới hơn được giữ lại để đánh giá cuối. Nhóm chưa chốt tỷ lệ chia vì còn phụ thuộc độ dài và chất lượng dữ liệu.

Một điểm cần chú ý là chia theo thời gian của nhãn: nhãn của mẫu train không được sang giai đoạn validation hoặc test. Tuy nhiên, lịch sử đã quan sát ở giai đoạn trước vẫn có thể dùng làm đầu vào dự báo ở giai đoạn sau. Các vùng trên slide chỉ thể hiện thứ tự, không thể hiện tỷ lệ. Nhóm có thể dùng Eigen trong C++ để giải bài toán bình phương tối thiểu; tài liệu triển khai được liên kết phía dưới.

---

# 08_evaluation

Nhóm sẽ đánh giá hai câu hỏi riêng. Câu thứ nhất là mô hình có tạo ra dự báo hữu ích hơn những cách đơn giản hay không. Baseline thứ nhất dự báo bằng nhiệt độ hiện tại T tại t. Baseline thứ hai dự báo bằng nhiệt độ cùng giờ ngày hôm trước của thời điểm mục tiêu, tức T tại t trừ hai mươi mốt. Hai baseline và mô hình nhóm phải được đánh giá trên đúng cùng tập test và cùng các thời điểm hợp lệ.

Thước đo chính dự kiến là MAE, tức lấy trị tuyệt đối của sai số mỗi lần dự báo rồi tính trung bình. Vì nhiệt độ dùng độ C, MAE cũng có đơn vị độ C. Hiện chưa có số liệu để khẳng định mô hình sẽ thắng baseline. Nếu kết quả không tốt hơn, nhóm vẫn cần báo cáo đúng và phân tích giới hạn.

Câu thứ hai là phần cứng có thực hiện đúng phép tính đã đặc tả hay không. Nhóm đo sai lệch giữa C++ số thực và số cố định để thấy tác động của lượng tử hóa. Sau đó yêu cầu RTL khớp bit với reference số cố định khi xét đúng valid và latency. Các số LUT, FF, DSP và độ trễ lấy từ kết quả tổng hợp. Ngưỡng sai lệch lượng tử hóa sẽ được chốt sau thử nghiệm, không đặt một con số tùy ý ở buổi đề xuất.

---

# 09_fixed_point

Mô hình ban đầu được tính bằng số thực trong C++ để thuận tiện nghiên cứu. Khi chuyển sang FPGA, nhóm dự kiến dùng số cố định. Trước hết phải xem nhiệt độ nằm trong khoảng nào, các hệ số lớn đến đâu và tổng trung gian có thể tăng lên bao nhiêu. Từ đó mới chọn số bit có dấu và số bit phần lẻ. Vì chưa có dữ liệu và hệ số thực nghiệm, nhóm chưa chốt một Q format cụ thể.

Việc thống nhất định dạng đầu vào và đầu ra vẫn chưa đủ. Nhóm còn phải quy định độ rộng của tích và tổng, vị trí dịch bit, cách làm tròn và cách xử lý tràn. Saturation nghĩa là chặn tại biên biểu diễn; wrap là giữ các bit theo độ rộng quy định. Chọn cách nào phải được ghi thành đặc tả và dùng giống nhau trong C++ fixed và RTL.

Mô hình tham chiếu cần làm đúng từng bước như mạch, kể cả những chỗ giảm độ rộng. Các trường hợp nhiệt độ âm, biên biểu diễn và tràn số được kiểm tra có chủ đích. Nhóm sẽ luôn tách sai số dự báo so với thực tế khỏi sai lệch do số cố định so với số thực, vì hai loại sai số có nguyên nhân khác nhau.

---

# 10_architecture

Sơ đồ này là kiến trúc chức năng dự kiến của lõi tính toán. Mỗi khi một mẫu mới hợp lệ đến, bộ đệm cập nhật lịch sử và cho phép đọc các mốc hiện tại, ba giờ trước, hai mươi mốt giờ trước và hai mươi bốn giờ trước. Bộ đệm giữ hai mươi lăm mẫu liên tiếp; trước khi đủ dữ liệu, mạch chưa được báo một dự báo hợp lệ.

Nhánh thứ nhất tạo hiệu liên ngày rồi nhân a. Nhánh thứ hai tạo hiệu ba giờ rồi nhân b. Khối cộng nhận hai kết quả, cộng với nhiệt độ tại t trừ hai mươi mốt và độ lệch c. Đầu ra là dự báo cho t cộng ba. Hai nhánh trên slide mô tả phép toán, chưa có nghĩa bắt buộc phải dùng hai bộ nhân chạy song song. Nhóm sẽ quyết định dùng chung hay song song sau khi biết board và các giới hạn tài nguyên.

Clock điều khiển hoạt động mạch, còn valid cho biết khi nào một mẫu thật sự được nhận. Cần phân biệt hai khái niệm thời gian: trễ một mẫu ở đây tương ứng một giờ trong chuỗi dữ liệu; độ trễ tính toán của mạch được tính bằng chu kỳ clock. Mạch không phải chờ ba giờ thực để tạo giá trị dự báo.

---

# 11_verification

Nhóm dự kiến kiểm chứng theo ba tầng, dùng cùng bộ dữ liệu để thuận tiện truy vết. Tầng thứ nhất nằm trong C++, so mô hình số thực với mô hình số cố định. Mục đích là đánh giá phần sai lệch thêm do lượng tử hóa và kiểm tra các miền giá trị khó, chẳng hạn nhiệt độ âm, gần biên biểu diễn hoặc thay đổi nhanh.

Tầng thứ hai dùng testbench, viết tắt là TB trên slide, để kiểm tra RTL. Với mỗi đầu vào hợp lệ, testbench xác định đầu ra cần so và thời điểm đầu ra xuất hiện. Mục tiêu là khớp bit với reference fixed, không chỉ gần nhau về giá trị. Ngoài phép tính, phải kiểm cả reset, tràn số, trạng thái chưa đủ mẫu và các khoảng gián đoạn valid. Khi có khoảng nghỉ mà không nhận mẫu, bộ đệm không được tự hiểu đó là một mẫu mới.

Tầng thứ ba chạy cùng dữ liệu trên board và đối chiếu với reference. Tầng này kiểm thêm giao tiếp, thứ tự các mẫu, cách đóng gói dữ liệu và log đầu ra. Một lõi đúng trong mô phỏng vẫn có thể tích hợp sai nếu truyền dữ liệu sai dấu hoặc sai thứ tự byte. Vì vậy ba tầng bổ sung cho nhau và mỗi tầng có một câu hỏi kiểm chứng cụ thể.

---

# 12_demo

Kịch bản demo dự kiến là phát lại dữ liệu lịch sử từ máy tính. Nhóm không cần chờ mỗi giờ mới có một mẫu, nhưng vẫn giữ nguyên thứ tự của chuỗi. PC đọc CSV, gửi các mẫu lần lượt vào FPGA. UART là một phương án dự kiến nếu board và công cụ hỗ trợ thuận tiện; giao tiếp cuối cùng sẽ chốt khi biết phần cứng.

Sau khi nhận đủ lịch sử, FPGA tính dự báo và gửi kết quả về. PC ghi log, ghép dự báo với thời điểm mục tiêu rồi đối chiếu với nhiệt độ thực trong CSV. Có thể hiển thị kết quả để người xem nhận ra các đoạn dự báo tốt hoặc sai lệch lớn. Đây mới là kịch bản thiết kế; nhóm chưa có giao diện hay kết quả chạy board để trình diễn ở buổi này.

Điều quan trọng là PC có thể biết toàn bộ dữ liệu lịch sử để đánh giá, nhưng ở mỗi bước chỉ được truyền những mẫu đến thời điểm t vào FPGA. Nhãn tại t cộng ba không được đưa vào đầu vào của phép dự báo. Như vậy việc phát nhanh chỉ rút ngắn thời gian demo, vẫn giữ được điều kiện sử dụng dữ liệu quá khứ của bài toán.

---

# 13_schedule

Nhóm chia mười hai tuần thành bốn giai đoạn với sản phẩm cụ thể. Ba tuần đầu tập trung học những kiến thức cần dùng, lấy và kiểm dữ liệu, tạo CSV sạch cùng hai baseline. Đây là bước quan trọng vì nếu chuỗi thời gian sai thì mô hình và RTL có thể cùng cho ra một kết quả không có ý nghĩa.

Trong tuần bốn đến sáu, nhóm xây chương trình C++, tìm hệ số, thử đặc trưng trên validation và bắt đầu đánh giá số cố định. Tuần bảy đến chín dành cho lõi RTL, testbench và đối chiếu bit. Song song với mô phỏng, nhóm chuẩn bị giao tiếp và điều kiện tích hợp để không dồn toàn bộ việc board vào cuối kỳ.

Ba tuần cuối dùng để hoàn thiện demo, đánh giá cuối trên tập test, lấy báo cáo tài nguyên và tổng hợp các giới hạn. Mỗi giai đoạn phải có thứ có thể chạy hoặc kiểm tra, chẳng hạn file dữ liệu hợp lệ, hệ số kèm phép đánh giá, hoặc testbench khớp reference. Đây là lịch dự kiến theo tuần thực hiện; ngày báo cáo buổi hai sẽ được điều chỉnh theo thông báo chính thức của thầy.

---

# 14_team_risks

Nhóm phân công theo ba mảng nhưng thống nhất giao diện chung từ đầu. Người thứ nhất phụ trách dữ liệu và C++, tạo CSV, baseline, hệ số, MAE và reference. Rủi ro chính ở mảng này là giờ bị thiếu, lặp hoặc không cùng chuẩn thời gian; cần phát hiện và xử lý trước khi tạo mẫu, không chỉ xóa một dòng rồi coi các dòng còn lại là liên tiếp.

Người thứ hai phụ trách số cố định và RTL, gồm bộ đệm, lõi số học, tổng hợp và phối hợp tích hợp board. Khi board chưa rõ, vẫn có thể làm lõi tính toán độc lập và kiểm chứng bằng mô phỏng trước. Người thứ ba phụ trách testbench và demo, từ test vector, so bit đến truyền nhận và log kết quả. Rủi ro mô hình có sai số cao là trách nhiệm của cả nhóm: cùng xem lại trên validation và báo cáo trung thực kết quả cuối trên test.

Ba người cần cùng hiểu định dạng dữ liệu và hệ số, dấu của số, quy tắc làm tròn và tràn, valid và latency. Các thỏa thuận này giúp mã C++, RTL và testbench khớp nhau. Trước khi thuyết trình, nhóm thay nhãn Người một, Người hai, Người ba bằng tên thành viên thực tế.

---

# 15_conclusion

Tóm lại, sản phẩm nhóm hướng đến là một hệ thống dự báo nhiệt độ sau ba giờ từ các giá trị quá khứ. C++ tìm hệ số của mô hình tuyến tính; FPGA thực hiện phép tính số cố định và đưa ra dự báo khi nhận đủ lịch sử. Nhóm cần có hai loại bằng chứng: đánh giá chất lượng dự báo với baseline trên dữ liệu chưa dùng huấn luyện, và chứng minh RTL khớp mô hình tham chiếu số cố định.

Ở buổi đề xuất này, nhóm xin thầy góp ý ba điểm để chốt phạm vi triển khai. Thứ nhất là bài toán dự báo một đại lượng nhiệt độ với đích ba giờ có phù hợp chủ đề được giao hay không. Thứ hai là board FPGA và công cụ nhóm sẽ sử dụng. Thứ ba là mức demo phần cứng tối thiểu cần có ở cuối kỳ. Phần bổ sung độ ẩm hoặc áp suất chỉ được thực hiện khi phần lõi đã hoàn thành và được kiểm chứng. Nhóm xin cảm ơn thầy và các bạn đã theo dõi.
