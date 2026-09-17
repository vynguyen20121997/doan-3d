# -*- coding: utf-8 -*-
"""
Sinh file .docx đồ án IE402 từ đúng template của thầy (Mau_do_an_IE402.docx).

Cách làm: mở template, giữ nguyên trang bìa / bảng thành viên / mục lục / phần
tài liệu tham khảo, chỉ thay các đoạn giữ chỗ dạng <...> bằng nội dung thật.

    python tools/build_docx.py
"""
import os
import copy
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(os.path.expanduser("~"), "Downloads", "Mau_do_an_IE402.docx")
OUT = os.path.join(ROOT, "DO-AN-IE402-Cham-cong-dinh-vi-3D.docx")
DG = os.path.join(ROOT, "docs", "diagrams")
SHOT = os.path.join(ROOT, "docs")

MAX_W = 6.1          # inch — bề ngang tối đa vừa khổ A4 lề mặc định
MAX_H = 7.8          # inch — cao tối đa để ảnh không tràn sang trang sau

TIEU_DE = ("HỆ THỐNG CHẤM CÔNG ĐỊNH VỊ 3D\n"
           "THEO MÔ HÌNH KHỐI KHÔNG GIAN PHÂN TẦNG")


# ---------------------------------------------------------------------------
#  Hạ tầng chèn nội dung
# ---------------------------------------------------------------------------
class Builder:
    """Gom các phần tử mới rồi chèn vào trước một đoạn giữ chỗ."""

    def __init__(self, doc, anchor):
        self.doc = doc
        self.anchor = anchor          # paragraph giữ chỗ

    def _move(self, element):
        self.anchor._element.addprevious(element)

    def para(self, text="", bold=False, italic=False, size=None, align=None):
        p = self.doc.add_paragraph()
        run = p.add_run(text)
        run.bold = bold
        run.italic = italic
        if size:
            run.font.size = Pt(size)
        if align:
            p.alignment = align
        self._move(p._element)
        return p

    def heading(self, text, level=3):
        p = self.doc.add_paragraph(text, style="Heading %d" % level)
        self._move(p._element)
        return p

    def _list_para(self, style):
        """Dùng style danh sách của template nếu có, không thì tự thụt lề."""
        try:
            return self.doc.add_paragraph(style=style), True
        except KeyError:
            p = self.doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.3)
            p.paragraph_format.space_after = Pt(4)
            return p, False

    def bullets(self, items, style="List Bullet", marker="• "):
        for it in items:
            p, styled = self._list_para(style)
            prefix = "" if styled else marker
            if isinstance(it, tuple):      # (phần in đậm, phần thường)
                r = p.add_run(prefix + it[0]); r.bold = True
                p.add_run(it[1])
            else:
                p.add_run(prefix + it)
            self._move(p._element)

    def numbers(self, items):
        for i, it in enumerate(items, 1):
            p, styled = self._list_para("List Number")
            p.add_run(("" if styled else "%d. " % i) + it)
            self._move(p._element)

    def table(self, headers, rows, widths=None):
        t = self.doc.add_table(rows=1, cols=len(headers))
        t.style = "Table Grid"
        for i, h in enumerate(headers):
            cell = t.rows[0].cells[i]
            cell.text = ""
            r = cell.paragraphs[0].add_run(h)
            r.bold = True
            r.font.size = Pt(10)
        for row in rows:
            cells = t.add_row().cells
            for i, v in enumerate(row):
                cells[i].text = ""
                r = cells[i].paragraphs[0].add_run(str(v))
                r.font.size = Pt(10)
        if widths:
            for row in t.rows:
                for i, w in enumerate(widths):
                    row.cells[i].width = Inches(w)
        self._move(t._element)
        self.para()                      # đoạn trống sau bảng
        return t

    def code(self, text):
        for line in text.split("\n"):
            p = self.doc.add_paragraph()
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(line if line else " ")
            r.font.name = "Consolas"
            r.font.size = Pt(8.5)
            self._move(p._element)
        self.para()

    def image(self, filename, caption=None, max_w=MAX_W, max_h=MAX_H):
        path = filename if os.path.isabs(filename) else os.path.join(DG, filename)
        if not os.path.exists(path):
            self.para("[thiếu ảnh: %s]" % os.path.basename(path), italic=True)
            return
        w_px, h_px = Image.open(path).size
        w_in = max_w
        h_in = w_in * h_px / w_px
        if h_in > max_h:
            h_in = max_h
            w_in = h_in * w_px / h_px
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(path, width=Inches(w_in))
        self._move(p._element)
        if caption:
            c = self.doc.add_paragraph()
            c.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = c.add_run(caption)
            r.italic = True
            r.font.size = Pt(9.5)
            self._move(c._element)
        self.para()

    def finish(self):
        """Xoá đoạn giữ chỗ."""
        self.anchor._element.getparent().remove(self.anchor._element)


def fill(doc, marker, writer):
    """Tìm đoạn chứa `marker` rồi thay bằng nội dung do `writer(b)` sinh ra."""
    for p in doc.paragraphs:
        if marker in p.text:
            b = Builder(doc, p)
            writer(b)
            b.finish()
            return True
    raise SystemExit("KHÔNG tìm thấy đoạn giữ chỗ: %r" % marker)


