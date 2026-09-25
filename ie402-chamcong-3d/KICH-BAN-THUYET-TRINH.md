# Kịch bản thuyết trình — Đồ án IE402

**Đề tài:** Xây dựng hệ thống chấm công định vị dựa trên mô hình khối không gian 3 chiều phân tầng
**Nhóm 1** · GVHD: ThS. Phan Thanh Vũ
**Slide nguồn:** `SLIDE-BAO-CAO-IE402-Cham-cong-dinh-vi-3D.pptx` — 43 trang

---

## 0. Phân công và thời lượng

| Lượt | Người | Slide | Nội dung | Thời lượng |
|---|---|---|---|---|
| 1 | **Khôi** | 1 – 9 | Mở đầu · Tổng quan và đặt vấn đề | 6:00 |
| 2 | **Tín** | 10 – 17 | Cơ sở lý thuyết · Mô hình MAP · Thuật toán | 6:00 |
| 3 | **Nhân** | 18 – 29 | Phân tích, thiết kế và cài đặt | 7:30 |
| 4 | **Vy** | 30 – 37 | Kết quả thực nghiệm | 3:00 |
| 5 | **Vy** | — | **DEMO TRỰC TIẾP** | 4:00 |
| 6 | **Tín** | 38 – 40 | Kết luận, hướng phát triển, phân công | 1:30 |
| 7 | **Khôi** | 41 | Phụ lục — bản đồ địa giới TP.HCM 3D | 0:45 |
| 8 | **Nhân** | 42 | Những câu hỏi nhóm đã chuẩn bị | 0:45 |
| 9 | **Vy** | 43 | Cảm ơn và mời đặt câu hỏi | 0:30 |
|  |  |  | **Tổng** | **≈ 30 phút** |

**Nguyên tắc chia:** mỗi người nói đúng phần mình làm trong slide 40 — Tín (mô hình dữ liệu) nói chương lý thuyết, Nhân (máy chủ) nói chương cài đặt, Khôi (bản đồ 3D) nói phần mở đầu và phụ lục bản đồ, Vy (giao diện + kiểm thử) nói kết quả và chạy demo.

### ⚠️ Ba việc phải sửa trong slide trước khi bảo vệ

1. **Slide 1** còn ghi `Thành viên A · Thành viên B · Thành viên C · Thành viên D` — phải thay bằng tên thật: Nguyễn Hữu Tín · Nguyễn Minh Khôi · Nguyễn Tường Vy · Võ Thành Nhân.
2. **Slide 40** còn dùng nhãn A/B/C/D — thay thành: A = Tín, B = Nhân, C = Khôi, D = Vy.
3. **Slide 27** ghi "Mười ba điểm cuối API" — hệ thống hiện có **16 điểm cuối** (đã bổ sung 3 endpoint xuất CSV). Sửa con số, hoặc nếu không kịp thì Nhân nói rõ bằng miệng: *"sau khi in slide nhóm bổ sung thêm ba điểm cuối xuất tệp, tổng là mười sáu"*.

---

# LƯỢT 1 — KHÔI · Slide 1 – 9 · 6 phút

## Slide 1 — Trang bìa

> Em chào thầy và các bạn. Nhóm 1 xin trình bày đồ án cuối kỳ môn Hệ thống thông tin địa lý 3 chiều.
>
> Đề tài của nhóm là **xây dựng hệ thống chấm công định vị dựa trên mô hình khối không gian ba chiều phân tầng**. Nhóm đặt tên mô hình là **MAP — Multi-floor Attendance Prism**, tức khối chấm công phân tầng.
>
> Câu hỏi mà đồ án đặt ra rất ngắn: *khi hàng rào địa lý hai chiều không còn đủ, thì thay bằng cái gì?*
>
> Nhóm gồm bốn thành viên: Tín, Khôi, Vy và Nhân. Em là Khôi, xin trình bày phần mở đầu.

## Slide 2 — Nội dung trình bày

> Bài trình bày gồm năm phần.
>
> Phần một, em đặt vấn đề: vì sao hàng rào địa lý hai chiều thất bại trong toà nhà cao tầng.
> Phần hai, bạn Tín trình bày cơ sở lý thuyết và mô hình MAP.
> Phần ba, bạn Nhân trình bày phân tích, thiết kế và cài đặt.
> Phần bốn, bạn Vy trình bày kết quả thực nghiệm **và chạy demo trực tiếp hệ thống**.
> Phần năm là kết luận và phân công.
>
> Nếu thầy chỉ nhớ một điều từ buổi hôm nay, nhóm mong đó là dòng chữ ở góc phải màn hình: **"đúng toà nhà, sai tầng"**. Đó là trạng thái mà mô hình hai chiều không thể sinh ra, và là trọng tâm của cả đồ án.

## Slide 3 — Chương 01

> Phần một: Tổng quan và đặt vấn đề.

*(chuyển slide ngay, không dừng lâu ở slide phân chương)*

## Slide 4 — Bối cảnh

> Chấm công định vị là hình thức xác nhận sự có mặt bằng toạ độ của điện thoại, thay cho máy chấm công cố định. Hầu hết ứng dụng ở Việt Nam đều dựng trên đúng một kỹ thuật: **hàng rào địa lý hai chiều** — một hình tròn bán kính R hoặc một đa giác phẳng.
>
> Kỹ thuật đó trả lời được đúng một câu hỏi: *"người này có nằm trong vùng trên mặt phẳng hay không?"*
>
> Thầy nhìn ba con số bên phải. Toà nhà nhóm dùng thử nghiệm có **42 tầng**. Trong đó nhóm đặt **3 văn phòng ở ba dải tầng khác nhau**. Nhưng cả ba văn phòng chỉ có **một cặp toạ độ kinh độ – vĩ độ** duy nhất, vì chúng nằm chồng lên nhau trên cùng một mặt bằng.
>
> Điểm đáng nói là công nghệ đã sẵn sàng từ lâu: PostGIS hỗ trợ hình học có toạ độ Z, ArcGIS Maps SDK dựng được khối ba chiều ngay trên trình duyệt. Khoảng cách giữa năng lực công nghệ đã có và cách các ứng dụng chấm công đang làm — đó chính là khoảng trống mà đồ án nhắm vào.

## Slide 5 — Bốn hạn chế của hàng rào 2D

> Nhóm chỉ ra bốn hạn chế cụ thể.
>
> **Một — không phân biệt theo chiều cao.** Nhân viên tầng 5 và nhân viên tầng 22 có cùng toạ độ. Người ngồi quán cà phê dưới tầng trệt vẫn chấm công hợp lệ cho văn phòng tầng 22.
>
> **Hai — sai số GPS trong đô thị.** Hiệu ứng *urban canyon*: tín hiệu bị nhà cao tầng che chắn và phản xạ nhiều đường, sai số ngang lên tới hàng chục mét, đủ để lọt sang toà nhà kế bên.
>
> **Ba — không phát hiện được gian lận theo chiều đứng.** Giả lập GPS hay nhờ người chấm hộ dưới sảnh đều cho toạ độ ngang đúng. Mà dữ liệu hai chiều không lưu độ cao, nên sau đó không còn gì để rà soát.
>
> **Bốn — không trực quan hoá để đối chiếu.** Một chấm trên bản đồ phẳng không nói được nó nằm trong hay ngoài khối văn phòng, nên giá trị đối chứng rất thấp.
>
> Điều nhóm muốn nhấn: bốn hạn chế này **không độc lập**. Chúng đều bắt nguồn từ đúng một nguyên nhân — phép kiểm tra chạy trên hình chiếu xuống mặt phẳng. Sửa nguyên nhân đó thì cả bốn cùng được giải.

## Slide 6 — Minh hoạ: cùng toạ độ, ba tầng

> Hình này nói thay lời. Ba nhân viên, ba tầng khác nhau, nhưng hình chiếu xuống mặt đất của cả ba **trùng khít một điểm**.
>
> Hàng rào hai chiều kết luận cả ba đều hợp lệ. Mô hình khối thì tách được ra, và sinh thêm một trạng thái thứ ba: **NGHI NGỜ**.

