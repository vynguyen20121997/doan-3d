# -*- coding: utf-8 -*-
"""
Sinh báo cáo Checkpoint 2 — tập trung vào 5 nội dung được yêu cầu:

    1. Xác định thực thể, quan hệ và xây dựng mô hình dữ liệu
    2. Thiết kế database diagram
    3. Thiết kế use case diagram
    4. Thiết kế data flow diagram
    5. Thiết kế sequence diagram

Kế thừa style từ báo cáo Checkpoint 1 đã sinh, và lấy số liệu lược đồ trực tiếp
từ scratch/mo-ta-bang.json (do tools/sinh_so_do_csdl.py đọc từ CSDL đang chạy).

Thứ tự chạy:
    python tools/sinh_so_do_csdl.py      # đọc CSDL -> sơ đồ + mô tả bảng
    python tools/so_do_checkpoint2.py    # sinh HTML để render Mermaid
    (chụp ảnh các sơ đồ vào docs/cp2/)
    python tools/build_checkpoint2.py
"""
import copy
import json
import os

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Inches, Pt
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STYLE_SRC = os.path.join(ROOT, "CHECKPOINT1-Cham-cong-dinh-vi-3D.docx")
OUT = os.path.join(ROOT, "CHECKPOINT2-Cham-cong-dinh-vi-3D.docx")
CP2 = os.path.join(ROOT, "docs", "cp2")
MOTA = os.path.join(ROOT, "scratch", "mo-ta-bang.json")

MAX_W, MAX_H = 6.0, 7.5

THANH_VIEN = [
    ("23730217", "Nguyễn Hữu Tín"),
    ("23730177", "Nguyễn Minh Khôi"),
    ("23730226", "Nguyễn Tường Vy"),
    ("23730204", "Võ Thành Nhân"),
]

# ---------------------------------------------------------------------------
if not os.path.exists(STYLE_SRC):
    raise SystemExit("Cần có %s để kế thừa style. Chạy build_checkpoint1.py trước."
                     % os.path.basename(STYLE_SRC))
if not os.path.exists(MOTA):
    raise SystemExit("Thiếu %s — chạy tools/sinh_so_do_csdl.py trước." % MOTA)

with open(MOTA, encoding="utf-8") as f:
    LUOC_DO = json.load(f)

doc = Document(STYLE_SRC)

# numPr dùng để tắt đánh số cho Heading 1 kiểu "DANH MỤC HÌNH"
_no_num = None
for p in doc.paragraphs:
    if p.text.strip() == "DANH MỤC HÌNH":
        pPr = p._p.find(qn("w:pPr"))
        if pPr is not None:
            n = pPr.find(qn("w:numPr"))
            if n is not None:
                _no_num = copy.deepcopy(n)
        break

body = doc.element.body
for child in list(body):
    if child.tag != qn("w:sectPr"):
        body.remove(child)

C = WD_ALIGN_PARAGRAPH.CENTER
_cnt = {"c1": 0, "c2": 0, "c3": 0}


def para(text="", bold=False, italic=False, size=None, align=None, indent=None):
    p = doc.add_paragraph()
    if text:
        r = p.add_run(text)
        r.bold, r.italic = bold, italic
        if size:
            r.font.size = Pt(size)
    if align is not None:
        p.alignment = align
    if indent is not None:
        p.paragraph_format.first_line_indent = Inches(indent)
    return p


def body_text(t):
    return para(t, align=WD_ALIGN_PARAGRAPH.JUSTIFY, indent=0.3)


def _tat_so(p):
    if _no_num is None:
        return
    pPr = p._p.get_or_add_pPr()
    cu = pPr.find(qn("w:numPr"))
    if cu is not None:
        pPr.remove(cu)
    pPr.insert(0, copy.deepcopy(_no_num))


def h1(text, numbered=True):
    if numbered:
        _cnt["c1"] += 1
        _cnt["c2"] = _cnt["c3"] = 0
        text = "Chương %d: %s" % (_cnt["c1"], text)
    p = doc.add_paragraph(text, style="Heading 1")
    _tat_so(p)
    return p


def h2(text):
    _cnt["c2"] += 1
    _cnt["c3"] = 0
    p = doc.add_paragraph("%d.%d\t%s" % (_cnt["c1"], _cnt["c2"], text), style="Heading 2")
    _tat_so(p)
    return p


def h3(text):
    _cnt["c3"] += 1
    p = doc.add_paragraph("%d.%d.%d\t%s" % (_cnt["c1"], _cnt["c2"], _cnt["c3"], text),
                          style="Heading 3")
    _tat_so(p)
    return p


def bullets(items):
    for it in items:
        doc.add_paragraph(it, style="List Bullet")


def mono(text):
    for line in text.split("\n"):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.left_indent = Inches(0.3)
        r = p.add_run(line if line else " ")
        r.font.name = "Consolas"
        r.font.size = Pt(9)
    para()