# ---------------------------------------------------------------------------
#  Nội dung từng mục
# ---------------------------------------------------------------------------
def ch1_tong_quan(b):
    b.para("Chấm công định vị (geolocation-based attendance) là hình thức xác nhận sự "
           "có mặt của người lao động bằng toạ độ thiết bị di động, thay cho máy chấm "
           "công vân tay hoặc thẻ từ đặt cố định. Hình thức này trở nên phổ biến khi "
           "doanh nghiệp có nhiều chi nhánh, nhân viên làm việc tại công trường hoặc "
           "di chuyển liên tục — việc yêu cầu tất cả về một máy chấm công vật lý là "
           "không khả thi.")
    b.para("Hầu hết ứng dụng chấm công định vị hiện nay đều dựa trên hàng rào địa lý "
           "hai chiều (2D geofence): một hình tròn bán kính R quanh một toạ độ, hoặc "
           "một đa giác phẳng. Hệ thống chỉ trả lời được câu hỏi “người này có đứng "
           "trong vùng hay không” trên mặt phẳng, hoàn toàn bỏ qua chiều cao.")
    b.para("Đồ án xây dựng một hệ thống chấm công định vị sử dụng mô hình khối ba "
           "chiều, cho phép phân biệt vị trí người lao động theo cả chiều đứng, áp "
           "dụng cho bối cảnh toà nhà văn phòng cao tầng tại TP. Hồ Chí Minh.")


def ch1_dat_van_de(b):
    b.para("Hàng rào 2D thất bại trong chính bối cảnh mà chấm công định vị được dùng "
           "nhiều nhất — toà nhà văn phòng cao tầng ở đô thị. Bốn vấn đề cụ thể:")
    b.para("a) Không phân biệt được theo chiều cao.", bold=True)
    b.para("Một cao ốc 40 tầng có hàng chục doanh nghiệp thuê các tầng khác nhau. "
           "Nhân viên công ty A ở tầng 5 và nhân viên công ty B ở tầng 22 có cùng một "
           "toạ độ kinh độ – vĩ độ. Hàng rào 2D chấp nhận cả hai như nhau. Nghiêm "
           "trọng hơn, một người ngồi ở quán cà phê tầng trệt hoặc đang ở hầm giữ xe "
           "vẫn được ghi nhận “chấm công hợp lệ” cho văn phòng tầng 22.")
    b.para("b) Sai số GPS trong đô thị (hiệu ứng urban canyon).", bold=True)
    b.para("Tín hiệu vệ tinh bị các khối nhà cao tầng che chắn và phản xạ nhiều đường "
           "(multipath), khiến sai số ngang có thể lên tới hàng chục mét — đủ để một "
           "người đứng ở toà nhà kế bên vẫn lọt vào hàng rào. Trên mô hình 2D không "
           "có cách nào phân tích hay khoanh vùng hiện tượng này; phải có mô hình "
           "khối của các công trình xung quanh mới mô tả được vùng bị che khuất.")
    b.para("c) Không phát hiện được gian lận theo chiều đứng.", bold=True)
    b.para("Các thủ thuật phổ biến như dùng ứng dụng giả lập vị trí (fake GPS) hoặc "
           "nhờ đồng nghiệp chấm hộ ngay dưới sảnh đều tạo ra bản ghi “đúng toạ độ” "
           "nhưng sai độ cao hoặc sai quy luật di chuyển. Dữ liệu 2D không lưu giữ "
           "thông tin cần thiết để phát hiện.")
    b.para("d) Không trực quan hoá được để đối chiếu khi có tranh chấp.", bold=True)
    b.para("Khi phát sinh tranh chấp về công, người quản lý cần nhìn thấy nhân viên "
           "đã chấm công ở đâu. Một điểm trên bản đồ phẳng không cho biết điểm đó nằm "
           "trong hay ngoài khối văn phòng.")


def ch1_y_nghia(b):
    b.para("Ý nghĩa.", bold=True)
    b.para("Đề tài chuyển bài toán chấm công từ phép kiểm tra “điểm thuộc đa giác” "
           "(2D) sang phép kiểm tra “điểm thuộc khối” (3D). Nhờ đó giải quyết được "
           "lớp bài toán mà hệ thống 2D không xử lý được: phân biệt doanh nghiệp theo "
           "tầng trong cùng một cao ốc, và kiểm chứng tính hợp lệ của bản ghi chấm "
           "công theo chiều đứng. Đây cũng là minh hoạ cụ thể cho giá trị thực tiễn "
           "của việc bổ sung chiều thứ ba vào một hệ thống thông tin địa lý.")
    b.para()
    b.para("Mục tiêu cụ thể.", bold=True)
    b.table(
        ["Mã", "Mục tiêu", "Tiêu chí hoàn thành"],
        [
            ["M1", "Xây dựng mô hình dữ liệu 3D cho vùng chấm công phân tầng",
             "Mô hình MAP (mục 2.2) được định nghĩa hình thức và cài đặt trong CSDL không gian"],
            ["M2", "Cài đặt thuật toán kiểm tra bao hàm khối có xét sai số",
             "Hàm trả về ba trạng thái HỢP LỆ / NGHI NGỜ / NGOÀI VÙNG, thời gian phản hồi dưới 200 ms"],
            ["M3", "Ứng dụng web cho ba vai trò: nhân viên, quản lý, quản trị",
             "Đủ luồng chấm công – giải trình – duyệt – báo cáo"],
            ["M4", "Trực quan hoá 3D bản ghi chấm công",
             "SceneView hiển thị khối toà nhà, khối văn phòng và điểm chấm công đúng cao độ"],
            ["M5", "Phát hiện bốn dạng bất thường R1–R4",
             "Sinh cảnh báo kèm mức độ cho người quản lý"],
            ["M6", "Cho phép quản trị viên dựng khối vùng chấm công trên bản đồ 3D",
             "Công cụ vẽ đa giác nền và nhập dải tầng, hệ thống tự suy ra cao độ"],
        ],
        widths=[0.5, 2.3, 3.3])


