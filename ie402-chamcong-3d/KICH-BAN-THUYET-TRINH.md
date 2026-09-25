# Kịch bản thuyết trình — Đồ án IE402

**Đề tài:** Hệ thống chấm công định vị theo mô hình khối không gian 3 chiều phân tầng
**Nhóm 1** · GVHD: ThS. Phan Thanh Vũ · 43 slide · ≈ 30 phút

> Bản dài (lời thoại đầy đủ từng câu) nằm trong lịch sử git, commit `ad86a59`.

---

## Phân công

| Lượt | Người | Slide | Nội dung | Phút |
|---|---|---|---|---|
| 1 | **Khôi** | 1 – 9 | Mở đầu · Đặt vấn đề | 6 |
| 2 | **Tín** | 10 – 17 | Lý thuyết · Mô hình MAP · Thuật toán | 6 |
| 3 | **Nhân** | 18 – 29 | Thiết kế · CSDL · API · Bảo mật | 7½ |
| 4 | **Vy** | 30 – 37 | Kết quả thực nghiệm | 3 |
| 5 | **Vy** | — | **DEMO TRỰC TIẾP** | 4 |
| 6 | **Tín** | 38 – 40 | Kết luận · Phân công | 1½ |
| 7 | **Khôi** | 41 | Phụ lục bản đồ TP.HCM | ¾ |
| 8 | **Nhân** | 42 | Câu hỏi đã chuẩn bị | ¾ |
| 9 | **Vy** | 43 | Cảm ơn | ½ |

Chia theo đúng vai trò trong slide 40: Tín = mô hình dữ liệu, Nhân = máy chủ, Khôi = bản đồ 3D, Vy = giao diện + kiểm thử.

### ⚠️ Sửa slide trước khi bảo vệ

1. **Slide 1** — còn `Thành viên A · B · C · D`, thay bằng tên thật.
2. **Slide 40** — nhãn A/B/C/D → A = Tín, B = Nhân, C = Khôi, D = Vy.
3. **Slide 27** — ghi "13 điểm cuối API", thực tế đã là **16** (thêm 3 endpoint xuất CSV). Không kịp sửa thì Nhân đính chính bằng miệng.

---

# KHÔI · Slide 1 – 9

**1. Bìa** — Chào thầy và các bạn. Nhóm 1 trình bày đề tài *hệ thống chấm công định vị theo mô hình khối không gian ba chiều phân tầng*; nhóm đặt tên mô hình là **MAP — Multi-floor Attendance Prism**. Câu hỏi của đồ án: khi hàng rào địa lý 2D không còn đủ thì thay bằng gì.

**2. Nội dung** — Năm phần: đặt vấn đề, mô hình MAP, thiết kế và cài đặt, kết quả kèm demo trực tiếp, kết luận. Nếu thầy chỉ nhớ một điều, xin nhớ dòng này: **"đúng toà nhà, sai tầng"** — trạng thái mà mô hình 2D không sinh ra được.

**3. Chương 01** — Phần một: Tổng quan và đặt vấn đề. *(chuyển nhanh)*

**4. Bối cảnh** — Hầu hết app chấm công ở Việt Nam dựng trên một kỹ thuật duy nhất: hàng rào địa lý 2D, trả lời đúng một câu hỏi *"có nằm trong vùng trên mặt phẳng không"*. Toà nhà thử nghiệm có **42 tầng**, **3 văn phòng** ở ba dải tầng, nhưng chỉ **1 cặp toạ độ** — vì chúng chồng lên nhau. Trong khi đó PostGIS đã hỗ trợ toạ độ Z từ lâu, ArcGIS dựng được khối 3D trên trình duyệt. Khoảng cách giữa công nghệ sẵn có và cách người ta đang làm chính là khoảng trống của đồ án.

**5. Bốn hạn chế** — (a) Không phân biệt chiều cao: người ngồi quán cà phê tầng trệt vẫn chấm hợp lệ cho văn phòng tầng 22. (b) Sai số GPS đô thị: hiệu ứng urban canyon, sai số hàng chục mét. (c) Không phát hiện gian lận theo chiều đứng: dữ liệu 2D không lưu độ cao nên không còn gì để rà soát. (d) Không trực quan hoá để đối chiếu. **Cả bốn đều từ một nguyên nhân: phép kiểm tra chạy trên hình chiếu xuống mặt phẳng.** Sửa nguyên nhân đó thì cả bốn cùng được giải.

