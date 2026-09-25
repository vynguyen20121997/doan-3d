// Chèn trang "MỤC LỤC" + mục lục tự động ngay TRƯỚC dòng "DANH MỤC HÌNH".
// Bản checkpoint 2 không có sẵn dòng MỤC LỤC nên phải tự tạo.
//   node tools/chen_muc_luc2.mjs        (chạy ngay sau khi tải lại trang)
import { moTabDocs, sleep } from './gdoc_lib.mjs';

const { send, ev, bam, phim, chup, timChu, lenhTrinhDon, dungVaoTaiLieu, choTaiXong }
  = await moTabDocs();

await choTaiXong();
await send('Page.bringToFront');
await dungVaoTaiLieu(220);

// --- 1. nhảy tới dòng "DANH MỤC HÌNH"
await phim(70, 'f', 'KeyF', 2, ['find']);
await sleep(1600);
await send('Input.insertText', { text: 'DANH MỤC HÌNH' });
await sleep(1800);
await phim(13, 'Enter', 'Enter');
await sleep(1400);
// đóng thanh tìm kiếm bằng đúng nút Close — nếu còn mở nó chặn mọi trình đơn
await ev(`(() => { const b = [...document.querySelectorAll('[aria-label*=Close],[aria-label*=Đóng]')]
     .find(e => e.offsetParent !== null); if (b) b.click(); return !!b; })()`);
await sleep(1200);
console.log('Đã nhảy tới DANH MỤC HÌNH');

// --- 2. về đầu dòng, chèn hai dòng trống phía trên
await phim(36, 'Home', 'Home');
await sleep(400);
await phim(13, 'Enter', 'Enter');   // đẩy DANH MỤC HÌNH xuống
await sleep(600);
await phim(13, 'Enter', 'Enter');
await sleep(600);
await phim(38, 'ArrowUp', 'ArrowUp');
await sleep(300);
await phim(38, 'ArrowUp', 'ArrowUp');
await sleep(600);

// --- 3. gõ tiêu đề MỤC LỤC rồi xuống dòng trống bên dưới
await send('Input.insertText', { text: 'MỤC LỤC' });
await sleep(1200);
await phim(40, 'ArrowDown', 'ArrowDown');
await sleep(300);
await phim(36, 'Home', 'Home');
await sleep(600);
await chup('ml2-truoc-khi-chen');

// --- 4. Alt + / -> "table of contents" -> bản có số trang
const kq = await lenhTrinhDon('table of contents', '/table of contents/i');
if (!kq) { await chup('ml2-khong-thay'); throw new Error('Không thấy lệnh Table of contents'); }
console.log('Bấm:', kq.txt);
await sleep(2500);
await chup('ml2-sau-khi-chen');
console.log('Xong — xem scratch/ml2-sau-khi-chen.png');
process.exit(0);
