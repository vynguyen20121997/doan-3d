// Dán nội dung checkpoint1.html vào tab Google Docs đang mở.
//
// Cách hoạt động:
//   1. Mở file HTML trong một tab mới của chính Chrome đang debug.
//   2. Chọn tất cả + copy -> clipboard thật của hệ điều hành (giữ được text/html).
//   3. Chuyển sang tab Google Docs, đặt con trỏ vào vùng soạn thảo, gửi Ctrl+V.
//
//   node tools/paste_to_gdoc.mjs

const PORT = process.env.CDP_PORT || 9333;
const HTML_PATH = process.env.HTML_PATH ||
  'file:///D:/UIT/ie402-chamcong-3d/scratch/checkpoint1.html';

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
  const send = (method, params = {}) =>
    new Promise((ok, err) => {
      const mid = ++id;
      waiting.set(mid, { ok, err });
      ws.send(JSON.stringify({ id: mid, method, params }));
    });
  return { ws, send };
}

async function pageSocket(targetId) {
  const { ws, send } = await openSocket(
    `ws://127.0.0.1:${PORT}/devtools/page/${targetId}`);
  const evaluate = async (expression) => {
    const r = await send('Runtime.evaluate', {
      expression, awaitPromise: true, returnByValue: true, userGesture: true,
    });
    if (r.exceptionDetails) {
      throw new Error(r.exceptionDetails.exception?.description || 'lỗi JS');
    }
    return r.result.value;
  };
  return { ws, send, evaluate };
}

async function listPages() {
  const r = await fetch(`http://127.0.0.1:${PORT}/json/list`);
  return (await r.json()).filter((t) => t.type === 'page');
}

async function main() {
  // --- tìm tab Google Docs
  let pages = await listPages();
  const docTab = pages.find((p) => p.url.includes('docs.google.com/document'));
  if (!docTab) throw new Error('Không thấy tab Google Docs nào đang mở');
  console.log('Tab Docs :', docTab.title);

  // --- mở tab chứa nội dung
  const ver = await (await fetch(`http://127.0.0.1:${PORT}/json/version`)).json();
  const browser = await openSocket(ver.webSocketDebuggerUrl);
  const { targetId } = await browser.send('Target.createTarget', { url: HTML_PATH });
  console.log('Đã mở tab nội dung, chờ tải…');
  await sleep(6000);

  // --- chọn tất cả + copy
  const src = await pageSocket(targetId);
  await src.send('Target.activateTarget', { targetId }).catch(() => {});
  await browser.send('Target.activateTarget', { targetId });
  await sleep(800);

  const info = await src.evaluate(
    `JSON.stringify({h1: document.querySelectorAll('h1').length,
                     tables: document.querySelectorAll('table').length,
                     imgs: document.querySelectorAll('img').length,
                     chars: document.body.innerText.length})`);
  console.log('Nội dung nguồn:', info);

  const copied = await src.evaluate(
    `(() => { const s = getSelection(); s.removeAllRanges();
       const r = document.createRange(); r.selectNodeContents(document.body);
       s.addRange(r); return document.execCommand('copy'); })()`);
  console.log('execCommand copy ->', copied);
  await sleep(1500);

  // --- sang tab Docs và dán
  const dst = await pageSocket(docTab.id);
  await browser.send('Target.activateTarget', { targetId: docTab.id });
  await sleep(1500);

  // đặt con trỏ vào vùng soạn thảo
  const box = await dst.evaluate(
    `(() => { const el = document.querySelector('.kix-appview-editor') || document.body;
       const r = el.getBoundingClientRect();
       return JSON.stringify({x: Math.round(r.x + r.width/2), y: Math.round(r.y + 120)}); })()`);
  const { x, y } = JSON.parse(box);
  for (const type of ['mousePressed', 'mouseReleased']) {
    await dst.send('Input.dispatchMouseEvent',
      { type, x, y, button: 'left', clickCount: 1 });
  }
  await sleep(700);

  // Ctrl+A - chon toan bo noi dung cu de ban dan de len
  await dst.send('Input.dispatchKeyEvent', {
    type: 'rawKeyDown', modifiers: 2, windowsVirtualKeyCode: 65,
    key: 'a', code: 'KeyA', commands: ['selectAll'],
  });
  await dst.send('Input.dispatchKeyEvent', {
    type: 'keyUp', modifiers: 2, windowsVirtualKeyCode: 65, key: 'a', code: 'KeyA',
  });
  await sleep(1200);

  // Ctrl+V — kèm commands:['paste'] để Chrome thực thi lệnh sửa đổi
  await dst.send('Input.dispatchKeyEvent', {
    type: 'rawKeyDown', modifiers: 2, windowsVirtualKeyCode: 86,
    key: 'v', code: 'KeyV', commands: ['paste'],
  });
  await dst.send('Input.dispatchKeyEvent', {
    type: 'keyUp', modifiers: 2, windowsVirtualKeyCode: 86,
    key: 'v', code: 'KeyV',
  });
  console.log('Đã gửi Ctrl+V, chờ Google Docs xử lý…');
  await sleep(20000);

  const after = await dst.evaluate(
    `JSON.stringify({chars: document.body.innerText.length,
                     snippet: document.body.innerText.replace(/\\s+/g,' ').slice(0, 200)})`);
  console.log('Sau khi dán:', after);

  // đóng tab nội dung
  await browser.send('Target.closeTarget', { targetId }).catch(() => {});
  src.ws.close(); dst.ws.close(); browser.ws.close();
  process.exit(0);
}

main().catch((e) => { console.error('LỖI:', e.message); process.exit(1); });