def ch2_co_so_ly_thuyet(b):
    b.para("Các mô hình biểu diễn đối tượng ba chiều thường dùng trong GIS được so "
           "sánh trong bảng sau:")
    b.table(
        ["Mô hình", "Mô tả", "Ưu điểm", "Nhược điểm"],
        [
            ["2.5D Prism (khối đùn)", "Đa giác nền được đùn lên theo chiều cao",
             "Nhẹ; dựng trực tiếp từ footprint và số tầng; phép kiểm tra bao hàm rất rẻ",
             "Không mô tả được phần nhô ra, mái vòm hay nội thất"],
            ["B-Rep (Boundary Representation)", "Mô tả bằng tập mặt – cạnh – đỉnh",
             "Chính xác, biểu diễn được hình học phức tạp",
             "Dữ liệu nặng, khó dựng và khó truy vấn không gian"],
            ["CSG (Constructive Solid Geometry)", "Tổ hợp Boolean các khối cơ bản",
             "Gọn với hình dạng quy tắc",
             "Không phù hợp với dữ liệu đo đạc thực tế"],
            ["Voxel / Octree", "Chia không gian thành các ô lập phương",
             "Tốt cho truy vấn thể tích và mô phỏng lan truyền",
             "Tốn bộ nhớ, mất độ chính xác ở biên"],
            ["TIN", "Lưới tam giác bất quy tắc",
             "Phù hợp mô tả địa hình",
             "Chỉ là bề mặt, không phải khối đặc"],
        ],
        widths=[1.2, 1.5, 1.8, 1.6])
    b.para("Lựa chọn: mô hình 2.5D Prism.", bold=True)
    b.bullets([
        "Bài toán chỉ cần trả lời “điểm có nằm trong khối văn phòng hay không”, không "
        "cần mô tả chi tiết kiến trúc. Prism là mức chi tiết vừa đủ, tương đương LoD1 "
        "trong chuẩn CityGML.",
        "Phép kiểm tra tách được thành hai bước có chi phí thấp: kiểm tra điểm thuộc "
        "đa giác trên mặt phẳng bằng thuật toán ray casting (độ phức tạp O(n) theo số "
        "đỉnh), và so sánh cao độ với dải [z_min, z_max]. Đáp ứng mục tiêu M2.",
        "Dữ liệu đầu vào sẵn có: footprint toà nhà lấy được từ OpenStreetMap; số tầng "
        "và chiều cao tầng lấy từ khảo sát thực tế. Không cần quét laser hay mô hình BIM.",
        "Được ArcGIS Maps SDK for JavaScript hỗ trợ trực tiếp qua PolygonSymbol3D kết "
        "hợp ExtrudeSymbol3DLayer, và được PostGIS hỗ trợ qua kiểu hình học có toạ độ Z.",
    ])
    b.para("Nhược điểm chấp nhận được: mọi tầng của một văn phòng bị coi là một khối "
           "liền, không mô tả được vách ngăn bên trong. Với bài toán chấm công — chỉ "
           "cần xác định người lao động thuộc văn phòng nào — đây không phải hạn chế "
           "thực chất.", italic=True)