## Slide 7 — Ý tưởng cốt lõi

> Ý tưởng của đồ án gói trong một mũi tên: chuyển từ **"điểm thuộc đa giác"** sang **"điểm thuộc khối"**. Từ hai chiều với hai trạng thái, sang ba chiều với ba trạng thái.
>
> Nhóm nhìn ý tưởng này ở ba khía cạnh.
>
> **Học thuật:** mô hình 2.5D khối đùn, tương đương mức LoD1 của chuẩn CityGML, đã đủ giải một lớp bài toán nghiệp vụ có giá trị. Không cần BIM, không cần quét laser.
>
> **Ứng dụng:** chi phí số hoá rất thấp — chỉ cần mặt bằng công trình lấy từ OpenStreetMap, số tầng, và chiều cao tầng trung bình.
>
> **Thiết kế hệ thống:** hệ thống trung thực về giới hạn của chính nó. Khi không đủ căn cứ, nó nói "nghi ngờ" và chuyển quyết định cho con người, chứ không đoán bừa.

## Slide 8 — Sáu mục tiêu

> Nhóm đặt sáu mục tiêu, mỗi mục tiêu kèm một tiêu chí hoàn thành đo được, không phải phát biểu chung chung.
>
> M1 là mô hình dữ liệu 3D. M2 là thuật toán kiểm tra trả về ba trạng thái, phản hồi dưới 200 mili-giây. M3 là ứng dụng web cho ba vai trò. M4 là trực quan hoá 3D. M5 là phát hiện bốn dạng bất thường. M6 là cấu hình khối từ dữ liệu toà nhà.
>
> Ở chương 5, nhóm đối chiếu lại từng tiêu chí: **năm trên sáu mục tiêu đạt đầy đủ, riêng M6 chỉ đạt một phần** — nhóm sẽ nói rõ vì sao ở cuối bài.

## Slide 9 — Phạm vi

> Phạm vi thực hiện: một toà nhà có thật là IFC One Saigon, 42 tầng, cao 195,3 mét. Ba văn phòng giả định ở ba dải tầng 5–8, 20–24 và 35–40. Mức chi tiết LoD1. Nguồn độ cao hỗn hợp: ưu tiên thiết bị đo, dự phòng bằng tầng khai báo. Ứng dụng web chạy môi trường cục bộ.
>
> Nằm ngoài phạm vi: định vị trong nhà bằng Wi-Fi hay BLE, ứng dụng di động gốc, sinh trắc học, chống giả lập vị trí ở mức hệ điều hành, và triển khai lên đám mây có HTTPS.
>
> Nhóm nêu rõ giới hạn ngay từ đầu, vì đó cũng là một phần của kết quả: nó cho biết chính xác cần bổ sung gì để đi tiếp.
>
> **Em xin mời bạn Tín trình bày phần cơ sở lý thuyết.**

---

# LƯỢT 2 — TÍN · Slide 10 – 17 · 6 phút

## Slide 10 — Chương 02

> Phần hai: Cơ sở lý thuyết và mô hình MAP.

## Slide 11 — Chọn mô hình biểu diễn 3D

> Trước khi dựng mô hình, nhóm khảo sát năm cách biểu diễn đối tượng ba chiều.
>
> **Khối đùn 2.5D** rất nhẹ, dựng thẳng từ mặt bằng, nhưng không mô tả được phần nhô ra hay mái vòm.
> **B-Rep** chính xác nhất nhưng dữ liệu nặng, truy vấn chậm.
> **CSG** gọn với hình dạng quy chuẩn nhưng không hợp với dữ liệu đo đạc thực tế.
> **Voxel** tốt cho truy vấn thể tích nhưng tốn bộ nhớ và mất độ chính xác ở biên.
> **TIN** chỉ mô tả bề mặt, không phải khối đặc — không dùng được cho bài toán bao hàm.
>
> Nhóm chọn **khối đùn**, với bốn lý do.
>
> Thứ nhất, bài toán chỉ cần trả lời đúng một câu hỏi: điểm có trong khối văn phòng không. Không cần mô tả hình học phức tạp hơn thế.
> Thứ hai, phép kiểm tra tách được thành hai bước rất rẻ: ray casting độ phức tạp O(n) cho mặt phẳng, cộng một phép so sánh số thực cho chiều cao.
> Thứ ba, dữ liệu đầu vào có sẵn: mặt bằng OSM, số tầng, chiều cao tầng.
> Thứ tư, cả PostGIS lẫn ArcGIS SDK đều hỗ trợ trực tiếp.
>
> Đây đúng bằng mức LoD1 của CityGML — chi tiết vừa đủ, không thừa.

## Slide 12 — Bài toán khó nhất: độ cao

> Phần khó nhất của đồ án không phải hình học, mà là **lấy được độ cao đáng tin**.
>
> Ba ràng buộc thực tế.
>
> Một, độ chính xác theo chiều đứng của GNSS kém hơn chiều ngang **hai đến ba lần**, vì thiết bị đo độ cao ellipsoid rồi mới quy sang độ cao chính bằng mô hình geoid nội bộ.
>
> Hai, trong nhà thì gần như không dùng được: thuộc tính `altitude` thường trả về null, hoặc `altitudeAccuracy` lên tới hàng chục mét — lớn hơn cả chiều cao vài tầng cộng lại.
>
> Ba, dữ liệu mở thiếu chiều cao: **chỉ 3,7 % công trình trong OpenStreetMap có thuộc tính height**.
>
> Giải pháp của nhóm là **chấp nhận nguồn độ cao hỗn hợp**. Ưu tiên độ cao thiết bị đo được, nhưng chỉ khi `altitudeAccuracy` nhỏ hơn 15 mét. Vượt ngưỡng đó thì suy từ tầng người dùng khai báo, theo công thức:
>
> **z = z_nền + (tầng − 0,5) × h_tầng**
>
> Hệ số 0,5 đặt điểm ở giữa chiều cao tầng, để sai số phân bố đều về hai phía thay vì dồn một bên.
>
> Và điều quan trọng nhất: **nguồn độ cao được ghi thẳng vào bản ghi**. Nên mỗi bản ghi luôn tự nói được nó đáng tin tới mức nào.

## Slide 13 — Ba hướng giải bài toán xác định tầng

> Nhóm so sánh với hai hướng khác trong tài liệu.
>
> **Cảm biến khí áp:** độ phân giải khoảng 1 mét, đủ phân biệt từng tầng. Nhưng giá trị tuyệt đối trôi theo thời tiết, phải hiệu chuẩn liên tục.
>
> **Hạ tầng phát sóng trong nhà** — Wi-Fi RSSI fingerprinting hoặc BLE beacon: chính xác tốt, là giải pháp công nghiệp phổ biến. Nhưng phải lắp đặt và khảo sát bản đồ tín hiệu cho từng toà nhà, chi phí triển khai cao.
>
> **Hướng của đồ án là hướng thứ ba: mô hình không gian.** Nhóm không cải thiện phép đo, mà cải thiện **cái mô hình mà phép đo được đối chiếu vào**. Ưu điểm: không cần thêm phần cứng. Nhược điểm: phụ thuộc chất lượng nguồn độ cao đầu vào.
>
> Ba hướng này **bổ sung cho nhau chứ không loại trừ nhau**. Mô hình MAP được thiết kế để nhận độ cao từ bất kỳ nguồn nào, miễn nguồn đó được ghi lại cùng bản ghi.

## Slide 14 — Mô hình MAP

