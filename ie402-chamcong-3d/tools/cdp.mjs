// Tiện ích nói chuyện CDP trực tiếp với Chrome đang mở cổng 9333.
// Dùng WebSocket có sẵn của Node (>= 22), không cần cài thêm gói.
//
//   node tools/cdp.mjs eval "<biểu thức JS>"
//   node tools/cdp.mjs paste-html <đường dẫn file .html>

const PORT = process.env.CDP_PORT || 9333;

async function firstPage() {
  const res = await fetch(`http://127.0.0.1:${PORT}/json/list`);
  const list = await res.json();
  const page = list.find((t) => t.type === 'page');
  if (!page) throw new Error('Không tìm thấy tab nào');
  return page;
}

export async function connect() {
  const page = await firstPage();
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((ok, err) => {
    ws.addEventListener('open', ok, { once: true });
    ws.addEventListener('error', err, { once: true });
  });

  let id = 0;
  const waiting = new Map();
  ws.addEventListener('message', (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.id && waiting.has(msg.id)) {
      const { ok, err } = waiting.get(msg.id);
      waiting.delete(msg.id);
      msg.error ? err(new Error(JSON.stringify(msg.error))) : ok(msg.result);
    }
  });

  const send = (method, params = {}) =>
    new Promise((ok, err) => {
      const mid = ++id;
      waiting.set(mid, { ok, err });
      ws.send(JSON.stringify({ id: mid, method, params }));
    });

  const evaluate = async (expression, awaitPromise = true) => {
    const r = await send('Runtime.evaluate', {
      expression,
      awaitPromise,
      returnByValue: true,
      userGesture: true,
    });
    if (r.exceptionDetails) {
      throw new Error(r.exceptionDetails.exception?.description || 'lỗi JS');
    }
    return r.result.value;
  };

  return { page, send, evaluate, close: () => ws.close() };
}

// ---------------------------------------------------------------------------
if (process.argv[2]) {
  const [, , cmd, arg] = process.argv;
  const c = await connect();

  if (cmd === 'eval') {
    console.log(JSON.stringify(await c.evaluate(arg), null, 1));
  } else if (cmd === 'url') {
    console.log(c.page.url, '|', c.page.title);
  } else {
    console.log('lệnh không hợp lệ');
  }
  c.close();
  process.exit(0);
}