def table(headers, rows, widths=None, caption=None):
    if caption:
        c = para(caption, align=C, size=10)
        c.runs[0].italic = True
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    for i, htxt in enumerate(headers):
        cell = t.rows[0].cells[i]
        cell.text = ""
        r = cell.paragraphs[0].add_run(htxt)
        r.bold = True
        r.font.size = Pt(9.5)
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            r = cells[i].paragraphs[0].add_run(str(v))
            r.font.size = Pt(9.5)
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Inches(w)
    para()
    return t


def image(ten, caption=None, max_h=MAX_H):
    path = os.path.join(CP2, ten)
    if not os.path.exists(path):
        para("[thiếu ảnh: %s]" % ten, italic=True)
        return
    w_px, h_px = Image.open(path).size
    w_in = MAX_W
    h_in = w_in * h_px / w_px
    if h_in > max_h:
        h_in = max_h
        w_in = h_in * w_px / h_px
    p = doc.add_paragraph()
    p.alignment = C
    p.add_run().add_picture(path, width=Inches(w_in))
    if caption:
        c = para(caption, align=C, size=9.5)
        c.runs[0].italic = True
    para()


def page_break():
    doc.add_page_break()


# ===========================================================================
#  BÌA
# ===========================================================================
para("ĐẠI HỌC QUỐC GIA THÀNH PHỐ HỒ CHÍ MINH", align=C, bold=True, size=13)
para("TRƯỜNG ĐẠI HỌC CÔNG NGHỆ THÔNG TIN", align=C, bold=True, size=13)
para("TRUNG TÂM PHÁT TRIỂN CNTT", align=C, bold=True, size=13)
para(); para(); para()
para("BÁO CÁO CHECKPOINT 2", align=C, bold=True, size=16)
para("HỆ THỐNG THÔNG TIN ĐỊA LÝ 3 CHIỀU", align=C, bold=True, size=14)
para()
para("ĐỀ TÀI:", align=C, bold=True, size=13)
para("XÂY DỰNG HỆ THỐNG CHẤM CÔNG ĐỊNH VỊ 3D", align=C, bold=True, size=17)
para("THEO MÔ HÌNH KHỐI KHÔNG GIAN PHÂN TẦNG", align=C, bold=True, size=17)
para(); para()
para("Nội dung: mô hình dữ liệu · database diagram · use case diagram", align=C, italic=True, size=12)
para("data flow diagram · sequence diagram", align=C, italic=True, size=12)
para(); para()
para("GVHD: ThS. PHAN THANH VŨ", align=C, bold=True, size=13)
para("Nhóm 1", align=C, bold=True, size=13)
para("Sinh viên thực hiện:", align=C, bold=True, size=13)
for mssv, ten in THANH_VIEN:
    para("%s\t%s" % (mssv, ten), align=C, size=13)
para(); para(); para()
para("TP. Hồ Chí Minh, tháng 9 năm 2026", align=C, italic=True, size=13)
page_break()

# ===========================================================================
#  DANH MỤC
# ===========================================================================
h1("DANH MỤC HÌNH", numbered=False)
for d in [
    "Hình 1.1\tMô hình dữ liệu mức khái niệm",
    "Hình 2.1\tSơ đồ cơ sở dữ liệu sinh trực tiếp từ CSDL đang chạy",
    "Hình 3.1\tSơ đồ trường hợp sử dụng",
    "Hình 4.1\tSơ đồ luồng dữ liệu mức ngữ cảnh",
    "Hình 4.2\tSơ đồ luồng dữ liệu mức 1",
    "Hình 4.3\tSơ đồ luồng dữ liệu mức 2 — kiểm tra bao hàm khối",
    "Hình 5.1\tSơ đồ trình tự — đăng nhập",
    "Hình 5.2\tSơ đồ trình tự — chấm công",
    "Hình 5.3\tSơ đồ trình tự — gửi và duyệt đơn giải trình",
    "Hình 5.4\tSơ đồ trình tự — xuất báo cáo công",
]:
    para(d)

h1("DANH MỤC BẢNG", numbered=False)
for d in [
    "Bảng 1.1\tDanh sách thực thể và ý nghĩa",
    "Bảng 1.2\tCác quan hệ và bản số",
    "Bảng 1.3\tMô hình quan hệ sau khi chuyển đổi",
    "Bảng 2.1\tThống kê lược đồ vật lý",
    "Bảng 2.2\tRàng buộc duy nhất",
    "Bảng 2.3\tChỉ mục",
    "Bảng 2.4\tHàm nghiệp vụ trong cơ sở dữ liệu",
    "Bảng 3.1\tĐặc tả use case UC2 — Chấm công",
    "Bảng 3.2\tĐặc tả use case UC8 — Duyệt đơn giải trình",
    "Bảng 4.1\tĐặc tả các tiến trình trong DFD mức 1",
    "Bảng 4.2\tCác kho dữ liệu",
]:
    para(d)
page_break()

# ===========================================================================
#  CHƯƠNG 1 — MÔ HÌNH DỮ LIỆU
# ===========================================================================
h1("XÁC ĐỊNH THỰC THỂ, QUAN HỆ VÀ XÂY DỰNG MÔ HÌNH DỮ LIỆU")

