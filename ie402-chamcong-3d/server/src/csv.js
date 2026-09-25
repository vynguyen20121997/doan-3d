// Xuất CSV cho Excel.
//
// Hai điểm bắt buộc để Excel bản tiếng Việt mở đúng:
//   - có BOM UTF-8, nếu không dấu tiếng Việt sẽ thành ký tự lạ;
//   - khai báo sep=; ở dòng đầu, vì Excel theo locale Việt Nam dùng dấu chấm phẩy
//     làm dấu phân cách cột, còn dấu phẩy là dấu thập phân.
const BOM = "﻿";

function oCsv(v) {
  if (v === null || v === undefined) return "";
  if (v instanceof Date) return v.toISOString().replace("T", " ").slice(0, 19);
  if (typeof v === "boolean") return v ? "Có" : "Không";
  // Cắt đuôi rác của số thực (104.97500000000001) nhưng vẫn giữ đủ 7 chữ số
  // thập phân cho kinh/vĩ độ.
  if (typeof v === "number" && !Number.isInteger(v)) {
    return String(Number(v.toFixed(7)));
  }
  const s = String(v);
  return /[";\n\r]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
}

/** cot: [[khoá, nhãn], …] — nhãn là tiêu đề cột hiển thị trong Excel. */
function taoCsv(cot, dong) {
  const dau = cot.map((c) => oCsv(c[1])).join(";");
  const than = dong.map((r) => cot.map((c) => oCsv(r[c[0]])).join(";"));
  return BOM + "sep=;\r\n" + [dau].concat(than).join("\r\n") + "\r\n";
}

/** Gửi kèm tên tệp; tên có dấu nên phải dùng filename* theo RFC 5987. */
function guiCsv(res, tenTep, noiDung) {
  res.setHeader("Content-Type", "text/csv; charset=utf-8");
  res.setHeader(
    "Content-Disposition",
    "attachment; filename=\"" + tenTep.replace(/[^\w.\-]/g, "_") + "\"; " +
      "filename*=UTF-8''" + encodeURIComponent(tenTep)
  );
  res.send(noiDung);
}

module.exports = { taoCsv, guiCsv };