def ch2_mo_hinh_hoa(b):
    b.para("Mô hình prism thuần tuý được biến đổi thành mô hình phục vụ riêng bài "
           "toán chấm công, đặt tên là MAP — Khối chấm công phân tầng "
           "(Multi-floor Attendance Prism).")
    b.para()
    b.para("a) Định nghĩa", bold=True)
    b.code("MAP = ( P, z_min, z_max, δxy, δz )")
    b.table(
        ["Thành phần", "Ý nghĩa"],
        [
            ["P", "Đa giác nền (footprint) phần sàn mà văn phòng thuê, hệ toạ độ WGS84"],
            ["z_min", "Cao độ tuyệt đối của sàn tầng thấp nhất văn phòng chiếm dụng"],
            ["z_max", "Cao độ tuyệt đối của trần tầng cao nhất"],
            ["δxy", "Biên dung sai ngang, bù cho sai số GPS đô thị"],
            ["δz", "Biên dung sai đứng, bù cho sai số đo cao độ"],
        ],
        widths=[1.1, 5.0])
    b.para("Cao độ được suy ra từ thông tin toà nhà và dải tầng văn phòng thuê:")
    b.code("z_min = z_nen + (tang_bat_dau - 1) x h_tang\n"
           "z_max = z_nen +  tang_ket_thuc      x h_tang")
    b.para("Khối dùng để kiểm tra là khối MAP đã nới biên dung sai:")
    b.code("MAP+ = ( buffer(P, δxy),  z_min - δz,  z_max + δz )")
    b.para()
    b.para("b) Phép kiểm tra bao hàm", bold=True)
    b.para("Với bản ghi chấm công tại điểm Q = (kinh độ, vĩ độ, cao độ):")
    b.code("trong_khoi(Q, MAP+)  <=>  pointInPolygon(Q.xy, buffer(P, δxy))\n"
           "                      AND  (z_min - δz) <= Q.alt <= (z_max + δz)")
    b.para("Kết quả được phân thành ba trạng thái thay vì nhị phân đúng/sai:")
    b.table(
        ["Trạng thái", "Điều kiện", "Ý nghĩa nghiệp vụ"],
        [
            ["HỢP LỆ", "Thoả cả điều kiện ngang và điều kiện đứng, độ chính xác thiết bị đạt ngưỡng",
             "Ghi nhận công bình thường"],
            ["NGHI NGỜ", "Thoả điều kiện ngang nhưng sai điều kiện đứng",
             "Đúng toà nhà, sai tầng — cần xác minh"],
            ["NGOÀI VÙNG", "Không thoả điều kiện ngang",
             "Từ chối, đề nghị gửi đơn giải trình"],
        ],
        widths=[1.0, 3.0, 2.1])
    b.para("Trạng thái NGHI NGỜ chính là giá trị mà mô hình 2D không thể sinh ra. Đây "
           "là đóng góp cốt lõi của mô hình MAP.", italic=True)
    b.para()
    b.para("c) Bốn quy tắc phát hiện bất thường", bold=True)
    b.table(
        ["Mã", "Quy tắc", "Cơ sở phát hiện"],
        [
            ["R1", "Sai tầng", "Thoả điều kiện ngang nhưng lệch cao độ vượt δz"],
            ["R2", "Dịch chuyển bất khả thi",
             "Vận tốc suy ra giữa hai bản ghi liên tiếp vượt ngưỡng (ví dụ 150 km/h)"],
            ["R3", "Độ chính xác bất thường",
             "Giá trị accuracy quá nhỏ so với thực tế đô thị (dấu hiệu giả lập GPS) hoặc quá lớn"],
            ["R4", "Trùng thiết bị",
             "Nhiều nhân viên chấm công từ cùng một định danh thiết bị trong thời gian ngắn"],
        ],
        widths=[0.5, 1.6, 4.0])
    b.para()
    b.para("d) Các đối tượng trong mô hình", bold=True)
    b.table(
        ["Đối tượng", "Vai trò trong mô hình không gian"],
        [
            ["Toà nhà", "Khối bao ngoài, có footprint và cao độ nền — đóng vai trò nền cảnh 3D"],
            ["Văn phòng", "Đơn vị thuê, chiếm dải tầng từ tầng bắt đầu đến tầng kết thúc"],
            ["Khu vực chấm công", "Hiện thực của khối MAP: P, z_min, z_max, δxy, δz"],
            ["Bản ghi chấm công", "Điểm ba chiều kèm độ chính xác và thời điểm"],
            ["Cảnh báo bất thường", "Kết quả áp bốn quy tắc R1–R4 lên bản ghi"],
        ],
        widths=[1.5, 4.6])


def ch2_erd(b):
    b.para("Mô hình ERD gồm 15 thực thể, chia thành bốn nhóm: tổ chức (công ty, phòng "
           "ban), không gian (toà nhà, văn phòng, khu vực chấm công), nhân sự (nhân "
           "viên, người dùng, vai trò, thiết bị) và nghiệp vụ chấm công (ca làm việc, "
           "phân ca, bản ghi chấm công, cảnh báo, đơn giải trình).")
    b.image("01-erd.png", "Hình 2.1 — Sơ đồ quan hệ thực thể (ERD)")
    b.para("Ba thực thể mang tính không gian, là phần khác biệt so với một hệ thống "
           "chấm công thông thường:")
    b.table(
        ["Thực thể", "Thuộc tính không gian", "Giải thích"],
        [
            ["TOA_NHA", "footprint (Polygon), cao_do_nen, so_tang, chieu_cao_tang",
             "Khối bao của công trình; là gốc để suy ra cao độ của mọi tầng"],
            ["KHU_VUC_CHAM_CONG", "da_giac_nen (Polygon), z_min, z_max, dung_sai_ngang, dung_sai_dung",
             "Hiện thực trực tiếp của khối MAP; quan hệ 1–1 với văn phòng"],
            ["BAN_GHI_CHAM_CONG", "vi_tri (PointZ), do_chinh_xac_ngang, do_chinh_xac_dung",
             "Điểm 3D thiết bị báo về; là đầu vào của phép kiểm tra bao hàm"],
        ],
        widths=[1.4, 2.2, 2.5])
    b.para("Các quan hệ chính:")
    b.bullets([
        "TOA_NHA 1–n VAN_PHONG: một toà nhà chứa nhiều văn phòng của nhiều công ty khác nhau.",
        "VAN_PHONG 1–1 KHU_VUC_CHAM_CONG: mỗi văn phòng tương ứng đúng một khối MAP.",
        "KHU_VUC_CHAM_CONG 1–n BAN_GHI_CHAM_CONG: một khối xác thực nhiều lần chấm công.",
        "BAN_GHI_CHAM_CONG 1–n CANH_BAO_BAT_THUONG: một bản ghi có thể vi phạm nhiều quy tắc.",
        "BAN_GHI_CHAM_CONG 1–0..1 DON_GIAI_TRINH: mỗi bản ghi có tối đa một đơn giải trình.",
    ])