h2("Phương pháp xác định thực thể")
body_text(
    "Thực thể được rút ra từ các danh từ nghiệp vụ xuất hiện trong phát biểu bài toán, "
    "sau đó loại bỏ những danh từ chỉ là thuộc tính hoặc đồng nghĩa. Bài toán đặt ra ba "
    "nhóm dữ liệu cần lưu: nhóm tổ chức (ai làm việc cho ai), nhóm không gian (khối "
    "không gian nào được coi là hợp lệ) và nhóm nghiệp vụ chấm công (ai chấm công lúc "
    "nào, ở đâu, kết quả ra sao).")
body_text(
    "Điểm khác biệt so với một hệ thống chấm công thông thường nằm ở nhóm không gian: "
    "ngoài toà nhà và văn phòng, mô hình còn cần một thực thể riêng mô tả khối không "
    "gian dùng để xác thực — chính là khối MAP. Tách khối này thành thực thể độc lập "
    "thay vì gộp vào văn phòng cho phép một văn phòng đổi dung sai hoặc vô hiệu hoá "
    "khối mà không ảnh hưởng dữ liệu tổ chức.")

h2("Danh sách thực thể")
table(
    ["Nhóm", "Thực thể", "Ý nghĩa nghiệp vụ"],
    [
        ["Tổ chức", "CONG_TY", "Doanh nghiệp thuê văn phòng và sử dụng hệ thống"],
        ["Tổ chức", "PHONG_BAN", "Đơn vị trực thuộc công ty"],
        ["Tổ chức", "NHAN_VIEN", "Người lao động thực hiện chấm công"],
        ["Tài khoản", "NGUOI_DUNG", "Tài khoản đăng nhập gắn với một nhân viên"],
        ["Tài khoản", "VAI_TRO", "Nhân viên, quản lý hoặc quản trị viên"],
        ["Tài khoản", "THIET_BI", "Thiết bị đã dùng để chấm công, phục vụ quy tắc R4"],
        ["Không gian", "TOA_NHA", "Công trình: footprint, cao độ nền, số tầng, chiều cao tầng"],
        ["Không gian", "VAN_PHONG", "Phần sàn một công ty thuê, xác định bởi dải tầng"],
        ["Không gian", "KHU_VUC_CHAM_CONG", "Hiện thực của khối MAP dùng để xác thực vị trí"],
        ["Ca làm việc", "CA_LAM_VIEC", "Khung giờ vào/ra và số phút cho phép đi trễ"],
        ["Ca làm việc", "PHAN_CA", "Gán ca cho nhân viên theo từng ngày"],
        ["Chấm công", "BAN_GHI_CHAM_CONG", "Một lần chấm công kèm vị trí ba chiều và trạng thái"],
        ["Chấm công", "CANH_BAO_BAT_THUONG", "Kết quả áp bốn quy tắc R1–R4 lên bản ghi"],
        ["Chấm công", "DON_GIAI_TRINH", "Đơn nhân viên gửi khi bản ghi bị từ chối hoặc nghi ngờ"],
    ],
    widths=[0.9, 1.9, 3.3],
    caption="Bảng 1.1 — Danh sách thực thể và ý nghĩa")

h2("Quan hệ giữa các thực thể")
table(
    ["Quan hệ", "Bản số", "Giải thích"],
    [
        ["TOA_NHA – VAN_PHONG", "1 – N",
         "Một toà nhà chứa nhiều văn phòng của nhiều công ty khác nhau"],
        ["CONG_TY – VAN_PHONG", "1 – N", "Một công ty có thể thuê nhiều văn phòng"],
        ["VAN_PHONG – KHU_VUC_CHAM_CONG", "1 – 1",
         "Mỗi văn phòng ứng với đúng một khối MAP; tách riêng để đổi dung sai độc lập"],
        ["CONG_TY – PHONG_BAN", "1 – N", "Một công ty có nhiều phòng ban"],
        ["PHONG_BAN – NHAN_VIEN", "1 – N", "Một phòng ban gồm nhiều nhân viên"],
        ["NHAN_VIEN – NGUOI_DUNG", "1 – 1", "Mỗi nhân viên có đúng một tài khoản"],
        ["VAI_TRO – NGUOI_DUNG", "1 – N", "Một vai trò gán cho nhiều tài khoản"],
        ["NHAN_VIEN – THIET_BI", "1 – N", "Một nhân viên có thể đăng ký nhiều thiết bị"],
        ["NHAN_VIEN – PHAN_CA", "1 – N", "Mỗi ngày một nhân viên được xếp một ca"],
        ["CA_LAM_VIEC – PHAN_CA", "1 – N", "Một ca áp dụng cho nhiều lượt phân ca"],
        ["NHAN_VIEN – BAN_GHI_CHAM_CONG", "1 – N", "Một nhân viên có nhiều lần chấm công"],
        ["KHU_VUC_CHAM_CONG – BAN_GHI_CHAM_CONG", "1 – N",
         "Một khối MAP xác thực nhiều bản ghi"],
        ["BAN_GHI_CHAM_CONG – CANH_BAO_BAT_THUONG", "1 – N",
         "Một bản ghi có thể vi phạm nhiều quy tắc cùng lúc"],
        ["BAN_GHI_CHAM_CONG – DON_GIAI_TRINH", "1 – 0..1",
         "Mỗi bản ghi có tối đa một đơn giải trình"],
    ],
    widths=[2.3, 0.75, 3.05],
    caption="Bảng 1.2 — Các quan hệ và bản số")

