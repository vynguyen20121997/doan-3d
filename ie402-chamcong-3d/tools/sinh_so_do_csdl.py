# -*- coding: utf-8 -*-
"""
Sinh sơ đồ cơ sở dữ liệu (database diagram) TRỰC TIẾP từ CSDL đang chạy.

Đọc pg_catalog / information_schema để lấy bảng, cột, kiểu, khoá chính, khoá ngoại,
ràng buộc và chỉ mục, rồi xuất ra:
  - scratch/so-do-csdl.mmd   : mã Mermaid erDiagram (sơ đồ vật lý)
  - scratch/mo-ta-bang.json  : mô tả chi tiết để chèn vào báo cáo

Nhờ đọc thẳng từ CSDL nên sơ đồ luôn khớp với hệ thống thật, không sợ lệch
so với tài liệu.

    python tools/sinh_so_do_csdl.py
"""
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PSQL = r"D:\pgportable\pgsql\bin\psql.exe"
CONN = ["-h", "127.0.0.1", "-p", "55432", "-U", "postgres", "-d", "chamcong3d"]
OUT_MMD = os.path.join(ROOT, "scratch", "so-do-csdl.mmd")
OUT_JSON = os.path.join(ROOT, "scratch", "mo-ta-bang.json")


def truy_van(sql):
    """Chạy một câu SQL, trả về danh sách dòng đã tách theo dấu |.

    Lưu ý: bảng spatial_ref_sys là bảng hệ thống do PostGIS tạo ra để lưu
    danh mục hệ quy chiếu, không thuộc lược đồ của đề tài nên bị loại khỏi
    mọi truy vấn bên dưới.
    """
    env = dict(os.environ, PGCLIENTENCODING="UTF8")
    r = subprocess.run([PSQL] + CONN + ["-tAF", "|", "-c", sql],
                       capture_output=True, text=True, encoding="utf-8", env=env)
    if r.returncode != 0:
        raise SystemExit("Lỗi psql: " + r.stderr)
    return [d.split("|") for d in r.stdout.strip().split("\n") if d.strip()]


# --- cột của từng bảng --------------------------------------------------
COT = """
SELECT c.relname, a.attname,
       format_type(a.atttypid, a.atttypmod),
       CASE WHEN a.attnotnull THEN 'NOT NULL' ELSE '' END,
       COALESCE(pg_get_expr(d.adbin, d.adrelid), '')
  FROM pg_class c
  JOIN pg_namespace n ON n.oid = c.relnamespace
  JOIN pg_attribute a ON a.attrelid = c.oid
  LEFT JOIN pg_attrdef d ON d.adrelid = c.oid AND d.adnum = a.attnum
 WHERE n.nspname = 'public' AND c.relkind = 'r'
   AND c.relname <> 'spatial_ref_sys'
   AND a.attnum > 0 AND NOT a.attisdropped
 ORDER BY c.relname, a.attnum;
"""

# --- khoá chính ---------------------------------------------------------
KHOA_CHINH = """
SELECT c.relname, a.attname
  FROM pg_constraint k
  JOIN pg_class c ON c.oid = k.conrelid
  JOIN pg_namespace n ON n.oid = c.relnamespace
  JOIN unnest(k.conkey) AS col(num) ON true
  JOIN pg_attribute a ON a.attrelid = c.oid AND a.attnum = col.num
 WHERE k.contype = 'p' AND n.nspname = 'public' AND c.relname <> 'spatial_ref_sys'
 ORDER BY c.relname;
"""

# --- khoá ngoại ---------------------------------------------------------
KHOA_NGOAI = """
SELECT c.relname AS bang_con, a.attname AS cot_con,
       f.relname AS bang_cha, af.attname AS cot_cha, k.conname
  FROM pg_constraint k
  JOIN pg_class c  ON c.oid = k.conrelid
  JOIN pg_class f  ON f.oid = k.confrelid
  JOIN pg_namespace n ON n.oid = c.relnamespace
  JOIN unnest(k.conkey)  WITH ORDINALITY AS cc(num, ord) ON true
  JOIN unnest(k.confkey) WITH ORDINALITY AS ff(num, ord) ON ff.ord = cc.ord
  JOIN pg_attribute a  ON a.attrelid  = c.oid AND a.attnum  = cc.num
  JOIN pg_attribute af ON af.attrelid = f.oid AND af.attnum = ff.num
 WHERE k.contype = 'f' AND n.nspname = 'public' AND c.relname <> 'spatial_ref_sys'
 ORDER BY c.relname;
"""

