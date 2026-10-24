'use strict';
const fs = require('fs');
const path = require('path');
const os = require('os');
const http = require('http');
const { spawn } = require('child_process');

async function testTypingShot() {
  const ROOT = path.resolve(__dirname, '..');
  const OUT = path.join(ROOT, 'output');
  const server = http.createServer((req, res) => {
    let filename = path.resolve(ROOT, '.' + decodeURIComponent(new URL(req.url, 'http://127.0.0.1').pathname));
    if (!fs.existsSync(filename)) { res.writeHead(404).end(); return; }
    const ext = path.extname(filename);
    const types = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'application/javascript', '.png': 'image/png' };
    res.writeHead(200, { 'Content-Type': types[ext] || 'text/html; charset=utf-8' });
    fs.createReadStream(filename).pipe(res);
  });
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const port = server.address().port;
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'wutang-type-shot-'));
  const edge = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
  const browser = spawn(edge, ['--headless=new', '--remote-debugging-port=0', '--user-data-dir=' + profile, 'about:blank']);
  
  const portFile = path.join(profile, 'DevToolsActivePort');
  for (let i = 0; i < 50 && !fs.existsSync(portFile); i++) await new Promise(r => setTimeout(r, 100));
  const debugPort = Number(fs.readFileSync(portFile, 'utf8').split(/\r?\n/)[0]);
  const target = await (await fetch('http://127.0.0.1:' + debugPort + '/json/new?about:blank', { method: 'PUT' })).json();
  const socket = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise(r => socket.addEventListener('open', r, { once: true }));
  let seq = 0;
  function send(method, params = {}) {
    return new Promise((resolve) => {
      const id = ++seq;
      const handler = (e) => {
        const msg = JSON.parse(e.data);
        if (msg.id === id) { socket.removeEventListener('message', handler); resolve(msg.result); }
      };
      socket.addEventListener('message', handler);
      socket.send(JSON.stringify({ id, method, params }));
    });
  }
  await send('Page.enable');
  await send('Emulation.setDeviceMetricsOverride', { width: 1280, height: 950, deviceScaleFactor: 1, mobile: false });
  await send('Page.navigate', { url: 'http://127.0.0.1:' + port + '/output/sleep-feature-preview.html' });
  await new Promise(r => setTimeout(r, 1000));
  await send('Runtime.evaluate', { expression: 'document.querySelector("#tabWellbeing").click()', userGesture: true });
  await new Promise(r => setTimeout(r, 300));
  await send('Runtime.evaluate', { expression: 'document.querySelector(\'[data-sleep-flow="mind"]\').click()', userGesture: true });
  // Wait halfway through typing
  await new Promise(r => setTimeout(r, 450));
  const shot = await send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync(path.join(OUT, 'sleep-typing-test.png'), Buffer.from(shot.data, 'base64'));
  socket.close();
  browser.kill();
  server.close();
  console.log('Typing screenshot captured successfully');
}
testTypingShot();