> Đây là đóng góp chính của đồ án.
>
> **MAP = ( P, z_min, z_max, δxy, δz )** — một bộ năm thành phần.
>
> **P** là đa giác nền, hình chiếu phần sàn văn phòng thuê, hệ WGS84.
> **z_min** là cao độ tuyệt đối mặt sàn tầng thấp nhất.
> **z_max** là cao độ tuyệt đối trần tầng cao nhất.
> **δxy** là biên dung sai ngang, bù sai số GPS đô thị, mặc định 25 mét.
> **δz** là biên dung sai đứng, bù sai số đo độ cao, mặc định 5 mét.
>
> Khi kiểm tra, nhóm không dùng khối gốc mà dùng **khối đã nới biên MAP⁺**: đa giác nền được buffer thêm δxy, dải cao độ nới ra δz về hai phía.
>
> Xin nhấn mạnh: **hai thành phần dung sai chính là điểm khác biệt giữa MAP và một khối đùn thông thường.** Chúng biến khối hình học cứng thành khối có biên mềm — phản ánh đúng bản chất của phép đo GPS: kết quả đo không phải một điểm, mà là một vùng xác suất.

## Slide 15 — Suy dải cao độ từ dải tầng

> Người quản trị **không nhập z_min và z_max** — nhập tay hai con số cao độ thì rất dễ sai. Họ nhập **dải tầng ghi trong hợp đồng thuê**, hệ thống tự suy ra cao độ bằng một trigger chạy trước khi ghi.
>
> Công thức: `z_min = z_nền + (tầng_đầu − 1) × h_tầng` và `z_max = z_nền + tầng_cuối × h_tầng`.
>
> Áp vào toà nhà thử nghiệm: cao độ nền 5 mét, chiều cao tầng 4,65 mét.
>
> Alpha Tech thuê tầng 5 đến 8, ra dải **23,60 – 42,20 mét**.
> Beta Finance thuê tầng 20 đến 24, ra **93,35 – 116,60 mét**.
> Gamma Media thuê tầng 35 đến 40, ra **163,10 – 191,00 mét**.
>
> Thầy chú ý dòng dưới cùng: **ba khối này có đa giác nền trùng khít nhau, chỉ khác ở dải cao độ.** Đây là minh chứng trực tiếp cho luận điểm của đồ án — với hệ hai chiều, ba văn phòng này là **một** vùng duy nhất.

## Slide 16 — Phép kiểm tra bao hàm

> Thuật toán trung tâm nằm gọn trong một dòng: điểm Q nằm trong khối khi và chỉ khi **hình chiếu ngang của nó nằm trong đa giác đã buffer**, VÀ **cao độ của nó nằm trong dải đã nới biên**.
>
> Hai điều kiện đó cho ba trạng thái.
>
> **HỢP LỆ** — thoả cả ngang lẫn đứng, và độ chính xác thiết bị trong ngưỡng. Ghi nhận công bình thường.
>
> **NGHI NGỜ** — thoả ngang nhưng vi phạm đứng; hoặc độ chính xác quá kém để kết luận. Đây chính là *"đúng toà nhà, sai tầng"*, cần xác minh.
>
> **NGOÀI VÙNG** — vi phạm điều kiện ngang. Từ chối, và gợi ý gửi đơn giải trình.
>
> Trạng thái ở giữa — NGHI NGỜ — là giá trị mà mô hình hai chiều **không thể sinh ra**. Không phải vì nó không muốn, mà vì nó được định nghĩa bằng một điều kiện đứng mà hệ 2D không có dữ liệu để kiểm tra.

## Slide 17 — Bốn quy tắc R1 – R4

> Ngoài trạng thái, hệ thống còn áp bốn quy tắc phát hiện bất thường.
>
> **R1 — Sai tầng**, mức CAO. Thoả ngang nhưng cao độ lệch khỏi dải khối quá δz. Hệ thống quy đổi độ lệch ra **số tầng**, để quản lý đọc là hiểu ngay chứ không phải nhẩm mét.
>
> **R2 — Dịch chuyển bất khả thi**, mức CAO. Lấy hai bản ghi liên tiếp của cùng nhân viên, suy ra vận tốc; vượt 150 km/h thì cảnh báo.
>
> **R3 — Độ chính xác bất thường**, mức trung bình. Hai đầu: accuracy nhỏ hơn 1 mét là nhỏ bất thường với đô thị, nghi giả lập GPS; lớn hơn 100 mét là không đủ tin cậy.
>
> **R4 — Trùng thiết bị**, mức trung bình. Nhiều nhân viên khác nhau chấm công từ cùng một định danh thiết bị trong vòng 10 phút.
>
> Nhóm xin nói rõ ngay ở đây, thay vì để thầy hỏi: **bốn quy tắc này không loại trừ gian lận, chúng chỉ làm tăng chi phí gian lận.** Nhóm nêu đúng giới hạn đó chứ không tuyên bố hệ thống chống được gian lận.
>
> **Xin mời bạn Nhân trình bày phần thiết kế và cài đặt.**

---

# LƯỢT 3 — NHÂN · Slide 18 – 29 · 7 phút 30

## Slide 18 — Chương 03

> Phần ba: Phân tích, thiết kế và cài đặt.

## Slide 19 — Yêu cầu hệ thống

> Nhóm đặc tả **13 yêu cầu chức năng** chia theo ba vai trò.
>
> Nhân viên có tám chức năng, từ F01 đăng nhập đến F08 gửi đơn giải trình — trong đó F03 là lấy vị trí 3D từ thiết bị hoặc chọn vị trí mô phỏng, F06 là xem bản đồ 3D.
>
> Quản lý có bốn: bảng điều khiển, danh sách cảnh báo, duyệt đơn, và báo cáo công theo tháng.
>
> Quản trị viên có một: quản lý dữ liệu toà nhà, văn phòng và khối MAP.
>
> Bảy yêu cầu phi chức năng, em xin nêu ba cái quan trọng nhất. **N02** — bản ghi và cảnh báo phải ghi trong cùng một giao dịch, không được có bản ghi mồ côi. **N06** — logic kiểm tra đặt trong cơ sở dữ liệu, không nằm ở tầng ứng dụng. **N01** — chấm công phản hồi dưới 200 mili-giây.

## Slide 20 — Sơ đồ trường hợp sử dụng

> Sơ đồ use case có bốn nhóm tác nhân: nhân viên với UC1 đến UC5, quản lý với UC6 đến UC8, quản trị viên với UC9 đến UC11.
>
> Nhóm thứ tư là điểm em muốn nhấn: **dịch vụ nội bộ**, gồm UC12 kiểm tra bao hàm khối và UC13 áp quy tắc bất thường.
>
> Hai use case này **luôn được UC2 bao hàm bằng quan hệ include**, và **không tác nhân nào gọi trực tiếp được**. Đó là một quyết định thiết kế có chủ đích: không có lối vào nào tạo ra được một bản ghi chấm công mà chưa qua kiểm tra.

## Slide 21 — Sơ đồ luồng dữ liệu mức 0 và mức 1

> Sơ đồ ngữ cảnh mức 0: bốn tác nhân ngoài trao đổi dữ liệu với hệ thống — nhân viên, quản lý, quản trị viên, và **dịch vụ định vị của thiết bị**. Tác nhân thứ tư này hay bị bỏ sót, nhưng nó là nguồn của toàn bộ dữ liệu toạ độ.
>
> Mức 1 phân rã thành **bảy tiến trình và sáu kho dữ liệu**. Bảy tiến trình: xác thực, thu nhận vị trí 3D, kiểm tra bao hàm khối, phát hiện bất thường, xử lý giải trình, tổng hợp báo cáo, và quản trị khối MAP.

## Slide 22 — DFD mức 2 và sơ đồ trình tự

> Bên trái là phân rã tiến trình 3.0 — kiểm tra bao hàm. Bên phải là sơ đồ trình tự một lượt chấm công.
>
> Ba điểm em muốn nêu.
>
> **Thứ tự có chủ đích:** kiểm tra điều kiện ngang trước. Nếu đã ngoài vùng thì không cần xét cao độ — đây là thứ tự cho chi phí tính toán thấp nhất.
>
> **Ba nhánh kết quả** nằm trong một khối lựa chọn của sơ đồ trình tự, và ánh xạ thẳng sang mã HTTP: **200** hợp lệ, **202** ghi nhận chờ xác minh, **422** ngoài vùng.
>
> **Nguồn cao độ tách bạch:** tiến trình 3.2 quyết định dùng cao độ đo được hay suy từ tầng khai báo, rồi ghi nguồn đó vào bản ghi.