image("01-mo-hinh-du-lieu.png",
      "Hình 1.1 — Mô hình dữ liệu mức khái niệm: 14 thực thể chia ba nhóm tổ chức, "
      "không gian và nghiệp vụ chấm công")

h2("Chuyển sang mô hình quan hệ")
body_text(
    "Mỗi thực thể trở thành một quan hệ. Quan hệ 1–N được cài đặt bằng cách đặt khoá "
    "ngoại ở phía nhiều; quan hệ 1–1 giữa VAN_PHONG và KHU_VUC_CHAM_CONG được cài đặt "
    "bằng khoá ngoại kèm ràng buộc duy nhất để bảo đảm không có hai khối cho cùng một "
    "văn phòng.")
mono(
    "CONG_TY(ma_cong_ty, ten_cong_ty, ma_so_thue)\n"
    "PHONG_BAN(ma_phong_ban, ma_cong_ty*, ten_phong_ban)\n"
    "TOA_NHA(ma_toa_nha, ten, dia_chi, footprint, cao_do_nen, so_tang,\n"
    "        chieu_cao_tang, nguon_du_lieu)\n"
    "VAN_PHONG(ma_van_phong, ma_cong_ty*, ma_toa_nha*, ten,\n"
    "          tang_bat_dau, tang_ket_thuc)\n"
    "KHU_VUC_CHAM_CONG(ma_khu_vuc, ma_van_phong* UNIQUE, da_giac_nen,\n"
    "                  z_min, z_max, dung_sai_ngang, dung_sai_dung, dang_hieu_luc)\n"
    "NHAN_VIEN(ma_nhan_vien, ma_cong_ty*, ma_phong_ban*, ho_ten, email,\n"
    "          ngay_vao_lam, dang_lam_viec)\n"
    "VAI_TRO(ma_vai_tro, ten_vai_tro)\n"
    "NGUOI_DUNG(ma_nguoi_dung, ma_nhan_vien* UNIQUE, ma_vai_tro*,\n"
    "           ten_dang_nhap UNIQUE, mat_khau_bam)\n"
    "THIET_BI(ma_thiet_bi, ma_nhan_vien*, dinh_danh_thiet_bi, he_dieu_hanh,\n"
    "         duoc_tin_cay)\n"
    "CA_LAM_VIEC(ma_ca, ten_ca, gio_vao, gio_ra, tre_toi_da_phut)\n"
    "PHAN_CA(ma_phan_ca, ma_nhan_vien*, ma_ca*, ngay_lam_viec)\n"
    "BAN_GHI_CHAM_CONG(ma_ban_ghi, ma_nhan_vien*, ma_khu_vuc*, ma_thiet_bi*,\n"
    "                  thoi_diem, loai, vi_tri, do_chinh_xac_ngang,\n"
    "                  do_chinh_xac_dung, nguon_cao_do, tang_khai_bao, trang_thai)\n"
    "CANH_BAO_BAT_THUONG(ma_canh_bao, ma_ban_ghi*, ma_quy_tac, muc_do,\n"
    "                    mo_ta, da_xu_ly)\n"
    "DON_GIAI_TRINH(ma_don, ma_nhan_vien*, ma_ban_ghi* UNIQUE, ly_do,\n"
    "               trang_thai, nguoi_duyet*, thoi_diem_gui)")
para("Ghi chú: gạch chân là khoá chính, dấu * là khoá ngoại.", italic=True, size=10)

h3("Kiểm tra chuẩn hoá")
bullets([
    "Dạng chuẩn 1 (1NF): mọi thuộc tính đều nguyên tố. Riêng footprint và vi_tri là "
    "kiểu hình học của PostGIS — đây vẫn là giá trị nguyên tố ở mức nghiệp vụ vì hệ "
    "thống không bao giờ truy vấn vào từng đỉnh riêng lẻ mà luôn dùng cả hình.",
    "Dạng chuẩn 2 (2NF): mọi quan hệ đều dùng khoá chính đơn (mã tự tăng) nên không "
    "tồn tại phụ thuộc hàm bộ phận.",
    "Dạng chuẩn 3 (3NF): không có thuộc tính nào phụ thuộc bắc cầu vào khoá. Ví dụ "
    "tên công ty chỉ nằm ở CONG_TY, các bảng khác tham chiếu bằng khoá ngoại.",
    "Ngoại lệ có chủ đích: z_min và z_max của KHU_VUC_CHAM_CONG là thuộc tính dẫn "
    "xuất từ cao độ nền và dải tầng, về lý thuyết vi phạm 3NF. Hệ thống vẫn lưu trữ "
    "chúng vì phép xác thực chấm công được gọi rất thường xuyên và cần so sánh trực "
    "tiếp; tính nhất quán được bảo đảm bằng trigger tg_khu_vuc_cao_do tự suy lại giá "
    "trị mỗi khi thêm hoặc sửa.",
])
page_break()

