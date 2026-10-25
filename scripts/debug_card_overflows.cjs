'use strict';
const fs = require('fs');
const path = require('path');
const os = require('os');
const http = require('http');
const { spawn } = require('child_process');

const ROOT = path.resolve(__dirname, '..');
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

  const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'wutang-overflow-debug-'));
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

    const evaluate = async expr => {
      const res = await cdp.send('Runtime.evaluate', { expression: `(() => { ${expr} })()`, awaitPromise: true, returnByValue: true, userGesture: true });
      if (res.exceptionDetails) throw new Error(res.exceptionDetails.exception?.description || res.exceptionDetails.text);
      return res.result.value;
    };

    const vp = { width: 375, height: 812 };
    await cdp.send('Emulation.setDeviceMetricsOverride', { width: vp.width, height: vp.height, deviceScaleFactor: 2, mobile: true });
    await cdp.send('Page.navigate', { url: `http://127.0.0.1:${port}/frontend/index.html` });
    await wait(1500);

    const inspect = async (label, fnStr) => {
      const res = await evaluate(fnStr);
      console.log(`\n=== ${label} ===`);
      console.log(JSON.stringify(res, null, 2));
    };

    const shotDir = path.join(ROOT, 'output', 'debug_screenshots');
    fs.mkdirSync(shotDir, { recursive: true });

    async function takeScreenshot(name) {
      const { data } = await cdp.send('Page.captureScreenshot', { format: 'png' });
      fs.writeFileSync(path.join(shotDir, `${name}.png`), Buffer.from(data, 'base64'));
    }

    const checkOverflow = async (sceneName, selectorOrContainer, childSelector) => {
      const result = await evaluate(`
        const container = document.querySelector('${selectorOrContainer}');
        if (!container) return { error: 'container not found: ${selectorOrContainer}' };
        const cRect = container.getBoundingClientRect();
        const children = '${childSelector}' ? Array.from(container.querySelectorAll('${childSelector}')) : Array.from(container.children);
        const overflows = [];
        for (const el of children) {
          const r = el.getBoundingClientRect();
          if (r.width === 0 && r.height === 0) continue;
          // 容差 0.5px
          if (r.right > cRect.right + 0.5 || r.left < cRect.left - 0.5 || r.width > cRect.width + 0.5) {
            overflows.push({
              tag: el.tagName,
              id: el.id,
              className: el.className,
              rect: { left: r.left, right: r.right, width: r.width },
              cRect: { left: cRect.left, right: cRect.right, width: cRect.width },
              overflowRight: r.right - cRect.right,
              overflowLeft: cRect.left - r.left
            });
          }
        }
        return {
          sceneName: '${sceneName}',
          container: { id: container.id, className: container.className, rect: cRect },
          overflowCount: overflows.length,
          overflows: overflows.slice(0, 10)
        };
      `);
      console.log(`\n--- Overflow Check [${sceneName}] ---`);
      console.log(JSON.stringify(result, null, 2));
    };

    // 针对典型移动端视口 320, 360, 375, 390 截图和测量
    for (const w of [320, 360, 375, 390]) {
      await cdp.send('Emulation.setDeviceMetricsOverride', { width: w, height: 812, deviceScaleFactor: 2, mobile: true });
      await wait(300);

      // 1. Growth - Card
      await evaluate(`
        document.getElementById('tabGrowth').click();
        const cardTabBtn = document.getElementById('entryBtnCard');
        if (cardTabBtn) cardTabBtn.click();
      `);
      await wait(400);
      await checkOverflow(`w${w}_GrowthCard`, '#growthEntryMount', '#awarenessCardBox, .awareness-card-container, .awareness-stage, .awareness-text-column');
      await takeScreenshot(`view_${w}_growth_card`);

      // 2. Growth - Journal
      await evaluate(`
        document.getElementById('tabGrowth').click();
        const journalTabBtn = document.getElementById('entryBtnJournal');
        if (journalTabBtn) journalTabBtn.click();
      `);
      await wait(400);
      await checkOverflow(`w${w}_GrowthJournal_EntryMount`, '#growthEntryMount', '.slider-control-card, #journalInputText, #entryJournalArea, #checkinAndJournalCard, .entry-switch-bar, .mood-chip-group');
      await checkOverflow(`w${w}_GrowthJournal_InnerCard`, '#checkinAndJournalCard', '.slider-control-card, #journalInputText, input, textarea');
      await takeScreenshot(`view_${w}_growth_journal`);

      // 3. Wellbeing - Resources
      await evaluate(`
        document.getElementById('tabWellbeing').click();
        const resTabBtn = document.getElementById('wbBtnResources');
        if (resTabBtn) resTabBtn.click();
        const btn = document.getElementById('btnToggleResources');
        const resPanel = document.getElementById('resourcePanel');
        if (btn && resPanel && resPanel.classList.contains('hidden')) {
          btn.click();
        }
      `);
      await wait(400);
      await checkOverflow(`w${w}_WellbeingResources`, '#resourcePanel', '.resource-grid, .resource-card, #resourceRegionFilter');
      await takeScreenshot(`view_${w}_wellbeing_resources`);

      // 4. Studio - Review
      await evaluate(`
        const tabStudio = document.getElementById('tabStudio');
        if (tabStudio) {
          tabStudio.style.display = 'inline-flex';
          tabStudio.classList.remove('hidden');
          tabStudio.click();
        }
        const reviewNav = document.querySelector('[data-view="studioReview"]');
        if (reviewNav) reviewNav.click();
      `);
      await wait(400);
      await checkOverflow(`w${w}_StudioReview_MainCard`, '#studioReview', '#draftCaseSelect, .review-grid, .article-preview-pane, .checklist-pane');
      await takeScreenshot(`view_${w}_studio_review`);
    }

  } catch (err) {
    console.error('Inner error:', err);
  } finally {
    if (cdp) {
      try { await cdp.socket.close(); } catch(e){}
    }
    try { browser.kill(); } catch(e){}
    server.close();
    await wait(500);
    try {
      fs.rmSync(profile, { recursive: true, force: true });
    } catch (e) {}
  }
}

main().catch(console.error);
