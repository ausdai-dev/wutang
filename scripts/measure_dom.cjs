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
    const types = { '.html': 'text/html; charset=utf-8', '.js': 'application/javascript', '.json': 'application/json', '.png': 'image/png', '.css': 'text/css' };
    const stat = fs.statSync(filename);
    const headers = { 'Content-Type': types[path.extname(filename)] || 'application/octet-stream' };
    res.writeHead(200, { ...headers, 'Content-Length': stat.size });
    fs.createReadStream(filename).pipe(res);
  });

  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const port = server.address().port;

  const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'wutang-measure-'));
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
      const res = await cdp.send('Runtime.evaluate', { expression: `(() => { ${expr} })()`, awaitPromise: true, returnByValue: true });
      if (res.exceptionDetails) throw new Error(res.exceptionDetails.exception?.description || res.exceptionDetails.text);
      return res.result.value;
    };

    await cdp.send('Emulation.setDeviceMetricsOverride', { width: 375, height: 812, deviceScaleFactor: 2, mobile: true });
    await cdp.send('Page.navigate', { url: `http://127.0.0.1:${port}/frontend/index.html` });
    await wait(1000);
    await evaluate(`localStorage.setItem('wutang_manager_active', 'true');`);
    await cdp.send('Page.reload');
    await wait(1200);

    const logMetrics = async (title, fn) => {
      console.log(`\n=== ${title} ===`);
      const data = await evaluate(fn);
      console.log(JSON.stringify(data, null, 2));
    };

    for (const w of [320, 360, 375, 390]) {
      await cdp.send('Emulation.setDeviceMetricsOverride', { width: w, height: 812, deviceScaleFactor: 2, mobile: true });
      await wait(200);

      console.log(`\n================= Viewport: ${w}px =================`);

      // 1. Growth Card
      await logMetrics(`1. Growth Card (${w}px)`, `
        document.getElementById('tabGrowth').click();
        document.getElementById('entryBtnCard').click();

        const mount = document.getElementById('growthEntryMount');
        const box = document.getElementById('awarenessCardBox');
        const stage = document.querySelector('.awareness-stage');
        const col = document.querySelector('.awareness-card-column');
        const textCol = document.querySelector('.awareness-text-column');

        const mR = mount.getBoundingClientRect();
        const bR = box.getBoundingClientRect();
        return {
          mountW: mount.offsetWidth,
          boxW: box.offsetWidth,
          boxScrollW: box.scrollWidth,
          mountRect: { left: mR.left, right: mR.right },
          boxRect: { left: bR.left, right: bR.right },
          overflowRight: bR.right - mR.right,
          overflowLeft: mR.left - bR.left
        };
      `);

      // 2. Growth Journal
      await logMetrics(`2. Growth Journal (${w}px)`, `
        document.getElementById('tabGrowth').click();
        document.getElementById('entryBtnJournal').click();

        const mount = document.getElementById('growthEntryMount');
        const innerCard = document.getElementById('checkinAndJournalCard');
        const sliders = Array.from(document.querySelectorAll('.slider-control-card'));
        const textarea = document.getElementById('journalInputText');

        const mR = mount.getBoundingClientRect();
        return {
          mountW: mount.offsetWidth,
          mountRight: mR.right,
          sliders: sliders.map(s => {
            const r = s.getBoundingClientRect();
            return { w: s.offsetWidth, right: r.right, overflowRight: r.right - mR.right };
          }),
          textarea: {
            w: textarea.offsetWidth,
            right: textarea.getBoundingClientRect().right,
            overflowRight: textarea.getBoundingClientRect().right - mR.right
          }
        };
      `);

      // 3. Wellbeing Resources
      await logMetrics(`3. Wellbeing Resources (${w}px)`, `
        document.getElementById('tabWellbeing').click();
        document.getElementById('wbBtnResources').click();
        const btn = document.getElementById('btnToggleResources');
        const resPanel = document.getElementById('resourcePanel');
        if (btn && resPanel && resPanel.classList.contains('hidden')) {
          btn.click();
        }

        const card = document.querySelector('#wellbeingResourcesSection .card');
        const cR = card.getBoundingClientRect();
        const resCards = Array.from(document.querySelectorAll('.resource-card'));

        return {
          cardW: card.offsetWidth,
          cardRight: cR.right,
          resCount: resCards.length,
          firstRes: resCards[0] ? {
            w: resCards[0].offsetWidth,
            right: resCards[0].getBoundingClientRect().right,
            overflowRight: resCards[0].getBoundingClientRect().right - cR.right
          } : null
        };
      `);

      // 4. Studio Review
      await logMetrics(`4. Studio Review (${w}px)`, `
        const tabStudio = document.getElementById('tabStudio');
        if (tabStudio) tabStudio.click();
        const reviewNav = document.querySelector('[data-view="studioReview"]');
        if (reviewNav) reviewNav.click();

        const card = document.getElementById('studioReview');
        const select = document.getElementById('draftCaseSelect');
        const preview = document.getElementById('articlePreviewPane');
        const cR = card.getBoundingClientRect();
        const sR = select.getBoundingClientRect();
        const pR = preview.getBoundingClientRect();

        return {
          cardW: card.offsetWidth,
          cardRight: cR.right,
          select: {
            w: select.offsetWidth,
            right: sR.right,
            overflowRight: sR.right - cR.right
          },
          preview: {
            w: preview.offsetWidth,
            right: pR.right,
            overflowRight: pR.right - cR.right
          }
        };
      `);
    }

  } finally {
    if (cdp) try { await cdp.socket.close(); } catch(e){}
    try { browser.kill(); } catch(e){}
    server.close();
    await wait(400);
    try { fs.rmSync(profile, { recursive: true, force: true }); } catch (e) {}
  }
}

main().catch(console.error);