## Slide 23 — Kiến trúc ba lớp

> Hệ thống chia ba lớp.
>
> **Lớp trình bày** là ứng dụng web: HTML, CSS, JavaScript thuần, ArcGIS Maps SDK 4.29, HTML5 Geolocation API. Xin lưu ý một câu trong ô này: lớp này **không tự kết luận bất cứ điều gì về tính hợp lệ**. Nó chỉ gửi toạ độ lên và hiển thị kết quả trả về.
>
> **Lớp ứng dụng** là máy chủ REST: Node.js, Express 4, JSON Web Token, bcrypt.
>
> **Lớp dữ liệu** là PostgreSQL 17 với PostGIS 3.6: 14 bảng, 4 hàm, 1 trigger. Ngoài lưu trữ, lớp này **chứa luôn các hàm nghiệp vụ không gian**.
>
> Vì sao đặt thuật toán trong cơ sở dữ liệu? Để có **đúng một cài đặt duy nhất**. Dù gọi từ API, từ script nạp dữ liệu, hay từ psql trực tiếp, đều đi qua cùng một hàm. Không lối vào nào tạo được bản ghi chưa qua kiểm tra.

## Slide 24 — Lược đồ CSDL

> Sơ đồ thực thể liên kết có **14 thực thể**, các thuộc tính hình học ghi rõ kiểu không gian: `GEOMETRY(Polygon, 4326)` cho đa giác nền, `GEOMETRY(PointZ, 4326)` cho vị trí chấm công.
>
> Bốn con số: **14 bảng, 4 hàm nghiệp vụ, 1 trigger, 4 chỉ mục GiST**.
>
> Bốn hàm nghiệp vụ: `tinh_dai_cao_do()` suy z_min và z_max từ dải tầng; `kiem_tra_bao_ham()` trả về một trong ba trạng thái; `kiem_tra_r2()` tính vận tốc suy ra; và trigger `trg_dong_bo_cao_do()` tự điền cao độ khi ghi.
>
> *(nếu thầy hỏi vì sao 14 mà không phải 15: PostGIS tự tạo thêm bảng `spatial_ref_sys`, nhưng đó là bảng hệ thống của extension, không phải bảng của lược đồ nhóm thiết kế — nhóm đã kiểm tra bằng `pg_class` và loại nó ra)*

## Slide 25 — Hàm kiem_tra_bao_ham()

> Đây là mã thật của hàm, không phải mã giả.
>
> **Bước 1** — điều kiện ngang: `ST_DWithin` trên kiểu **geography**, với dung sai δxy. Ép về geography là chi tiết quyết định tính đúng đắn: nó cho phép dung sai tính **bằng mét trên mặt ellipsoid**, chứ không phải bằng độ. Nếu để kiểu geometry thì 25 "đơn vị" sẽ là 25 độ, sai hoàn toàn. Không thoả thì trả về ngay `NGOAI_VUNG`.
>
> **Bước 2** — điều kiện đứng: lấy `ST_Z` của điểm, so với dải đã nới biên δz. Không thoả thì trả `NGHI_NGO` — đúng toà nhà, sai tầng.
>
> **Bước 3** — chốt chặn độ chính xác: nếu sai số đo lớn hơn gấp đôi dung sai thì cũng trả `NGHI_NGO`. Lý do: khi sai số quá lớn, kết quả "nằm trong vùng" **không còn mang thông tin** — có thể đúng chỉ vì may mắn.

## Slide 26 — Xử lý một lượt chấm công

> Một lượt chấm công đi qua sáu bước, **tất cả trong một giao dịch duy nhất**: kiểm tra đầu vào, tra khối MAP, xác định cao độ, kiểm tra bao hàm, áp R1 đến R4, rồi ghi và phản hồi. Nếu bất kỳ bước nào lỗi thì huỷ toàn bộ, không để lại bản ghi dở dang.
>
> Em muốn dừng ở ô cuối: **hệ thống phải giải thích được kết luận của mình.**
>
> Phản hồi trả về không chỉ là một chữ "nghi ngờ". Nó gồm: khoảng cách ngang tới khối, cao độ đã dùng và **nguồn** của cao độ đó, dải cao độ khối, hai giá trị dung sai, độ lệch, và danh sách cảnh báo kèm mô tả định lượng.
>
> Lát nữa trong phần demo, thầy sẽ thấy đúng những con số này hiện trên màn hình.

## Slide 27 — Các điểm cuối API

> Bảng này liệt kê các điểm cuối. Em xin đính chính: slide ghi **mười ba**, nhưng sau khi in slide nhóm bổ sung thêm **ba điểm cuối xuất tệp CSV** — xuất lịch sử chấm công, xuất cảnh báo, và xuất báo cáo công. **Tổng hiện tại là mười sáu.**
>
> Cột quyền chia rõ ba mức: không cần đăng nhập, đã đăng nhập, và quản lý.
>
> Điểm cuối `POST /api/cham-cong` là nơi tập trung toàn bộ nghiệp vụ — chính là sáu bước em vừa trình bày, tất cả trong một giao dịch.

## Slide 28 — Bảo mật

> Ba lớp kiểm soát.
>
> **Xác thực:** mật khẩu băm bằng bcrypt, không lưu dạng thô. Đăng nhập thành công thì phát thẻ JWT hạn tám giờ, mang mã người dùng, mã nhân viên và vai trò.
>
> **Phân quyền theo vai trò:** một lớp trung gian riêng kiểm tra vai trò trước khi cho vào các điểm cuối quản lý. Vai trò nhân viên gọi vào sẽ nhận **403**. Nhóm đã kiểm chứng bằng thử thật, không chỉ đọc mã.
>
> **Kiểm soát quyền sở hữu dữ liệu:** đây là lớp hay bị bỏ. Truy vấn lịch sử luôn lọc theo mã nhân viên **lấy từ thẻ JWT**, không lấy từ tham số người dùng gửi lên. Nên không ai đổi một con số trên URL để xem lịch sử của người khác được.
>
> Và ba điểm nhóm ghi nhận là **chưa đạt chuẩn triển khai thật**: cơ sở dữ liệu dùng phương thức `trust` và chỉ nghe 127.0.0.1 — thật thì phải `scram-sha-256`. Khoá ký JWT để mặc định trong tệp cấu hình mẫu — thật thì phải sinh ngẫu nhiên riêng. Và hệ thống chạy trên HTTP vì là môi trường cục bộ — thật thì bắt buộc HTTPS, mà đó cũng là điều kiện để Geolocation API hoạt động.

## Slide 29 — Trực quan hoá

> Phần bản đồ ba chiều.
>
> Khối được đùn theo **cao độ tuyệt đối**: `GraphicsLayer` đặt `elevationInfo` ở chế độ `absolute-height`, chiều cao đùn bằng z_max trừ z_min. Đây là điểm bắt buộc — nếu để chế độ tương đối theo mặt đất thì khối sẽ trôi theo địa hình và sai hoàn toàn.
>
> Khối của nhân viên đang đăng nhập được tô đậm và viền dày hơn các khối khác.
>
> Điểm chấm công là khối cầu đường kính 5 mét, đổi màu theo trạng thái: xanh hợp lệ, vàng nghi ngờ, đỏ ngoài vùng.
>
> Và chế độ **mô phỏng vị trí**: bấm lên bản đồ để lấy toạ độ ngang, cao độ suy từ thanh trượt tầng. Điểm quan trọng là chế độ này **giữ nguyên toàn bộ logic máy chủ** — nó chỉ thay nguồn toạ độ, không bỏ qua bất kỳ bước kiểm tra nào.
>
> **Xin mời bạn Vy trình bày kết quả và chạy demo.**

