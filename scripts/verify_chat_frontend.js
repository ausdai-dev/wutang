#!/usr/bin/env node
'use strict';
const fs = require('fs');
const path = require('path');
let JSDOM;
try { ({ JSDOM } = require('jsdom')); }
catch (_) { ({ JSDOM } = require('C:/Users/ausda/.workbuddy-ai/binaries/node/workspace/node_modules/jsdom')); }
const { TextDecoder, TextEncoder } = require('util');
const html = fs.readFileSync(path.join(__dirname, '..', 'frontend', 'index.html'), 'utf8');
const enc = new TextEncoder();
const wait = (ms = 0) => new Promise((resolve) => setTimeout(resolve, ms));
const events = (items) => items.map((item) => `data: ${JSON.stringify(item)}\n\n`);
const plans = [];
const requests = [];
const chatHeaders = [];
const memoryRequests = [];
const confirmations = [];
let memoryItems = [];
let memoryCounter = 0;
let memoryFailure = false;
let deferMemory = false;
let resolveMemory;
let lastChatUrl = '';
const jsonResponse = (data, status = 200) => ({ ok: status >= 200 && status < 300, status, json: () => Promise.resolve(data) });
function responseFrom(chunks) {
  let index = 0;
  return { ok: true, body: { getReader() { return { read() {
    if (index >= chunks.length) return Promise.resolve({ done: true });
    const item = chunks[index++];
    const value = item && item.bytes ? item.bytes : enc.encode(item && item.text ? item.text : item);
    if (item && item.delay) return new Promise((resolve) => setTimeout(() => resolve({ done: false, value }), item.delay));
    return Promise.resolve({ done: false, value });
  } }; } } };
}
function check(name, condition) {
  console.log(`  ${condition ? 'PASS' : 'FAIL'}  ${name}`);
  if (!condition) process.exitCode = 1;
}
const dom = new JSDOM(html, {
  url: 'http://127.0.0.1:8011/',
  runScripts: 'dangerously', pretendToBeVisual: true,
  beforeParse(window) {
    window.TextDecoder = TextDecoder;
    window.TextEncoder = TextEncoder;
    window.AbortController = global.AbortController;
    window.confirm = (text) => { confirmations.push(text); return confirmations.answer !== false; };
    window.fetch = (url, options = {}) => {
      lastChatUrl = String(url);
      if (String(url).includes('/api/health')) return Promise.resolve(jsonResponse({ status: 'healthy', model: 'test', llm_configured: true }));
      if (String(url).includes('/api/auth/login')) { const second = JSON.parse(options.body).account === 'second@example.test'; return Promise.resolve(jsonResponse({ access_token: second ? 'second-account-token' : 'test-account-token', user: { id: second ? 10 : 9, name: second ? '第二账号' : '测试用户', account: second ? 'second@example.test' : 'test@example.test' } })); }
      if (String(url).includes('/api/memory')) {
        const body = options.body ? JSON.parse(options.body) : null;
        const suffix = String(url).split('/api/memory')[1];
        memoryRequests.push({ method: options.method, headers: options.headers, body, suffix });
        if (deferMemory && options.method === 'GET') return new Promise((resolve) => { resolveMemory = resolve; });
        if (memoryFailure) return Promise.resolve(jsonResponse({}, 401));
        if (!['Bearer test-account-token', 'Bearer second-account-token'].includes(options.headers.Authorization)) return Promise.resolve(jsonResponse({}, 401));
        if (options.headers.Authorization === 'Bearer second-account-token' && options.method === 'GET') return Promise.resolve(jsonResponse({ status: 'success', memories: [] }));
        if (options.method !== 'GET' && body?.confirmed !== true) return Promise.resolve(jsonResponse({}, 400));
        if (options.method === 'POST') { const item = { id: String(++memoryCounter), content: body.content, source_type: body.source_type || 'manual', confirmed: true, created_at: '2026-10-24T12:00:00', updated_at: '2026-10-24T12:00:00' }; memoryItems.push(item); return Promise.resolve(jsonResponse({ status: 'success', memory: { ...item } })); }
        if (options.method === 'PATCH') { const item = memoryItems.find((entry) => entry.id === suffix.slice(1)); if (!item) return Promise.resolve(jsonResponse({}, 404)); item.content = body.content; item.updated_at = '2026-10-24T12:01:00'; return Promise.resolve(jsonResponse({ status: 'success', memory: { ...item } })); }
        if (options.method === 'DELETE') { const before = memoryItems.length; memoryItems = suffix ? memoryItems.filter((entry) => entry.id !== suffix.slice(1)) : []; return Promise.resolve(jsonResponse({ status: 'success', deleted: before - memoryItems.length })); }
        return Promise.resolve(jsonResponse({ status: 'success', memories: memoryItems.map((item) => ({ ...item })) }));
      }
      requests.push(JSON.parse(options.body));
      chatHeaders.push(options.headers);
      const plan = plans.shift();
      if (!plan) throw new Error('测试未提供 SSE 计划');
      return Promise.resolve(responseFrom(plan));
    };
  }
});
const { document: doc } = dom.window;
const send = async (text) => {
  doc.getElementById('chatInput').value = text;
  doc.getElementById('btnChatSend').click();
  await wait(15);
};
(async () => {
  await wait(30);
  console.log('=== 聊天面板与 SSE ===');
  check('聊天面板为默认主页入口', !!doc.getElementById('sageChatPanel') && !doc.getElementById('sageChatPanel').classList.contains('hidden'));
  check('聊天输入限制为 2000 字', doc.getElementById('chatInput').maxLength === 2000);
  check('8011 预览使用同源 API', dom.window.location.port !== '8011' || lastChatUrl.indexOf('127.0.0.1:8011') >= 0);

  doc.getElementById('btnChatMode').click();
  check('可从默认孔子单聊切换至圆桌群聊', doc.getElementById('chatTitle').textContent.includes('三家圆桌'));
  const utf8Event = enc.encode('data: {"type":"token","speaker":"confucius","content":"先听你说。"}\n\n');
  plans.push([
    'data: {"type":"start"}\n\n',
    ...events([{ type: 'speaker_start', speaker: 'confucius', name: '孔子' }]),
    { bytes: utf8Event.slice(0, 56) },
    { bytes: utf8Event.slice(56, 59) },
    { bytes: utf8Event.slice(59) },
    ...events([{ type: 'speaker_end', speaker: 'confucius' }, { type: 'speaker_start', speaker: 'laozi', name: '老子' }, { type: 'token', speaker: 'laozi', content: '先留一点余地。' }, { type: 'done' }])
  ]);
  await send('第一件事');
  check('群聊请求默认 round_limit 为 2', requests[0].mode === 'group' && requests[0].round_limit === 2);
  check('群聊默认不指定 target', requests[0].target === null && requests[0].master === null);
  check('跨 chunk token 被拼接为气泡', doc.getElementById('chatMessages').textContent.includes('先听你说。'));
  check('一轮群聊渲染两位角色', doc.querySelectorAll('#chatMessages .chat-row:not(.mine)').length === 2);

  check('@老子选择器在群聊中存在', [...doc.querySelectorAll('#chatMentionBar button')].some((node) => node.textContent === '@老子'));
  [...doc.querySelectorAll('#chatMentionBar button')].find((node) => node.textContent === '@老子').click();
  plans.push(events([{ type: 'speaker_start', speaker: 'laozi', name: '老子' }, { type: 'token', speaker: 'laozi', content: '第二轮。' }, { type: 'done' }]));
  await send('继续说');
  check('@老子将 target 传给后端', requests[1].target === 'laozi');
  check('下一轮历史保留 assistant speaker', requests[1].messages.some((m) => m.role === 'assistant' && m.speaker === 'confucius'));

  doc.getElementById('btnChatNew').click();
  const longText = '字'.repeat(2000);
  for (let i = 0; i < 10; i++) { plans.push(events([{ type: 'done' }])); await send(longText); }
  const cropped = requests[requests.length - 1].messages;
  check('请求历史最多 40 条', cropped.length <= 40);
  check('请求历史总量最多 16000 字', cropped.reduce((sum, message) => sum + message.content.length, 0) <= 16000);
  check('请求历史末条固定为 user', cropped[cropped.length - 1].role === 'user');

  doc.getElementById('chatMoreSage').value = 'zhuangzi';
  doc.getElementById('chatMoreSage').dispatchEvent(new dom.window.Event('change'));
  plans.push(events([{ type: 'speaker_start', speaker: 'zhuangzi', name: '庄子' }, { type: 'token', speaker: 'zhuangzi', content: '换个角度。' }, { type: 'done' }]));
  await send('想听庄子');
  const soloRequest = requests[requests.length - 1];
  check('更多先贤走 solo master', soloRequest.mode === 'solo' && soloRequest.master === 'zhuangzi' && soloRequest.target === null);

  const beforeSafety = doc.querySelectorAll('#chatMessages .chat-row:not(.mine)').length;
  plans.push(events([{ type: 'safety', level: 'high_risk', message: '请优先联系可信的人。' }, { type: 'speaker_start', speaker: 'confucius', name: '孔子' }, { type: 'token', speaker: 'confucius', content: '不得显示' }, { type: 'done' }]));
  await send('安全测试');
  check('safety 显示服务端安全引导', doc.getElementById('chatMessages').textContent.includes('请优先联系可信的人。'));
  check('safety 后不继续角色回复', doc.querySelectorAll('#chatMessages .chat-row:not(.mine)').length === beforeSafety);
  check('safety 后清除解忧笺整理出口', doc.getElementById('btnChatOrganize').disabled);

  plans.push([ { text: 'data: {"type":"speaker_start","speaker":"confucius"}\n\n', delay: 25 }, { text: 'data: {"type":"token","speaker":"confucius","content":"旧流不得显示"}\n\n', delay: 25 } ]);
  plans.push(events([{ type: 'done' }]));
  await send('旧请求');
  doc.getElementById('chatInput').value = '新请求';
  doc.getElementById('chatInput').dispatchEvent(new dom.window.Event('input'));
  doc.getElementById('btnChatSend').click();
  await wait(65);
  check('新输入会中止旧请求且旧 token 不串入', !doc.getElementById('chatMessages').textContent.includes('旧流不得显示'));

  plans.push([ { text: 'data: {"type":"speaker_start","speaker":"confucius"}\n\n', delay: 25 }, { text: 'data: {"type":"token","speaker":"confucius","content":"停止后不得显示"}\n\n', delay: 25 } ]);
  await send('停止测试');
  doc.getElementById('btnChatStop').click();
  await wait(65);
  check('停止按钮隔离后续旧流 token', !doc.getElementById('chatMessages').textContent.includes('停止后不得显示'));

  plans.push(events([{ type: 'mode', mode: 'offline' }, { type: 'speaker_start', speaker: 'zhuangzi', name: '庄子' }, { type: 'token', speaker: 'zhuangzi', content: '离线引导内容' }, { type: 'done' }]));
  await send('离线测试');
  check('offline 明确提示并标识离线模板', doc.getElementById('chatStatus').textContent.includes('离线模式') && doc.getElementById('chatMessages').textContent.includes('离线引导模板 · 非模型生成') && doc.getElementById('chatMessages').textContent.includes('离线引导内容'));

  console.log('=== 会话摘要与角色跳过 ===');
  doc.getElementById('btnChatNew').click();
  plans.push(events([{ type: 'summary', summary: '<img src=x onerror=alert(1)>用户希望简短建议。' }, { type: 'speaker_start', speaker: 'laozi' }, { type: 'speaker_skip', speaker: 'laozi' }, { type: 'done' }]));
  await send('记住当前前文');
  check('summary通过纯文本展示且不生成气泡', doc.getElementById('chatSummaryText').textContent.includes('<img') && !doc.querySelector('#chatSummaryText img') && !doc.querySelector('#chatMessages .chat-row:not(.mine)'));
  plans.push(events([{ type: 'done' }])); await send('再说一句');
  const summaryRequest = requests.at(-1);
  check('摘要跨轮发送且不混入assistant历史', summaryRequest.summary.includes('简短建议') && !summaryRequest.messages.some((item) => item.role === 'assistant'));
  check('摘要与倾诉未写入浏览器长期存储', !Object.keys(dom.window.localStorage).some((key) => /chat|memory|summary/.test(key)));
  doc.getElementById('btnChatNew').click(); plans.push(events([{ type: 'done' }])); await send('新对话');
  check('新对话清空摘要和短期历史', requests.at(-1).summary === '' && requests.at(-1).messages.length === 1 && doc.getElementById('chatSummaryText').textContent.includes('暂无摘要'));
  check('访客不调用长期记忆API且聊天明确禁用', memoryRequests.length === 0 && requests.at(-1).use_memory === false && !chatHeaders.at(-1).Authorization && doc.getElementById('chatMemoryStatus').textContent.includes('登录'));
  doc.getElementById('btnChatNew').click();
  for (let i = 0; i < 4; i++) { plans.push(events([{ type: 'done' }])); await send(String(i) + '前'.repeat(1999)); }
  plans.push(events([{ type: 'summary', summary: '[用户原话]早期前文', retained_messages: [{ role: 'user', content: '2' + '前'.repeat(1999) }, { role: 'user', content: '3' + '前'.repeat(1999) }, { role: 'user', content: '第五轮' + '字'.repeat(1997) }] }, { type: 'done' }])); await send('第五轮' + '字'.repeat(1997));
  check('长聊裁剪前向服务端发送完整短期窗口', requests.at(-1).messages.length === 5 && requests.at(-1).messages[0].content.startsWith('0') && requests.at(-1).messages.reduce((sum, item) => sum + item.content.length, 0) === 10000);
  plans.push(events([{ type: 'done' }])); await send('接续摘要');
  check('服务端摘要覆盖后才裁剪短期历史并跨轮接续', requests.at(-1).summary === '[用户原话]早期前文' && requests.at(-1).messages.length === 4 && requests.at(-1).messages[0].content.startsWith('2'));
  plans.push(events([{ type: 'summary', summary: '[用户原话]早期前文；[用户原话]新增前文', retained_messages: [{ role: 'user', content: '接续摘要' }, { role: 'user', content: '再更新摘要' }] }, { type: 'done' }])); await send('再更新摘要');
  plans.push(events([{ type: 'done' }])); await send('继续');
  check('后续摘要更新并再次裁剪不混入assistant历史', requests.at(-1).summary.includes('新增前文') && requests.at(-1).messages.length === 3 && !requests.at(-1).messages.some((item) => item.role === 'assistant'));

  console.log('=== 登录后的长期记忆管理 ===');
  doc.getElementById('btnChatMemoryLogin').click();
  doc.getElementById('authInputAccount').value = 'test@example.test'; doc.getElementById('authInputPassword').value = 'password'; doc.getElementById('btnSubmitLoginAction').click();
  await wait(30);
  check('真实登录回调显示服务端记忆面板并携带token', !doc.getElementById('chatMemoryControls').classList.contains('hidden') && memoryRequests.at(-1)?.headers.Authorization === 'Bearer test-account-token');
  const submitMemory = async (content, confirmed) => { doc.getElementById('chatMemoryInput').value = content; doc.getElementById('chatMemoryConfirm').checked = confirmed; doc.getElementById('chatMemoryForm').dispatchEvent(new dom.window.Event('submit', { bubbles: true, cancelable: true })); await wait(15); };
  await submitMemory('我喜欢简短的建议', false);
  check('未明确确认不调用保存API', !memoryRequests.some((item) => item.method === 'POST') && doc.getElementById('chatMemoryStatus').textContent.includes('勾选确认'));
  const literal = '<img src=x onerror=alert(1)>我喜欢简短的建议';
  await submitMemory(literal, true);
  check('确认保存走账号API且渲染来源日期和纯文本', memoryRequests.some((item) => item.method === 'POST' && item.body.confirmed === true && !('user_id' in item.body)) && doc.getElementById('chatMemoryList').textContent.includes(literal) && doc.getElementById('chatMemoryList').textContent.includes('来源：用户明确确认') && doc.getElementById('chatMemoryList').textContent.includes('2026-10-24') && !doc.querySelector('#chatMemoryList img'));
  doc.querySelector('#chatMemoryList button').click();
  check('编辑需再次确认且不自动保存', !doc.getElementById('chatMemoryConfirm').checked && doc.getElementById('chatMemoryInput').value === literal);
  await submitMemory('我希望先听具体建议', true);
  check('手动编辑同步PATCH接口', memoryRequests.some((item) => item.method === 'PATCH' && item.body.content === '我希望先听具体建议') && doc.getElementById('chatMemoryList').textContent.includes('先听具体建议'));
  plans.push(events([{ type: 'done' }])); await send('登录后聊天');
  check('聊天复用Authorization且默认使用确认记忆', chatHeaders.at(-1).Authorization === 'Bearer test-account-token' && requests.at(-1).use_memory === true && !('user_id' in requests.at(-1)));
  doc.getElementById('chatSkipMemory').checked = true;
  plans.push(events([{ type: 'done' }])); await send('这一轮不用记忆');
  check('本次不使用开关禁用记忆但保留认证和短期历史', requests.at(-1).use_memory === false && chatHeaders.at(-1).Authorization && requests.at(-1).messages.length >= 2);
  const storage = Object.keys(dom.window.localStorage).map((key) => dom.window.localStorage.getItem(key)).join('');
  check('长期记忆文本不假存到localStorage', !storage.includes('先听具体建议'));
  confirmations.answer = false;
  const beforeClear = memoryRequests.length; doc.getElementById('btnChatMemoryClear').click(); await wait();
  check('取消清空确认不发删除请求', memoryRequests.length === beforeClear);
  confirmations.answer = true;
  doc.querySelectorAll('#chatMemoryList button')[1].click(); await wait(15);
  check('手动删除单条记忆需确认并同步服务端', memoryRequests.some((item) => item.method === 'DELETE' && item.suffix === '/1') && memoryItems.length === 0 && confirmations.some((text) => text.includes('删除这条')));
  await submitMemory('我偏好每天一个小行动', true);
  doc.getElementById('btnChatMemoryClear').click(); await wait(15);
  check('确认后可清空账号长期记忆', memoryRequests.some((item) => item.method === 'DELETE' && item.suffix === '') && memoryItems.length === 0 && doc.getElementById('chatMemoryList').textContent.includes('尚未保存'));
  memoryFailure = true; doc.getElementById('btnChatMemoryRefresh').click(); await wait(15);
  check('认证失效明确提示而不宣称保存成功', doc.getElementById('chatMemoryStatus').textContent.includes('重新登录'));
  check('记忆API返回401清除失效token与账号缓存', !dom.window.localStorage.getItem('wutang_auth_token') && !dom.window.localStorage.getItem('wutang_current_user') && doc.getElementById('chatMemoryControls').classList.contains('hidden'));
  memoryFailure = false; doc.getElementById('btnChatMemoryLogin').click(); doc.getElementById('authInputAccount').value = 'test@example.test'; doc.getElementById('authInputPassword').value = 'password'; doc.getElementById('btnSubmitLoginAction').click(); await wait(30);
  plans.push(events([{ type: 'summary', summary: '第一账号会话摘要' }, { type: 'done' }])); await send('第一账号上下文');
  doc.getElementById('chatMemoryInput').value = '第一账号未保存候选';
  deferMemory = true; doc.getElementById('btnChatMemoryRefresh').click();
  doc.getElementById('btnLogoutUser').click(); await wait();
  resolveMemory(jsonResponse({ memories: [{ id: 'stale', content: '旧账号迟到响应', source_type: 'manual', created_at: '2026-10-24' }] })); await wait(15);
  check('退出后迟到的旧账号API响应不回填记忆', !doc.getElementById('chatMemoryList').textContent.includes('迟到响应'));
  check('退出账号移除token并隐藏服务端记忆', !dom.window.localStorage.getItem('wutang_auth_token') && doc.getElementById('chatMemoryControls').classList.contains('hidden') && !doc.querySelector('#chatMemoryList .chat-memory-item'));
  plans.push(events([{ type: 'done' }])); await send('退出后继续');
  check('退出后匿名请求不携带旧身份与摘要', !chatHeaders.at(-1).Authorization && requests.at(-1).use_memory === false && requests.at(-1).summary === '' && requests.at(-1).messages.length === 1);
  deferMemory = false;
  doc.getElementById('btnChatMemoryLogin').click(); doc.getElementById('authInputAccount').value = 'second@example.test'; doc.getElementById('authInputPassword').value = 'password'; doc.getElementById('btnSubmitLoginAction').click(); await wait(30);
  check('切换第二账号后清除第一账号摘要和候选记忆', dom.window.localStorage.getItem('wutang_auth_token') === 'second-account-token' && doc.getElementById('chatSummaryText').textContent.includes('暂无摘要') && !doc.getElementById('chatMemoryInput').value && doc.getElementById('chatMemoryList').textContent.includes('尚未保存'));
  plans.push(events([{ type: 'memory_status', status: 'loaded', count: 0 }, { type: 'done' }])); await send('第二账号新话题');
  check('第二账号聊天仅携带新token且历史重新开始', chatHeaders.at(-1).Authorization === 'Bearer second-account-token' && requests.at(-1).summary === '' && requests.at(-1).messages.length === 1);
  check('loaded事件独立展示本轮记忆使用状态', doc.getElementById('chatMemoryRoundStatus').textContent.includes('已读取'));
  plans.push(events([{ type: 'memory_status', status: 'unavailable', message: '暂不可用' }, { type: 'speaker_start', speaker: 'confucius' }, { type: 'token', speaker: 'confucius', content: '仍可继续聊天' }, { type: 'done' }])); await send('服务暂不可用');
  check('unavailable事件明确未用记忆且继续回复', doc.getElementById('chatMemoryRoundStatus').textContent.includes('未使用长期记忆') && doc.getElementById('chatMessages').textContent.includes('仍可继续聊天'));
  plans.push(events([{ type: 'memory_status', status: 'disabled' }, { type: 'done' }])); await send('停用状态');
  check('disabled事件展示用户停用状态', doc.getElementById('chatMemoryRoundStatus').textContent.includes('已按你的选择停用'));
  plans.push(events([{ type: 'memory_status', status: 'anonymous' }, { type: 'done' }])); await send('匿名状态');
  check('anonymous事件明确访客未使用记忆', doc.getElementById('chatMemoryRoundStatus').textContent.includes('访客模式，未使用'));
  doc.getElementById('chatMemoryInput').value = '第二账号候选';
  plans.push(events([{ type: 'summary', summary: '第二账号摘要' }, { type: 'done' }])); await send('第二账号旧上下文');
  dom.window.localStorage.setItem('wutang_auth_token', 'test-account-token'); dom.window.localStorage.setItem('wutang_current_user', JSON.stringify({ id: 9, name: '测试用户' }));
  dom.window.dispatchEvent(new dom.window.StorageEvent('storage', { key: 'wutang_auth_token', newValue: 'test-account-token' })); await wait(20);
  check('token替换同步清除旧聊天摘要与候选记忆', doc.getElementById('chatSummaryText').textContent.includes('暂无摘要') && !doc.getElementById('chatMemoryInput').value && !doc.getElementById('chatMessages').textContent.includes('第二账号旧上下文'));
  dom.window.close();
  if (process.exitCode) process.exitCode = 1;
})();
