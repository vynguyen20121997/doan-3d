// Chức năng của quản lý và quản trị viên: cảnh báo, duyệt đơn, báo cáo công.
const express = require("express");
const { q } = require("../db");
const { canDangNhap, canCoVaiTro } = require("../auth");

const router = express.Router();
const laQuanLy = [canDangNhap, canCoVaiTro("QUAN_LY", "QUAN_TRI")];

/* ------------------------------------------------------------------ *
 * Danh sách cảnh báo bất thường, sắp theo mức độ rồi theo thời gian
 * ------------------------------------------------------------------ */
router.get("/canh-bao", laQuanLy, async (req, res) => {
  const chuaXuLy = req.query.chua_xu_ly === "1";
  const { rows } = await q(
    `SELECT c.ma_canh_bao, c.ma_quy_tac, c.muc_do, c.mo_ta, c.da_xu_ly,
            b.ma_ban_ghi, b.thoi_diem, b.loai, b.trang_thai,
            ST_X(b.vi_tri) AS kinh_do, ST_Y(b.vi_tri) AS vi_do, ST_Z(b.vi_tri) AS cao_do,
            nv.ho_ten, ct.ten_cong_ty
       FROM canh_bao_bat_thuong c
       JOIN ban_ghi_cham_cong b ON b.ma_ban_ghi = c.ma_ban_ghi
       JOIN nhan_vien nv ON nv.ma_nhan_vien = b.ma_nhan_vien
       JOIN cong_ty  ct  ON ct.ma_cong_ty  = nv.ma_cong_ty
      WHERE ($1 = false OR c.da_xu_ly = false)
      ORDER BY CASE c.muc_do WHEN 'CAO' THEN 1 WHEN 'TRUNG_BINH' THEN 2 ELSE 3 END,
               b.thoi_diem DESC
      LIMIT 200`,
    [chuaXuLy]
  );
  res.json(rows);
});

/* ------------------------------------------------------------------ *
 * Đơn giải trình: xem danh sách và duyệt
 * ------------------------------------------------------------------ */
router.get("/giai-trinh", laQuanLy, async (req, res) => {
  const { rows } = await q(
    `SELECT d.ma_don, d.ly_do, d.trang_thai, d.thoi_diem_gui,
            nv.ho_ten, b.ma_ban_ghi, b.thoi_diem, b.trang_thai AS trang_thai_ban_ghi,
            ST_X(b.vi_tri) AS kinh_do, ST_Y(b.vi_tri) AS vi_do, ST_Z(b.vi_tri) AS cao_do
       FROM don_giai_trinh d
       JOIN nhan_vien nv ON nv.ma_nhan_vien = d.ma_nhan_vien
       JOIN ban_ghi_cham_cong b ON b.ma_ban_ghi = d.ma_ban_ghi
      WHERE ($1::text IS NULL OR d.trang_thai = $1)
      ORDER BY d.thoi_diem_gui DESC
      LIMIT 200`,
    [req.query.trang_thai || null]
  );
  res.json(rows);
});

router.put("/giai-trinh/:id", laQuanLy, async (req, res) => {
  const { trang_thai } = req.body || {};
  if (!["DA_DUYET", "TU_CHOI"].includes(trang_thai)) {
    return res.status(400).json({ loi: "Trạng thái phải là DA_DUYET hoặc TU_CHOI" });
  }
  const client = await require("../db").pool.connect();
  try {
    await client.query("BEGIN");
    const d = await client.query(
      `UPDATE don_giai_trinh
          SET trang_thai = $1, nguoi_duyet = $2
        WHERE ma_don = $3 AND trang_thai = 'CHO_DUYET'
        RETURNING ma_ban_ghi`,
      [trang_thai, req.nguoiDung.ma_nhan_vien, req.params.id]
    );
    if (!d.rows.length) {
      await client.query("ROLLBACK");
      return res.status(404).json({ loi: "Không thấy đơn đang chờ duyệt" });
    }
    // Duyệt đơn thì công nhận bản ghi và đóng các cảnh báo liên quan.
    if (trang_thai === "DA_DUYET") {
      await client.query(
        `UPDATE ban_ghi_cham_cong SET trang_thai = 'HOP_LE' WHERE ma_ban_ghi = $1`,
        [d.rows[0].ma_ban_ghi]
      );
      await client.query(
        `UPDATE canh_bao_bat_thuong SET da_xu_ly = true WHERE ma_ban_ghi = $1`,
        [d.rows[0].ma_ban_ghi]
      );
    }
    await client.query("COMMIT");
    res.json({ ma_don: Number(req.params.id), trang_thai });
  } catch (e) {
    await client.query("ROLLBACK");
    throw e;
  } finally {
    client.release();
  }
});

/* ------------------------------------------------------------------ *
 * Bảng điều khiển + báo cáo công
 * ------------------------------------------------------------------ */
router.get("/dashboard", laQuanLy, async (_req, res) => {
  const [tt, cb, don] = await Promise.all([
    q(`SELECT trang_thai, count(*)::int AS so_luong
         FROM ban_ghi_cham_cong GROUP BY trang_thai`),
    q(`SELECT ma_quy_tac, count(*)::int AS so_luong
         FROM canh_bao_bat_thuong GROUP BY ma_quy_tac ORDER BY ma_quy_tac`),
    q(`SELECT trang_thai, count(*)::int AS so_luong
         FROM don_giai_trinh GROUP BY trang_thai`),
  ]);
  res.json({
    theo_trang_thai: tt.rows,
    theo_quy_tac: cb.rows,
    don_giai_trinh: don.rows,
  });
});

router.get("/bao-cao/cong", laQuanLy, async (req, res) => {
  const thang = req.query.thang || new Date().toISOString().slice(0, 7); // YYYY-MM
  const { rows } = await q(
    `SELECT nv.ma_nhan_vien, nv.ho_ten, ct.ten_cong_ty,
            count(*) FILTER (WHERE b.loai = 'VAO')::int              AS so_lan_vao,
            count(*) FILTER (WHERE b.trang_thai = 'HOP_LE')::int     AS hop_le,
            count(*) FILTER (WHERE b.trang_thai = 'NGHI_NGO')::int   AS nghi_ngo,
            count(*) FILTER (WHERE b.trang_thai = 'NGOAI_VUNG')::int AS ngoai_vung,
            count(DISTINCT date(b.thoi_diem))::int                   AS so_ngay_cong
       FROM nhan_vien nv
       JOIN cong_ty ct ON ct.ma_cong_ty = nv.ma_cong_ty
       LEFT JOIN ban_ghi_cham_cong b
              ON b.ma_nhan_vien = nv.ma_nhan_vien
             AND to_char(b.thoi_diem, 'YYYY-MM') = $1
      GROUP BY nv.ma_nhan_vien, nv.ho_ten, ct.ten_cong_ty
      ORDER BY nv.ma_nhan_vien`,
    [thang]
  );
  res.json({ thang, dong: rows });
});

module.exports = router;
