#!/usr/bin/env node
/**
 * 悟堂·东方解忧处 —— 本地 MCP 连接器（wutang-kb）
 *
 * 零依赖，纯 Node 标准库实现 MCP stdio 传输（换行分隔的 JSON-RPC 2.0）。
 * 把项目的知识库与工作流暴露为可调用工具，使任何 WorkBuddy 会话都能
 * 检索经典、核验出处、做风险分流、脱敏与生成解忧笺。
 *
 * 暴露的工具：
 *   search_classics     按主题/场景检索经典条目
 *   check_citation      核验一条候选引文的出处状态
 *   assess_risk         风险分流（high_risk / review / normal）
 *   redact_text         去标识化 + 可识别项清单
 *   list_scenarios      四类场景与微行动库
 *   render_relief_card  生成东方解忧笺 HTML
 *
 * 用法：node wutang-kb-server.js
 */
'use strict';

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const CLASSICS_PATH = path.join(ROOT, 'frontend', 'assets', 'classics.json');
const DATA_PATH = path.join(ROOT, 'frontend', 'assets', 'wutang-data.json');

let CLASSICS = [];
let DATA = {};
try {
  CLASSICS = JSON.parse(fs.readFileSync(CLASSICS_PATH, 'utf8'));
  DATA = JSON.parse(fs.readFileSync(DATA_PATH, 'utf8'));
} catch (e) {
  process.stderr.write(`[wutang-kb] 无法加载知识库：${e.message}\n`);
}

const RISK_RE = (DATA.riskPatterns || []).map(p => new RegExp(p));

/* ------------------------------------------------------------------ 工具实现 */

function assessRisk(text) {
  const t = String(text || '');
  for (const k of DATA.riskHigh || []) {
    if (t.includes(k)) return { risk_status: 'high_risk', evidence: `关键词命中：${k}` };
  }
  for (const re of RISK_RE) {
    const m = re.exec(t);
    if (m) return { risk_status: 'high_risk', evidence: `句式命中：${m[0]}` };
  }
  for (const k of DATA.riskReview || []) {
    if (t.includes(k)) return { risk_status: 'review', evidence: `边界词命中：${k}` };
  }
  return { risk_status: 'normal', evidence: '' };
}

function searchClassics(query, scenario, limit) {
  const q = String(query || '');
  const lim = Math.max(1, Math.min(20, limit || 5));
  const scored = CLASSICS
    .filter(c => c.status !== 'not_found')
    .map(c => {
      let s = 0;
      if (scenario && String(c.scenarios || '').split(';').includes(scenario)) s += 6;
      for (const th of String(c.themes || '').split(';')) if (th && q.includes(th)) s += 4;
      if (q && c.quote.includes(q)) s += 10;
      if (c.status === 'verified') s += 2;
      return { score: s, c };
    })
    .sort((a, b) => b.score - a.score)
    .slice(0, lim);
  return {
    query: q, scenario: scenario || null, count: scored.length,
    results: scored.map(x => ({
      source_id: x.c.id, quote: x.c.quote, book: x.c.book, chapter: x.c.chapter,
      era_author: x.c.era_author, translation: x.c.translation,
      interpretation: x.c.interpretation, themes: x.c.themes, scenarios: x.c.scenarios,
      verification_status: x.c.status, edition: x.c.edition, note: x.c.note,
      score: x.score,
    })),
  };
}

function checkCitation(quote) {
  const q = String(quote || '').trim();
  const hit = CLASSICS.find(c => c.quote.trim() === q);
  if (!hit) {
    return {
      quote: q, status: 'not_found', source_id: '', book: '', chapter: '',
      can_quote_directly: false,
      note: '知识库中未找到该引文的可核验出处。禁止作为直接引语输出；如需使用，请改为现代转述并明确标注。',
    };
  }
  return {
    quote: hit.quote, status: hit.status, source_id: hit.id, book: hit.book,
    chapter: hit.chapter, era_author: hit.era_author, translation: hit.translation,
    interpretation: hit.interpretation, edition: hit.edition, verifier: hit.verifier,
    can_quote_directly: hit.status === 'verified',
    note: hit.note,
  };
}

