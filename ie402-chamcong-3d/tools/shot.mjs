// Chụp màn hình tab Google Docs, có thể cuộn tới đầu tài liệu trước.
//   node tools/shot.mjs <ten-file> [top|none] [so-lan-pagedown]
import fs from 'fs';

const PORT = process.env.CDP_PORT || 9333;
const NAME = process.argv[2] || 'doc';
const MODE = process.argv[3] || 'none';
const PGDN = parseInt(process.argv[4] || '0', 10);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const ws0 = await (async () => {
  const pages = (await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json())
    .filter((t) => t.type === 'page');
  const tab = pages.find((p) => p.url.includes('docs.google.com/document'));
  const ws = new WebSocket(`ws://127.0.0.1:${PORT}/devtools/page/${tab.id}`);
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
})();

const { ws, send } = ws0;
const key = async (vk, k, code, mods = 0, cmds) => {
  await send('Input.dispatchKeyEvent', {
    type: 'rawKeyDown', modifiers: mods, windowsVirtualKeyCode: vk,
    key: k, code, ...(cmds ? { commands: cmds } : {}),
  });
  await send('Input.dispatchKeyEvent',
    { type: 'keyUp', modifiers: mods, windowsVirtualKeyCode: vk, key: k, code });
};

const rect = await send('Runtime.evaluate', {
  expression: `(() => { const e = document.querySelector('.kix-appview-editor');
     const b = e.getBoundingClientRect();
     return JSON.stringify({x: Math.round(b.x + b.width/2), y: Math.round(b.y + 150)}); })()`,
  returnByValue: true,
});
const { x, y } = JSON.parse(rect.result.value);
for (const type of ['mousePressed', 'mouseReleased']) {
  await send('Input.dispatchMouseEvent', { type, x, y, button: 'left', clickCount: 1 });
}
await sleep(400);

if (MODE === 'top') {
  await key(36, 'Home', 'Home', 2);   // Ctrl+Home
  await sleep(2500);
}
for (let i = 0; i < PGDN; i++) {
  await key(34, 'PageDown', 'PageDown');
  await sleep(500);
}
await sleep(1500);

const s = await send('Page.captureScreenshot', { format: 'png' });
fs.writeFileSync(`scratch/${NAME}.png`, Buffer.from(s.data, 'base64'));
console.log('ảnh ->', `scratch/${NAME}.png`);
ws.close();
process.exit(0);
