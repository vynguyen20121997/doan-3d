// Đặt font cho toàn bộ tài liệu Google Docs: chọn tất cả -> mở hộp font -> bấm đúng mục.
//   node tools/set_font2.mjs "Times New Roman"
import fs from 'fs';

const PORT = process.env.CDP_PORT || 9333;
const FONT = process.argv[2] || 'Times New Roman';
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function openSocket(url) {
  const ws = new WebSocket(url);
  await new Promise((ok, err) => {
    ws.addEventListener('open', ok, { once: true });
    ws.addEventListener('error', err, { once: true });
  });
  let id = 0;
  const waiting = new Map();
  ws.addEventListener('message', (ev) => {
    const m = JSON.parse(ev.data);
    if (m.id && waiting.has(m.id)) {
      const { ok, err } = waiting.get(m.id);
      waiting.delete(m.id);
      m.error ? err(new Error(JSON.stringify(m.error))) : ok(m.result);
    }
  });
  return {
    ws,
    send: (method, params = {}) =>
      new Promise((ok, err) => {
        const mid = ++id;
        waiting.set(mid, { ok, err });
        ws.send(JSON.stringify({ id: mid, method, params }));
      }),
  };
}

const pages = (await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json())
  .filter((t) => t.type === 'page');
const tab = pages.find((p) => p.url.includes('docs.google.com/document'));
if (!tab) throw new Error('Không thấy tab Google Docs');
const { ws, send } = await openSocket(`ws://127.0.0.1:${PORT}/devtools/page/${tab.id}`);

const evaluate = async (expression) => {
  const r = await send('Runtime.evaluate',
    { expression, awaitPromise: true, returnByValue: true, userGesture: true });
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description);
  return r.result.value;
};
const clickAt = async (x, y) => {
  await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x, y });
  for (const type of ['mousePressed', 'mouseReleased']) {
    await send('Input.dispatchMouseEvent', { type, x, y, button: 'left', clickCount: 1 });
  }
};
const rectOf = async (sel) => {
  const v = await evaluate(
    `(() => { const e = document.querySelector(${JSON.stringify(sel)});
       if (!e) return null; const r = e.getBoundingClientRect();
       return JSON.stringify({x: Math.round(r.x + r.width/2), y: Math.round(r.y + r.height/2)}); })()`);
  return v ? JSON.parse(v) : null;
};

// 1. chọn toàn bộ tài liệu
const ed = await rectOf('.kix-appview-editor');
await clickAt(ed.x, ed.y - 100);
await sleep(600);
await send('Input.dispatchKeyEvent', {
  type: 'rawKeyDown', modifiers: 2, windowsVirtualKeyCode: 65,
  key: 'a', code: 'KeyA', commands: ['selectAll'],
});
await send('Input.dispatchKeyEvent',
  { type: 'keyUp', modifiers: 2, windowsVirtualKeyCode: 65, key: 'a', code: 'KeyA' });
await sleep(1200);
console.log('Đã chọn toàn bộ tài liệu');

// 2. mở hộp chọn font
const ff = await rectOf('#docs-font-family');
await clickAt(ff.x, ff.y);
await sleep(2200);

// 3. tìm đúng mục font trong menu đang mở (so khớp toàn bộ nhãn)
const found = await evaluate(
  `(() => {
     const want = ${JSON.stringify(FONT)};
     const all = [...document.querySelectorAll('div,span,li')].filter((e) => {
       if (e.offsetParent === null) return false;
       if (e.children.length > 1) return false;
       return e.textContent.trim() === want;
     });
     if (!all.length) return null;
     const e = all[0];
     const b = e.getBoundingClientRect();
     return JSON.stringify({x: Math.round(b.x + b.width/2), y: Math.round(b.y + b.height/2),
                            w: Math.round(b.width)});
   })()`);

if (!found) {
  const shot = await send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync('scratch/font-menu-fail.png', Buffer.from(shot.data, 'base64'));
  throw new Error(`Không thấy mục "${FONT}" trong menu (đã chụp scratch/font-menu-fail.png)`);
}
const pos = JSON.parse(found);
console.log('Thấy mục font tại', pos);
await clickAt(pos.x, pos.y);
await sleep(3500);

const now = await evaluate(`document.querySelector('#docs-font-family').innerText.trim()`);
console.log('Hộp font sau khi chọn:', JSON.stringify(now));

const shot = await send('Page.captureScreenshot', { format: 'png' });
fs.writeFileSync('scratch/after-font.png', Buffer.from(shot.data, 'base64'));
console.log('Đã lưu scratch/after-font.png');

ws.close();
process.exit(0);