---

# LƯỢT 4 — VY · Slide 30 – 37 · 3 phút

## Slide 30 — Chương 04

> Phần bốn: Kết quả thực nghiệm. Em là Vy, phụ trách giao diện và kiểm thử.

## Slide 31 — Toà nhà thử nghiệm

> Nhóm chọn **IFC One Saigon**, trước đây là Saigon One Tower, ở 34 Tôn Đức Thắng, phường Sài Gòn.
>
> Mặt bằng là đa giác 19 đỉnh lấy từ OpenStreetMap. Cao độ nền 5 mét. 42 tầng, cao 195,3 mét, suy ra chiều cao tầng trung bình 4,65 mét. Dung sai áp dụng δxy 25 mét và δz 5 mét cho cả ba khối.
>
> Ba lý do chọn toà nhà này: nó **có thật** nên dễ kiểm chứng bằng ảnh vệ tinh; nó **đủ cao** để tình huống sai tầng có ý nghĩa thực tế; và mặt bằng **có sẵn trong OSM** với hình dạng đặc trưng dễ nhận ra.
>
> Con số bên phải là một phát hiện phụ của đồ án: **chỉ 3,7 %** công trình ở TP.HCM trong dữ liệu OpenStreetMap có thuộc tính height hoặc building:levels. Chiều cao phải nhập tay và ghi rõ nguồn.

## Slide 32 — Môi trường và kiểm chứng trigger

> Môi trường: PostgreSQL 17.6 với PostGIS 3.6.2, Node.js và Express 4 trên cổng 3000, ArcGIS Maps SDK 4.29. Dữ liệu: một toà nhà, ba khối MAP, bốn nhân viên.
>
> `schema.sql` và `seed.sql` chạy hết, thoát mã 0, tạo đúng 14 bảng, 4 hàm và 1 trigger, không có cảnh báo nào.
>
> Bảng dưới là phần em muốn nhấn: nhóm **kiểm chứng trigger bằng cách tính tay rồi đối chiếu**. Alpha Tech tầng 5–8: công thức cho 5 cộng 4 nhân 4,65 bằng 23,60; hệ thống ghi 23,60. Beta Finance ra 93,35. Gamma Media ra 163,10.
>
> **Cả ba khớp chính xác tới hai chữ số thập phân.** Mọi con số trong phần này đều là kết quả chạy thật, tái lập được bằng script kèm mã nguồn.

## Slide 33 — Ba kịch bản đối chiếu 3D và 2D

> Đây là kết quả trọng tâm của cả đồ án.
>
> **TH1** — nhân viên Alpha Tech chấm công ở tầng 6, cao độ 28,25 mét. Mô hình 3D: HỢP LỆ. Hàng rào 2D: hợp lệ. Hai bên cùng đúng.
>
> **TH3** — nhân viên đứng cách toà nhà khoảng 300 mét. Mô hình 3D: NGOÀI VÙNG. Hàng rào 2D: ngoài vùng. Hai bên lại cùng đúng.
>
> **TH2** — vẫn nhân viên đó, cùng toạ độ ngang, nhưng đang ở tầng 22, cao độ 104,98 mét. Mô hình 3D: **NGHI NGỜ**, lệch +62,78 mét, tương đương 13,5 tầng. Hàng rào 2D: **hợp lệ** — **bỏ sót hoàn toàn**.
>
> Hai mô hình trùng nhau ở hai trên ba kịch bản, và **tách nhau đúng ở TH2**.
>
> Em xin nói thêm một ý: TH2 **không phải trường hợp biên hiếm gặp**. Trong một cao ốc cho thuê nhiều tầng, chuyện nhân viên đi họp ở tầng khác là chuyện thường ngày. Nên tỉ lệ bỏ sót thực tế có thể rất lớn. Và mô hình 3D còn **định lượng** được: 62,78 mét quy ra 13,5 tầng — con số mà người quản lý đọc là hiểu ngay.

## Slide 34 — Bằng chứng TH2

> Hình này là bằng chứng trực quan cho TH2.
>
> Quả cầu xám nằm trong khối màu xanh của Beta Finance, tầng 20–24. Còn khối hợp lệ của nhân viên là khối màu cam Alpha Tech, tầng 5–8, nằm phía dưới.
>
> Năm con số: cao độ điểm 104,98 mét; dải khối hợp lệ 23,60 đến 42,20 mét; độ lệch **+62,78 mét**; quy ra **13,5 tầng**; và khoảng cách ngang **0,0 mét**.
>
> Chính con số 0,0 mét ở cuối giải thích vì sao hàng rào 2D kết luận hợp lệ: **toạ độ ngang nằm gọn trong mặt bằng toà nhà**. Chỉ mô hình khối mới phát hiện được sai tầng và sinh cảnh báo R1 mức CAO.

## Slide 35 — Giao diện ứng dụng

> Bên trái là màn hình nhân viên: thông tin làm việc, thanh trượt tầng, và bản đồ 3D. Bên phải là bảng điều khiển quản lý.
>
> Các con số dưới ảnh là kết quả một phiên chạy thử: 4 hợp lệ, 2 nghi ngờ, 6 cảnh báo, và **cả bốn quy tắc R1 đến R4 đều sinh được cảnh báo** — nghĩa là không có quy tắc nào chỉ nằm trên giấy.
>
> Ảnh chụp thì nói được đến đây thôi. **Em xin chuyển sang chạy trực tiếp hệ thống.**

*(→ chuyển sang phần DEMO, quay lại slide 36 sau khi demo xong)*

## Slide 36 — Hiệu năng và đối chiếu mục tiêu

*(nói sau khi demo xong)*

> Quay lại phần đánh giá.
>
> Thời gian phản hồi một lượt chấm công phía máy chủ: tra khối MAP dưới 5 mili-giây, hàm kiểm tra bao hàm dưới 10, hàm kiểm tra R2 dưới 10, ghi bản ghi và cảnh báo dưới 15. **Tổng dưới 50 mili-giây**, trong khi chỉ tiêu đặt ra là dưới 200. Thầy vừa thấy điều đó trong demo — kết quả hiện ra gần như tức thì.
>
> Đối chiếu sáu mục tiêu: M1 đến M5 **đạt**. Riêng **M6 chỉ đạt một phần** — hệ thống suy được z_min, z_max từ dải tầng bằng trigger, nhưng **chưa có giao diện để quản trị viên tự vẽ khối MAP trên bản đồ**; hiện vẫn phải nạp bằng SQL. Nhóm ghi đúng là "một phần" chứ không làm tròn lên thành "đạt".

## Slide 37 — Hạn chế

> Sáu hạn chế nhóm nêu trung thực.
>
> **Một** — độ cao GPS trong nhà gần như không dùng được, nên đa số trường hợp phải dùng tầng khai báo. Khi đó phép kiểm tra trở thành **"đối chiếu khai báo"** chứ không phải **"xác minh độc lập"**. Đây là hạn chế lớn nhất, nhóm không giấu.
>
> **Hai** — chưa dùng cảm biến bổ trợ; Wi-Fi, BLE, khí áp kế chỉ được nêu hướng.
>
> **Ba** — dữ liệu chiều cao công trình rất thiếu, chỉ 3,7 %. Rào cản khi triển khai diện rộng nằm ở **dữ liệu**, không ở phần mềm.
>
> **Bốn** — không chặn được giả lập vị trí cấp hệ điều hành.
>
> **Năm** — chiều cao tầng lấy theo giá trị trung bình, mà tầng trệt và tầng kỹ thuật thường cao hơn, nên cao độ suy ra cho tầng cao có thể lệch vài mét.
>
> **Sáu** — chưa kiểm thử ở quy mô lớn; hiệu năng đo trên một toà nhà và vài chục bản ghi.
>
> Nhóm cho rằng **biết rõ giới hạn của một hệ thống đo lường cũng quan trọng như biết nó làm được gì.**
>
> **Xin mời bạn Tín trình bày phần kết luận.**

