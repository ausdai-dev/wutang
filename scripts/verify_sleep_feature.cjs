'use strict';
const fs = require('fs');
const path = require('path');
const os = require('os');
const http = require('http');
const { spawn } = require('child_process');
const ROOT = path.resolve(__dirname, '..');
const OUT = path.join(ROOT, 'output');
const wait = ms => new Promise(resolve => setTimeout(resolve, ms));
const checks = [];
const errors = [];
function check(name, passed, evidence) {
  checks.push({ name, passed: !!passed, evidence });
  console.log(`${passed ? 'PASS' : 'FAIL'} ${name} ${JSON.stringify(evidence || '')}`);
  if (!passed) throw new Error(name);
}
async function connect(url) {
  const socket = new WebSocket(url);
  await new Promise((resolve, reject) => { socket.addEventListener('open', resolve, { once: true }); socket.addEventListener('error', reject, { once: true }); });
  let seq = 0;
  const pending = new Map();
  socket.addEventListener('message', event => {
    const msg = JSON.parse(event.data);
    if (msg.method === 'Runtime.exceptionThrown') errors.push(msg.params.exceptionDetails.exception?.description || msg.params.exceptionDetails.text);
    const request = pending.get(msg.id);
    if (request) { pending.delete(msg.id); msg.error ? request.reject(new Error(JSON.stringify(msg.error))) : request.resolve(msg.result); }
  });
  return { socket, send(method, params = {}) { return new Promise((resolve, reject) => { const id = ++seq; pending.set(id, { resolve, reject }); socket.send(JSON.stringify({ id, method, params })); }); } };
}
async function main() {
  const source = fs.readFileSync(path.join(ROOT, 'frontend/index.html'), 'utf8');
  const preview = source.replace(/<head>/i, '<head>\n<base href="../frontend/">');
  fs.writeFileSync(path.join(OUT, 'sleep-feature-preview.html'), preview);
  check('预览与构建页同源，仅补资源基址', preview.replace('\n<base href="../frontend/">', '') === source);
  const server = http.createServer((req, res) => {
    let filename;
    try { filename = path.resolve(ROOT, '.' + decodeURIComponent(new URL(req.url, 'http://127.0.0.1').pathname)); } catch { res.writeHead(400).end(); return; }
    if (!filename.startsWith(ROOT + path.sep)) { res.writeHead(403).end(); return; }
    if (!fs.existsSync(filename) || !fs.statSync(filename).isFile()) { res.writeHead(404).end(); return; }
    const types = { '.html': 'text/html; charset=utf-8', '.js': 'application/javascript', '.json': 'application/json', '.m4a': 'audio/mp4', '.png': 'image/png', '.jpg': 'image/jpeg', '.css': 'text/css' };
    const stat = fs.statSync(filename), headers = { 'Content-Type': types[path.extname(filename)] || 'application/octet-stream', 'Accept-Ranges': 'bytes' };
    const match = /^bytes=(\d+)-(\d*)$/.exec(req.headers.range || '');
    if (match) { const start = Number(match[1]), end = match[2] ? Math.min(Number(match[2]), stat.size - 1) : stat.size - 1; res.writeHead(206, { ...headers, 'Content-Range': `bytes ${start}-${end}/${stat.size}`, 'Content-Length': end - start + 1 }); fs.createReadStream(filename, { start, end }).pipe(res); }
    else { res.writeHead(200, { ...headers, 'Content-Length': stat.size }); fs.createReadStream(filename).pipe(res); }
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'wutang-sleep-edge-'));
  const edge = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
  const browser = spawn(edge, ['--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check', '--disable-background-networking', '--remote-debugging-port=0', '--remote-debugging-address=127.0.0.1', `--user-data-dir=${profile}`, 'about:blank'], { stdio: 'ignore' });
  let cdp;
  try {
    const portFile = path.join(profile, 'DevToolsActivePort');
    for (let i = 0; i < 100 && !fs.existsSync(portFile); i++) await wait(100);
    if (!fs.existsSync(portFile)) throw new Error('Edge 调试端口未就绪');
    const port = Number(fs.readFileSync(portFile, 'utf8').split(/\r?\n/)[0]);
    const target = await (await fetch(`http://127.0.0.1:${port}/json/new?about:blank`, { method: 'PUT' })).json();
    cdp = await connect(target.webSocketDebuggerUrl);
    await cdp.send('Runtime.enable'); await cdp.send('Page.enable'); await cdp.send('Network.enable');
    await cdp.send('Network.setBlockedURLs', { urls: ['https://*', 'http://localhost:8000/*'] });
    await cdp.send('Page.addScriptToEvaluateOnNewDocument', { source: `window.fetch = async function(){ return new Response('{}',{status:503}); };` });
    const evaluate = async expression => { const result = await cdp.send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true, userGesture: true }); if (result.exceptionDetails) throw new Error(result.exceptionDetails.exception?.description || result.exceptionDetails.text); return result.result.value; };
    const click = selector => evaluate(`document.querySelector(${JSON.stringify(selector)}).click()`);
    const until = async (expression, name) => { for (let i = 0; i < 100; i++) { if (await evaluate(expression)) return; await wait(80); } throw new Error('等待超时：' + name); };
    const audioState = () => evaluate(`({src:bgmAudio.getAttribute('src'),paused:bgmAudio.paused,volume:bgmAudio.volume,currentTime:bgmAudio.currentTime,readyState:bgmAudio.readyState,error:bgmAudio.error&&bgmAudio.error.code})`);
    await cdp.send('Emulation.setDeviceMetricsOverride', { width: 1280, height: 900, deviceScaleFactor: 1, mobile: false });
    await cdp.send('Page.navigate', { url: `http://127.0.0.1:${server.address().port}/output/sleep-feature-preview.html` });
    await until(`!!document.getElementById('tabWellbeing') && typeof openSleepGuide==='function'`, '页面初始化');
    check('页面初始不自动播放', (await audioState()).paused, await audioState());
    await click('#tabWellbeing');
    check('心境首屏只出现一个模块、三流程', await evaluate(`document.querySelectorAll('#sleepHomeSection').length===1 && document.querySelectorAll('[data-sleep-flow]').length===3 && document.querySelector('#wellbeingArea > div').firstElementChild.id==='sleepHomeSection'`));
    for (const flow of ['mind', 'body', 'wake']) {
      await click(`[data-sleep-flow="${flow}"]`);
      const initial = await evaluate(`sleepStepText.textContent`);
      await click('#sleepSkip');
      check(flow + ' 流程跳过并前进一步', await evaluate(`sleepSession.classList.contains('is-open') && sleepStepNum.textContent.includes('2') && sleepStepText.textContent!==${JSON.stringify(initial)}`));
      for (let i = 0; i < 4; i++) await click('#sleepNext');
      check(flow + ' 完成退出并恢复键盘焦点', await evaluate(`!sleepSession.classList.contains('is-open') && document.activeElement.getAttribute('data-sleep-flow')===${JSON.stringify(flow)}`));
    }
    await evaluate(`document.querySelector('[data-sleep-flow="body"]').focus()`);
    await cdp.send('Input.dispatchKeyEvent', { type: 'keyDown', key: 'Enter', code: 'Enter', windowsVirtualKeyCode: 13 });
    await cdp.send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'Enter', code: 'Enter', windowsVirtualKeyCode: 13 });
    check('键盘 Enter 启动流程', await evaluate(`sleepSession.classList.contains('is-open')`));
    await cdp.send('Input.dispatchKeyEvent', { type: 'keyDown', key: 'Escape', code: 'Escape', windowsVirtualKeyCode: 27 });
    check('键盘 Escape 停止流程', await evaluate(`!sleepSession.classList.contains('is-open')`));
    await evaluate(`bgmEngine.togglePanel()`);
    check('音乐面板和今夜安歇快捷入口可用', await evaluate(`bgmPanel.classList.contains('show') && !!document.getElementById('bgmSleepEntry')`));
    await click('#bgmSleepEntry');
    check('音乐面板入口进入心境并关闭面板', await evaluate(`!wellbeingArea.classList.contains('hidden')&&!bgmPanel.classList.contains('show')`));
    await click('#btnBgmToggle');
    await until(`!bgmAudio.paused && bgmAudio.readyState>=2`, '普通音乐真实解码播放');
    await evaluate(`bgmAudio.currentTime=12; bgmAudio.volume=.42; document.getElementById('bgmVolumeSlider').value=42; document.getElementById('bgmVolumeSlider').dispatchEvent(new Event('input',{bubbles:true}));`);
    const ordinary = await audioState();
    await evaluate(`sleepTrackSelect.value='2';sleepTrackSelect.dispatchEvent(new Event('change'));sleepVolume.value='13';sleepVolume.dispatchEvent(new Event('input'));sleepTimer.value='5';sleepTimer.dispatchEvent(new Event('change'));`);
    const untouched = await audioState();
    check('未启动睡前音乐时控件不改普通BGM', ordinary.src === untouched.src && ordinary.volume === untouched.volume && !untouched.paused && untouched.currentTime >= ordinary.currentTime, { ordinary, untouched });
    await click('#sleepMusicToggle');
    await until(`!bgmAudio.paused && bgmAudio.readyState>=2 && bgmAudio.src.includes('autumn_rain_zheng')`, '睡前曲真实播放');
    check('睡前播放器复用单个音频、应用曲目音量', await evaluate(`document.querySelectorAll('audio').length===1 && Math.abs(bgmAudio.volume-.13)<.001`), await audioState());
    await click('#sleepStop');
    await until(`!bgmAudio.paused && bgmAudio.src.includes('flowing_mind') && bgmAudio.currentTime>=12`, '手动退出后元数据加载和恢复位置');
    const restored = await audioState();
    check('手动退出恢复普通曲目、音量、播放位置', restored.src === ordinary.src && Math.abs(restored.volume - .42) < .001 && restored.currentTime < 16, restored);
    await click('#sleepMusicToggle');
    await until(`!bgmAudio.paused&&bgmAudio.readyState>=2&&bgmAudio.src.includes('autumn_rain_zheng')`, '睡前播放');
    await click('[data-sleep-flow="wake"]');
    await click('#tabGrowth');
    await until(`!bgmAudio.paused&&bgmAudio.src.includes('flowing_mind')&&bgmAudio.readyState>=2`, '导航恢复普通BGM');
    check('离开Tab退出引导并恢复普通音乐', await evaluate(`!sleepSession.classList.contains('is-open')&&Math.abs(bgmAudio.volume-.42)<.001`), await audioState());
    await click('#tabWellbeing');
    await evaluate(`window.__sleepClock={timeouts:[],intervals:[]};const realTimeout=window.setTimeout,realInterval=window.setInterval;window.setTimeout=function(fn,ms,...args){const id=realTimeout(fn,ms===300000?80:ms,...args);if(ms===300000)__sleepClock.timeouts.push(id);return id};window.setInterval=function(fn,ms,...args){const id=realInterval(fn,ms===250?10:ms,...args);if(ms===250)__sleepClock.intervals.push(id);return id};sleepTimer.value='5';sleepFade.checked=true;`);
    await click('#sleepMusicToggle');
    await until(`bgmAudio.paused && bgmAudio.volume===0`, '加速5分钟定时渐弱结束');
    await wait(250);
    check('定时渐弱结束保持静音且不重启原BGM', await evaluate(`bgmAudio.paused&&bgmAudio.volume===0&&__sleepClock.timeouts.length>0&&__sleepClock.intervals.length>0`), await audioState());
    await evaluate(`sleepFade.checked=false`);
    await click('#sleepMusicToggle');
    await until(`bgmAudio.paused&&bgmAudio.volume===0`, '不渐弱定时结束');
    check('不渐弱定时结束不恢复原曲播放', (await audioState()).paused, await audioState());
    await evaluate(`sleepTimer.value='0'`); await click('#sleepMusicToggle');
    await until(`!bgmAudio.paused&&bgmAudio.readyState>=2`, '无定时睡前音乐');
    await click('#sleepStop');
    await evaluate(`sleepTimer.value='5'`); await click('#sleepMusicToggle'); await click('#sleepStop');
    const stopped = await audioState(); await wait(500); const later = await audioState();
    check('手动停止清理定时器，不延迟误停背景音乐', stopped.src === later.src && stopped.paused === later.paused && stopped.volume === later.volume, { stopped, later });
    await cdp.send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-reduced-motion', value: 'reduce' }] });
    check('减少动态效果设置受尊重', await evaluate(`matchMedia('(prefers-reduced-motion: reduce)').matches && getComputedStyle(sleepStepText).transitionDuration==='0s'`));
    await evaluate(`sleepHomeSection.scrollIntoView({behavior:'instant',block:'start'})`); await wait(150);
    const desktopShot = await cdp.send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false });
    fs.writeFileSync(path.join(OUT, 'sleep-feature-desktop.png'), Buffer.from(desktopShot.data, 'base64'));
    await cdp.send('Emulation.setDeviceMetricsOverride', { width: 390, height: 844, deviceScaleFactor: 1, mobile: true });
    await evaluate(`sleepHomeSection.scrollIntoView({behavior:'instant',block:'start'})`); await wait(200);
    const mobileLayout = await evaluate(`({columns:getComputedStyle(document.querySelector('.sleep-flow-grid')).gridTemplateColumns,viewport:innerWidth,documentWidth:document.documentElement.scrollWidth,flowWidths:[...document.querySelectorAll('[data-sleep-flow]')].map(b=>b.getBoundingClientRect().width),flowTops:[...document.querySelectorAll('[data-sleep-flow]')].map(b=>Math.round(b.getBoundingClientRect().top))})`);
    check('390px 移动端三按钮并列单排无横向溢出', mobileLayout.documentWidth <= mobileLayout.viewport && mobileLayout.columns.trim().split(/\s+/).length === 3 && Math.abs(mobileLayout.flowTops[0] - mobileLayout.flowTops[1]) <= 2 && Math.abs(mobileLayout.flowTops[0] - mobileLayout.flowTops[2]) <= 2, mobileLayout);
    const mobileShot = await cdp.send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false });
    fs.writeFileSync(path.join(OUT, 'sleep-feature-mobile.png'), Buffer.from(mobileShot.data, 'base64'));
    await click('[data-sleep-flow="wake"]'); await click('#sleepSkip'); await click('#sleepStop');
    check('移动端三流程按钮支持继续、跳过和退出', await evaluate(`!sleepSession.classList.contains('is-open')`));
    check('真实浏览器没有新增脚本异常', errors.length === 0, errors);
  } finally {
    fs.writeFileSync(path.join(OUT, 'sleep-feature-browser-results.json'), JSON.stringify({ browser: '本机 Edge headless / CDP；真实音频解码，非手机真机', checks, errors }, null, 2));
    if (cdp) { try { await cdp.send('Browser.close'); } catch {} cdp.socket.close(); }
    browser.kill(); server.close();
  }
}
main().catch(error => { console.error(error.stack); process.exitCode = 1; });