**6. Minh hoạ** — Ba nhân viên, ba tầng, hình chiếu trùng khít một điểm. Hàng rào 2D nói cả ba hợp lệ. Mô hình khối tách được, và sinh trạng thái thứ ba: **NGHI NGỜ**.

**7. Ý tưởng cốt lõi** — Chuyển từ **"điểm thuộc đa giác"** sang **"điểm thuộc khối"**; từ 2 chiều 2 trạng thái sang 3 chiều 3 trạng thái. *Học thuật:* LoD1 đã đủ giải bài toán, không cần BIM hay quét laser. *Ứng dụng:* chi phí số hoá rất thấp — chỉ cần mặt bằng OSM, số tầng, chiều cao tầng. *Thiết kế:* hệ thống trung thực về giới hạn của mình — không đủ căn cứ thì nói "nghi ngờ" và chuyển cho con người.

**8. Sáu mục tiêu** — M1 mô hình 3D, M2 thuật toán 3 trạng thái dưới 200 ms, M3 web ba vai trò, M4 trực quan hoá, M5 bốn quy tắc bất thường, M6 cấu hình khối từ dữ liệu toà nhà. Mỗi mục tiêu có tiêu chí đo được. Kết quả: **5/6 đạt, M6 đạt một phần** — nhóm sẽ nói rõ ở cuối.

**9. Phạm vi** — *Trong:* IFC One Saigon 42 tầng, ba văn phòng dải 5–8 / 20–24 / 35–40, mức LoD1, nguồn độ cao hỗn hợp, web cục bộ. *Ngoài:* Wi-Fi/BLE indoor, app di động gốc, sinh trắc học, chống fake GPS cấp OS, triển khai đám mây HTTPS. Nêu giới hạn từ đầu cũng là một phần kết quả — nó cho biết cần bổ sung gì để đi tiếp. **Xin mời bạn Tín.**

---

# TÍN · Slide 10 – 17

**10. Chương 02** — Cơ sở lý thuyết và mô hình MAP.

**11. Chọn mô hình 3D** — Nhóm khảo sát năm cách: khối đùn 2.5D, B-Rep, CSG, Voxel, TIN. Chọn **khối đùn** vì bốn lý do: bài toán chỉ cần trả lời một câu hỏi bao hàm; tách được thành hai bước rẻ — ray casting O(n) cộng một phép so sánh số thực; dữ liệu đầu vào có sẵn (mặt bằng OSM + số tầng + chiều cao tầng); và PostGIS lẫn ArcGIS đều hỗ trợ trực tiếp. Đúng bằng mức **LoD1** của CityGML.

**12. Bài toán khó nhất: độ cao** — Ba ràng buộc: độ chính xác đứng kém hơn ngang **2–3 lần**; trong nhà `altitude` thường null hoặc sai số hàng chục mét; và **chỉ 3,7 %** công trình OSM có thuộc tính height. Giải pháp là **nguồn độ cao hỗn hợp** — ưu tiên thiết bị đo khi `altitudeAccuracy` < 15 m, ngoài ngưỡng thì suy từ tầng khai báo theo **z = z_nền + (tầng − 0,5) × h_tầng**. Hệ số 0,5 đặt điểm giữa tầng để sai số phân bố đều hai phía. Quan trọng nhất: **nguồn độ cao được ghi thẳng vào bản ghi**, nên mỗi bản ghi tự nói được nó đáng tin tới đâu.

**13. Ba hướng xác định tầng** — Khí áp kế: phân giải ~1 m nhưng trôi theo thời tiết. Wi-Fi/BLE: chính xác tốt nhưng phải lắp đặt và khảo sát từng toà nhà. **Hướng của đồ án là thứ ba — mô hình không gian: không cải thiện phép đo, mà cải thiện cái mô hình mà phép đo được đối chiếu vào.** Ba hướng bổ sung nhau chứ không loại trừ; MAP nhận độ cao từ bất kỳ nguồn nào, miễn nguồn đó được ghi lại.

**14. Mô hình MAP** — **MAP = ( P, z_min, z_max, δxy, δz )**. P là đa giác nền WGS84; z_min sàn tầng thấp nhất; z_max trần tầng cao nhất; δxy dung sai ngang mặc định 25 m; δz dung sai đứng mặc định 5 m. Khi kiểm tra dùng khối đã nới biên **MAP⁺**. **Hai thành phần dung sai chính là điểm khác biệt giữa MAP và khối đùn thường** — chúng biến khối cứng thành khối có biên mềm, phản ánh đúng bản chất phép đo GPS: kết quả không phải một điểm mà là một vùng xác suất.