---

# LƯỢT 5 — VY · DEMO TRỰC TIẾP · 4 phút

> **Chèn vào giữa slide 35 và slide 36.**

## A. Bật ứng dụng — cách nhanh (nhấp đúp, 30 giây)

Trong thư mục `D:\UIT\ie402-chamcong-3d\` có sẵn hai tệp:

| Tệp | Làm gì |
|---|---|
| **`BAT-DEMO.bat`** | Nhấp đúp → bật PostgreSQL, kiểm tra CSDL, bật máy chủ Node, tự mở trình duyệt |
| **`TAT-DEMO.bat`** | Nhấp đúp → tắt máy chủ Node rồi tắt PostgreSQL |

Nhấp đúp `BAT-DEMO.bat`, chờ khoảng 20 giây, cửa sổ đen sẽ hiện:

```
[1/3] Bat PostgreSQL + PostGIS (cong 55432)...
      server started
[2/3] Kiem tra co so du lieu...
       so_nhan_vien
                  4          <-- phải thấy số 4
[3/3] Bat may chu Node (cong 3000)...
============================================================
 DA SAN SANG:  http://127.0.0.1:3000
============================================================
```

**Thấy đủ ba dòng `[1/3] [2/3] [3/3]` và con số `4` là chạy đúng.**
Một cửa sổ đen thứ hai (tiêu đề *"May chu cham cong 3D"*) sẽ mở ra và **phải để nguyên đó suốt buổi** — đóng nó là tắt máy chủ.

> Quy trình này đã được chạy thử từ trạng thái tắt hoàn toàn (cả PostgreSQL lẫn Node đều không chạy) và lên thành công.

---

## B. Bật ứng dụng — cách gõ tay (khi .bat không chạy)

Mở **PowerShell**, gõ khối này:

```powershell
# 1. Bật PostgreSQL + PostGIS trên cổng 55432
& 'D:\pgportable\pgsql\bin\pg_ctl.exe' -D D:\pgportable\data `
    -o '-p 55432 -c listen_addresses=127.0.0.1' `
    -l D:\pgportable\server.log start

# 2. Kiểm tra CSDL sống — phải in ra "3.6 USE_GEOS=1 ..."
& 'D:\pgportable\pgsql\bin\psql.exe' -h 127.0.0.1 -p 55432 -U postgres `
    -d chamcong3d -c "SELECT postgis_version();"
```

Mở **cửa sổ PowerShell thứ hai** (máy chủ phải chiếm một cửa sổ riêng):

```powershell
cd D:\UIT\ie402-chamcong-3d\server
npm start
```

Phải hiện đúng dòng:

```
Máy chủ chấm công 3D đang chạy: http://127.0.0.1:3000
```

Rồi mở trình duyệt vào **http://127.0.0.1:3000**.

> **Không cần tạo tệp `.env`.** `server/src/db.js` đã có sẵn giá trị mặc định đúng (127.0.0.1 : 55432, user `postgres`, database `chamcong3d`). Tệp `.env.example` chỉ để tham khảo.

### Kiểm tra sống trước khi vào phòng

Mở **http://127.0.0.1:3000/healthz** — phải thấy:

```json
{"trang_thai":"ok","postgis":"3.6 USE_GEOS=1 USE_PROJ=1 USE_STATS=1","bay_gio":"..."}
```

- `healthz` không ra gì → **máy chủ Node chưa chạy**.
- `healthz` ra lỗi kết nối → **PostgreSQL chưa chạy**.

### Tắt sau khi xong

Nhấp đúp `TAT-DEMO.bat`, hoặc gõ tay:

```powershell
# tắt Node: Ctrl+C trong cửa sổ đang chạy npm start, hoặc đóng cửa sổ đó
& 'D:\pgportable\pgsql\bin\pg_ctl.exe' -D D:\pgportable\data stop
```

---

## C. Bảng lỗi khi bật app

| Triệu chứng | Nguyên nhân | Cách xử lý |
|---|---|---|
| `pg_ctl: another server might be running` | PostgreSQL đã chạy sẵn | **Không sao**, bỏ qua — vẫn chạy tiếp bình thường |
| `psql: could not connect to server` | PostgreSQL chưa lên | Xem `D:\pgportable\server.log`, chạy lại bước 1 |
| `Error: listen EADDRINUSE :::3000` | Cổng 3000 đang bị chiếm | Chạy `TAT-DEMO.bat` rồi bật lại |
| `database "chamcong3d" does not exist` | Chưa nạp CSDL | Chạy lại các lệnh nạp trong `db/README.md` |
| Trang trắng, không hiện gì | Máy chủ chưa lên hẳn | Chờ thêm 5 giây rồi F5 |
| Trang hiện nhưng bản đồ trống | ArcGIS SDK tải từ CDN, **cần mạng** | Bật Wi-Fi / 4G; không có mạng thì dùng ảnh dự phòng |

> ⚠️ **Bản đồ 3D cần Internet** vì ArcGIS Maps SDK và ảnh vệ tinh tải từ CDN. Phải thử mạng của phòng bảo vệ trước. Không có mạng thì phần bản đồ trống, nhưng **API và mọi con số trong panel bên trái vẫn chạy đúng** — vẫn demo được, chỉ mất phần hình.

---

## D. Danh sách kiểm tra 15 phút trước khi vào phòng

- [ ] Chạy `BAT-DEMO.bat`, thấy `so_nhan_vien = 4`.
- [ ] Mở `http://127.0.0.1:3000/healthz` → `trang_thai: ok`.
- [ ] **Cửa sổ 1:** đăng nhập `an.nv` / `123456`, tab **Chấm công**, bản đồ 3D đã tải xong (thấy toà nhà và ba dải màu cam / xanh / tím).
- [ ] **Cửa sổ 2:** đăng nhập `binh.tt` / `123456`, tab **Quản lý** — mở sẵn để không phải đăng xuất trước mặt thầy.
- [ ] Phóng to trình duyệt lên **125 %** (Ctrl + `+`) để người ngồi xa đọc được số.
- [ ] Tắt thông báo Windows, tắt Zalo / Slack / mail.
- [ ] Cắm sạc, tắt chế độ tiết kiệm pin — không thì GPU bị bóp, bản đồ 3D giật.
- [ ] **Ảnh dự phòng** mở sẵn ở cửa sổ khác: `scratch/demo/nha-tang06.png`, `nha-tang22.png`, `quanly-xuat.png`.
- [ ] Thử trước **một lượt chấm công tầng 6** cho chắc, rồi để đó — lúc demo làm lại từ đầu.

---

## Kịch bản demo — 5 bước

### Bước 0 — Vào đề (15 giây)

> Em đang đăng nhập bằng tài khoản **an.nv** — Nguyễn Văn An, nhân viên Alpha Tech, thuê **tầng 5 đến 8**.
>
> Khung bên trái cho biết dải cao độ khối của bạn ấy là **23,60 đến 42,20 mét**, dung sai δxy 25 mét và δz 5 mét. Bên phải là toà nhà IFC One Saigon dựng ba chiều, đặt đúng vị trí thật trên ảnh vệ tinh.
>
> Ba dải màu trên toà nhà là ba văn phòng: **cam là Alpha Tech tầng 5–8**, xanh dương là Beta Finance tầng 20–24, tím là Gamma Media tầng 35–40.

### Bước 1 — TH1: chấm công đúng tầng → HỢP LỆ (45 giây)

**Thao tác:**
1. Bấm nút **"Mô phỏng (bấm bản đồ)"**.
2. Bấm vào **giữa toà nhà** trên bản đồ.
3. Kéo thanh trượt tầng về **6**.
4. Bấm **"Chấm công VÀO"**.

**Lời nói:**