# ===========================================================================
#  CHƯƠNG 2 — DATABASE DIAGRAM
# ===========================================================================
h1("THIẾT KẾ DATABASE DIAGRAM")

h2("Cách xây dựng sơ đồ")
body_text(
    "Sơ đồ cơ sở dữ liệu trong chương này không vẽ tay mà được sinh tự động bằng script "
    "tools/sinh_so_do_csdl.py. Script kết nối vào cơ sở dữ liệu đang chạy, đọc các bảng "
    "hệ thống pg_class, pg_attribute, pg_constraint và pg_indexes để lấy danh sách "
    "bảng, cột, kiểu dữ liệu, khoá chính, khoá ngoại, ràng buộc duy nhất và chỉ mục, "
    "rồi kết xuất ra mã Mermaid.")
body_text(
    "Cách làm này bảo đảm sơ đồ luôn khớp với hệ thống thật: khi lược đồ thay đổi, chỉ "
    "cần chạy lại script là sơ đồ trong báo cáo được cập nhật, không có nguy cơ tài "
    "liệu và mã nguồn nói hai điều khác nhau.")
body_text(
    "Lưu ý khi đọc kết quả: PostGIS tự tạo thêm bảng spatial_ref_sys để lưu danh mục "
    "hệ quy chiếu toạ độ. Bảng này thuộc về phần mở rộng chứ không thuộc lược đồ của đề "
    "tài nên đã được loại khỏi sơ đồ và khỏi các con số thống kê.")

bang = LUOC_DO["bang"]
so_cot = sum(len(v) for v in bang.values())
table(
    ["Hạng mục", "Số lượng"],
    [
        ["Bảng dữ liệu của đề tài", len(bang)],
        ["Tổng số cột", so_cot],
        ["Khoá ngoại", len(LUOC_DO["khoa_ngoai"])],
        ["Ràng buộc duy nhất", len(LUOC_DO["duy_nhat"])],
        ["Chỉ mục (không tính khoá chính)", len(LUOC_DO["chi_muc"])],
        ["Hàm nghiệp vụ và trigger", len(LUOC_DO["ham"])],
    ],
    widths=[3.4, 1.3],
    caption="Bảng 2.1 — Thống kê lược đồ vật lý (đọc từ CSDL đang chạy)")

image("02-so-do-csdl.png",
      "Hình 2.1 — Sơ đồ cơ sở dữ liệu: %d bảng, %d cột, %d khoá ngoại, kèm kiểu dữ "
      "liệu thật của từng cột" % (len(bang), so_cot, len(LUOC_DO["khoa_ngoai"])))

h2("Kiểu dữ liệu không gian")
body_text(
    "Hai cột quyết định tính chất ba chiều của hệ thống đều dùng kiểu hình học của "
    "PostGIS với hệ quy chiếu WGS84 (mã EPSG 4326):")
table(
    ["Cột", "Kiểu", "Vai trò"],
    [
        ["toa_nha.footprint", "GEOMETRY(Polygon, 4326)", "Hình chiếu bằng của công trình"],
        ["khu_vuc_cham_cong.da_giac_nen", "GEOMETRY(Polygon, 4326)",
         "Đa giác nền P của khối MAP"],
        ["ban_ghi_cham_cong.vi_tri", "GEOMETRY(PointZ, 4326)",
         "Điểm ba chiều do thiết bị báo về; thành phần Z chính là cao độ dùng để "
         "phân biệt tầng"],
    ],
    widths=[1.9, 1.8, 2.4])
body_text(
    "Vì EPSG:4326 dùng đơn vị độ, mọi phép tính khoảng cách đều phải ép sang kiểu "
    "geography để nhận kết quả bằng mét — đây là lý do hàm kiem_tra_bao_ham dùng "
    "ST_DWithin trên geography thay vì so sánh trực tiếp trên toạ độ độ.")

h2("Ràng buộc toàn vẹn")
table(
    ["Bảng", "Ràng buộc"],
    [[r["bang"], r["dinh_nghia"]] for r in LUOC_DO["duy_nhat"]],
    widths=[1.7, 4.4],
    caption="Bảng 2.2 — Ràng buộc duy nhất")
body_text(
    "Đáng chú ý là ràng buộc duy nhất trên phan_ca(ma_nhan_vien, ngay_lam_viec) — bảo "
    "đảm mỗi nhân viên chỉ được xếp một ca mỗi ngày, và trên "
    "thiet_bi(ma_nhan_vien, dinh_danh_thiet_bi) — cho phép dùng lệnh ghi có kiểm tra "
    "trùng khi một thiết bị chấm công nhiều lần.")