const CITIES = ['北京', '上海', '广州', '深圳', '杭州', '南京', '成都', '武汉', '西安', '重庆',
  '苏州', '天津', '长沙', '郑州', '青岛', '宁波', '厦门', '合肥', '济南', '福州'];
const KIN = ['婆婆', '公公', '岳父', '岳母', '老公', '老婆', '继父', '继母', '大姑', '小叔',
  '嫂子', '弟媳', '姐夫', '妹夫', '表哥', '表姐', '堂哥', '堂姐'];
const ORG_SUFFIX = '公司|集团|银行|学校|中学|小学|大学|医院|事务所|工作室|科技|传媒|设计院';
const SURNAMES = '王李张刘陈杨黄赵周吴徐孙马朱胡郭何高林罗郑梁谢宋唐许韩冯邓曹彭曾肖田董袁潘于蒋蔡余杜叶程苏魏吕丁任沈姚卢姜崔钟谭陆汪范金石廖贾夏韦付方白邹孟熊秦邱江尹薛闫段雷侯龙史陶黎贺顾毛郝龚邵万钱严覃武戴莫孔向汤';
const NAME_STOP = '一句话说的不没也还都就却但而在是有和跟把被让给很太真好了又再更';
const NAME_RE = `[${SURNAMES}][\\u4e00-\\u9fa5][^${NAME_STOP}]|[${SURNAMES}][\\u4e00-\\u9fa5]`;

function redactText(text) {
  let t = String(text || '');
  const items = [];
  const sub = (re, repl, kind, reason) => {
    const ms = t.match(new RegExp(re, 'g')) || [];
    for (const m of ms) items.push({ type: kind, original: m, replacement: repl, reason });
    t = t.replace(new RegExp(re, 'g'), repl);
  };
  sub('(?:今年|去年|前年|明年|\\d{4}年)?\\d{1,2}月\\d{1,2}[日号](?:那天)?', '有一天', 'date', '具体日期');
  sub('\\d{4}年\\d{1,2}月', '有一年', 'date', '具体年月');
  sub(`[\\u4e00-\\u9fa5]{0,10}?(?:${ORG_SUFFIX})`, '一家机构', 'organization', '可识别的单位名称');
  for (const c of CITIES) if (t.includes(c)) { items.push({ type: 'location', original: c, replacement: '某城市', reason: '具体城市' }); t = t.split(c).join('某城市'); }
  sub(`(?:我叫|名叫|叫)(${NAME_RE})`, '一位来访者', 'person_name', '直接姓名');
  sub(`(?:我)?(?:${KIN.join('|')})(${NAME_RE})`, '家人', 'person_name', '亲属称谓 + 姓名，可定位到具体个人');
  for (const k of KIN) if (t.includes(k)) { items.push({ type: 'kinship', original: k, replacement: '家人', reason: '亲属关系可缩小识别范围' }); t = t.split(k).join('家人'); }
  return {
    redacted_text: t, risk_items: items,
    review_required: true,
    reminder: '人名替换不是充分脱敏。必须由人工复核：当事人的熟人读到后能否反推出是谁？「职业+城市+事件+时间」组合是否唯一？',
  };
}

function listScenarios() {
  return {
    scenarios: (DATA.scenarios || []).map(s => ({
      key: s.key, label: s.label, sub: s.sub, goal: s.goal,
      micro_actions: (DATA.microActions || {})[s.key] || [],
    })),
    note: '场景是体验入口，不是诊断分类。不得根据标签推断用户患有某种心理疾病。',
  };
}