> Em chọn chế độ mô phỏng và bấm vào giữa toà nhà để lấy toạ độ. Thầy để ý: em kéo thanh trượt về **tầng 6**, và **tấm sàn tầng 6 sáng lên màu xanh lá** — nó nằm gọn trong dải cam của Alpha Tech.
>
> Bây giờ chấm công vào.
>
> Kết quả: **HỢP LỆ**. Khoảng cách ngang tới khối **0 mét**, cao độ **30,58 mét**, nằm trong dải 23,60 đến 42,20. Không có cảnh báo nào.
>
> Đây là TH1 — hệ 2D và hệ 3D cùng kết luận đúng.

### Bước 2 — TH2: cùng toạ độ, sai tầng → NGHI NGỜ *(đây là điểm nhấn của cả bài)* (75 giây)

**Thao tác:**
1. **Không bấm lại bản đồ** — giữ nguyên toạ độ.
2. Kéo thanh trượt lên **22**.
3. Bấm **"Chấm công RA"**.

**Lời nói:**

> Bây giờ là tình huống quan trọng nhất. Em **không đụng gì đến vị trí trên bản đồ** — toạ độ kinh độ, vĩ độ giữ nguyên y như lần trước. Em chỉ kéo thanh trượt lên **tầng 22**.
>
> *(dừng 2 giây, chỉ tay lên màn hình)*
>
> Thầy nhìn toà nhà: **tấm sàn sáng đã nhảy từ dải cam lên tận dải xanh dương** — tức là từ văn phòng Alpha Tech lên văn phòng Beta Finance, cách nhau mười mấy tầng.
>
> Chấm công ra.
>
> Kết quả: **NGHI NGỜ — đúng toà nhà, sai tầng.**
>
> Các con số: khoảng cách ngang vẫn là **0 mét** — nghĩa là với hàng rào hai chiều, lần chấm công này **hợp lệ hoàn toàn**. Nhưng cao độ là **104,98 mét**, trong khi dải khối cho phép chỉ tới 42,20. Lệch **+62,78 mét**.
>
> Và đây là dòng em muốn thầy chú ý nhất — cảnh báo **R1 mức CAO**: *"Sai tầng: lệch 62,78 mét so với dải khối, tương đương 13,5 tầng."*
>
> Hệ thống không chỉ nói "sai", nó nói **sai bao nhiêu tầng**. Người quản lý không cần biết mét là gì cũng hiểu ngay.
>
> **Đây chính là trạng thái mà mô hình hai chiều không thể sinh ra.** Cùng một toạ độ, cùng một nhân viên, hai kết luận khác nhau.

### Bước 3 — TH3: ra ngoài toà nhà → NGOÀI VÙNG (30 giây)

**Thao tác:**
1. Bấm **"Mô phỏng"** lại.
2. Bấm vào một điểm **cách toà nhà vài trăm mét** (ví dụ bên kia đường Võ Văn Kiệt).
3. Bấm **"Chấm công VÀO"**.

**Lời nói:**

> Trường hợp cuối: em bấm ra ngoài toà nhà, cách khoảng 300 mét.
>
> Kết quả: **NGOÀI VÙNG**, khoảng cách ngang **316 mét**, vượt xa dung sai 25 mét. Bị từ chối.
>
> Và thầy để ý có thêm cảnh báo **R2 — dịch chuyển bất khả thi**: hệ thống tự so với lần chấm công liền trước, thấy vận tốc suy ra vượt 150 km/h. Quy tắc này chạy tự động, không cần ai bật.

### Bước 4 — Gửi giải trình và quản lý duyệt (60 giây)

**Thao tác:**
1. Sang tab **Lịch sử**, tìm bản ghi **NGHI NGỜ** ở bước 2, bấm **"Gửi giải trình"**, nhập lý do: *"Họp với khách hàng ở tầng 22."*
2. **Chuyển sang cửa sổ trình duyệt thứ hai** (đang đăng nhập `binh.tt`), tab **Quản lý**.
3. Tải lại trang. Chỉ vào **Bảng điều khiển** và **danh sách cảnh báo**.
4. Ở mục **Đơn giải trình chờ duyệt**, bấm **Duyệt**.
5. Quay lại cửa sổ nhân viên, tab **Lịch sử**, tải lại.

**Lời nói:**

> Nhân viên không bị kết tội. Bạn ấy gửi đơn giải trình cho bản ghi nghi ngờ: *"họp với khách hàng ở tầng 22"*.
>
> Em chuyển sang tài khoản quản lý — chị Trần Thị Bình.
>
> Bảng điều khiển tổng hợp theo trạng thái, theo quy tắc, và số đơn chờ duyệt. Danh sách cảnh báo sắp theo **mức độ trước, thời gian sau** — cảnh báo mức CAO luôn nổi lên đầu.
>
> Quản lý duyệt đơn.
>
> *(quay lại cửa sổ nhân viên, tải lại)*
>
> Và bản ghi đã **tự chuyển từ NGHI NGỜ sang HỢP LỆ**, đồng thời cảnh báo R1 liên quan cũng được đóng lại. Toàn bộ nằm trong một giao dịch — hoặc cả hai cùng đổi, hoặc không cái nào đổi.

### Bước 5 — Xuất tệp (30 giây)

**Thao tác:** ở cửa sổ quản lý, bấm **"Xuất CSV"** ở mục *Báo cáo công tháng này*, rồi mở tệp bằng Excel.

**Lời nói:**

> Cuối cùng là phần xuất dữ liệu. Ba nút Xuất CSV: nhân viên xuất lịch sử của chính mình, quản lý xuất cảnh báo và xuất báo cáo công.
>
> *(mở tệp trong Excel)*
>
> Tệp mở bằng Excel **đúng dấu tiếng Việt và đúng cột** — nhóm có xử lý hai chi tiết: ghi BOM UTF-8, và khai báo `sep=;` ở dòng đầu, vì Excel theo locale Việt Nam dùng dấu chấm phẩy làm dấu phân cách cột.
>
> Em xin hết phần demo, quay lại slide đánh giá.

---

## Nếu có sự cố

| Tình huống | Xử lý |
|---|---|
| Bản đồ 3D không tải | Nói tiếp bằng **số liệu trên panel bên trái** (vẫn đúng và đủ), rồi mở ảnh `nha-tang22.png` để minh hoạ. Đừng F5 quá 1 lần. |
| Máy chủ chết | *"Xin phép thầy em dùng ảnh chụp kết quả đã kiểm chứng"* → chuyển sang thư mục ảnh, chạy tiếp kịch bản bằng lời. |
| Bấm bản đồ không ăn | Kiểm tra nút **Mô phỏng** đã bật chưa (phải hiện *"Đang chờ… bấm lên bản đồ"*). |
| Thầy hỏi giữa chừng | Trả lời ngắn, rồi *"phần này em có chuẩn bị kỹ ở slide 42, xin phép trả lời đầy đủ ở cuối ạ"*. |
| Số trên màn hình ≠ số trên slide 35 | Nói thẳng: *"Số trên slide là của phiên chạy lúc viết báo cáo, số trên màn hình là của phiên đang chạy — logic giống nhau, chỉ khác số bản ghi đã tạo."* **Đừng lúng túng, đây là điều bình thường.** |

---

# LƯỢT 6 — TÍN · Slide 38 – 40 · 1 phút 30

## Slide 38 — Chương 05

> Phần cuối: Kết luận và phân công.

## Slide 39 — Đóng góp và hướng phát triển