**15. Suy cao độ từ dải tầng** — Quản trị viên **không nhập z_min/z_max** (dễ sai), họ nhập dải tầng trong hợp đồng thuê; một trigger tự suy: `z_min = z_nền + (tầng_đầu − 1) × h_tầng`, `z_max = z_nền + tầng_cuối × h_tầng`. Với nền 5 m và tầng 4,65 m: Alpha 23,60–42,20 · Beta 93,35–116,60 · Gamma 163,10–191,00. **Ba khối có đa giác nền trùng khít, chỉ khác dải cao độ** — với hệ 2D đây là *một* vùng duy nhất.

**16. Phép kiểm tra bao hàm** — Điểm nằm trong khối khi hình chiếu ngang nằm trong đa giác đã buffer **và** cao độ nằm trong dải đã nới biên. Ba kết quả: **HỢP LỆ** (thoả cả hai), **NGHI NGỜ** (thoả ngang, sai đứng — hoặc độ chính xác quá kém), **NGOÀI VÙNG** (sai ngang). Trạng thái ở giữa là thứ mô hình 2D **không thể sinh ra** — vì nó định nghĩa bằng một điều kiện đứng mà hệ 2D không có dữ liệu để kiểm tra.

**17. Bốn quy tắc R1–R4** — **R1** sai tầng (CAO): lệch khỏi dải quá δz, **quy đổi ra số tầng** cho quản lý dễ hình dung. **R2** dịch chuyển bất khả thi (CAO): vận tốc giữa hai bản ghi vượt 150 km/h. **R3** độ chính xác bất thường (TB): < 1 m nghi fake GPS, > 100 m không đủ tin. **R4** trùng thiết bị (TB): nhiều nhân viên cùng một thiết bị trong 10 phút. Xin nói rõ ngay: **bốn quy tắc không loại trừ gian lận, chỉ làm tăng chi phí gian lận.** **Xin mời bạn Nhân.**

---

# NHÂN · Slide 18 – 29

**18. Chương 03** — Phân tích, thiết kế và cài đặt.

**19. Yêu cầu** — 13 yêu cầu chức năng: nhân viên F01–F08, quản lý F09–F12, quản trị F13. Bảy yêu cầu phi chức năng, ba cái quan trọng nhất: **N02** bản ghi và cảnh báo trong cùng một giao dịch; **N06** logic kiểm tra đặt trong CSDL; **N01** phản hồi dưới 200 ms.

**20. Use case** — Bốn nhóm tác nhân. Nhóm thứ tư là **dịch vụ nội bộ**: UC12 kiểm tra bao hàm và UC13 áp quy tắc — hai use case này **luôn được UC2 include và không tác nhân nào gọi trực tiếp được**. Đó là quyết định thiết kế có chủ đích: không lối vào nào tạo được bản ghi chưa qua kiểm tra.

**21. DFD mức 0 và 1** — Mức 0 có bốn tác nhân ngoài, trong đó **dịch vụ định vị của thiết bị** hay bị bỏ sót nhưng là nguồn của toàn bộ dữ liệu toạ độ. Mức 1 phân rã thành **bảy tiến trình, sáu kho dữ liệu**.

**22. DFD mức 2 + sơ đồ trình tự** — Ba ý: **thứ tự có chủ đích** — kiểm ngang trước, đã ngoài vùng thì khỏi xét cao độ, chi phí thấp nhất. **Ba nhánh** ánh xạ thẳng sang mã HTTP: 200 hợp lệ, 202 chờ xác minh, 422 ngoài vùng. **Nguồn cao độ tách bạch** ở tiến trình 3.2 và được ghi vào bản ghi.

**23. Kiến trúc ba lớp** — *Trình bày:* JS thuần + ArcGIS SDK 4.29 + Geolocation API — lớp này **không tự kết luận gì về tính hợp lệ**. *Ứng dụng:* Node.js + Express + JWT + bcrypt. *Dữ liệu:* PostgreSQL 17 + PostGIS 3.6, chứa luôn hàm nghiệp vụ không gian. Đặt thuật toán trong CSDL để có **đúng một cài đặt duy nhất** — gọi từ API, từ script hay từ psql đều qua cùng một hàm.

