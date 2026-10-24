'use strict';
const fs = require('fs');
const path = require('path');
const os = require('os');
const http = require('http');
const { spawn } = require('child_process');

const ROOT = path.resolve(__dirname, '..');
const OUT = path.join(ROOT, 'output');
if (!fs.existsSync(OUT)) fs.mkdirSync(OUT, { recursive: true });

async function connect(url) {
  const socket = new WebSocket(url);
  await new Promise((resolve, reject) => {
    socket.addEventListener('open', resolve, { once: true });
    socket.addEventListener('error', reject, { once: true });
  });
  let seq = 0;
  const pending = new Map();
  socket.addEventListener('message', event => {
    const msg = JSON.parse(event.data);
    const request = pending.get(msg.id);
    if (request) {
      pending.delete(msg.id);
      msg.error ? request.reject(new Error(JSON.stringify(msg.error))) : request.resolve(msg.result);
    }
  });
  return {
    send(method, params = {}) {
      return new Promise((resolve, reject) => {
        const id = ++seq;
        pending.set(id, { resolve, reject });
        socket.send(JSON.stringify({ id, method, params }));
      });
    }
  };
}

async function main() {
  const server = http.createServer((req, res) => {
    let filename = path.resolve(ROOT, '.' + decodeURIComponent(new URL(req.url, 'http://127.0.0.1').pathname));
    if (!fs.existsSync(filename) || !fs.statSync(filename).isFile()) {
      res.writeHead(404).end();
      return;
    }
    const types = { '.html': 'text/html; charset=utf-8', '.js': 'application/javascript', '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg', '.css': 'text/css' };
    res.writeHead(200, { 'Content-Type': types[path.extname(filename)] || 'text/plain' });
    fs.createReadStream(filename).pipe(res);
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const port = server.address().port;

  const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'wutang-card-edge-'));
  const edge = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
  const browser = spawn(edge, [
    '--headless=new',
    '--disable-gpu',
    '--no-first-run',
    '--no-default-browser-check',
    '--remote-debugging-port=0',
    `--user-data-dir=${profile}`,
    'about:blank'
  ], { stdio: 'ignore' });

  let cdp;
  try {
    let endpoint;
    const start = Date.now();
    while (!endpoint && Date.now() - start < 10000) {
      try {
        const res = await fetch('http://127.0.0.1:' + fs.readFileSync(path.join(profile, 'DevToolsActivePort'), 'utf8').split('\n')[0].trim() + '/json/list');
        const list = await res.json();
        const target = list.find(t => t.type === 'page' && !t.url.startsWith('chrome-extension:'));
        endpoint = target?.webSocketDebuggerUrl;
      } catch (e) {
        await new Promise(r => setTimeout(r, 200));
      }
    }
    if (!endpoint) throw new Error('无法连接 Edge 调试端口');

    cdp = await connect(endpoint);
    await cdp.send('Page.enable');
    await cdp.send('Runtime.enable');
    await cdp.send('Emulation.setDeviceMetricsOverride', { width: 500, height: 850, deviceScaleFactor: 2, mobile: false });
    await cdp.send('Page.navigate', { url: `http://127.0.0.1:${port}/frontend/index.html` });
    await new Promise(r => setTimeout(r, 2500));

    // 切换到成长页签（今日觉察牌）
    await cdp.send('Runtime.evaluate', {
      expression: `(function() {
        if (typeof switchMainTab === 'function') {
          switchMainTab('growth');
        } else {
          const tab = document.getElementById('tabGrowth');
          if (tab) tab.click();
        }
        const cardPill = document.getElementById('entryBtnCard');
        if (cardPill) cardPill.click();
      })()`
    });
    await new Promise(r => setTimeout(r, 1500));

    // 获取卡片元素并截图卡片区域
    // 获取卡片元素并截图卡片区域
    const clipRes = await cdp.send('Runtime.evaluate', {
      expression: `(function() {
        const el = document.getElementById('awarenessCardBox');
        if (!el) return null;
        el.scrollIntoView({ block: 'center' });
        const rect = el.getBoundingClientRect();
        return { x: rect.left, y: rect.top, width: rect.width, height: rect.height };
      })()`,
      returnByValue: true
    });

    const clip = clipRes.result.value;
    console.log('Card box rect:', clip);

    let shot;
    if (clip && clip.width > 0 && clip.height > 0) {
      shot = await cdp.send('Page.captureScreenshot', {
        format: 'png',
        clip: { x: Math.max(0, clip.x - 20), y: Math.max(0, clip.y - 20), width: clip.width + 40, height: clip.height + 40, scale: 2 }
      });
    } else {
      shot = await cdp.send('Page.captureScreenshot', { format: 'png' });
    }

    const outPath = path.join(OUT, 'starry-card-preview.png');
    fs.writeFileSync(outPath, Buffer.from(shot.data, 'base64'));
    console.log('[ok] Screenshot saved to', outPath);

  } finally {
    browser.kill();
    server.close();
  }
}

main().catch(console.error);