function renderReliefCard(a) {
  const brand = (DATA.brand || {}).name || '悟堂·东方解忧处';
  const slogan = (DATA.brand || {}).slogan || '';
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g,
    c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const status = a.quote_status || 'modern_paraphrase';
  const badge = { verified: '已核验', needs_review: '辑录·待复核', modern_paraphrase: '现代转述' }[status] || '现代转述';
  return `<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">
<title>东方解忧笺 · ${esc(a.case_id || '')}</title>
<style>body{margin:0;background:#F5EFE4;font-family:"PingFang SC","Microsoft YaHei",sans-serif;
padding:40px 16px;color:#2B2724;line-height:1.75}
.jian{background:#FBF7F0;border:1px solid #D3C8B6;border-radius:4px;max-width:520px;margin:0 auto;
padding:44px 40px;position:relative}
.jian::before{content:"";position:absolute;inset:10px;border:1px solid #E4DCCF;border-radius:2px}
.inner{position:relative;text-align:center}
.brand{font-size:12px;letter-spacing:.32em;color:#8C3A2B;margin-bottom:22px}
.theme{font-family:"Songti SC","SimSun",serif;font-size:15px;letter-spacing:.18em;color:#B08A4A;margin-bottom:24px}
.quote{font-family:"Songti SC","SimSun",serif;font-size:23px;line-height:1.9;margin:0 0 12px}
.src{font-size:12px;color:#7A736C;margin-bottom:22px}
.div{width:38px;height:1px;background:#D3C8B6;margin:0 auto 24px}
.exp{font-size:14.5px;color:#4A443E;line-height:1.85;margin:0 0 26px;text-align:left}
.act{background:#fff;border:1px solid #E4DCCF;border-radius:4px;padding:16px 18px;text-align:left}
.act .k{font-size:11.5px;letter-spacing:.14em;color:#8C3A2B;display:block;margin-bottom:6px}
.act .v{font-size:14px;line-height:1.7}
.foot{margin-top:26px;font-size:11.5px;color:#7A736C;letter-spacing:.1em}</style></head>
<body><div class="jian"><div class="inner">
<div class="brand">${esc(brand)}</div>
<div class="theme">${esc(a.theme)}</div>
<p class="quote">${esc(a.quote)}</p>
<div class="src">${esc(a.quote_source)}　${badge}</div>
<div class="div"></div>
<p class="exp">${esc(a.explanation)}</p>
<div class="act"><span class="k">今晚 5 分钟微行动</span><span class="v">${esc(a.micro_action)}</span></div>
<div class="foot">${esc(slogan)}</div>
</div></div></body></html>`;
}

/* ------------------------------------------------------------------ 工具表 */

