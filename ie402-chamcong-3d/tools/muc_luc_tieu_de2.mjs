// Dòng tiêu đề "MỤC LỤC" đang là Title nên vẫn tự liệt kê trong chính mục lục.
// Đổi nó sang Normal text rồi định dạng tay (in đậm, canh giữa, 14pt) — trông y hệt
// tiêu đề nhưng không lọt vào mục lục nữa. Sau đó làm mới mục lục.
import { moTabDocs, sleep } from './gdoc_lib.mjs';

const { send, ev, bam, chup, choTaiXong, dungVaoTaiLieu } = await moTabDocs();
await choTaiXong();
await send('Page.bringToFront');
await dungVaoTaiLieu(220);
await sleep(1200);

const HOP = JSON.parse(await ev(
  `(() => { const e = [...document.querySelectorAll('.goog-toolbar-menu-button-caption')]
       .find(x => x.offsetParent !== null &&
             /^(Normal text|Title|Subtitle|Heading \d)$/i.test(x.textContent.trim()));
     if (!e) return 'null'; const b = e.getBoundingClientRect();
     return JSON.stringify({x: Math.round(b.x + b.width/2), y: Math.round(b.y + b.height/2)}); })()`) || 'null');
if (!HOP) throw new Error('Không thấy hộp kiểu đoạn');

// đưa con trỏ tới tiêu đề qua bảng dàn ý
const dy = JSON.parse(await ev(
  `(() => { const e = [...document.querySelectorAll('.navigation-item-content-container')]
       .find(x => x.offsetParent !== null && x.textContent.trim() === 'MỤC LỤC');
     if (!e) return 'null'; const b = e.getBoundingClientRect();
     return JSON.stringify({x: Math.round(b.x + b.width/2), y: Math.round(b.y + b.height/2)}); })()`) || 'null');
if (!dy) throw new Error('Không thấy MỤC LỤC trong bảng dàn ý');
await bam(dy.x, dy.y);
await sleep(2500);

const go = async (vk, key, code, mods = 0, text) => {
  await send('Input.dispatchKeyEvent', {
    type: text ? 'keyDown' : 'rawKeyDown', modifiers: mods,
    windowsVirtualKeyCode: vk, key, code, ...(text ? { text } : {}) });
  if (text) await send('Input.dispatchKeyEvent', { type: 'char', key, text });
  await send('Input.dispatchKeyEvent',
    { type: 'keyUp', modifiers: mods, windowsVirtualKeyCode: vk, key, code });
};

// --- Normal text
await bam(HOP.x, HOP.y);
await sleep(1500);
await go(78, 'N', 'KeyN', 0, 'N');       // gõ N -> nhảy tới "Normal text"
await sleep(1000);
await go(13, 'Enter', 'Enter');
await sleep(2500);

// --- chọn cả dòng rồi định dạng: đậm + canh giữa + cỡ 14
await go(36, 'Home', 'Home');
await sleep(400);
await go(35, 'End', 'End', 8);            // Shift+End
await sleep(600);
await go(66, 'b', 'KeyB', 2);             // Ctrl+B
await sleep(500);
await go(69, 'e', 'KeyE', 2 | 8);         // Ctrl+Shift+E : canh giữa
await sleep(800);

const oCo = JSON.parse(await ev(
  `(() => { const e = document.querySelector('#fontSizeSelect input, [aria-label*="Font size"] input, input#fontSizeSelect');
     if (!e) return 'null'; const b = e.getBoundingClientRect();
     return JSON.stringify({x: Math.round(b.x + b.width/2), y: Math.round(b.y + b.height/2)}); })()`) || 'null');
if (oCo) {
  await bam(oCo.x, oCo.y);
  await sleep(600);
  await go(65, 'a', 'KeyA', 2);
  await sleep(300);
  await send('Input.insertText', { text: '14' });
  await sleep(500);
  await go(13, 'Enter', 'Enter');
  await sleep(1500);
} else { console.log('Không thấy ô cỡ chữ — bỏ qua bước đặt 14pt'); }

// --- làm mới mục lục
await go(40, 'ArrowDown', 'ArrowDown');
await sleep(2000);
const rf = JSON.parse(await ev(
  `(() => { const e = [...document.querySelectorAll('button')]
       .filter(x => /update table of contents|cập nhật mục lục/i
                      .test((x.getAttribute('aria-label')||'') + ' ' + x.textContent))
       .map(x => x.getBoundingClientRect()).filter(b => b.width > 10);
     if (!e.length) return 'null'; const b = e[0];
     return JSON.stringify({x: Math.round(b.x + b.width/2), y: Math.round(b.y + b.height/2)}); })()`) || 'null');
console.log('Nút làm mới mục lục:', !!rf);
if (rf) { await bam(rf.x, rf.y); await sleep(4000); }
await chup('tt2-xong');
process.exit(0);
