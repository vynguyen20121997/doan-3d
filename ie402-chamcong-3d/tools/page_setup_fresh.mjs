// Đặt khổ giấy A4 + lề giống mẫu nhóm 9.
// CHẠY NGAY SAU KHI MỞ CHROME: trình đơn Google Docs chỉ chịu nghe thao tác
// tự động khi cửa sổ vừa mở và chưa bị tương tác nhiều.
//   node tools/page_setup_fresh.mjs
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
const findExact = async (t) => {
  const v = await ev(
    `(() => { const e = [...document.querySelectorAll('div,span,li,button')]
         .find(x => x.offsetParent !== null && x.children.length <= 1
                    && x.textContent.trim() === ${JSON.stringify(t)});
       if (!e) return null; const b = e.getBoundingClientRect();
       return JSON.stringify({x: Math.round(b.x + b.width/2), y: Math.round(b.y + b.height/2)}); })()`);
  return v ? JSON.parse(v) : null;
};
const PAPER = '/^(Letter|Legal|Statement|Executive|Folio|Tabloid|A3|A4|A5|B4|B5)\\s*\\(/';
const paperText = () => ev(
  `(() => { const e = [...document.querySelectorAll('div,span')]
       .find(x => x.offsetParent && x.children.length <= 1 && ${PAPER}.test(x.textContent.trim()));
     return e ? e.textContent.trim() : null; })()`);

// chờ tài liệu tải xong
for (let i = 0; i < 30; i++) {
  if (await ev(`!!document.querySelector('.kix-appview-editor')`)) break;
  await sleep(1000);
}
await sleep(3000);

// --- File > Page setup
const file = await findExact('File');
if (!file) throw new Error('Không thấy menu File');
await click(file.x, file.y);
await sleep(1800);
const ps = await findExact('Page setup');
if (!ps) { await shot('pf-file'); throw new Error('Không thấy Page setup'); }
await click(ps.x, ps.y);
await sleep(3000);
if (!(await ev(`!!document.querySelector('input[type=radio][value=Portrait]')`))) {
  await shot('pf-nodlg');
  throw new Error('Hộp thoại Page setup không mở');
}
console.log('Hộp thoại Page setup đã mở');

// --- Apply to: Whole document
const sel = await findExact('Selected content');
if (sel) {
  await click(sel.x, sel.y);
  await sleep(1200);
  const wd = await findExact('Whole document');
  if (wd) await click(wd.x, wd.y);
  await sleep(1500);
  console.log('Apply to -> Whole document');
}

// --- khổ giấy -> A4, chọn bằng phím mũi tên cho chắc
const ORDER = ['Letter', 'Tabloid', 'Legal', 'Statement', 'Executive', 'Folio',
               'A3', 'A4', 'A5', 'B4', 'B5'];
const cur = await paperText();
console.log('Khổ giấy đang là:', cur);
if (cur && !cur.startsWith('A4')) {
  const p = JSON.parse(await ev(
    `(() => { const e = [...document.querySelectorAll('div,span')]
         .find(x => x.offsetParent && x.children.length <= 1 && ${PAPER}.test(x.textContent.trim()));
       const b = e.getBoundingClientRect();
       return JSON.stringify({x: Math.round(b.x + b.width/2), y: Math.round(b.y + b.height/2)}); })()`));
  await click(p.x, p.y);
  await sleep(1800);
  const step = ORDER.indexOf('A4') - ORDER.findIndex((n) => cur.startsWith(n));
  console.log('di chuyển', step, 'mục trong danh sách');
  for (let i = 0; i < Math.abs(step); i++) {
    await key(step > 0 ? 40 : 38, step > 0 ? 'ArrowDown' : 'ArrowUp',
              step > 0 ? 'ArrowDown' : 'ArrowUp');
    await sleep(350);
  }
  await shot('pf-highlight');
  await key(13, 'Enter', 'Enter');
  await sleep(2000);
}
const after = await paperText();
console.log('Khổ giấy sau khi chọn:', after);
if (!after || !after.startsWith('A4')) { await shot('pf-wrong'); throw new Error('Chưa chọn được A4'); }

// --- lề Top / Bottom / Left / Right
const want = ['0.79', '0.79', '1.18', '0.79'];
for (let i = 0; i < 4; i++) {
  const b = JSON.parse(await ev(
    `(() => { const l = [...document.querySelectorAll('input[type=text]')]
         .filter(x => x.offsetParent !== null && /MaterialdesignGm3WizTextField/.test(x.className));
       const e = l[${i}]; if (!e) return 'null'; const r = e.getBoundingClientRect();
       return JSON.stringify({x: Math.round(r.x + r.width/2), y: Math.round(r.y + r.height/2)}); })()`));
  await click(b.x, b.y);
  await sleep(450);
  await key(65, 'a', 'KeyA', 2, ['selectAll']);
  await sleep(300);
  await send('Input.insertText', { text: want[i] });
  await sleep(600);
}
const vals = await ev(
  `JSON.stringify([...document.querySelectorAll('input[type=text]')]
     .filter(x => x.offsetParent !== null && /MaterialdesignGm3WizTextField/.test(x.className))
     .map(x => x.value))`);
console.log('Lề trong hộp thoại (T/B/L/R):', vals);
await shot('pf-before-ok');

const ok = await findExact('OK');
await click(ok.x, ok.y);
await sleep(4000);
await shot('pf-done');
console.log('Đã bấm OK');

ws.close();
process.exit(0);