**24. Lược đồ CSDL** — **14 bảng · 4 hàm · 1 trigger · 4 chỉ mục GiST**. Bốn hàm: `tinh_dai_cao_do()`, `kiem_tra_bao_ham()`, `kiem_tra_r2()`, và trigger `trg_dong_bo_cao_do()`. *(Nếu hỏi 14 hay 15: `spatial_ref_sys` là bảng hệ thống của PostGIS, nhóm đã kiểm bằng `pg_class` và loại ra.)*

**25. Hàm kiem_tra_bao_ham()** — Mã thật, không phải mã giả. Bước 1 điều kiện ngang bằng `ST_DWithin` **trên kiểu geography** — chi tiết này quyết định tính đúng đắn, vì nó cho dung sai tính **bằng mét trên ellipsoid** chứ không phải bằng độ; để kiểu geometry thì 25 "đơn vị" thành 25 độ, sai hoàn toàn. Bước 2 điều kiện đứng → `NGHI_NGO`. Bước 3 chốt chặn độ chính xác: sai số lớn hơn gấp đôi dung sai thì kết quả "nằm trong vùng" **không còn mang thông tin** — có thể đúng do may mắn.

**26. Một lượt chấm công** — Sáu bước trong **một giao dịch duy nhất**: kiểm đầu vào → tra khối MAP → xác định cao độ → kiểm bao hàm → áp R1–R4 → ghi và phản hồi. Lỗi bất kỳ bước nào thì huỷ toàn bộ. Ý quan trọng nhất: **hệ thống phải giải thích được kết luận của mình** — phản hồi gồm khoảng cách ngang, cao độ và **nguồn** của nó, dải khối, hai dung sai, độ lệch, và danh sách cảnh báo. Lát nữa thầy sẽ thấy đúng những con số này trong demo.

**27. API** — Slide ghi mười ba, nhưng sau khi in slide nhóm bổ sung **ba điểm cuối xuất CSV**, tổng hiện tại là **mười sáu**. `POST /api/cham-cong` là nơi tập trung toàn bộ nghiệp vụ.

**28. Bảo mật** — Ba lớp: **xác thực** (bcrypt + JWT hạn 8 giờ); **phân quyền vai trò** (middleware riêng, nhân viên gọi endpoint quản lý nhận 403 — đã thử thật); **kiểm soát quyền sở hữu** — lớp hay bị bỏ — truy vấn lịch sử lọc theo mã nhân viên **lấy từ thẻ JWT**, không lấy từ tham số người dùng gửi lên. Ba điểm chưa đạt chuẩn triển khai thật, nhóm ghi nhận: CSDL dùng `trust` (thật phải `scram-sha-256`), khoá JWT để mặc định, và chạy HTTP (thật phải HTTPS — cũng là điều kiện để Geolocation API hoạt động).

**29. Trực quan hoá** — Khối đùn theo **cao độ tuyệt đối** (`elevationInfo: absolute-height`) — bắt buộc, vì để chế độ tương đối thì khối trôi theo địa hình. Khối của người đang đăng nhập tô đậm hơn. Điểm chấm công là cầu 5 m đổi màu theo trạng thái. Chế độ **mô phỏng vị trí** chỉ thay nguồn toạ độ, **giữ nguyên toàn bộ logic máy chủ**. **Xin mời bạn Vy.**

---

# VY · Slide 30 – 37

**30. Chương 04** — Kết quả thực nghiệm. Em là Vy, phụ trách giao diện và kiểm thử.

**31. Toà nhà thử nghiệm** — IFC One Saigon, 34 Tôn Đức Thắng. Mặt bằng 19 đỉnh từ OSM, nền 5 m, 42 tầng cao 195,3 m, tầng trung bình 4,65 m, δxy 25 m và δz 5 m. Chọn vì: **có thật** nên kiểm chứng được bằng ảnh vệ tinh, **đủ cao** để tình huống sai tầng có nghĩa, và **có sẵn trong OSM**. Phát hiện phụ: chỉ **3,7 %** công trình TP.HCM trong OSM có thuộc tính chiều cao.

**32. Kiểm chứng trigger** — PostgreSQL 17.6 + PostGIS 3.6.2, Node + Express cổng 3000, ArcGIS 4.29. `schema.sql` và `seed.sql` chạy hết, thoát mã 0, tạo đúng 14 bảng / 4 hàm / 1 trigger. Nhóm **tính tay rồi đối chiếu**: Alpha 5 + 4×4,65 = 23,60, hệ thống ghi 23,60; Beta 93,35; Gamma 163,10. **Cả ba khớp tới hai chữ số thập phân.** Mọi con số phần này đều là kết quả chạy thật, tái lập được bằng script.

