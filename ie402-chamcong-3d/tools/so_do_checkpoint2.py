# -*- coding: utf-8 -*-
"""
Tập hợp toàn bộ sơ đồ của Checkpoint 2 và kết xuất ra HTML để render bằng Mermaid.

Các sơ đồ được viết bám sát mã nguồn đã cài đặt (server/src/routes/*.js,
db/schema.sql) chứ không phải bản thiết kế ban đầu, nên tài liệu và hệ thống khớp nhau.

    python tools/so_do_checkpoint2.py      -> scratch/so-do-cp2.html
"""
import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "scratch", "so-do-cp2.html")

# ---------------------------------------------------------------------------
# 1. MÔ HÌNH DỮ LIỆU MỨC KHÁI NIỆM — thực thể và quan hệ
# ---------------------------------------------------------------------------
ERD_KHAI_NIEM = """
erDiagram
    CONG_TY ||--o{ PHONG_BAN : "tổ chức thành"
    CONG_TY ||--o{ NHAN_VIEN : "tuyển dụng"
    CONG_TY ||--o{ VAN_PHONG : "thuê"
    TOA_NHA ||--o{ VAN_PHONG : "chứa"
    VAN_PHONG ||--|| KHU_VUC_CHAM_CONG : "được định nghĩa bởi"
    PHONG_BAN ||--o{ NHAN_VIEN : "gồm"
    NHAN_VIEN ||--|| NGUOI_DUNG : "có tài khoản"
    VAI_TRO ||--o{ NGUOI_DUNG : "phân quyền"
    NHAN_VIEN ||--o{ THIET_BI : "đăng ký"
    NHAN_VIEN ||--o{ PHAN_CA : "được xếp"
    CA_LAM_VIEC ||--o{ PHAN_CA : "áp dụng cho"
    NHAN_VIEN ||--o{ BAN_GHI_CHAM_CONG : "thực hiện"
    KHU_VUC_CHAM_CONG ||--o{ BAN_GHI_CHAM_CONG : "xác thực"
    THIET_BI ||--o{ BAN_GHI_CHAM_CONG : "ghi nhận từ"
    BAN_GHI_CHAM_CONG ||--o{ CANH_BAO_BAT_THUONG : "sinh ra"
    BAN_GHI_CHAM_CONG ||--o| DON_GIAI_TRINH : "được giải trình bởi"
    NHAN_VIEN ||--o{ DON_GIAI_TRINH : "gửi"

    TOA_NHA {
        string ten
        polygon footprint
        numeric cao_do_nen
        int so_tang
        numeric chieu_cao_tang
    }
    VAN_PHONG {
        string ten
        int tang_bat_dau
        int tang_ket_thuc
    }
    KHU_VUC_CHAM_CONG {
        polygon da_giac_nen "P"
        numeric z_min
        numeric z_max
        numeric dung_sai_ngang "delta xy"
        numeric dung_sai_dung "delta z"
    }
    BAN_GHI_CHAM_CONG {
        pointz vi_tri
        timestamptz thoi_diem
        string loai "VAO hoac RA"
        string trang_thai "HOP_LE NGHI_NGO NGOAI_VUNG"
        string nguon_cao_do "THIET_BI hoac KHAI_BAO"
    }
    CANH_BAO_BAT_THUONG {
        string ma_quy_tac "R1 R2 R3 R4"
        string muc_do
        bool da_xu_ly
    }
    DON_GIAI_TRINH {
        text ly_do
        string trang_thai "CHO_DUYET DA_DUYET TU_CHOI"
    }
"""

# ---------------------------------------------------------------------------
# 2. USE CASE — chỉ liệt kê chức năng ĐÃ cài đặt
# ---------------------------------------------------------------------------
USE_CASE = """
graph LR
    NV(("Nhân viên"))
    QL(("Quản lý"))
    QT(("Quản trị viên"))
    GPS[["Dịch vụ định vị<br/>của thiết bị"]]

    subgraph HT["Hệ thống chấm công định vị 3D"]
        direction TB
        UC1["UC1 · Đăng nhập<br/>(JWT, 3 vai trò)"]
        UC2["UC2 · Chấm công vào/ra"]
        UC3["UC3 · Kiểm tra bao hàm khối MAP"]
        UC4["UC4 · Phát hiện bất thường R1–R4"]
        UC5["UC5 · Xem lịch sử chấm công"]
        UC6["UC6 · Xem vị trí trên bản đồ 3D"]
        UC7["UC7 · Gửi đơn giải trình"]
        UC8["UC8 · Duyệt / từ chối đơn"]
        UC9["UC9 · Xem cảnh báo bất thường"]
        UC10["UC10 · Xem bảng điều khiển"]
        UC11["UC11 · Xuất báo cáo công"]
    end

    NV --> UC1
    NV --> UC2
    NV --> UC5
    NV --> UC6
    NV --> UC7
    QL --> UC8
    QL --> UC9
    QL --> UC10
    QL --> UC11
    QT --> UC8
    QT --> UC9
    QT --> UC10
    QT --> UC11
    UC2 -. include .-> UC3
    UC2 -. include .-> UC4
    UC2 --> GPS
    UC8 -. extend .-> UC5
"""

