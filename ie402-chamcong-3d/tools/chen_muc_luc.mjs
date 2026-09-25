// Chèn Mục lục tự động của Google Docs ngay dưới dòng "MỤC LỤC".
//
// Bài học từ các lần trước: trình đơn của Google Docs chỉ chịu thao tác tự động khi
// cửa sổ vừa mở và chưa bị tương tác nhiều, và ô "tìm trong trình đơn" (Alt + /)
// đáng tin hơn là bấm chuột vào từng cấp trình đơn.
//
//   node tools/chen_muc_luc.mjs        (chạy ngay sau khi mở Chrome)
import fs from 'fs';

const PORT = process.env.CDP_PORT || 9333;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const pages = (await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json())
  .filter((t) => t.type === 'page');
const tab = pages.find((p) => p.url.includes('docs.google.com/document'));
if (!tab) throw new Error('Không thấy tab Google Docs');
const ws = new WebSocket(`ws://127.0.0.1:${PORT}/devtools/page/${tab.id}`);
await new Promise((ok, err) => {
  ws.addEventListener('open', ok, { once: true });
  ws.addEventListener('error', err, { once: true });
});
let id = 0;
const waiting = new Map();
ws.addEventListener('message', (e) => {
  const m = JSON.parse(e.data);
  if (m.id && waiting.has(m.id)) {
    const { ok, err } = waiting.get(m.id);
    waiting.delete(m.id);
    m.error ? err(new Error(JSON.stringify(m.error))) : ok(m.result);
  }
});
const send = (method, params = {}) =>
  new Promise((ok, err) => {
    const mid = ++id;
    waiting.set(mid, { ok, err });
    ws.send(JSON.stringify({ id: mid, method, params }));
  });
const ev = async (x) => {
  const r = await send('Runtime.evaluate',
    { expression: x, awaitPromise: true, returnByValue: true, userGesture: true });
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description);
  return r.result.value;
};
const click = async (x, y) => {
  await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x, y });
  for (const t of ['mousePressed', 'mouseReleased']) {
    await send('Input.dispatchMouseEvent', { type: t, x, y, button: 'left', clickCount: 1 });
  }
};
const key = async (vk, k, code, mods = 0, cmds) => {
  await send('Input.dispatchKeyEvent', {
    type: 'rawKeyDown', modifiers: mods, windowsVirtualKeyCode: vk, key: k, code,
    ...(cmds ? { commands: cmds } : {}),
  });
  await send('Input.dispatchKeyEvent',
    { type: 'keyUp', modifiers: mods, windowsVirtualKeyCode: vk, key: k, code });
};
const shot = async (n) => {
  const s = await send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync(`scratch/${n}.png`, Buffer.from(s.data, 'base64'));
};

// --- chờ tài liệu tải xong
for (let i = 0; i < 40; i++) {
  if (await ev(`!!document.querySelector('.kix-appview-editor')`)) break;
  await sleep(1000);
}
await sleep(4000);
await send('Page.bringToFront');

// --- 1. đặt con trỏ vào tài liệu rồi tìm dòng "MỤC LỤC"
const ed = JSON.parse(await ev(
  `(() => { const e = document.querySelector('.kix-appview-editor');
     const r = e.getBoundingClientRect();
     return JSON.stringify({x: Math.round(r.x + r.width/2), y: Math.round(r.y + 220)}); })()`));
await click(ed.x, ed.y);
await sleep(700);

await key(70, 'f', 'KeyF', 2, ['find']);
await sleep(1600);
await send('Input.insertText', { text: 'MỤC LỤC' });
await sleep(1800);
await key(13, 'Enter', 'Enter');
await sleep(1400);

// đóng thanh tìm kiếm bằng đúng nút Close của nó, nếu không nó sẽ chặn trình đơn
await ev(`(() => { const b = [...document.querySelectorAll('[aria-label*=Close],[aria-label*=Đóng]')]
     .find(e => e.offsetParent !== null); if (b) b.click(); return !!b; })()`);
await sleep(1200);
console.log('Đã nhảy tới dòng MỤC LỤC');

// --- 2. xuống cuối dòng, tạo một dòng trống bên dưới
await key(35, 'End', 'End');
await sleep(400);
await key(13, 'Enter', 'Enter');
await sleep(900);

// --- 3. Alt + / rồi gõ "Table of contents", bấm vào kết quả
await key(191, '/', 'Slash', 1);
await sleep(1800);
await send('Input.insertText', { text: 'Table of contents' });
await sleep(2200);
await shot('ml-menusearch');

const ketQua = await ev(
  `(() => { const e = [...document.querySelectorAll('div,span')]
       .find(x => x.offsetParent !== null && x.children.length <= 1
                  && /^(Table of contents|Mục lục)$/i.test(x.textContent.trim())
                  && x.getBoundingClientRect().y > 200);
     if (!e) return null; const b = e.getBoundingClientRect();
     return JSON.stringify({txt: e.textContent.trim(),
       x: Math.round(b.x + b.width/2), y: Math.round(b.y + b.height/2)}); })()`);
if (!ketQua) { await shot('ml-khong-thay'); throw new Error('Không thấy kết quả "Table of contents"'); }
const kq = JSON.parse(ketQua);
console.log('Bấm kết quả:', kq.txt, '@', kq.x, kq.y);
await click(kq.x, kq.y);
await sleep(2500);
await shot('ml-submenu');

// --- 4. chọn kiểu mục lục (bản có số trang)
const kieu = await ev(
  `(() => { const ds = [...document.querySelectorAll('.goog-menuitem,[role=menuitem],div')]
       .filter(e => e.offsetParent !== null && e.children.length <= 2
                    && /page numbers|số trang/i.test(e.textContent))
       .map(e => { const b = e.getBoundingClientRect();
          return {t: e.textContent.trim().slice(0,40),
                  x: Math.round(b.x + b.width/2), y: Math.round(b.y + b.height/2),
                  w: Math.round(b.width), h: Math.round(b.height)}; })
       .filter(o => o.w > 80 && o.h > 15 && o.h < 90);
     return ds.length ? JSON.stringify(ds[0]) : null; })()`);
if (kieu) {
  const k = JSON.parse(kieu);
  console.log('Chọn kiểu:', k.t);
  await click(k.x, k.y);
} else {
  console.log('Không thấy kiểu "có số trang", chọn mục đầu tiên của submenu');
  const dau = await ev(
    `(() => { const e = [...document.querySelectorAll('.goog-menuitem')]
         .find(x => x.offsetParent !== null);
       if (!e) return null; const b = e.getBoundingClientRect();
       return JSON.stringify({x: Math.round(b.x + b.width/2), y: Math.round(b.y + b.height/2)}); })()`);
  if (dau) { const d = JSON.parse(dau); await click(d.x, d.y); }
}
await sleep(5000);
await shot('ml-xong');
console.log('Xong — xem scratch/ml-xong.png');

ws.close();
process.exit(0);