**33. Ba kịch bản** — **TH1** tầng 6, cao 28,25 m: 3D `HỢP LỆ`, 2D hợp lệ — cùng đúng. **TH3** cách 300 m: 3D `NGOÀI VÙNG`, 2D ngoài vùng — cùng đúng. **TH2** cùng toạ độ nhưng ở tầng 22, cao 104,98 m: 3D `NGHI NGỜ` lệch **+62,78 m ≈ 13,5 tầng**, 2D **hợp lệ — bỏ sót hoàn toàn**. Hai mô hình trùng nhau 2/3 kịch bản và tách nhau đúng ở TH2. TH2 **không phải trường hợp biên hiếm gặp** — trong cao ốc cho thuê, đi họp tầng khác là chuyện thường ngày, nên tỉ lệ bỏ sót thực tế có thể rất lớn.

**34. Bằng chứng TH2** — Quả cầu xám nằm trong khối xanh Beta Finance (tầng 20–24), còn khối hợp lệ là khối cam Alpha Tech (tầng 5–8) phía dưới. Cao độ 104,98 m · dải hợp lệ 23,60–42,20 · lệch **+62,78 m** ≈ **13,5 tầng** · khoảng cách ngang **0,0 m**. Chính con số 0,0 m giải thích vì sao 2D kết luận hợp lệ. Chỉ mô hình khối mới sinh được cảnh báo R1 mức CAO.

**35. Giao diện** — Màn hình nhân viên và bảng điều khiển quản lý. Số liệu một phiên chạy thử: 4 hợp lệ, 2 nghi ngờ, 6 cảnh báo, **cả bốn quy tắc R1–R4 đều sinh được cảnh báo** — không quy tắc nào chỉ nằm trên giấy. Ảnh chụp nói được đến đây thôi, **em xin chuyển sang chạy trực tiếp**. → **DEMO**

**36. Hiệu năng và mục tiêu** *(nói sau demo)* — Tra khối < 5 ms, kiểm bao hàm < 10 ms, kiểm R2 < 10 ms, ghi < 15 ms — **tổng dưới 50 ms** so với chỉ tiêu 200 ms; thầy vừa thấy kết quả ra gần như tức thì. M1–M5 **đạt**; **M6 chỉ đạt một phần** — trigger suy được cao độ nhưng **chưa có giao diện cho quản trị viên tự vẽ khối MAP**, hiện vẫn nạp bằng SQL. Nhóm ghi "một phần" chứ không làm tròn lên.

**37. Hạn chế** — (1) Độ cao GPS trong nhà gần như không dùng được nên đa số phải dùng tầng khai báo — phép kiểm tra thành **"đối chiếu khai báo"** chứ không phải **"xác minh độc lập"**; đây là hạn chế lớn nhất. (2) Chưa dùng cảm biến bổ trợ. (3) Dữ liệu chiều cao thiếu — rào cản nằm ở **dữ liệu**, không ở phần mềm. (4) Không chặn được fake GPS cấp OS. (5) Chiều cao tầng lấy trung bình nên tầng cao lệch vài mét. (6) Chưa kiểm thử quy mô lớn. **Biết rõ giới hạn của một hệ thống đo lường cũng quan trọng như biết nó làm được gì.** **Xin mời bạn Tín.**

---

# VY · DEMO TRỰC TIẾP — 4 phút

*(chèn giữa slide 35 và 36)*

## Bật ứng dụng

Nhấp đúp **`BAT-DEMO.bat`** trong `D:\UIT\ie402-chamcong-3d\`. Chờ ~20 giây, phải thấy đủ `[1/3] [2/3] [3/3]` và **`so_nhan_vien = 4`**. Cửa sổ đen *"May chu cham cong 3D"* **để nguyên** — đóng nó là tắt máy chủ. Xong việc chạy **`TAT-DEMO.bat`**.

Gõ tay nếu .bat hỏng:

```powershell
& 'D:\pgportable\pgsql\bin\pg_ctl.exe' -D D:\pgportable\data `
    -o '-p 55432 -c listen_addresses=127.0.0.1' -l D:\pgportable\server.log start
# cửa sổ thứ hai:
cd D:\UIT\ie402-chamcong-3d\server ; npm start
```

Kiểm tra sống: **http://127.0.0.1:3000/healthz** → `trang_thai: ok`.
Không ra gì = Node chưa chạy · lỗi kết nối = PostgreSQL chưa chạy. **Không cần tạo `.env`.**

