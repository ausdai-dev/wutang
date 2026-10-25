'use strict';
const fs = require('fs');
const path = require('path');
const os = require('os');
const http = require('http');
const { spawn } = require('child_process');

const ROOT = path.resolve(__dirname, '..');
const OUT = path.join(ROOT, 'output');
if (!fs.existsSync(OUT)) fs.mkdirSync(OUT, { recursive: true });

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

  const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'wutang-header-test-'));
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
  let allPassed = true;

  try {
    const portFile = path.join(profile, 'DevToolsActivePort');
    for (let i = 0; i < 100 && !fs.existsSync(portFile); i++) await wait(100);
    const dbgPort = Number(fs.readFileSync(portFile, 'utf8').split(/\r?\n/)[0]);
    const target = await (await fetch(`http://127.0.0.1:${dbgPort}/json/new?about:blank`, { method: 'PUT' })).json();
    cdp = await connect(target.webSocketDebuggerUrl);

    await cdp.send('Runtime.enable');
    await cdp.send('Page.enable');

    const evaluate = async expr => {
      const res = await cdp.send('Runtime.evaluate', { expression: `(() => { ${expr} })()`, awaitPromise: true, returnByValue: true, userGesture: true });
      if (res.exceptionDetails) throw new Error(res.exceptionDetails.exception?.description || res.exceptionDetails.text);
      return res.result.value;
    };

    const viewports = [
      { name: '超小屏 360px', width: 360, height: 740 },
      { name: '主流小屏 375px', width: 375, height: 812 },
      { name: '中等小屏 390px', width: 390, height: 844 },
      { name: '大屏手机 414px', width: 414, height: 896 }
    ];

    for (const vp of viewports) {
      console.log(`\n=== 正在测试视口: ${vp.name} (${vp.width}x${vp.height}) ===`);
      await cdp.send('Emulation.setDeviceMetricsOverride', { width: vp.width, height: vp.height, deviceScaleFactor: 2, mobile: true });
      await cdp.send('Page.navigate', { url: `http://127.0.0.1:${port}/frontend/index.html` });
      await wait(1200);

      const metrics = await evaluate(`
        const toPlain = r => ({ left: r.left, right: r.right, top: r.top, bottom: r.bottom, width: r.width, height: r.height });
        const h1 = document.querySelector('.brand-text h1');
        const h1Rect = toPlain(h1.getBoundingClientRect());
        const seal = document.querySelector('.seal-mark');
        const sealRect = toPlain(seal.getBoundingClientRect());
        const aiBtn = document.getElementById('btnAiStatus');
        const aiRect = toPlain(aiBtn.getBoundingClientRect());
        const fontBtn = document.getElementById('btnFontToggle');
        const fontRect = toPlain(fontBtn.getBoundingClientRect());
        const bgmBtn = document.getElementById('btnBgmToggle');
        const bgmRect = toPlain(bgmBtn.getBoundingClientRect());

        // 测量 h1 内文本是否换行：通过 TextNode 测量第一个字与最后一个字的高度
        const textNode = h1.firstChild;
        const range1 = document.createRange();
        range1.setStart(textNode, 0);
        range1.setEnd(textNode, 1);
        const rectFirstChar = range1.getBoundingClientRect();

        const rangeLast = document.createRange();
        rangeLast.setStart(textNode, textNode.length - 1);
        rangeLast.setEnd(textNode, textNode.length);
        const rectLastChar = rangeLast.getBoundingClientRect();

        const isCharWrapped = Math.abs(rectFirstChar.top - rectLastChar.top) > 5;
        const clearanceToAi = aiRect.left - h1Rect.right;
        const bgmOverflow = bgmRect.right - window.innerWidth;

        return {
          title: h1.textContent.trim(),
          isCharWrapped,
          h1Rect,
          sealRect,
          aiRect,
          fontRect,
          bgmRect,
          clearanceToAi,
          bgmOverflow
        };
      `);

      console.log(`  标题文字: "${metrics.title}"`);
      console.log(`  标题首字与末字垂直差检测: ${metrics.isCharWrapped ? '换行异常!' : '未换行 (同一行)'}`);
      console.log(`  标题右边界: ${metrics.h1Rect.right.toFixed(1)}px, AI按钮左边界: ${metrics.aiRect.left.toFixed(1)}px`);
      console.log(`  标题与AI按钮间安全间距: ${metrics.clearanceToAi.toFixed(1)}px`);
      console.log(`  按钮尺寸: AI=${metrics.aiRect.width.toFixed(1)}x${metrics.aiRect.height.toFixed(1)}, 字=${metrics.fontRect.width.toFixed(1)}x${metrics.fontRect.height.toFixed(1)}, 乐=${metrics.bgmRect.width.toFixed(1)}x${metrics.bgmRect.height.toFixed(1)}`);
      console.log(`  禅乐按钮右侧溢出量: ${metrics.bgmOverflow <= 0 ? '无溢出 (' + metrics.bgmOverflow.toFixed(1) + 'px)' : '溢出 ' + metrics.bgmOverflow.toFixed(1) + 'px!'}`);

      const passWrap = !metrics.isCharWrapped;
      const passOverlap = metrics.clearanceToAi >= 0;
      const passOverflow = metrics.bgmOverflow <= 0;
      const passButtonCompact = metrics.aiRect.width <= 25 && metrics.fontRect.width <= 25 && metrics.bgmRect.width <= 25;

      if (passWrap && passOverlap && passOverflow && passButtonCompact) {
        console.log(`  [PASS] ${vp.name} 标题单行完整、无重叠遮挡、按钮小巧紧凑、无右侧溢出!`);
      } else {
        console.error(`  [FAIL] ${vp.name} 存在异常: wrap=${passWrap}, overlap=${passOverlap}, overflow=${passOverflow}, compact=${passButtonCompact}`);
        allPassed = false;
      }

      // 截图顶栏留存
      const headerClip = await evaluate(`
        const header = document.querySelector('.global-header');
        const r = header.getBoundingClientRect();
        return { x: 0, y: 0, width: window.innerWidth, height: Math.min(r.bottom + 20, 200), scale: 2 };
      `);
      const shot = await cdp.send('Page.captureScreenshot', {
        format: 'png',
        clip: headerClip
      });
      const shotPath = path.join(OUT, `header-compact-buttons-${vp.width}.png`);
      fs.writeFileSync(shotPath, Buffer.from(shot.data, 'base64'));
      console.log(`  [截图已保存] ${shotPath}`);
    }

    // 额外测试: 模拟移动端聊天对话模式 (body.mobile-chat-fit)
    console.log(`\n=== 正在测试移动端聊天模式 (body.mobile-chat-fit @ 375px) ===`);
    await evaluate(`document.body.classList.add('mobile-chat-fit')`);
    await wait(300);
    const chatFitMetrics = await evaluate(`
      const h1 = document.querySelector('.brand-text h1');
      const h1Rect = h1.getBoundingClientRect();
      const aiBtn = document.getElementById('btnAiStatus');
      const aiRect = aiBtn.getBoundingClientRect();
      const textNode = h1.firstChild;
      const r1 = document.createRange(); r1.setStart(textNode, 0); r1.setEnd(textNode, 1);
      const r2 = document.createRange(); r2.setStart(textNode, textNode.length - 1); r2.setEnd(textNode, textNode.length);
      const isCharWrapped = Math.abs(r1.getBoundingClientRect().top - r2.getBoundingClientRect().top) > 5;
      return {
        isCharWrapped,
        clearanceToAi: aiRect.left - h1Rect.right
      };
    `);
    console.log(`  移动端聊天模式: 换行=${chatFitMetrics.isCharWrapped}, 与AI间距=${chatFitMetrics.clearanceToAi.toFixed(1)}px`);
    if (!chatFitMetrics.isCharWrapped && chatFitMetrics.clearanceToAi >= 0) {
      console.log(`  [PASS] mobile-chat-fit 下依然单行完整且无重叠!`);
    } else {
      console.error(`  [FAIL] mobile-chat-fit 下异常!`);
      allPassed = false;
    }

  } finally {
    if (cdp) await cdp.socket.close();
    browser.kill();
    server.close();
    try { fs.rmSync(profile, { recursive: true, force: true }); } catch {}
  }

  if (!allPassed) {
    process.exit(1);
  }
}

main().catch(err => {
  console.error('测试异常:', err);
  process.exit(1);
});
