// Sinh chuỗi băm bcrypt để dán vào seed.sql.
//   npm run hash            -> băm mật khẩu mặc định "123456"
//   npm run hash -- abc123  -> băm mật khẩu tự chọn
const bcrypt = require("bcryptjs");

const matKhau = process.argv[2] || "123456";
console.log(`mật khẩu : ${matKhau}`);
console.log(`bcrypt   : ${bcrypt.hashSync(matKhau, 10)}`);