# ---------------------------------------------------------------------------
# 3. DFD MỨC NGỮ CẢNH (mức 0)
# ---------------------------------------------------------------------------
DFD0 = """
graph LR
    NV["Nhân viên"]
    QL["Quản lý /<br/>Quản trị viên"]
    TB["Dịch vụ định vị<br/>thiết bị"]
    HT(("0<br/>Hệ thống<br/>chấm công<br/>định vị 3D"))

    NV -->|"thông tin đăng nhập,<br/>yêu cầu chấm công, đơn giải trình"| HT
    HT -->|"kết quả xác thực vị trí,<br/>lịch sử, thông báo"| NV
    TB -->|"kinh độ, vĩ độ, cao độ,<br/>độ chính xác"| HT
    QL -->|"quyết định duyệt đơn,<br/>yêu cầu báo cáo"| HT
    HT -->|"cảnh báo bất thường,<br/>bảng điều khiển, báo cáo công"| QL
"""

# ---------------------------------------------------------------------------
# 4. DFD MỨC 1 — bám đúng các tuyến API đã cài đặt
# ---------------------------------------------------------------------------
DFD1 = """
graph TB
    NV["Nhân viên"]
    QL["Quản lý / Quản trị"]
    TB["Dịch vụ định vị"]

    P1(("1.0<br/>Xác thực<br/>người dùng"))
    P2(("2.0<br/>Thu nhận<br/>vị trí 3D"))
    P3(("3.0<br/>Kiểm tra<br/>bao hàm khối"))
    P4(("4.0<br/>Phát hiện<br/>bất thường"))
    P5(("5.0<br/>Xử lý<br/>giải trình"))
    P6(("6.0<br/>Tổng hợp<br/>báo cáo"))

    D1[("D1 · nguoi_dung, vai_tro")]
    D2[("D2 · khu_vuc_cham_cong")]
    D3[("D3 · ban_ghi_cham_cong")]
    D4[("D4 · canh_bao_bat_thuong")]
    D5[("D5 · don_giai_trinh")]
    D6[("D6 · nhan_vien, ca_lam_viec")]

    NV -->|"tên đăng nhập, mật khẩu"| P1
    P1 <-->|"đối chiếu bcrypt"| D1
    P1 -->|"JWT kèm vai trò"| NV

    NV -->|"POST /api/cham-cong"| P2
    TB -->|"lat, lon, alt, accuracy"| P2
    P2 -->|"điểm 3D đã chuẩn hoá"| P3
    P3 <-->|"đọc khối MAP"| D2
    P3 -->|"bản ghi kèm trạng thái"| D3
    P3 -->|"bản ghi cần kiểm"| P4
    P4 <-->|"lịch sử gần nhất"| D3
    P4 -->|"cảnh báo R1–R4"| D4

    NV -->|"POST /api/giai-trinh"| P5
    QL -->|"PUT /api/giai-trinh/:id"| P5
    P5 <-->|"đơn"| D5
    P5 -->|"cập nhật trạng thái"| D3
    P5 -->|"đóng cảnh báo"| D4

    D3 --> P6
    D6 --> P6
    P6 -->|"GET /api/bao-cao/cong"| QL
    D4 -->|"GET /api/canh-bao"| QL
"""

# ---------------------------------------------------------------------------
# 5. DFD MỨC 2 — bung tiến trình 3.0 Kiểm tra bao hàm khối
# ---------------------------------------------------------------------------
DFD2 = """
graph TB
    VAO["Điểm 3D + mã nhân viên"]
    P31(("3.1<br/>Tra khối MAP<br/>của nhân viên"))
    P32(("3.2<br/>Xác định<br/>nguồn cao độ"))
    P33(("3.3<br/>Kiểm tra<br/>điều kiện ngang"))
    P34(("3.4<br/>Kiểm tra<br/>dải cao độ"))
    P35(("3.5<br/>Kết luận<br/>trạng thái"))
    D2[("D2 · khu_vuc_cham_cong")]
    RA["HOP_LE / NGHI_NGO / NGOAI_VUNG"]

    VAO --> P31
    P31 <--> D2
    P31 -->|"P, z_min, z_max, δxy, δz"| P32
    P32 -->|"z đo được hoặc suy từ tầng"| P33
    P33 -->|"ST_DWithin trên geography"| P34
    P33 -->|"ngoài δxy"| P35
    P34 -->|"z trong / ngoài dải"| P35
    P35 --> RA
"""