## Checklist 15 phút trước

- [ ] `BAT-DEMO.bat` chạy, thấy `so_nhan_vien = 4`, `/healthz` ok
- [ ] **Cửa sổ 1:** `an.nv` / `123456`, tab Chấm công, bản đồ đã tải (thấy toà nhà + ba dải cam/xanh/tím)
- [ ] **Cửa sổ 2:** `binh.tt` / `123456`, tab Quản lý — mở sẵn, khỏi đăng xuất trước mặt thầy
- [ ] Zoom trình duyệt **125 %**, tắt thông báo Windows/Zalo, cắm sạc (pin yếu → GPU bị bóp, bản đồ giật)
- [ ] **Ảnh dự phòng** mở sẵn: `scratch/demo/nha-tang06.png`, `nha-tang22.png`, `quanly-xuat.png`
- [ ] ⚠️ **Bản đồ 3D cần Internet** (ArcGIS + ảnh vệ tinh từ CDN) — thử mạng phòng bảo vệ trước. Mất mạng thì bản đồ trống nhưng **mọi con số ở panel trái vẫn đúng**, vẫn demo được.

## Năm bước

**0 · Vào đề (15 giây)** — Tài khoản **an.nv**, nhân viên Alpha Tech thuê **tầng 5–8**, dải cao độ **23,60–42,20 m**, δxy 25 m δz 5 m. Bên phải là IFC One Saigon dựng 3D đúng vị trí thật. Ba dải màu là ba văn phòng: **cam Alpha 5–8**, xanh Beta 20–24, tím Gamma 35–40.

**1 · TH1 → HỢP LỆ (45 giây)**
> Bấm **Mô phỏng** → bấm giữa toà nhà → kéo tầng về **6** → **Chấm công VÀO**

Em chọn mô phỏng, bấm giữa toà nhà. Thầy để ý: kéo về **tầng 6** thì **tấm sàn sáng lên màu xanh lá**, nằm gọn trong dải cam. Chấm công vào → **HỢP LỆ**, khoảng cách ngang **0 m**, cao độ **30,58 m**, trong dải 23,60–42,20. Không cảnh báo nào. Đây là TH1 — 2D và 3D cùng đúng.

**2 · TH2 → NGHI NGỜ · ĐIỂM NHẤN (75 giây)**
> **Không bấm lại bản đồ** → kéo tầng lên **22** → **Chấm công RA**

Đây là tình huống quan trọng nhất. Em **không đụng gì đến vị trí** — toạ độ giữ nguyên y như lần trước, chỉ kéo lên **tầng 22**.

*(dừng 2 giây, chỉ tay lên màn hình)*

Thầy nhìn toà nhà: **tấm sàn sáng đã nhảy từ dải cam lên tận dải xanh** — từ Alpha Tech lên Beta Finance, cách nhau mười mấy tầng.

Chấm công ra → **NGHI NGỜ — đúng toà nhà, sai tầng.** Khoảng cách ngang vẫn **0 m**, nghĩa là với hàng rào 2D lần này **hợp lệ hoàn toàn**. Nhưng cao độ **104,98 m** trong khi dải cho phép chỉ tới 42,20 — lệch **+62,78 m**. Và cảnh báo **R1 mức CAO**: *"Sai tầng: lệch 62,78 m so với dải khối, tương đương 13,5 tầng."*

Hệ thống không chỉ nói "sai", nó nói **sai bao nhiêu tầng**. **Đây chính là trạng thái mô hình 2D không thể sinh ra.**

**3 · TH3 → NGOÀI VÙNG (30 giây)**
> **Mô phỏng** → bấm cách toà nhà vài trăm mét → **Chấm công VÀO**

**NGOÀI VÙNG**, khoảng cách ngang **316 m**, vượt xa dung sai 25 m. Thêm cảnh báo **R2 — dịch chuyển bất khả thi**: hệ thống tự so với lần trước, vận tốc suy ra vượt 150 km/h. Quy tắc này chạy tự động.

**4 · Giải trình và duyệt (60 giây)**
> Tab **Lịch sử** → bản ghi NGHI NGỜ → **Gửi giải trình** *"Họp với khách hàng ở tầng 22"* → sang **cửa sổ 2** (`binh.tt`) tab Quản lý → **Duyệt** → quay lại cửa sổ 1, F5