# --- ràng buộc duy nhất -------------------------------------------------
DUY_NHAT = """
SELECT c.relname, k.conname, pg_get_constraintdef(k.oid)
  FROM pg_constraint k
  JOIN pg_class c ON c.oid = k.conrelid
  JOIN pg_namespace n ON n.oid = c.relnamespace
 WHERE k.contype = 'u' AND n.nspname = 'public' AND c.relname <> 'spatial_ref_sys'
 ORDER BY c.relname;
"""

# --- chỉ mục ------------------------------------------------------------
CHI_MUC = """
SELECT tablename, indexname, indexdef
  FROM pg_indexes
 WHERE schemaname = 'public'
   AND tablename <> 'spatial_ref_sys'
   AND indexname NOT LIKE '%_pkey'
 ORDER BY tablename;
"""

# --- hàm và trigger -----------------------------------------------------
HAM = """
SELECT p.proname, pg_get_function_arguments(p.oid), pg_get_function_result(p.oid)
  FROM pg_proc p JOIN pg_namespace n ON n.oid = p.pronamespace
 WHERE n.nspname = 'public'
   AND p.proname IN ('kiem_tra_bao_ham','kiem_tra_r2','tinh_dai_cao_do','trg_dong_bo_cao_do')
 ORDER BY p.proname;
"""


def main():
    cot, kc, kn = truy_van(COT), truy_van(KHOA_CHINH), truy_van(KHOA_NGOAI)
    dn, cm, ham = truy_van(DUY_NHAT), truy_van(CHI_MUC), truy_van(HAM)

    pk = {}
    for bang, c in kc:
        pk.setdefault(bang, set()).add(c)
    fk = {}
    for con, cc, cha, ccha, ten in kn:
        fk.setdefault(con, set()).add(cc)

    bang = {}
    for b, ten_cot, kieu, notnull, mac_dinh in cot:
        bang.setdefault(b, []).append({
            "cot": ten_cot, "kieu": kieu,
            "notnull": notnull == "NOT NULL", "mac_dinh": mac_dinh,
            "pk": ten_cot in pk.get(b, set()),
            "fk": ten_cot in fk.get(b, set()),
        })

    # ---------- Mermaid ----------
    def gon(k):
        """Rút gọn kiểu dữ liệu cho vừa sơ đồ."""
        k = (k.replace("character varying", "varchar")
              .replace("timestamp with time zone", "timestamptz")
              .replace("double precision", "float8")
              .replace("integer", "int"))
        return k.replace("(", "_").replace(")", "").replace(",", "_").replace(" ", "_")

    d = ["erDiagram"]
    for con, cc, cha, ccha, ten in kn:
        d.append("    %s ||--o{ %s : \"%s\"" % (cha.upper(), con.upper(), cc))
    for b in sorted(bang):
        d.append("    %s {" % b.upper())
        for c in bang[b]:
            nhan = "PK" if c["pk"] else ("FK" if c["fk"] else "")
            d.append("        %s %s %s" % (gon(c["kieu"]), c["cot"], nhan))
        d.append("    }")

    os.makedirs(os.path.dirname(OUT_MMD), exist_ok=True)
    with open(OUT_MMD, "w", encoding="utf-8") as f:
        f.write("\n".join(d))

    mo_ta = {
        "bang": bang,
        "khoa_ngoai": [{"bang_con": a, "cot_con": b2, "bang_cha": c2,
                        "cot_cha": d2, "ten": e} for a, b2, c2, d2, e in kn],
        "duy_nhat": [{"bang": a, "ten": b2, "dinh_nghia": c2} for a, b2, c2 in dn],
        "chi_muc": [{"bang": a, "ten": b2, "dinh_nghia": c2} for a, b2, c2 in cm],
        "ham": [{"ten": a, "tham_so": b2, "tra_ve": c2} for a, b2, c2 in ham],
    }
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(mo_ta, f, ensure_ascii=False, indent=1)

    print("Số bảng      :", len(bang))
    print("Số cột       :", sum(len(v) for v in bang.values()))
    print("Khoá ngoại   :", len(kn))
    print("Ràng buộc UQ :", len(dn))
    print("Chỉ mục      :", len(cm))
    print("Hàm nghiệp vụ:", ", ".join(h[0] for h in ham))
    print("->", OUT_MMD)
    print("->", OUT_JSON)


if __name__ == "__main__":
    main()