def ch2_quan_he(b):
    b.para("Chuyển mô hình ERD sang mô hình quan hệ (gạch chân là khoá chính, dấu ↑ "
           "là khoá ngoại):")
    b.code(
        "CONG_TY(ma_cong_ty, ten_cong_ty, ma_so_thue)\n\n"
        "PHONG_BAN(ma_phong_ban, ma_cong_ty↑, ten_phong_ban)\n\n"
        "TOA_NHA(ma_toa_nha, ten, dia_chi, footprint, cao_do_nen, so_tang,\n"
        "        chieu_cao_tang, nguon_du_lieu)\n\n"
        "VAN_PHONG(ma_van_phong, ma_cong_ty↑, ma_toa_nha↑, ten,\n"
        "          tang_bat_dau, tang_ket_thuc)\n\n"
        "KHU_VUC_CHAM_CONG(ma_khu_vuc, ma_van_phong↑, da_giac_nen, z_min, z_max,\n"
        "                  dung_sai_ngang, dung_sai_dung, dang_hieu_luc)\n\n"
        "NHAN_VIEN(ma_nhan_vien, ma_cong_ty↑, ma_phong_ban↑, ho_ten, email,\n"
        "          ngay_vao_lam, dang_lam_viec)\n\n"
        "THIET_BI(ma_thiet_bi, ma_nhan_vien↑, dinh_danh_thiet_bi, he_dieu_hanh,\n"
        "         duoc_tin_cay)\n\n"
        "CA_LAM_VIEC(ma_ca, ten_ca, gio_vao, gio_ra, tre_toi_da_phut)\n\n"
        "PHAN_CA(ma_phan_ca, ma_nhan_vien↑, ma_ca↑, ngay_lam_viec)\n\n"
        "BAN_GHI_CHAM_CONG(ma_ban_ghi, ma_nhan_vien↑, ma_khu_vuc↑, ma_thiet_bi↑,\n"
        "                  thoi_diem, loai, vi_tri, do_chinh_xac_ngang,\n"
        "                  do_chinh_xac_dung, nguon_cao_do, tang_khai_bao, trang_thai)\n\n"
        "CANH_BAO_BAT_THUONG(ma_canh_bao, ma_ban_ghi↑, ma_quy_tac, muc_do, mo_ta,\n"
        "                    da_xu_ly)\n\n"
        "DON_GIAI_TRINH(ma_don, ma_nhan_vien↑, ma_ban_ghi↑, ly_do, trang_thai,\n"
        "               nguoi_duyet↑, thoi_diem_gui)\n\n"
        "VAI_TRO(ma_vai_tro, ten_vai_tro)\n\n"
        "NGUOI_DUNG(ma_nguoi_dung, ma_nhan_vien↑, ma_vai_tro↑, ten_dang_nhap,\n"
        "           mat_khau_bam)")
    b.para("Mô tả chi tiết các thuộc tính đáng lưu ý:", bold=True)
    b.table(
        ["Thuộc tính", "Kiểu", "Mô tả"],
        [
            ["TOA_NHA.footprint", "GEOMETRY(Polygon, 4326)",
             "Hình chiếu bằng của công trình, hệ WGS84"],
            ["TOA_NHA.cao_do_nen", "NUMERIC(7,2)", "Cao độ mặt nền so với mực nước biển, đơn vị mét"],
            ["KHU_VUC.z_min / z_max", "NUMERIC(7,2)",
             "Thuộc tính dẫn xuất từ cao độ nền và dải tầng; lưu phi chuẩn hoá có chủ đích để tránh tính lại khi truy vấn nóng"],
            ["BAN_GHI.vi_tri", "GEOMETRY(PointZ, 4326)", "Toạ độ ba chiều thiết bị báo về"],
            ["BAN_GHI.nguon_cao_do", "VARCHAR(12)",
             "THIET_BI nếu cao độ do GPS đo được, KHAI_BAO nếu lấy theo tầng người dùng chọn"],
            ["BAN_GHI.trang_thai", "VARCHAR(12)", "HOP_LE | NGHI_NGO | NGOAI_VUNG"],
        ],
        widths=[1.5, 1.5, 3.1])
    b.para("Ràng buộc toàn vẹn:", bold=True)
    b.bullets([
        "VAN_PHONG.tang_bat_dau ≤ VAN_PHONG.tang_ket_thuc ≤ TOA_NHA.so_tang.",
        "KHU_VUC_CHAM_CONG.z_min < z_max; hai giá trị này được trigger tự suy ra khi để trống.",
        "Mỗi nhân viên chỉ có tối đa một bản ghi loại VAO chưa có bản ghi RA tương ứng trong ngày.",
        "PHAN_CA(ma_nhan_vien, ngay_lam_viec) là khoá dự tuyển — một người chỉ được xếp một ca mỗi ngày.",
    ])