Nhân viên không bị kết tội, bạn ấy gửi giải trình. Chuyển sang tài khoản quản lý: bảng điều khiển tổng hợp theo trạng thái và quy tắc; danh sách cảnh báo sắp **theo mức độ trước, thời gian sau**. Quản lý duyệt. Quay lại — bản ghi **tự chuyển NGHI NGỜ → HỢP LỆ** và cảnh báo R1 cũng đóng lại, **cả hai trong một giao dịch**.

**5 · Xuất tệp (30 giây)**
> Cửa sổ quản lý → **Xuất CSV** ở *Báo cáo công* → mở bằng Excel

Ba nút xuất CSV. Tệp mở bằng Excel **đúng dấu tiếng Việt và đúng cột** — nhóm xử lý hai chi tiết: ghi BOM UTF-8, và khai báo `sep=;` vì Excel locale Việt Nam dùng dấu chấm phẩy làm phân cách cột. **Em xin hết phần demo, quay lại slide đánh giá.**

## Khi có sự cố

| Tình huống | Xử lý |
|---|---|
| Bản đồ không tải | Nói tiếp bằng số liệu panel trái (vẫn đủ), mở ảnh `nha-tang22.png`. **Đừng F5 quá 1 lần.** |
| Máy chủ chết | *"Xin phép thầy em dùng ảnh chụp kết quả đã kiểm chứng"* → chạy tiếp bằng lời. **Không sửa lỗi trước mặt thầy.** |
| Bấm bản đồ không ăn | Nút **Mô phỏng** phải đang hiện *"Đang chờ… bấm lên bản đồ"* |
| Thầy hỏi giữa chừng | Trả lời ngắn, *"phần này em chuẩn bị ở slide 42, xin trả lời đầy đủ ở cuối ạ"* |
| Số khác slide 35 | *"Số trên slide là phiên chạy lúc viết báo cáo, số trên màn hình là phiên đang chạy — logic giống nhau, chỉ khác số bản ghi."* Bình thường, **đừng lúng túng.** |
| Lỗi bật app | `EADDRINUSE :::3000` → chạy `TAT-DEMO.bat` rồi bật lại · `could not connect` → PostgreSQL chưa lên, xem `D:\pgportable\server.log` · `database does not exist` → chạy `CAI-DAT.bat` |

---

# TÍN · Slide 38 – 40

**38. Chương 05** — Kết luận và phân công.

**39. Đóng góp và hướng phát triển** — *Học thuật:* mô hình MAP, chuyên biệt hoá khối đùn LoD1 cho bài toán xác thực vị trí, với hai thành phần dung sai đưa **thẳng vào định nghĩa**. *Kỹ thuật:* cài đặt hoàn chỉnh chỉ bằng mã nguồn mở và dữ liệu mở, logic quyết định đặt trong CSDL. *Ứng dụng:* bộ tiêu chí so sánh 2D/3D và ba kịch bản kiểm thử tối thiểu mà mọi hệ chấm công định vị nên vượt qua. *Tài liệu:* định lượng rào cản ít được nói tới — chỉ 3,7 % công trình có thuộc tính chiều cao.
Hướng phát triển — *Ngắn hạn:* công cụ vẽ khối MAP trên SceneView (chính là phần thiếu của M6), bảng cao độ thực tế từng tầng, triển khai HTTPS. *Trung hạn:* hợp nhất BLE và khí áp kế, nâng lên LoD2/LoD3. *Dài hạn:* khối MAP **có chiều thời gian** cho công trường, tích hợp tính lương, chuẩn hoá theo CityGML.

**40. Phân công** — Chia **theo lớp kiến trúc, không theo số trang**. **Tín** (nhóm trưởng) mô hình dữ liệu: đề xuất MAP, ERD, schema, hàm nghiệp vụ, trigger, biên tập báo cáo. **Nhân** máy chủ: Express, JWT, phân quyền, điểm cuối chấm công, giao dịch, R1–R4. **Khôi** bản đồ 3D: SceneView, camera, dựng khối MAP, vẽ điểm theo cao độ tuyệt đối, bản đồ TP.HCM. **Vy** giao diện và kiểm thử: bảy màn hình, luồng API, ba kịch bản đối chiếu, ảnh chụp và kịch bản trình diễn. Ba nguyên tắc: chia theo lớp; mỗi phần có một người chính và **một người đọc chéo**; **chốt lược đồ CSDL và danh sách API ngay tuần 4** để bốn người làm song song.

---

# KHÔI · Slide 41

