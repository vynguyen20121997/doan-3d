// Thư viện dùng chung để điều khiển Google Docs qua CDP.
// Gom lại các thao tác đã kiểm chứng được trong quá trình làm đồ án.
export const PORT = process.env.CDP_PORT || 9333;
export const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

export async function moTabDocs() {
  const pages = (await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json())
    .filter((t) => t.type === 'page');
  const tab = pages.find((p) => p.url.includes('docs.google.com/document'));
  if (!tab) throw new Error('Không thấy tab Google Docs nào đang mở');

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

  const ev = async (bieu_thuc) => {
    const r = await send('Runtime.evaluate',
      { expression: bieu_thuc, awaitPromise: true, returnByValue: true, userGesture: true });
    if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description);
    return r.result.value;
  };
  const bam = async (x, y) => {
    await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x, y });
    for (const t of ['mousePressed', 'mouseReleased']) {
      await send('Input.dispatchMouseEvent', { type: t, x, y, button: 'left', clickCount: 1 });
    }
  };
  const phim = async (vk, k, code, mods = 0, cmds) => {
    await send('Input.dispatchKeyEvent', {
      type: 'rawKeyDown', modifiers: mods, windowsVirtualKeyCode: vk, key: k, code,
      ...(cmds ? { commands: cmds } : {}),
    });
    await send('Input.dispatchKeyEvent',
      { type: 'keyUp', modifiers: mods, windowsVirtualKeyCode: vk, key: k, code });
  };
  const chup = async (ten) => {
    const s = await send('Page.captureScreenshot', { format: 'png' });
    (await import('fs')).writeFileSync(`scratch/${ten}.png`, Buffer.from(s.data, 'base64'));
  };

  // Tìm phần tử hiển thị có nội dung khớp, trả về toạ độ tâm.
  const timChu = async (mau, duoiY = 0) => {
    const v = await ev(
      `(() => { const re = ${mau};
         const e = [...document.querySelectorAll('div,span,li,button')]
           .find(x => x.offsetParent !== null && x.children.length <= 1
                      && re.test(x.textContent.trim())
                      && x.getBoundingClientRect().y > ${duoiY});
         if (!e) return null; const b = e.getBoundingClientRect();
         return JSON.stringify({txt: e.textContent.trim(),
           x: Math.round(b.x + b.width/2), y: Math.round(b.y + b.height/2)}); })()`);
    return v ? JSON.parse(v) : null;
  };

  // Mở một lệnh bằng ô "tìm trong trình đơn" (Alt + /) — cách ổn định nhất.
  const lenhTrinhDon = async (tuKhoa, mauKetQua) => {
    await phim(191, '/', 'Slash', 1);
    await sleep(1600);
    await send('Input.insertText', { text: tuKhoa });
    await sleep(2000);
    const kq = await timChu(mauKetQua, 120);
    if (!kq) return null;
    await bam(kq.x, kq.y);
    return kq;
  };

  const dungVaoTaiLieu = async (lechY = 220) => {
    const e = JSON.parse(await ev(
      `(() => { const el = document.querySelector('.kix-appview-editor');
         const r = el.getBoundingClientRect();
         return JSON.stringify({x: Math.round(r.x + r.width/2),
                                y: Math.round(r.y + ${lechY})}); })()`));
    await bam(e.x, e.y);
    await sleep(600);
  };

  const choTaiXong = async () => {
    for (let i = 0; i < 40; i++) {
      if (await ev(`!!document.querySelector('.kix-appview-editor')`)) break;
      await sleep(1000);
    }
    await sleep(3500);
  };

  return { ws, send, ev, bam, phim, chup, timChu, lenhTrinhDon, dungVaoTaiLieu, choTaiXong, tab };
}