h2("Chỉ mục")
table(
    ["Bảng", "Chỉ mục", "Định nghĩa"],
    [[r["bang"], r["ten"],
      r["dinh_nghia"].split(" ON ")[-1].replace("public.", "")]
     for r in LUOC_DO["chi_muc"]],
    widths=[1.5, 1.9, 2.7],
    caption="Bảng 2.3 — Chỉ mục")
body_text(
    "Hai chỉ mục GIST trên cột hình học là bắt buộc để truy vấn không gian không phải "
    "quét toàn bảng. Chỉ mục idx_bgcc_nv_thoi_diem phục vụ quy tắc R2, vốn luôn cần "
    "lấy bản ghi gần nhất của một nhân viên.")

h2("Hàm nghiệp vụ đặt trong cơ sở dữ liệu")
table(
    ["Hàm", "Tham số", "Trả về"],
    [[r["ten"], r["tham_so"][:60], r["tra_ve"]] for r in LUOC_DO["ham"]],
    widths=[1.6, 3.0, 1.5],
    caption="Bảng 2.4 — Hàm nghiệp vụ trong cơ sở dữ liệu")
body_text(
    "Toàn bộ logic không gian được đặt trong cơ sở dữ liệu thay vì ở tầng ứng dụng. "
    "Nhờ vậy chỉ tồn tại một bản cài đặt duy nhất, đặt ngay cạnh dữ liệu; máy chủ chỉ "
    "việc gọi hàm và nhận kết quả.")
page_break()

# ===========================================================================
#  CHƯƠNG 3 — USE CASE
# ===========================================================================
h1("THIẾT KẾ USE CASE DIAGRAM")

h2("Tác nhân")
table(
    ["Tác nhân", "Mô tả", "Quyền chính"],
    [
        ["Nhân viên", "Người lao động thuộc một văn phòng",
         "Chấm công, xem lịch sử và bản đồ 3D, gửi đơn giải trình"],
        ["Quản lý", "Người phụ trách theo dõi công của phòng ban",
         "Xem cảnh báo, duyệt đơn, xem bảng điều khiển và báo cáo"],
        ["Quản trị viên", "Người vận hành hệ thống",
         "Toàn bộ quyền của quản lý, thêm quản trị danh mục"],
        ["Dịch vụ định vị thiết bị", "Tác nhân hệ thống (không phải người)",
         "Cung cấp kinh độ, vĩ độ, cao độ và độ chính xác"],
    ],
    widths=[1.3, 2.1, 2.7])

image("03-use-case.png",
      "Hình 3.1 — Sơ đồ trường hợp sử dụng; sơ đồ chỉ liệt kê các chức năng đã được "
      "cài đặt trong hệ thống")

body_text(
    "Hai quan hệ include trong sơ đồ phản ánh đúng cách cài đặt: mỗi lần chấm công "
    "(UC2) bắt buộc gọi kiểm tra bao hàm khối (UC3) rồi áp bốn quy tắc phát hiện bất "
    "thường (UC4), không có đường đi nào bỏ qua hai bước này.")

h2("Đặc tả use case chính")
table(
    ["Mục", "Nội dung"],
    [
        ["Tên", "UC2 — Chấm công vào/ra"],
        ["Tác nhân", "Nhân viên; Dịch vụ định vị thiết bị"],
        ["Tiền điều kiện",
         "Đã đăng nhập, có khối MAP gán cho văn phòng của nhân viên"],
        ["Luồng chính",
         "1. Nhân viên mở màn hình chấm công.\n"
         "2. Hệ thống yêu cầu vị trí từ thiết bị.\n"
         "3. Thiết bị trả kinh độ, vĩ độ, cao độ, độ chính xác.\n"
         "4. Nhân viên xác nhận tầng đang làm việc.\n"
         "5. Hệ thống gọi kiem_tra_bao_ham để xác thực vị trí.\n"
         "6. Hệ thống áp bốn quy tắc R1–R4.\n"
         "7. Ghi bản ghi và cảnh báo trong một giao dịch, trả kết quả."],
        ["Luồng thay thế 3a",
         "Thiết bị không trả cao độ dùng được → lấy cao độ suy từ tầng khai báo, "
         "đánh dấu nguồn cao độ là KHAI_BAO"],
        ["Luồng ngoại lệ 5a",
         "Điểm nằm ngoài dung sai ngang → trạng thái NGOAI_VUNG, đề nghị gửi giải trình"],
        ["Luồng ngoại lệ 5b",
         "Trong vùng ngang nhưng lệch dải cao độ → trạng thái NGHI_NGO, sinh cảnh báo R1"],
        ["Hậu điều kiện", "Có một bản ghi chấm công mới kèm trạng thái xác định"],
    ],
    widths=[1.3, 4.8],
    caption="Bảng 3.1 — Đặc tả use case UC2 — Chấm công")