def ch2_usecase(b):
    b.para("Hệ thống có ba tác nhân người dùng (nhân viên, quản lý, quản trị viên) và "
           "một tác nhân hệ thống ngoài là dịch vụ định vị của thiết bị.")
    b.image("02-usecase.png", "Hình 2.2 — Sơ đồ trường hợp sử dụng")
    b.para("Đặc tả UC2 — Chấm công vào/ra", bold=True)
    b.table(
        ["Mục", "Nội dung"],
        [
            ["Tác nhân", "Nhân viên"],
            ["Tiền điều kiện",
             "Đã đăng nhập; thiết bị đã cấp quyền định vị; nhân viên có ca làm việc trong ngày"],
            ["Luồng chính",
             "1. Nhân viên mở màn hình chấm công.\n"
             "2. Hệ thống yêu cầu vị trí từ thiết bị.\n"
             "3. Thiết bị trả về kinh độ, vĩ độ, cao độ và độ chính xác.\n"
             "4. Nhân viên xác nhận tầng đang làm việc.\n"
             "5. Hệ thống thực hiện UC12 — kiểm tra bao hàm khối.\n"
             "6. Hệ thống thực hiện UC13 — áp bốn quy tắc R1–R4.\n"
             "7. Hệ thống lưu bản ghi kèm trạng thái và hiển thị kết quả."],
            ["Luồng thay thế 3a",
             "Thiết bị không trả được cao độ → dùng tầng khai báo ở bước 4, "
             "đánh dấu nguồn cao độ là KHAI_BAO"],
            ["Luồng ngoại lệ 5a",
             "Ngoài vùng ngang → từ chối, hiển thị khoảng cách tới khối gần nhất, "
             "gợi ý gửi đơn giải trình (UC5)"],
            ["Luồng ngoại lệ 5b",
             "Trong vùng ngang nhưng lệch tầng → lưu trạng thái NGHI NGỜ, sinh cảnh "
             "báo R1, thông báo cho quản lý"],
            ["Hậu điều kiện", "Có một bản ghi chấm công mới với trạng thái được xác định"],
        ],
        widths=[1.3, 4.8])
    b.para("Đặc tả UC10 — Dựng khối vùng chấm công 3D", bold=True)
    b.table(
        ["Mục", "Nội dung"],
        [
            ["Tác nhân", "Quản trị viên"],
            ["Tiền điều kiện", "Toà nhà đã tồn tại trong hệ thống"],
            ["Luồng chính",
             "1. Chọn toà nhà trên SceneView.\n"
             "2. Vẽ đa giác nền bằng công cụ phác thảo, hoặc kế thừa footprint của toà nhà.\n"
             "3. Nhập dải tầng văn phòng thuê.\n"
             "4. Hệ thống tự tính z_min và z_max từ cao độ nền và chiều cao tầng.\n"
             "5. Nhập dung sai ngang và dung sai đứng.\n"
             "6. Hệ thống dựng khối xem trước bằng ExtrudeSymbol3DLayer.\n"
             "7. Lưu khối."],
            ["Hậu điều kiện", "Khối MAP có hiệu lực, dùng để xác thực các lần chấm công sau"],
        ],
        widths=[1.3, 4.8])


def ch2_dfd(b):
    b.para("Sơ đồ mức 0 (sơ đồ ngữ cảnh)", bold=True)
    b.image("03-dfd0.png", "Hình 2.3 — DFD mức 0")
    b.para("Sơ đồ mức 1", bold=True)
    b.image("04-dfd1.png", "Hình 2.4 — DFD mức 1")
    b.para("Đặc tả các tiến trình:", bold=True)
    b.table(
        ["Tiến trình", "Đầu vào", "Xử lý", "Đầu ra"],
        [
            ["1.0 Xác thực người dùng", "Thông tin đăng nhập",
             "Đối chiếu kho D1, sinh token kèm vai trò", "Phiên làm việc"],
            ["2.0 Thu nhận vị trí 3D", "Yêu cầu chấm công, dữ liệu định vị thiết bị",
             "Chuẩn hoá toạ độ, xác định nguồn cao độ", "Điểm 3D kèm độ chính xác"],
            ["3.0 Kiểm tra bao hàm khối", "Điểm 3D, khối MAP từ kho D2",
             "Ray casting trên mặt phẳng và so sánh dải cao độ", "Bản ghi kèm trạng thái, ghi vào D3"],
            ["4.0 Phát hiện bất thường", "Bản ghi mới, lịch sử gần nhất từ D3",
             "Áp bốn quy tắc R1–R4", "Cảnh báo ghi vào D4"],
            ["5.0 Xử lý giải trình", "Đơn của nhân viên, quyết định của quản lý",
             "Cập nhật trạng thái đơn và bản ghi liên quan", "Đơn đã duyệt, bản ghi được hiệu chỉnh"],
            ["6.0 Tổng hợp báo cáo", "Bản ghi từ D3, ca làm việc từ D6",
             "Tính giờ công, số lần đi muộn, số lần bất thường", "Báo cáo tháng"],
            ["7.0 Quản trị khối MAP", "Footprint, dải tầng, dung sai",
             "Suy ra z_min/z_max, kiểm tra ràng buộc", "Khối MAP ghi vào D2"],
        ],
        widths=[1.3, 1.5, 1.9, 1.4])


def ch2_sequence(b):
    b.para("SD1 — Chấm công vào (gồm cả nhánh lệch tầng)", bold=True)
    b.image("05-sd1-cham-cong.png", "Hình 2.5 — Sơ đồ trình tự chấm công vào")
    b.para("Điểm cần chú ý: nhánh thứ hai của khối alt mô tả đúng tình huống mà hàng "
           "rào 2D bỏ sót — toạ độ ngang nằm trong vùng nhưng cao độ lệch khỏi dải "
           "tầng, hệ thống trả về NGHI NGỜ và sinh cảnh báo R1 thay vì chấp nhận.",
           italic=True)
    b.para()
    b.para("SD2 — Quản trị viên dựng khối vùng chấm công", bold=True)
    b.image("06-sd2-dung-khoi.png", "Hình 2.6 — Sơ đồ trình tự dựng khối MAP")
    b.para()
    b.para("SD3 — Duyệt đơn giải trình", bold=True)
    b.image("07-sd3-giai-trinh.png", "Hình 2.7 — Sơ đồ trình tự duyệt đơn giải trình")