**41. Phụ lục** — Sản phẩm nhóm làm **trong quá trình học** để làm chủ ArcGIS SDK trước khi vào đồ án chính: địa giới TP.HCM sau sáp nhập, hiệu lực 01/7/2025. **168 đơn vị cấp xã** (113 phường, 54 xã, 1 đặc khu); diện tích tính được **6.745 km²** so với công bố 6.772,6 — lệch dưới 0,5 %; **113/168 đơn vị có dữ liệu dân số**, số còn lại **vẽ xám, không bịa số**. Kỹ thuật kế thừa Lab 1–2, mở rộng thêm UniqueValueRenderer, visualVariables chia theo phân vị, nhãn label-3d có viền sáng, chuyển 3D ⇄ 2D giữ nguyên khung nhìn.

---

# NHÂN · Slide 42

**42. Câu hỏi đã chuẩn bị** — Nhóm chuẩn bị sáu câu, em lướt nhanh ba câu:
**"Sao không dùng geofence 2D cho đơn giản?"** → Kịch bản TH2 thầy vừa thấy trong demo.
**"GPS trong nhà không đo được độ cao thì mô hình còn ý nghĩa gì?"** → Chuyển từ *xác minh độc lập* sang *đối chiếu khai báo*: vẫn phát hiện được sự không nhất quán, vẫn lưu bằng chứng 3D, và sẵn sàng nhận độ cao từ beacon hay khí áp kế.
**"Sao PostGIS mà không MongoDB?"** → MongoDB chỉ có chỉ mục 2dsphere trên mặt cầu 2 chiều, không lưu và không truy vấn được thành phần độ cao — tức là **không cài đặt được mô hình của đồ án**.

---

# VY · Slide 43

**43. Cảm ơn** — Phần trình bày của nhóm 1 đến đây là hết. Xin tóm trong một câu: **khi chuyển phép kiểm tra từ "điểm thuộc đa giác" sang "điểm thuộc khối", hệ thống sinh ra được một trạng thái mới — "đúng toà nhà, sai tầng" — mà mô hình hai chiều không có dữ liệu để phát hiện.** Nhóm cảm ơn thầy và các bạn, và xin lắng nghe câu hỏi ạ.

---

## Ai trả lời câu hỏi nào

| Câu hỏi | Người | Ý chính |
|---|---|---|
| Sao không dùng geofence 2D? | Vy | TH2 — chuyện thường ngày trong cao ốc, không phải trường hợp biên |
| GPS trong nhà không đo được độ cao? | Tín | Chuyển sang *đối chiếu khai báo*; vẫn lưu bằng chứng 3D |
| Sao PostGIS mà không MongoDB? | Nhân | 2dsphere không lưu được thành phần Z |
| δxy 25 m và δz 5 m lấy từ đâu? | Tín | δxy theo sai số GNSS khu nhà cao tầng; δz ≈ chiều cao một tầng (4,65 m) |
| Có chống được fake GPS không? | Nhân | **Không.** R2–R4 chỉ tăng chi phí gian lận; cần chứng thực phía thiết bị |
| Nhiều toà nhà thì hiệu năng? | Nhân | Tra khối theo quan hệ nhân viên–công ty–văn phòng, không có bước tìm kiếm không gian; GiST sẵn nếu cần tìm khối gần nhất |
| **14 hay 15 bảng?** | Nhân | 14 bảng của lược đồ; `spatial_ref_sys` là bảng hệ thống PostGIS, đã kiểm bằng `pg_class` |
| **Sao M6 chỉ đạt một phần?** | Vy | Trigger suy được cao độ nhưng chưa có giao diện vẽ khối MAP; hiện nạp bằng SQL |
| **QUAN_TRI khác QUAN_LY chỗ nào?** | Nhân | **Hiện chưa khác** — vai trò thứ ba đã khai báo nhưng chưa có chức năng riêng, đúng với M6 đạt một phần |

## Lưu ý khi trình bày

- **Không đọc slide** — slide có chữ rồi, người nói bổ sung *vì sao*.
- **Dừng 2 giây sau con số quan trọng**, nhất là "62,78 mét" và "13,5 tầng".
- Chuyển người: người trước nói **"xin mời bạn X"**, người sau bước lên rồi mới nói.
- Không biết thì: *"Phần đó nhóm chưa khảo sát kỹ, em xin ghi nhận ạ."* — **trung thực ăn điểm hơn đoán bừa**, và đúng tinh thần cách đồ án nêu hạn chế.
