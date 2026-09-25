// Đổi dòng tiêu đề "MỤC LỤC" sang kiểu Title để nó không tự liệt kê trong chính mục lục.
//
// Lưu ý quan trọng: Google Docs vẽ nội dung bằng canvas — chữ trong tài liệu KHÔNG
// nằm trong DOM. Cách duy nhất định vị được một tiêu đề bằng mã là bấm vào nó trong
// bảng dàn ý (outline) bên trái.
import { moTabDocs, sleep } from './gdoc_lib.mjs';

const { send, ev, bam, chup, choTaiXong, dungVaoTaiLieu } = await moTabDocs();
await choTaiXong();
await send('Page.bringToFront');
await dungVaoTaiLieu(220);   // thanh công cụ chỉ hiện kiểu đoạn khi tài liệu có con trỏ
await sleep(1200);

// --- 0. đo sẵn vị trí hộp kiểu đoạn trên thanh công cụ
const HOP = JSON.parse(await ev(
  `(() => { const e = [...document.querySelectorAll('.goog-toolbar-menu-button-caption')]
       .find(x => x.offsetParent !== null &&
             /^(Normal text|Title|Subtitle|Heading \d)$/i.test(x.textContent.trim()));
     if (!e) return 'null'; const b = e.getBoundingClientRect();
     return JSON.stringify({x: Math.round(b.x + b.width/2), y: Math.round(b.y + b.height/2)}); })()`) || 'null');
if (!HOP) throw new Error('Không thấy hộp kiểu đoạn trên thanh công cụ');
console.log('Hộp kiểu đoạn @', HOP.x, HOP.y);

// --- 1. bấm mục "MỤC LỤC" trong bảng dàn ý để đưa con trỏ tới tiêu đề đó
const dy = JSON.parse(await ev(
  `(() => { const e = [...document.querySelectorAll('.navigation-item-content-container')]
       .find(x => x.offsetParent !== null && x.textContent.trim() === 'MỤC LỤC');
     if (!e) return 'null'; const b = e.getBoundingClientRect();
     return JSON.stringify({x: Math.round(b.x + b.width/2), y: Math.round(b.y + b.height/2)}); })()`) || 'null');
if (!dy) { await chup('tt-khong-thay-danyeu'); throw new Error('Không thấy MỤC LỤC trong bảng dàn ý'); }
await bam(dy.x, dy.y);
await sleep(2500);

const kieu = () => ev(
  `(() => { const e = [...document.querySelectorAll('.goog-toolbar-menu-button-caption')]
       .find(x => x.offsetParent !== null &&
             /^(Normal text|Title|Subtitle|Heading \d)$/i.test(x.textContent.trim()));
     return e ? e.textContent.trim() : null; })()`);
console.log('Kiểu trước khi đổi:', await kieu());

// --- 2. mở hộp kiểu đoạn rồi bấm "Title"
await bam(HOP.x, HOP.y);
await sleep(1800);

// Trình đơn kiểu đoạn không tra được bằng querySelector (Docs dựng nó ngoài DOM
// thường), nên điều hướng bằng bàn phím: gõ chữ T để nhảy tới "Title" rồi Enter.
await send('Input.dispatchKeyEvent',
  { type: 'keyDown', windowsVirtualKeyCode: 84, key: 'T', code: 'KeyT', text: 'T' });
await send('Input.dispatchKeyEvent',
  { type: 'char', key: 'T', text: 'T', unmodifiedText: 't' });
await send('Input.dispatchKeyEvent',
  { type: 'keyUp', windowsVirtualKeyCode: 84, key: 'T', code: 'KeyT' });
await sleep(1200);
await chup('tt-menu-sau-T');
await send('Input.dispatchKeyEvent',
  { type: 'rawKeyDown', windowsVirtualKeyCode: 13, key: 'Enter', code: 'Enter' });
await send('Input.dispatchKeyEvent',
  { type: 'keyUp', windowsVirtualKeyCode: 13, key: 'Enter', code: 'Enter' });
await sleep(3000);
console.log('Kiểu sau khi đổi:', await kieu());

// --- 3. làm mới mục lục (con trỏ đang ở tiêu đề, xuống một dòng là vào khối mục lục)
await send('Input.dispatchKeyEvent',
  { type: 'rawKeyDown', windowsVirtualKeyCode: 40, key: 'ArrowDown', code: 'ArrowDown' });
await send('Input.dispatchKeyEvent',
  { type: 'keyUp', windowsVirtualKeyCode: 40, key: 'ArrowDown', code: 'ArrowDown' });
await sleep(2000);
const rf = JSON.parse(await ev(
  `(() => { const e = [...document.querySelectorAll('button')]
       .filter(x => /update table of contents|cập nhật mục lục/i
                      .test((x.getAttribute('aria-label')||'') + ' ' + x.textContent))
       .map(x => x.getBoundingClientRect()).filter(b => b.width > 10);
     if (!e.length) return 'null'; const b = e[0];
     return JSON.stringify({lab: 'update table of contents',
       x: Math.round(b.x + b.width/2), y: Math.round(b.y + b.height/2)}); })()`) || 'null');
console.log('Nút làm mới:', rf && rf.lab);
if (rf) { await bam(rf.x, rf.y); await sleep(4000); }
await chup('tt-xong');
process.exit(0);
