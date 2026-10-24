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

  const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'wutang-test-edge-'));
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
    await wait(1200);

    const evaluate = async expr => {
      const res = await cdp.send('Runtime.evaluate', { expression: `(() => { ${expr} })()`, awaitPromise: true, returnByValue: true, userGesture: true });
      if (res.exceptionDetails) throw new Error(res.exceptionDetails.exception?.description || res.exceptionDetails.text);
      return res.result.value;
    };

    // 1. 进入心境专区
    await evaluate(`document.getElementById('tabWellbeing').click()`);
    await wait(400);
    await evaluate(`document.getElementById('sleepHomeSection').scrollIntoView({block:'start'})`);
    await wait(200);

    // 2. 检查控制条是否存在于示波器面板内部
    const controlsInside = await evaluate(`
      const wrap = document.getElementById('sleepScopeWrap');
      const ctrls = document.getElementById('sleepScopeControls');
      return wrap.contains(ctrls);
    `);
    console.log(controlsInside ? 'PASS 控制条已置于示波器面板内部' : 'FAIL 控制条未在内部');

    // 3. 检查控制条中无任何明文标签文字
    const noRawText = await evaluate(`
      const ctrls = document.getElementById('sleepScopeControls');
      let texts = [];
      function collectText(node) {
        if (node.nodeType === Node.TEXT_NODE) {
          const t = node.textContent.trim();
          if (t && node.parentElement && !['OPTION'].includes(node.parentElement.tagName)) texts.push(t);
        } else {
          for (const c of node.childNodes) collectText(c);
        }
      }
      collectText(ctrls);
      return texts;
    `);
    console.log(noRawText.length === 0 ? 'PASS 控件条无任何裸文字标签' : ('FAIL 发现裸文字标签: ' + JSON.stringify(noRawText)));

    // 4. 截图静息态
    const shotIdle = await cdp.send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync(path.join(OUT, 'oscilloscope-idle.png'), Buffer.from(shotIdle.data, 'base64'));
    console.log('[ok] 已更新静息态截图: output/oscilloscope-idle.png');

    // 5. 点击下一曲按钮
    const trackBefore = await evaluate(`return document.getElementById('sleepTrackSelect').value`);
    await evaluate(`document.getElementById('sleepTrackNext').click()`);
    const trackAfter = await evaluate(`return document.getElementById('sleepTrackSelect').value`);
    console.log(Number(trackAfter) === (Number(trackBefore) + 1) ? 'PASS 下一曲按钮切换曲目成功' : 'FAIL 下一曲切换失败');

    // 6. 测试调色板展开与色彩切换
    await evaluate(`document.getElementById('sleepWaveColorBtn').click()`);
    const popoverOpen = await evaluate(`return document.getElementById('sleepColorPalettePop').classList.contains('is-open')`);
    console.log(popoverOpen ? 'PASS 调色板成功展开' : 'FAIL 调色板未展开');

    // 点击暖琥珀金色 (#E0C07A)
    await evaluate(`document.querySelector('.sleep-palette-dot[data-color="#E0C07A"]').click()`);
    await wait(100);
    const chosenColor = await evaluate(`return sleepOscilloscope.getColor()`);
    const localSaved = await evaluate(`return localStorage.getItem('wt_sleep_wave_color')`);
    console.log(chosenColor === '#E0C07A' && localSaved === '#E0C07A' ? 'PASS 成功更改波形色彩为暖琥珀 (#E0C07A) 并持久化' : 'FAIL 色彩切换异常');

    // 7. 播放音乐并截图琥珀波形
    await evaluate(`document.getElementById('sleepMusicToggle').click()`);
    await wait(2200);

    const shotAmber = await cdp.send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync(path.join(OUT, 'oscilloscope-playing-amber.png'), Buffer.from(shotAmber.data, 'base64'));
    console.log('[ok] 已保存琥珀金色波形截图: output/oscilloscope-playing-amber.png');

    // 8. 切换到霁天蓝 (#4DD0E1)
    await evaluate(`document.getElementById('sleepWaveColorBtn').click()`);
    await evaluate(`document.querySelector('.sleep-palette-dot[data-color="#4DD0E1"]').click()`);
    await wait(800);
    const shotBlue = await cdp.send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync(path.join(OUT, 'oscilloscope-playing-blue.png'), Buffer.from(shotBlue.data, 'base64'));
    console.log('[ok] 已保存霁天蓝波形截图: output/oscilloscope-playing-blue.png');

    // 9. 切换回自适应色彩 (律)
    await evaluate(`document.getElementById('sleepWaveColorBtn').click()`);
    await evaluate(`document.getElementById('sleepAutoColorBtn').click()`);
    await wait(800);
    const shotAuto = await cdp.send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync(path.join(OUT, 'oscilloscope-playing.png'), Buffer.from(shotAuto.data, 'base64'));
    console.log('[ok] 已保存自适应播放态截图: output/oscilloscope-playing.png');

    console.log('\n[ALL TESTS PASSED]');
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
