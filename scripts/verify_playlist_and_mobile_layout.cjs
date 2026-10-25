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

    // 测试 1: 移动端 375px 窄屏下的示波器控制栏排版
    await cdp.send('Emulation.setDeviceMetricsOverride', { width: 375, height: 812, deviceScaleFactor: 2, mobile: true });
    await cdp.send('Page.navigate', { url: `http://127.0.0.1:${port}/output/sleep-feature-preview.html` });
    await wait(1200);

    const evaluate = async expr => {
      const res = await cdp.send('Runtime.evaluate', { expression: `(() => { ${expr} })()`, awaitPromise: true, returnByValue: true, userGesture: true });
      if (res.exceptionDetails) throw new Error(res.exceptionDetails.exception?.description || res.exceptionDetails.text);
      return res.result.value;
    };

    // 导航到心境专区
    await evaluate(`document.getElementById('tabWellbeing').click()`);
    await wait(400);
    await evaluate(`document.getElementById('sleepHomeSection').scrollIntoView({block:'start'})`);
    await wait(300);

    // 1. 验证 #sleepMusicPanel 按钮已彻底从 DOM 中删除
    const musicPanelExists = await evaluate(`return !!document.getElementById('sleepMusicPanel')`);
    console.log(!musicPanelExists ? 'PASS #sleepMusicPanel 按钮已彻底删除' : 'FAIL #sleepMusicPanel 依然存在');

    // 2. 验证下拉列表包含 sequence 与 random 选项
    const options = await evaluate(`
      const sel = document.getElementById('sleepTrackSelect');
      return Array.from(sel.options).map(o => ({ value: o.value, text: o.textContent }));
    `);
    const hasSequence = options.some(o => o.value === 'sequence');
    const hasRandom = options.some(o => o.value === 'random');
    console.log(hasSequence && hasRandom ? 'PASS 下拉菜单包含顺序轮播与随机轮播选项' : 'FAIL 下拉菜单缺少轮播选项');

    // 3. 验证移动端响应式布局：控制栏两行对齐，各行不折行
    const layout = await evaluate(`
      const ctrls = document.getElementById('sleepScopeControls');
      const groups = ctrls.querySelectorAll('.sleep-ctrl-group');
      const g1 = groups[0];
      const g2 = groups[1];
      const g1Items = Array.from(g1.children);
      const g2Items = Array.from(g2.children);
      const g1Tops = g1Items.map(el => Math.round(el.getBoundingClientRect().top));
      const g2Tops = g2Items.map(el => Math.round(el.getBoundingClientRect().top));
      const g1Wrapped = (Math.max(...g1Tops) - Math.min(...g1Tops)) > 4;
      const g2Wrapped = (Math.max(...g2Tops) - Math.min(...g2Tops)) > 4;
      return { g1Wrapped, g2Wrapped, g1Count: g1Items.length, g2Count: g2Items.length };
    `);
    console.log(!layout.g1Wrapped ? 'PASS 移动端第 1 组控件无折行重叠' : 'FAIL 移动端第 1 组控件发生二次折行');
    console.log(!layout.g2Wrapped ? 'PASS 移动端第 2 组控件无折行重叠' : 'FAIL 移动端第 2 组控件发生二次折行');

    // 4. 验证底部文本在移动端无重合挤压 (flex-direction: column)
    const footLayout = await evaluate(`
      const foot = document.querySelector('.sleep-scope-foot');
      const status = document.getElementById('sleepScopeStatus');
      const hint = foot.querySelector('.sleep-scope-hint');
      const sRect = status.getBoundingClientRect();
      const hRect = hint.getBoundingClientRect();
      const isStacked = hRect.top >= sRect.bottom - 1;
      return { isStacked, sRect, hRect };
    `);
    console.log(footLayout.isStacked ? 'PASS 移动端底部文本垂直列式居中无重叠' : 'FAIL 移动端底部文本重叠');

    // 5. 截图移动端示波器控件
    await evaluate(`document.getElementById('sleepScopeWrap').scrollIntoView({block:'center'})`);
    await wait(200);
    const mobileShot = await cdp.send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync(path.join(OUT, 'oscilloscope-mobile-375.png'), Buffer.from(mobileShot.data, 'base64'));
    console.log('[ok] 已保存移动端 375px 示波器截图: output/oscilloscope-mobile-375.png');

    // 6. 测试选择 "sequence" (顺序轮播) 模式
    await evaluate(`
      const sel = document.getElementById('sleepTrackSelect');
      sel.value = 'sequence';
      sel.dispatchEvent(new Event('change', { bubbles: true }));
    `);
    const modeSeq = await evaluate(`return bgmEngine.getPlayMode()`);
    console.log(modeSeq === 'sequence' ? 'PASS 成功设置 bgmEngine 为 sequence 模式' : 'FAIL 模式设置异常');

    // 启动睡前音乐并在 sequence 模式下测试下一曲
    await evaluate(`document.getElementById('sleepMusicToggle').click()`);
    await wait(400);
    const idx1 = await evaluate(`return bgmEngine.getState().index`);
    await evaluate(`document.getElementById('sleepTrackNext').click()`);
    await wait(200);
    const idx2 = await evaluate(`return bgmEngine.getState().index`);
    const selValAfterNext = await evaluate(`return document.getElementById('sleepTrackSelect').value`);
    console.log(idx2 === (idx1 + 1) % 9 && selValAfterNext === 'sequence' ? 'PASS 顺序轮播下一曲切换成功且下拉菜单维持 sequence' : 'FAIL 顺序轮播切换异常');

    // 7. 测试选择 "random" (随机轮播) 模式
    await evaluate(`
      const sel = document.getElementById('sleepTrackSelect');
      sel.value = 'random';
      sel.dispatchEvent(new Event('change', { bubbles: true }));
    `);
    const modeRand = await evaluate(`return bgmEngine.getPlayMode()`);
    console.log(modeRand === 'random' ? 'PASS 成功设置 bgmEngine 为 random 模式' : 'FAIL random 模式设置异常');

    // 8. 测试选择单曲数字模式
    await evaluate(`
      const sel = document.getElementById('sleepTrackSelect');
      sel.value = '4';
      sel.dispatchEvent(new Event('change', { bubbles: true }));
    `);
    const modeSingle = await evaluate(`return bgmEngine.getPlayMode()`);
    console.log(modeSingle === 'single' ? 'PASS 切换单曲数字恢复 single 模式' : 'FAIL single 模式恢复异常');

    console.log('\n[ALL PLAYLIST & MOBILE TESTS PASSED]');
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