table(
    ["Mục", "Nội dung"],
    [
        ["Tên", "UC8 — Duyệt / từ chối đơn giải trình"],
        ["Tác nhân", "Quản lý hoặc Quản trị viên"],
        ["Tiền điều kiện", "Tồn tại đơn ở trạng thái CHO_DUYET"],
        ["Luồng chính",
         "1. Quản lý mở tab Quản lý, hệ thống liệt kê đơn chờ duyệt kèm vị trí 3D.\n"
         "2. Quản lý chọn Duyệt hoặc Từ chối.\n"
         "3. Nếu duyệt: cập nhật đơn sang DA_DUYET, chuyển bản ghi sang HOP_LE và "
         "đóng toàn bộ cảnh báo của bản ghi đó, tất cả trong một giao dịch.\n"
         "4. Bảng điều khiển và báo cáo công được tải lại."],
        ["Luồng ngoại lệ 1a",
         "Người gọi không có vai trò quản lý → hệ thống trả HTTP 403"],
        ["Luồng ngoại lệ 2a",
         "Đơn đã được xử lý trước đó → hệ thống báo không tìm thấy đơn đang chờ duyệt"],
        ["Hậu điều kiện",
         "Trạng thái đơn, bản ghi và cảnh báo nhất quán với nhau"],
    ],
    widths=[1.3, 4.8],
    caption="Bảng 3.2 — Đặc tả use case UC8 — Duyệt đơn giải trình")
page_break()

# ===========================================================================
#  CHƯƠNG 4 — DFD
# ===========================================================================
h1("THIẾT KẾ DATA FLOW DIAGRAM")

h2("Sơ đồ mức ngữ cảnh")
body_text(
    "Ở mức ngữ cảnh, toàn bộ hệ thống được xem như một tiến trình duy nhất trao đổi dữ "
    "liệu với ba tác nhân ngoài. Điểm cần lưu ý là dịch vụ định vị của thiết bị được "
    "tách thành một tác nhân riêng chứ không gộp vào nhân viên, vì dữ liệu vị trí do "
    "phần cứng sinh ra chứ không do người dùng nhập — đây cũng là lý do hệ thống phải "
    "đánh giá độ tin cậy của dữ liệu này bằng các quy tắc R3.")
image("04-dfd-muc-0.png", "Hình 4.1 — Sơ đồ luồng dữ liệu mức ngữ cảnh")

h2("Sơ đồ mức 1")
image("05-dfd-muc-1.png", "Hình 4.2 — Sơ đồ luồng dữ liệu mức 1")
table(
    ["Tiến trình", "Đầu vào", "Xử lý", "Đầu ra"],
    [
        ["1.0 Xác thực người dùng", "Tên đăng nhập, mật khẩu",
         "Đối chiếu chuỗi băm bcrypt, ký JWT kèm vai trò", "Token phiên làm việc"],
        ["2.0 Thu nhận vị trí 3D", "Yêu cầu chấm công, dữ liệu định vị",
         "Chuẩn hoá toạ độ, xác định nguồn cao độ", "Điểm ba chiều kèm độ chính xác"],
        ["3.0 Kiểm tra bao hàm khối", "Điểm 3D, khối MAP",
         "Gọi kiem_tra_bao_ham: kiểm tra ngang rồi kiểm tra dải cao độ",
         "Một trong ba trạng thái"],
        ["4.0 Phát hiện bất thường", "Bản ghi mới, lịch sử gần nhất",
         "Áp bốn quy tắc R1–R4", "Cảnh báo kèm mức độ"],
        ["5.0 Xử lý giải trình", "Đơn của nhân viên, quyết định của quản lý",
         "Cập nhật đơn, bản ghi và cảnh báo trong một giao dịch", "Trạng thái mới"],
        ["6.0 Tổng hợp báo cáo", "Bản ghi chấm công, dữ liệu nhân sự",
         "Đếm theo trạng thái, gom nhóm theo nhân viên và tháng", "Báo cáo công"],
    ],
    widths=[1.3, 1.5, 1.9, 1.3],
    caption="Bảng 4.1 — Đặc tả các tiến trình trong DFD mức 1")

table(
    ["Kho", "Bảng tương ứng", "Nội dung"],
    [
        ["D1", "nguoi_dung, vai_tro", "Tài khoản và phân quyền"],
        ["D2", "khu_vuc_cham_cong", "Khối MAP: đa giác nền, dải cao độ, dung sai"],
        ["D3", "ban_ghi_cham_cong", "Bản ghi chấm công kèm vị trí ba chiều"],
        ["D4", "canh_bao_bat_thuong", "Cảnh báo sinh từ bốn quy tắc"],
        ["D5", "don_giai_trinh", "Đơn giải trình và trạng thái duyệt"],
        ["D6", "nhan_vien, ca_lam_viec, phan_ca", "Dữ liệu nhân sự và ca làm việc"],
    ],
    widths=[0.6, 2.2, 3.3],
    caption="Bảng 4.2 — Các kho dữ liệu")

