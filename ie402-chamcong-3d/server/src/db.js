// Kết nối PostgreSQL/PostGIS dùng chung cho toàn bộ máy chủ.
const { Pool } = require("pg");

const pool = new Pool({
  host: process.env.PGHOST || "127.0.0.1",
  port: Number(process.env.PGPORT || 55432),
  user: process.env.PGUSER || "postgres",
  password: process.env.PGPASSWORD || "",
  database: process.env.PGDATABASE || "chamcong3d",
  max: 10,
});

// Ghi log truy vấn chậm để tiện theo dõi khi trình diễn.
async function q(sql, params) {
  const t0 = Date.now();
  const res = await pool.query(sql, params);
  const ms = Date.now() - t0;
  if (ms > 200) {
    console.warn(`[db] truy vấn ${ms} ms: ${sql.split("\n")[0].slice(0, 70)}…`);
  }
  return res;
}

module.exports = { pool, q };
