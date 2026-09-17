// Xác thực bằng JWT và phân quyền theo vai trò.
const jwt = require("jsonwebtoken");

const SECRET = process.env.JWT_SECRET || "ie402-chamcong-3d-doi-khi-trien-khai-that";
const HAN_DUNG = "8h";

function taoToken(nguoiDung) {
  return jwt.sign(
    {
      ma_nguoi_dung: nguoiDung.ma_nguoi_dung,
      ma_nhan_vien: nguoiDung.ma_nhan_vien,
      ten_dang_nhap: nguoiDung.ten_dang_nhap,
      vai_tro: nguoiDung.ten_vai_tro,
    },
    SECRET,
    { expiresIn: HAN_DUNG }
  );
}

// Middleware: bắt buộc đã đăng nhập.
function canDangNhap(req, res, next) {
  const header = req.headers.authorization || "";
  const token = header.startsWith("Bearer ") ? header.slice(7) : null;
  if (!token) {
    return res.status(401).json({ loi: "Chưa đăng nhập" });
  }
  try {
    req.nguoiDung = jwt.verify(token, SECRET);
    next();
  } catch (e) {
    res.status(401).json({ loi: "Phiên đăng nhập không hợp lệ hoặc đã hết hạn" });
  }
}

// Middleware: giới hạn theo vai trò, ví dụ canCoVaiTro("QUAN_LY", "QUAN_TRI").
function canCoVaiTro(...vaiTro) {
  return (req, res, next) => {
    if (!req.nguoiDung || !vaiTro.includes(req.nguoiDung.vai_tro)) {
      return res.status(403).json({ loi: "Không đủ quyền thực hiện chức năng này" });
    }
    next();
  };
}

module.exports = { taoToken, canDangNhap, canCoVaiTro, SECRET };
