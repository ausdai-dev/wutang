'use strict';
const fs = require('fs');
const path = require('path');
const os = require('os');
const http = require('http');
const { spawn } = require('child_process');

const ROOT = path.resolve(__dirname, '..');
const OUT = path.join(ROOT, 'output');
const wait = ms => new Promise(resolve => setTimeout(resolve, ms));

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
    socket,
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
  const source = fs.readFileSync(path.join(ROOT, 'frontend/index.html'), 'utf8');
  const preview = source.replace(/<head>/i, '<head>\n<base href="../frontend/">');
  fs.writeFileSync(path.join(OUT, 'sleep-feature-preview.html'), preview);

  const server = http.createServer((req, res) => {
    let filename;
    try {
      filename = path.resolve(ROOT, '.' + decodeURIComponent(new URL(req.url, 'http://127.0.0.1').pathname));
    } catch {
      res.writeHead(400).end();
      return;
    }
    if (!filename.startsWith(ROOT + path.sep)) { res.writeHead(403).end(); return; }
    if (!fs.existsSync(filename) || !fs.statSync(filename).isFile()) { res.writeHead(404).end(); return; }
    const types = { '.html': 'text/html; charset=utf-8', '.js': 'application/javascript', '.json': 'application/json', '.m4a': 'audio/mp4', '.png': 'image/png', '.jpg': 'image/jpeg', '.css': 'text/css' };
    const stat = fs.statSync(filename);
    const headers = { 'Content-Type': types[path.extname(filename)] || 'application/octet-stream', 'Accept-Ranges': 'bytes' };
    res.writeHead(200, { ...headers, 'Content-Length': stat.size });
    fs.createReadStream(filename).pipe(res);
  });

  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const port = server.address().port;

  const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'wutang-scope-edge-'));
  const edge = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
  const browser = spawn(edge, [
    '--headless=new',
    '--disable-gpu',
    '--no-first-run',
    '--remote-debugging-port=0',
    `--user-data-dir=${profile}`,
    'about:blank'
  ], { stdio: 'ignore' });

  let cdp;
  try {
    const portFile = path.join(profile, 'DevToolsActivePort');
    for (let i = 0; i < 100 && !fs.existsSync(portFile); i++) await wait(100);
    const dbgPort = Number(fs.readFileSync(portFile, 'utf8').split(/\r?\n/)[0]);
    const target = await (await fetch(`http://127.0.0.1:${dbgPort}/json/new?about:blank`, { method: 'PUT' })).json();
    cdp = await connect(target.webSocketDebuggerUrl);

    await cdp.send('Runtime.enable');
    await cdp.send('Page.enable');
    await cdp.send('Emulation.setDeviceMetricsOverride', { width: 1200, height: 950, deviceScaleFactor: 2, mobile: false });

    await cdp.send('Page.navigate', { url: `http://127.0.0.1:${port}/output/sleep-feature-preview.html` });
    await wait(1500);

    // 切换到心境专区
    await cdp.send('Runtime.evaluate', { expression: `document.getElementById('tabWellbeing').click()` });
    await wait(600);

    // 滚动到 sleepHomeSection
    await cdp.send('Runtime.evaluate', { expression: `document.getElementById('sleepHomeSection').scrollIntoView({block:'start'})` });
    await wait(400);

    // 1. 截图静息态
    const shot1 = await cdp.send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync(path.join(OUT, 'oscilloscope-idle.png'), Buffer.from(shot1.data, 'base64'));
    console.log('[ok] 已保存静息态截图: output/oscilloscope-idle.png');

    // 2. 点击播放音乐，进入播放状态
    await cdp.send('Runtime.evaluate', { expression: `document.getElementById('sleepMusicToggle').click()`, userGesture: true });
    await wait(2200); // 让波形舒展，粒子游动，进入吸气/呼气高峰

    const shot2 = await cdp.send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync(path.join(OUT, 'oscilloscope-playing.png'), Buffer.from(shot2.data, 'base64'));
    console.log('[ok] 已保存播放态截图: output/oscilloscope-playing.png');

  } finally {
    if (cdp) {
      try { await cdp.send('Browser.close'); } catch {}
      cdp.socket.close();
    }
    browser.kill();
    server.close();
  }
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