> Đồ án có bốn đóng góp.
>
> **Học thuật:** mô hình MAP — chuyên biệt hoá khối đùn LoD1 cho bài toán xác thực vị trí, với hai thành phần dung sai đưa **thẳng vào định nghĩa** chứ không phải thêm vào lúc cài đặt.
>
> **Kỹ thuật:** cài đặt hoàn chỉnh chỉ bằng thành phần mã nguồn mở và dữ liệu mở, với logic quyết định đặt trong cơ sở dữ liệu.
>
> **Ứng dụng:** bộ tiêu chí so sánh 2D/3D và ba kịch bản kiểm thử tối thiểu mà nhóm cho rằng **mọi hệ chấm công định vị nên vượt qua**.
>
> **Tài liệu:** định lượng một rào cản ít được nói tới — chỉ 3,7 % công trình trong dữ liệu mở có thuộc tính chiều cao.
>
> Hướng phát triển chia ba mốc. Ngắn hạn: hoàn thiện công cụ vẽ khối MAP trên SceneView — đây chính là phần còn thiếu của mục tiêu M6; lưu bảng cao độ thực tế từng tầng; và triển khai lên hạ tầng có HTTPS để thử nghiệm thực địa.
>
> Trung hạn: hợp nhất BLE beacon và khí áp kế vào mô hình MAP, nâng mức chi tiết lên LoD2 hoặc LoD3.
>
> Dài hạn: mở rộng cho công trường với khối MAP **có chiều thời gian**, tích hợp hệ thống tính lương, và chuẩn hoá trao đổi mô hình theo CityGML.

## Slide 40 — Phân công

> Nhóm chia việc **theo lớp kiến trúc, không theo số trang**.
>
> Em — **Tín** — nhóm trưởng, phụ trách mô hình dữ liệu: đề xuất mô hình MAP và phép kiểm tra bao hàm, thiết kế ERD và ràng buộc, viết schema, hàm nghiệp vụ và trigger, tổng hợp báo cáo.
>
> **Nhân** phụ trách máy chủ ứng dụng: Node.js và Express, xác thực JWT, phân quyền, điểm cuối chấm công, điều phối giao dịch, cài đặt bốn quy tắc R1–R4.
>
> **Khôi** phụ trách bản đồ ba chiều: SceneView, nền độ cao, camera, dựng khối MAP, vẽ điểm chấm công theo cao độ tuyệt đối, và bản đồ địa giới TP.HCM ở phụ lục.
>
> **Vy** phụ trách giao diện và kiểm thử: bảy màn hình, luồng gọi API, ba kịch bản kiểm thử đối chiếu, ảnh chụp và kịch bản trình diễn.
>
> Ba nguyên tắc nhóm áp dụng: chia theo lớp kiến trúc; mỗi phần có một người chính và **một người đọc chéo**; và **chốt lược đồ CSDL cùng danh sách API ngay tuần 4** để bốn người làm song song mà không chờ nhau.

---

# LƯỢT 7 — KHÔI · Slide 41 · 45 giây

## Slide 41 — Phụ lục: bản đồ địa giới TP.HCM 3D

> Slide này là sản phẩm nhóm làm **trong quá trình học**, để làm chủ ArcGIS Maps SDK trước khi áp dụng vào đồ án chính: bản đồ địa giới TP.HCM sau sáp nhập, hiệu lực 01/7/2025.
>
> Ba con số: **168 đơn vị cấp xã** — 113 phường, 54 xã, 1 đặc khu. Diện tích tính được **6.745 km²**, so với công bố 6.772,6 — lệch dưới 0,5 %. Và **113 trên 168 đơn vị có dữ liệu dân số**; số còn lại nhóm **vẽ màu xám, không bịa số**.
>
> Kỹ thuật kế thừa từ Lab 1 và Lab 2, mở rộng thêm: UniqueValueRenderer theo loại đơn vị, visualVariables chia theo phân vị, nhãn label-3d có viền sáng, và chuyển 3D sang 2D giữ nguyên khung nhìn.

---

# LƯỢT 8 — NHÂN · Slide 42 · 45 giây

## Slide 42 — Những câu hỏi nhóm đã chuẩn bị

> Nhóm chủ động chuẩn bị sáu câu hỏi thường gặp. Em xin lướt nhanh ba câu, ba câu còn lại xin phép trả lời khi thầy hỏi.
>
> **"Vì sao không dùng geofence 2D cho đơn giản?"** — Kịch bản TH2 thầy vừa thấy trong demo.
>
> **"GPS trong nhà không đo được độ cao thì mô hình còn ý nghĩa gì?"** — Hệ thống chuyển từ *xác minh độc lập* sang *đối chiếu khai báo*. Vẫn phát hiện được sự không nhất quán, vẫn lưu bằng chứng 3D, và sẵn sàng nhận độ cao từ beacon hay khí áp kế khi bổ sung.
>
> **"Vì sao PostGIS mà không phải MongoDB?"** — MongoDB chỉ có chỉ mục 2dsphere trên mặt cầu hai chiều, không lưu và không truy vấn được thành phần độ cao. Tức là **không cài đặt được mô hình của đồ án**.

---

# LƯỢT 9 — VY · Slide 43 · 30 giây

## Slide 43 — Cảm ơn

> Phần trình bày của nhóm 1 đến đây là hết.
>
> Nhóm xin tóm lại trong một câu: **khi chuyển phép kiểm tra từ "điểm thuộc đa giác" sang "điểm thuộc khối", hệ thống sinh ra được một trạng thái mới — "đúng toà nhà, sai tầng" — mà mô hình hai chiều không có dữ liệu để phát hiện.**
>
> Nhóm cảm ơn thầy và các bạn đã lắng nghe, và xin lắng nghe câu hỏi cùng góp ý ạ.

---

## Phụ lục — Sáu câu hỏi đã chuẩn bị (ai trả lời)

| Câu hỏi | Người trả lời | Ý chính |
|---|---|---|
| Vì sao không dùng geofence 2D? | Vy | TH2 — tình huống thường ngày trong cao ốc, không phải trường hợp biên |
| GPS trong nhà không đo được độ cao? | Tín | Chuyển từ *xác minh độc lập* sang *đối chiếu khai báo*; vẫn lưu bằng chứng 3D |
| Vì sao PostGIS mà không MongoDB? | Nhân | MongoDB chỉ có 2dsphere, không lưu được thành phần Z |
| δxy = 25 m và δz = 5 m lấy từ đâu? | Tín | δxy theo sai số GNSS điển hình khu nhà cao tầng; δz ≈ chiều cao một tầng (4,65 m) |
| Có chống được fake GPS không? | Nhân | **Không.** R2–R4 chỉ làm tăng chi phí gian lận; cần chứng thực phía thiết bị |
| Mở rộng nhiều toà nhà thì hiệu năng? | Nhân | Tra khối theo quan hệ nhân viên–công ty–văn phòng, không có bước tìm kiếm không gian; GiST sẵn cho trường hợp tìm khối gần nhất |

### Ba câu có thể bị hỏi thêm mà slide chưa có

- **"14 bảng hay 15 bảng?"** → Nhân: 14 bảng của lược đồ nhóm thiết kế; `spatial_ref_sys` là bảng hệ thống do PostGIS tự tạo, đã kiểm tra bằng `pg_class` và loại ra.
- **"Vì sao mục tiêu M6 chỉ đạt một phần?"** → Vy: trigger suy được cao độ từ dải tầng, nhưng chưa có giao diện cho quản trị viên tự vẽ khối MAP; hiện nạp bằng SQL. Đây là việc đầu tiên trong hướng phát triển ngắn hạn.
- **"Vai trò QUAN_TRI khác QUAN_LY chỗ nào?"** → Nhân: hiện **chưa khác** — vai trò thứ ba đã khai báo trong CSDL và middleware nhưng chưa có chức năng riêng. Nhóm ghi nhận đây là phần chưa hoàn thiện, đúng với M6 đạt một phần.

---

## Lời khuyên chung khi trình bày

- **Không đọc slide.** Slide có chữ rồi; người nói bổ sung *vì sao*, không lặp lại *cái gì*.
- **Dừng 2 giây sau mỗi con số quan trọng** — đặc biệt "62,78 mét" và "13,5 tầng".
- Khi chuyển người: người trước nói rõ **"xin mời bạn X"**, người sau bước lên rồi mới nói.
- Nếu không biết câu trả lời: *"Phần đó nhóm chưa khảo sát kỹ, em xin ghi nhận ạ."* — **trung thực ăn điểm hơn đoán bừa**, và tinh thần đó cũng đúng với cách cả đồ án nêu hạn chế.