def ch3_cong_nghe(b):
    b.table(
        ["Lớp", "Công nghệ", "Lý do lựa chọn"],
        [
            ["Bản đồ 3D", "ArcGIS Maps SDK for JavaScript 4.29 (SceneView, GraphicsLayer, "
                          "PolygonSymbol3D, ExtrudeSymbol3DLayer, SketchViewModel)",
             "Đúng công nghệ môn học; hỗ trợ sẵn khối đùn, công cụ phác thảo 3D và lớp địa hình"],
            ["Giao diện", "React + Vite", "Tách thành phần rõ ràng, thuận tiện chia việc trong nhóm"],
            ["Định vị", "HTML5 Geolocation API",
             "Chạy trực tiếp trên trình duyệt di động, không cần cài ứng dụng"],
            ["Máy chủ", "Node.js + Express", "Cùng ngôn ngữ với phía giao diện, triển khai nhanh"],
            ["Cơ sở dữ liệu", "PostgreSQL + PostGIS",
             "Lưu được hình học có toạ độ Z; có sẵn ST_Contains, ST_DWithin, ST_Distance "
             "trên kiểu geography cho kết quả tính bằng mét"],
            ["Xác thực", "JWT + bcrypt", "Phân quyền ba vai trò nhân viên / quản lý / quản trị"],
            ["Dữ liệu nền", "OpenStreetMap qua Overpass API",
             "Nguồn footprint toà nhà miễn phí, giấy phép ODbL"],
            ["Triển khai", "Vercel (giao diện) + Render (máy chủ và CSDL)",
             "Đủ dùng ở mức đồ án, có HTTPS sẵn"],
        ],
        widths=[1.0, 2.1, 3.0])
    b.para("Lưu ý kỹ thuật bắt buộc: Geolocation API chỉ hoạt động trên kết nối HTTPS "
           "hoặc localhost. Khi trình diễn trên điện thoại phải dùng tên miền có chứng "
           "chỉ hoặc công cụ tạo đường hầm như ngrok; mở bằng địa chỉ IP nội bộ sẽ bị "
           "trình duyệt từ chối cấp quyền định vị.", bold=True)


def ch3_giao_dien(b):
    b.para("Danh sách màn hình của ứng dụng:")
    b.table(
        ["STT", "Màn hình", "Thành phần chính"],
        [
            ["1", "Đăng nhập", "Biểu mẫu tài khoản, điều hướng theo vai trò"],
            ["2", "Chấm công (ưu tiên giao diện di động)",
             "Nút vào/ra cỡ lớn, hiển thị độ chính xác GPS, ô chọn tầng, bản đồ thu nhỏ"],
            ["3", "Lịch sử chấm công", "Bảng theo tháng, tô màu theo trạng thái"],
            ["4", "Bản đồ 3D vị trí chấm công",
             "SceneView: khối toà nhà, các khối MAP bán trong suốt, điểm chấm công đặt đúng cao độ"],
            ["5", "Bảng điều khiển quản lý", "Thống kê đi muộn/đúng giờ, danh sách cảnh báo R1–R4"],
            ["6", "Duyệt đơn giải trình", "Danh sách đơn kèm xem vị trí 3D của bản ghi liên quan"],
            ["7", "Quản trị khối MAP",
             "Công cụ vẽ đa giác trên SceneView, nhập dải tầng và dung sai, xem trước khối"],
            ["8", "Báo cáo công", "Bảng tổng hợp theo phòng ban, xuất Excel/PDF"],
        ],
        widths=[0.4, 1.9, 3.8])
    b.para("Màn hình số 4 là màn hình đặc thù của đề tài. Hình dưới là bản dựng thử "
           "nghiệm trên toà nhà IFC One Saigon với ba khối MAP ứng với ba doanh nghiệp "
           "thuê ở ba dải tầng khác nhau:")
    b.image(os.path.join(SHOT, "01-ba-khoi-MAP.png"),
            "Hình 3.1 — Ba khối MAP trong cùng một toà nhà: Alpha Tech (cam, tầng 5–8), "
            "Beta Finance (xanh, tầng 20–24), Gamma Media (tím, tầng 35–40)")