# ---------------------------------------------------------------------------
# 6–9. SEQUENCE DIAGRAM
# ---------------------------------------------------------------------------
SD_DANG_NHAP = """
sequenceDiagram
    actor NV as Người dùng
    participant W as Giao diện web
    participant API as Express /api/dang-nhap
    participant DB as PostgreSQL

    NV->>W: Nhập tên đăng nhập + mật khẩu
    W->>API: POST /api/dang-nhap
    API->>DB: SELECT nguoi_dung JOIN vai_tro JOIN nhan_vien
    DB-->>API: mat_khau_bam, ten_vai_tro
    API->>API: bcrypt.compare(mật khẩu, mat_khau_bam)
    alt Đúng mật khẩu
        API->>API: Ký JWT (ma_nhan_vien, vai_tro), hạn 8 giờ
        API-->>W: 200 + token + thông tin người dùng
        W->>W: Lưu token, ẩn tab Quản lý nếu là nhân viên
    else Sai
        API-->>W: 401 Sai tên đăng nhập hoặc mật khẩu
    end
"""

SD_CHAM_CONG = """
sequenceDiagram
    actor NV as Nhân viên
    participant W as Giao diện web
    participant GPS as Geolocation API
    participant API as POST /api/cham-cong
    participant DB as PostgreSQL + PostGIS

    NV->>W: Bấm "Chấm công VÀO"
    W->>GPS: getCurrentPosition(enableHighAccuracy)
    GPS-->>W: lat, lon, alt, accuracy, altitudeAccuracy
    W->>W: alt không dùng được → lấy cao độ từ tầng khai báo
    W->>API: {loai, kinh_do, vi_do, cao_do, tang_khai_bao, thiết bị}

    API->>DB: BEGIN
    API->>DB: SELECT khối MAP của nhân viên
    DB-->>API: P, z_min, z_max, δxy, δz
    API->>DB: SELECT kiem_tra_bao_ham(khu_vuc, điểm, độ chính xác)
    DB-->>API: HOP_LE | NGHI_NGO | NGOAI_VUNG
    API->>DB: SELECT kiem_tra_r2(nhân viên, điểm, now())
    DB-->>API: có/không dịch chuyển bất khả thi
    API->>DB: INSERT ban_ghi_cham_cong

    alt Lệch khỏi dải cao độ
        API->>DB: INSERT canh_bao R1 (mức CAO)
    end
    alt Vận tốc vượt ngưỡng
        API->>DB: INSERT canh_bao R2 (mức CAO)
    end
    alt accuracy bất thường
        API->>DB: INSERT canh_bao R3
    end
    alt Thiết bị dùng chung
        API->>DB: INSERT canh_bao R4
    end

    API->>DB: COMMIT
    API-->>W: trạng thái, khoảng cách, lệch cao độ, danh sách cảnh báo
    W-->>NV: Hiển thị kết quả + vẽ điểm lên bản đồ 3D
"""

SD_GIAI_TRINH = """
sequenceDiagram
    actor NV as Nhân viên
    actor QL as Quản lý
    participant W as Giao diện web
    participant API as Express
    participant DB as PostgreSQL

    NV->>W: Bấm "Gửi giải trình" ở tab Lịch sử
    W->>API: POST /api/giai-trinh {ma_ban_ghi, ly_do}
    API->>DB: Kiểm tra bản ghi có thuộc về nhân viên không
    alt Không phải bản ghi của mình
        API-->>W: 403 Bản ghi không thuộc về bạn
    else Hợp lệ
        API->>DB: INSERT don_giai_trinh (CHO_DUYET)
        API-->>W: Đã gửi, chờ duyệt
    end

    QL->>W: Mở tab Quản lý
    W->>API: GET /api/giai-trinh?trang_thai=CHO_DUYET
    API->>DB: SELECT đơn kèm bản ghi và vị trí 3D
    DB-->>API: Danh sách
    API-->>W: Hiển thị bảng đơn chờ duyệt

    QL->>W: Bấm "Duyệt"
    W->>API: PUT /api/giai-trinh/:id {DA_DUYET}
    API->>DB: BEGIN
    API->>DB: UPDATE don_giai_trinh SET trang_thai, nguoi_duyet
    API->>DB: UPDATE ban_ghi_cham_cong SET trang_thai = 'HOP_LE'
    API->>DB: UPDATE canh_bao_bat_thuong SET da_xu_ly = true
    API->>DB: COMMIT
    API-->>W: Đã duyệt
    W->>API: Tải lại bảng điều khiển và báo cáo công
"""