h2("Sơ đồ mức 2 — bung tiến trình kiểm tra bao hàm khối")
body_text(
    "Tiến trình 3.0 là phần lõi của đề tài nên được bung tiếp xuống mức 2. Sơ đồ cho "
    "thấy rõ phép kiểm tra được tách thành hai điều kiện độc lập: điều kiện ngang quyết "
    "định có nằm trong phạm vi toà nhà hay không, điều kiện đứng quyết định có đúng dải "
    "tầng hay không. Chính việc tách này tạo ra trạng thái trung gian NGHI_NGO — thoả "
    "điều kiện ngang nhưng trượt điều kiện đứng — là trạng thái mà hàng rào hai chiều "
    "không thể sinh ra.")
image("06-dfd-muc-2.png",
      "Hình 4.3 — Sơ đồ luồng dữ liệu mức 2 của tiến trình kiểm tra bao hàm khối")
page_break()

# ===========================================================================
#  CHƯƠNG 5 — SEQUENCE
# ===========================================================================
h1("THIẾT KẾ SEQUENCE DIAGRAM")
body_text(
    "Bốn sơ đồ trình tự dưới đây mô tả các kịch bản chính của hệ thống. Các sơ đồ được "
    "vẽ theo đúng mã nguồn đã cài đặt trong server/src/routes, nên tên điểm cuối, thứ "
    "tự lời gọi và phạm vi giao dịch trên sơ đồ trùng khớp với hệ thống đang chạy.")

h2("Đăng nhập")
image("07-sd-dang-nhap.png", "Hình 5.1 — Sơ đồ trình tự đăng nhập")
body_text(
    "Mật khẩu không bao giờ được so sánh trực tiếp: hệ thống lấy chuỗi băm bcrypt từ "
    "cơ sở dữ liệu rồi dùng hàm so khớp. Token trả về chứa mã nhân viên và vai trò, "
    "nhờ đó các yêu cầu sau không cần truy vấn lại bảng phân quyền.")

h2("Chấm công")
image("08-sd-cham-cong.png", "Hình 5.2 — Sơ đồ trình tự chấm công")
body_text(
    "Đây là sơ đồ quan trọng nhất. Ba điểm cần chú ý: thứ nhất, giao diện tự quyết định "
    "dùng cao độ đo được hay cao độ suy từ tầng khai báo tuỳ theo chất lượng tín hiệu; "
    "thứ hai, máy chủ không tự tính toán không gian mà gọi hàm trong cơ sở dữ liệu; thứ "
    "ba, toàn bộ việc ghi bản ghi và ghi cảnh báo nằm giữa BEGIN và COMMIT nên không "
    "thể xảy ra tình trạng có bản ghi mà thiếu cảnh báo hoặc ngược lại.")

h2("Gửi và duyệt đơn giải trình")
image("09-sd-giai-trinh.png", "Hình 5.3 — Sơ đồ trình tự gửi và duyệt đơn giải trình")
body_text(
    "Sơ đồ thể hiện hai tác nhân trên cùng một dòng thời gian. Khi quản lý duyệt đơn, "
    "ba bảng được cập nhật cùng lúc trong một giao dịch: đơn chuyển sang DA_DUYET, bản "
    "ghi chấm công chuyển sang HOP_LE và các cảnh báo liên quan được đánh dấu đã xử lý.")

h2("Xuất báo cáo công")
image("10-sd-bao-cao.png", "Hình 5.4 — Sơ đồ trình tự xuất báo cáo công")
body_text(
    "Sơ đồ này minh hoạ lớp phân quyền: yêu cầu đi qua hai lớp trung gian là kiểm tra "
    "đăng nhập và kiểm tra vai trò trước khi chạm tới cơ sở dữ liệu. Nhân viên thường "
    "gọi điểm cuối này sẽ nhận HTTP 403, đã được kiểm chứng khi chạy thử hệ thống.")
page_break()

# ===========================================================================
#  KẾT LUẬN
# ===========================================================================
h1("KẾT LUẬN CHECKPOINT 2", numbered=False)
body_text(
    "Checkpoint 2 hoàn thành đủ năm nội dung được yêu cầu. Điểm khác biệt so với một "
    "bộ tài liệu thiết kế thông thường là toàn bộ sơ đồ ở đây đều phản ánh hệ thống "
    "đã cài đặt và đang chạy, chứ không phải bản dự kiến:")
bullets([
    "Sơ đồ cơ sở dữ liệu được sinh tự động từ chính cơ sở dữ liệu đang chạy, nên số "
    "bảng, số cột, kiểu dữ liệu và khoá ngoại là số liệu thật.",
    "Sơ đồ use case chỉ liệt kê chức năng đã cài đặt, không kê thêm chức năng dự kiến.",
    "Sơ đồ luồng dữ liệu đặt tên tiến trình theo đúng các điểm cuối API có thật.",
    "Sơ đồ trình tự vẽ theo mã nguồn trong server/src/routes, kể cả phạm vi giao dịch.",
])
body_text(
    "Nhờ vậy, khi bảo vệ có thể mở song song tài liệu và hệ thống để đối chiếu từng "
    "chi tiết mà không sợ lệch nhau.")

doc.save(OUT)
print("DONE ->", OUT)