def ch4_ket_qua(b):
    b.para("Bản dựng thử nghiệm sử dụng dữ liệu thật: footprint toà nhà IFC One "
           "Saigon lấy từ OpenStreetMap (way/306578560), 42 tầng, chiều cao 195,3 m; "
           "cao độ nền giả định 5 m nên chiều cao tầng trung bình là 4,65 m. Ba văn "
           "phòng giả lập được đặt tại ba dải tầng khác nhau nhưng dùng chung một "
           "footprint — tức là có cùng toạ độ kinh độ, vĩ độ.")
    b.para()
    b.para("Kết quả ba tình huống kiểm thử", bold=True)
    b.table(
        ["Tình huống", "Cao độ điểm", "Khoảng cách ngang",
         "Kết quả hệ thống 3D", "Kết quả hàng rào 2D"],
        [
            ["Nhân viên Alpha Tech chấm công tại tầng 6", "28,25 m", "0 m",
             "HỢP LỆ", "Hợp lệ"],
            ["Nhân viên Alpha Tech chấm công tại tầng 22", "104,98 m", "0 m",
             "NGHI NGỜ (lệch +62,78 m ≈ 13,5 tầng)", "Hợp lệ — bỏ sót"],
            ["Nhân viên Alpha Tech chấm công cách toà nhà 270 m", "28,25 m", "270,2 m",
             "NGOÀI VÙNG", "Ngoài vùng"],
        ],
        widths=[1.9, 0.9, 1.0, 1.5, 0.9])
    b.para("Tình huống thứ hai là kết quả quan trọng nhất của đồ án: cùng một toạ độ "
           "ngang, hàng rào 2D kết luận hợp lệ trong khi mô hình MAP phát hiện được "
           "sai lệch 13,5 tầng và chuyển bản ghi sang trạng thái cần xác minh.",
           bold=True)
    b.image(os.path.join(SHOT, "02-ket-qua-nghi-ngo.png"),
            "Hình 4.1 — Màn hình kết quả tình huống sai tầng; điểm chấm công (hình "
            "cầu) nằm trong khối của doanh nghiệp khác")
    b.para("Kết quả đạt được", bold=True)
    b.bullets([
        "Định nghĩa và cài đặt hoàn chỉnh mô hình MAP, gồm công thức suy cao độ từ dải tầng.",
        "Thuật toán kiểm tra bao hàm khối trả về ba trạng thái, chạy hoàn toàn ở phía "
        "trình duyệt trong bản dựng thử và có bản cài đặt tương ứng bằng hàm PL/pgSQL "
        "trên PostGIS.",
        "Trực quan hoá 3D cho phép nhìn thấy trực tiếp vị trí chấm công so với khối văn phòng.",
        "Chứng minh được bằng số liệu rằng hàng rào 2D bỏ sót tình huống sai tầng.",
    ])
    b.para("Hạn chế", bold=True)
    b.numbers([
        "Độ cao GPS trong nhà rất kém. Tín hiệu vệ tinh gần như không thu được trong "
        "lòng nhà cao tầng; thuộc tính altitude mà Geolocation API trả về thường là "
        "null hoặc có sai số hàng chục mét, lớn hơn cả chiều cao vài tầng. Hệ thống "
        "vì vậy phải chấp nhận nguồn cao độ hỗn hợp: ưu tiên cao độ đo được, khi "
        "không có thì dùng tầng người dùng khai báo, và mô hình chỉ đóng vai trò đối "
        "chiếu chứ không tự quyết định.",
        "Chưa sử dụng cảm biến bổ trợ. Giải pháp công nghiệp cho định vị trong nhà là "
        "Wi-Fi RSSI, BLE beacon hoặc khí áp kế; trong phạm vi đồ án chỉ nêu hướng, "
        "chưa cài đặt.",
        "Dữ liệu chiều cao công trình từ OpenStreetMap rất thiếu. Khảo sát trên phạm "
        "vi TP. Hồ Chí Minh cho thấy trong 105.609 công trình có footprint, chỉ 3.944 "
        "công trình (khoảng 3,7 %) có thuộc tính height hoặc building:levels; phần "
        "còn lại phải nhập thủ công.",
        "Không thể chặn hoàn toàn việc giả lập GPS ở mức hệ điều hành từ phía ứng "
        "dụng web. Các quy tắc R2–R4 chỉ làm tăng chi phí gian lận chứ không loại bỏ "
        "được hoàn toàn.",
    ])


def ch4_dinh_huong(b):
    b.bullets([
        "Bổ sung định vị trong nhà bằng BLE beacon đặt theo tầng, hợp nhất kết quả với "
        "mô hình MAP để xác định tầng độc lập với GPS.",
        "Nâng mức chi tiết lên LoD2/LoD3 theo chuẩn CityGML để mô tả từng phòng, phục "
        "vụ chấm công theo khu vực làm việc thay vì theo tầng.",
        "Phân tích vùng che khuất tín hiệu GPS dựa trên mô hình khối của các toà nhà "
        "lân cận, từ đó tự động hiệu chỉnh dung sai ngang theo từng vị trí thay vì "
        "dùng một giá trị cố định.",
        "Mở rộng cho công trường xây dựng: khối MAP có cao độ thay đổi theo tiến độ "
        "thi công, tức bổ sung chiều thứ tư là thời gian.",
        "Tích hợp với hệ thống tính lương và hệ thống quản lý nhân sự sẵn có của doanh nghiệp.",
    ])


# ---------------------------------------------------------------------------
def main():
    if not os.path.exists(TEMPLATE):
        raise SystemExit("Không tìm thấy template: %s" % TEMPLATE)

    doc = Document(TEMPLATE)

    # Tên đồ án trên trang bìa
    for p in doc.paragraphs:
        if "<Tên đồ án>" in p.text:
            for r in p.runs:
                r.text = ""
            p.runs[0].text = TIEU_DE
            break

    fill(doc, "<Viết giới thiệu về đề tài", ch1_tong_quan)
    fill(doc, "<Vấn đề hiện đang tồn tại", ch1_dat_van_de)
    fill(doc, "<Trình bày ý nghĩa và mục tiêu", ch1_y_nghia)
    fill(doc, "<trình bày mô hình 2D, 3D", ch2_co_so_ly_thuyet)
    fill(doc, "<trình bày cách mà bạn biến đổi", ch2_mo_hinh_hoa)
    fill(doc, "<vẽ mô hình ERD", ch2_erd)
    fill(doc, "<chuyển mô hình ERD thành mô hình quan hệ", ch2_quan_he)
    fill(doc, "<Trình bày các use case", ch2_usecase)
    fill(doc, "<trình bày các DFD", ch2_dfd)
    fill(doc, "<Vẽ một số sơ đồ trình tự", ch2_sequence)
    fill(doc, "<Trình bày các công nghệ sử dụng>", ch3_cong_nghe)
    fill(doc, "<Chụp hình giao diện ứng dụng", ch3_giao_dien)
    fill(doc, "<Hình ảnh thực tế từ ứng dụng", ch4_ket_qua)
    fill(doc, "<Định hướng phát triển mở rộng", ch4_dinh_huong)

    doc.save(OUT)
    print("DONE ->", OUT)


if __name__ == "__main__":
    main()