SD_BAO_CAO = """
sequenceDiagram
    actor QL as Quản lý
    participant W as Giao diện web
    participant API as Express
    participant AUTH as Middleware phân quyền
    participant DB as PostgreSQL

    QL->>W: Mở tab Quản lý
    W->>API: GET /api/bao-cao/cong?thang=YYYY-MM
    API->>AUTH: canDangNhap + canCoVaiTro(QUAN_LY, QUAN_TRI)
    alt Vai trò không đủ
        AUTH-->>W: 403 Không đủ quyền
    else Đủ quyền
        AUTH->>API: Cho qua
        API->>DB: SELECT ... count FILTER theo trang_thai, GROUP BY nhân viên
        DB-->>API: Số lượt vào, hợp lệ, nghi ngờ, ngoài vùng, số ngày công
        API-->>W: JSON báo cáo
        W-->>QL: Hiển thị bảng báo cáo công
    end
"""

# ---------------------------------------------------------------------------
SO_DO = [
    ("01-mo-hinh-du-lieu", "Mô hình dữ liệu mức khái niệm", ERD_KHAI_NIEM),
    ("02-so-do-csdl", "Sơ đồ cơ sở dữ liệu (sinh từ CSDL đang chạy)", None),
    ("03-use-case", "Sơ đồ trường hợp sử dụng", USE_CASE),
    ("04-dfd-muc-0", "Sơ đồ luồng dữ liệu mức ngữ cảnh", DFD0),
    ("05-dfd-muc-1", "Sơ đồ luồng dữ liệu mức 1", DFD1),
    ("06-dfd-muc-2", "Sơ đồ luồng dữ liệu mức 2 — kiểm tra bao hàm khối", DFD2),
    ("07-sd-dang-nhap", "Sơ đồ trình tự — đăng nhập", SD_DANG_NHAP),
    ("08-sd-cham-cong", "Sơ đồ trình tự — chấm công", SD_CHAM_CONG),
    ("09-sd-giai-trinh", "Sơ đồ trình tự — gửi và duyệt đơn giải trình", SD_GIAI_TRINH),
    ("10-sd-bao-cao", "Sơ đồ trình tự — xuất báo cáo công", SD_BAO_CAO),
]


def main():
    csdl_path = os.path.join(ROOT, "scratch", "so-do-csdl.mmd")
    if not os.path.exists(csdl_path):
        raise SystemExit("Chạy tools/sinh_so_do_csdl.py trước để sinh sơ đồ CSDL.")
    csdl = io.open(csdl_path, encoding="utf-8").read()

    phan = []
    for i, (ten, tieu_de, ma) in enumerate(SO_DO, 1):
        noi_dung = csdl if ma is None else ma.strip()
        phan.append(
            '<div class="wrap"><h3>%d. %s</h3>'
            '<div class="mermaid" id="d%d">\n%s\n</div></div>' % (i, tieu_de, i, noi_dung))

    html = """<!DOCTYPE html><html><head><meta charset="utf-8">
<title>Sơ đồ Checkpoint 2</title>
<style>
 body{margin:0;background:#fff;font-family:"Segoe UI",Arial,sans-serif}
 .wrap{padding:20px;display:inline-block;vertical-align:top}
 h3{font-size:15px;margin:0 0 10px;color:#444}
 .mermaid{background:#fff}
</style>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
</head><body>
%s
<script>
 mermaid.initialize({startOnLoad:true, theme:'default', securityLevel:'loose',
   themeVariables:{fontFamily:'Segoe UI, Arial, sans-serif', fontSize:'15px'},
   sequence:{useMaxWidth:false}, flowchart:{useMaxWidth:false},
   er:{useMaxWidth:false, entityPadding:10, fontSize:13}});
</script>
</body></html>""" % ("\n".join(phan))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    io.open(OUT, "w", encoding="utf-8", newline="").write(html)
    print("Số sơ đồ:", len(SO_DO))
    print("->", OUT)
    for i, (ten, tieu_de, _) in enumerate(SO_DO, 1):
        print("   d%-2d %s" % (i, tieu_de))


if __name__ == "__main__":
    main()