const TOOLS = [
  {
    name: 'search_classics',
    description: '按主题或场景检索悟堂经典语料库，返回带 source_id 与核验状态的条目。用于为一条困扰匹配可核验的经典引用。',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: '用户文本或主题关键词，例如「内耗」「边界」「睡不着」' },
        scenario: { type: 'string', enum: ['work', 'relation', 'night', 'growth'], description: '场景标签（可选）' },
        limit: { type: 'integer', description: '返回条数，默认 5，最大 20' },
      },
      required: ['query'],
    },
  },
  {
    name: 'check_citation',
    description: '核验一条候选引文的出处状态。返回 verified / needs_review / not_found，并明确是否可作为直接引语。未命中时禁止编造出处。',
    inputSchema: {
      type: 'object',
      properties: { quote: { type: 'string', description: '待核验的原文，例如「君子求诸己，小人求诸人。」' } },
      required: ['quote'],
    },
  },
  {
    name: 'assess_risk',
    description: '风险分流：把用户文本判为 high_risk / review / normal，并给出触发依据。high_risk 时应终止普通流程，只输出安全回应。',
    inputSchema: {
      type: 'object',
      properties: { text: { type: 'string', description: '用户原始输入' } },
      required: ['text'],
    },
  },
  {
    name: 'redact_text',
    description: '去标识化：识别并替换姓名、单位、城市、日期、亲属关系等识别信息，返回脱敏文本与可识别项清单。仅产出待人工复核的草稿。',
    inputSchema: {
      type: 'object',
      properties: { text: { type: 'string', description: '待脱敏的案例文本' } },
      required: ['text'],
    },
  },
  {
    name: 'list_scenarios',
    description: '列出四类场景（职场/关系/深夜/成长）及其微行动库。',
    inputSchema: { type: 'object', properties: {} },
  },
  {
    name: 'render_relief_card',
    description: '生成东方解忧笺 HTML（暖白底、深红棕点缀、宋式排版）。卡片不得包含原始倾诉或任何可识别信息。',
    inputSchema: {
      type: 'object',
      properties: {
        case_id: { type: 'string' },
        theme: { type: 'string', description: '情绪/场景主题词' },
        quote: { type: 'string', description: '已核验原文，或明确标为现代转述的短句' },
        quote_source: { type: 'string', description: '书名·篇章，或「现代转述」' },
        quote_status: { type: 'string', enum: ['verified', 'needs_review', 'modern_paraphrase'] },
        explanation: { type: 'string', description: '一句现代解释' },
        micro_action: { type: 'string', description: '今晚 5 分钟微行动（一句话版）' },
      },
      required: ['theme', 'quote', 'quote_source', 'explanation', 'micro_action'],
    },
  },
];

function callTool(name, args) {
  switch (name) {
    case 'search_classics': return searchClassics(args.query, args.scenario, args.limit);
    case 'check_citation': return checkCitation(args.quote);
    case 'assess_risk': return assessRisk(args.text);
    case 'redact_text': return redactText(args.text);
    case 'list_scenarios': return listScenarios();
    case 'render_relief_card': return { html: renderReliefCard(args) };
    default: throw new Error(`未知工具：${name}`);
  }
}

/* ------------------------------------------------------- MCP stdio 传输层 */

function send(msg) { process.stdout.write(JSON.stringify(msg) + '\n'); }

function handle(req) {
  const { id, method, params } = req;
  const isNotification = (id === undefined || id === null);

  if (method === 'initialize') {
    send({
      jsonrpc: '2.0', id,
      result: {
        protocolVersion: (params && params.protocolVersion) || '2024-11-05',
        capabilities: { tools: { listChanged: false } },
        serverInfo: { name: 'wutang-kb', version: '1.0.0' },
      },
    });
    return;
  }
  if (method === 'notifications/initialized' || method === 'initialized') return;
  if (method === 'ping') { if (!isNotification) send({ jsonrpc: '2.0', id, result: {} }); return; }
  if (method === 'tools/list') {
    send({ jsonrpc: '2.0', id, result: { tools: TOOLS } });
    return;
  }
  if (method === 'tools/call') {
    try {
      const out = callTool(params.name, params.arguments || {});
      send({
        jsonrpc: '2.0', id,
        result: { content: [{ type: 'text', text: JSON.stringify(out, null, 2) }] },
      });
    } catch (e) {
      send({
        jsonrpc: '2.0', id,
        result: { content: [{ type: 'text', text: `错误：${e.message}` }], isError: true },
      });
    }
    return;
  }
  if (!isNotification) {
    send({ jsonrpc: '2.0', id, error: { code: -32601, message: `未实现的方法：${method}` } });
  }
}

let buf = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => {
  buf += chunk;
  let idx;
  while ((idx = buf.indexOf('\n')) >= 0) {
    const line = buf.slice(0, idx).trim();
    buf = buf.slice(idx + 1);
    if (!line) continue;
    try { handle(JSON.parse(line)); }
    catch (e) { process.stderr.write(`[wutang-kb] 解析失败：${e.message}\n`); }
  }
});
process.stdin.on('end', () => process.exit(0));
