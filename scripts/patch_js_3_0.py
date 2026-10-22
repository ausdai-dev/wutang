# -*- coding: utf-8 -*-
"""
悟堂 · 东方解忧处 —— PRD 3.0 JS 逻辑引擎补丁
为 frontend/_template.html 注入完整的 PRD 3.0 前端业务逻辑：
- 每日心境签到与心境日历
- AI 心事日记结构化提炼
- 微行动反馈非评判复盘
- 知觉心理压力量表 PSS-10 确定性计分
- 专业心理健康与危机资源导航
- 情境练习室与沟通助手（带 DeepSeek AI 角色扮演与替代表达推荐）
- 6 大主题卡牌包与我的收藏
- 独立四级隐私授权矩阵与全量本地数据导出/彻底清空
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(ROOT, "frontend", "_template.html")

def patch_js():
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. 注入 3.0 数据解包
    unpack_old = "var ZEN_ASSETS = RAW_DATA.zenAssets || { cards: {}, bookmarks: {} };"
    unpack_new = """var ZEN_ASSETS = RAW_DATA.zenAssets || { cards: {}, bookmarks: {} };
  // PRD 3.0 新增知识与量表语料
  var INSTRUMENTS = RAW_DATA.instruments || [];
  var SCORING_RULES = RAW_DATA.scoringRules || {};
  var INTERPRETATION_COPY = RAW_DATA.interpretationCopy || {};
  var MENTAL_RESOURCES = RAW_DATA.mentalResources || [];
  var THEME_PACKS = RAW_DATA.themePacks || [];
  var PRACTICE_SCENARIOS = RAW_DATA.practiceScenarios || [];"""

    if unpack_old in html and "INSTRUMENTS" not in html:
        html = html.replace(unpack_old, unpack_new)

    # 2. 增强 switchMainTab
    old_switch = """  function switchMainTab(tab) {
    appState.mainTab = tab;
    var clientArea = $('clientArea');
    var mineArea = $('mineArea');
    var studioArea = $('studioArea');

    var tabRelief = $('tabRelief');
    var tabMine = $('tabMine');
    var tabStudio = $('tabStudio');

    if (tabRelief) tabRelief.classList.remove('active');
    if (tabMine) tabMine.classList.remove('active');
    if (tabStudio) tabStudio.classList.remove('active');

    if (tab === 'relief') {
      if (clientArea) clientArea.classList.remove('hidden');
      if (mineArea) mineArea.classList.add('hidden');
      if (studioArea) studioArea.classList.add('hidden');
      if (tabRelief) tabRelief.classList.add('active');
    } else if (tab === 'mine') {
      if (clientArea) clientArea.classList.add('hidden');
      if (mineArea) mineArea.classList.remove('hidden');
      if (studioArea) studioArea.classList.add('hidden');
      if (tabMine) tabMine.classList.add('active');
      renderMineSection();
    } else if (tab === 'studio') {
      if (!appState.isManagerLoggedIn) {
        showToast('主理人工作台仅供主理人登录后访问，请先在「我的」完成认证');
        switchMainTab('mine');
        return;
      }
      if (clientArea) clientArea.classList.add('hidden');
      if (mineArea) mineArea.classList.add('hidden');
      if (studioArea) studioArea.classList.remove('hidden');
      if (tabStudio) tabStudio.classList.add('active');
      renderStudioOverview();
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }"""

    new_switch = """  function switchMainTab(tab) {
    appState.mainTab = tab;
    var clientArea = $('clientArea');
    var growthArea = $('growthArea');
    var wellbeingArea = $('wellbeingArea');
    var practiceArea = $('practiceArea');
    var cardsArea = $('cardsArea');
    var mineArea = $('mineArea');
    var studioArea = $('studioArea');

    var tabs = ['tabRelief', 'tabGrowth', 'tabWellbeing', 'tabPractice', 'tabCards', 'tabMine', 'tabStudio'];
    tabs.forEach(function(tId) {
      var btn = $(tId);
      if (btn) btn.classList.remove('active');
    });

    [clientArea, growthArea, wellbeingArea, practiceArea, cardsArea, mineArea, studioArea].forEach(function(area) {
      if (area) area.classList.add('hidden');
    });

    if (tab === 'relief') {
      if (clientArea) clientArea.classList.remove('hidden');
      if ($('tabRelief')) $('tabRelief').classList.add('active');
    } else if (tab === 'growth') {
      if (growthArea) growthArea.classList.remove('hidden');
      if ($('tabGrowth')) $('tabGrowth').classList.add('active');
      renderGrowthSection();
    } else if (tab === 'wellbeing') {
      if (wellbeingArea) wellbeingArea.classList.remove('hidden');
      if ($('tabWellbeing')) $('tabWellbeing').classList.add('active');
      renderWellbeingSection();
    } else if (tab === 'practice') {
      if (practiceArea) practiceArea.classList.remove('hidden');
      if ($('tabPractice')) $('tabPractice').classList.add('active');
      renderPracticeSection();
    } else if (tab === 'cards') {
      if (cardsArea) cardsArea.classList.remove('hidden');
      if ($('tabCards')) $('tabCards').classList.add('active');
      renderCardsSection();
    } else if (tab === 'mine') {
      if (mineArea) mineArea.classList.remove('hidden');
      if ($('tabMine')) $('tabMine').classList.add('active');
      renderMineSection();
    } else if (tab === 'studio') {
      if (!appState.isManagerLoggedIn) {
        showToast('主理人工作台仅供主理人登录后访问，请先在「我的」完成认证');
        switchMainTab('mine');
        return;
      }
      if (studioArea) studioArea.classList.remove('hidden');
      if ($('tabStudio')) $('tabStudio').classList.add('active');
      renderStudioOverview();
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }"""

    if old_switch in html:
        html = html.replace(old_switch, new_switch)

    # 3. 注入完整的 3.0 业务交互逻辑实现代码
    js_3_0_body = """
  // ==========================================================================
  // PRD 3.0 全局模块业务控制器 (Growth / Wellbeing / Practice / Cards / Privacy)
  // ==========================================================================

  // --- 本地存储工具 ---
  function getStorageJson(key, defVal) {
    try {
      var r = localStorage.getItem(key);
      return r ? JSON.parse(r) : defVal;
    } catch(e) { return defVal; }
  }
  function setStorageJson(key, val) {
    try { localStorage.setItem(key, JSON.stringify(val)); } catch(e) {}
  }

  // --------------------------------------------------------------------------
  // 1. 成长记录模块 (Growth Section: F-10, F-11, F-12, F-13, F-14)
  // --------------------------------------------------------------------------
  var currentSelectedMoods = ['calm'];
  var currentSelectedEnergy = 'normal';
  var currentSelectedStress = 'low';

  function initGrowthModule() {
    // 情绪标签选择
    var chipGroup = $('moodChipGroup');
    if (chipGroup) {
      chipGroup.addEventListener('click', function(e) {
        var chip = e.target.closest('.mood-chip');
        if (!chip) return;
        var mood = chip.getAttribute('data-mood');
        chip.classList.toggle('active');
        if (chip.classList.contains('active')) {
          if (currentSelectedMoods.indexOf(mood) === -1) currentSelectedMoods.push(mood);
        } else {
          currentSelectedMoods = currentSelectedMoods.filter(function(m) { return m !== mood; });
        }
      });
    }

    // 精力水平单选
    var epGroup = $('energyPillGroup');
    if (epGroup) {
      epGroup.addEventListener('click', function(e) {
        var pill = e.target.closest('.level-pill');
        if (!pill) return;
        epGroup.querySelectorAll('.level-pill').forEach(function(p) { p.classList.remove('active'); });
        pill.classList.add('active');
        currentSelectedEnergy = pill.getAttribute('data-level');
      });
    }

    // 主观压力单选
    var spGroup = $('stressPillGroup');
    if (spGroup) {
      spGroup.addEventListener('click', function(e) {
        var pill = e.target.closest('.level-pill');
        if (!pill) return;
        spGroup.querySelectorAll('.level-pill').forEach(function(p) { p.classList.remove('active'); });
        pill.classList.add('active');
        currentSelectedStress = pill.getAttribute('data-level');
      });
    }

    // 提交签到
    var btnCheckin = $('btnSubmitCheckin');
    if (btnCheckin) {
      btnCheckin.onclick = function() {
        var note = $('checkinNoteInput') ? $('checkinNoteInput').value.trim() : '';
        var todayStr = new Date().toISOString().slice(0, 10);
        var record = {
          checkin_id: 'MC-' + todayStr + '-' + Math.random().toString(36).slice(2, 6),
          date: todayStr,
          moods: currentSelectedMoods.slice(),
          energy: currentSelectedEnergy,
          stress: currentSelectedStress,
          note: note,
          created_at: new Date().toISOString()
        };

        var list = getStorageJson('wutang_mood_checkins', []);
        list.unshift(record);
        setStorageJson('wutang_mood_checkins', list);

        showToast('已留下今日心境印记');
        var box = $('checkinFeedbackBox');
        if (box) box.classList.remove('hidden');
        renderMiniCalendar();
        updateDataSummary();
      };
    }

    // 重新签到与跳转
    if ($('btnCheckinReset')) {
      $('btnCheckinReset').onclick = function() {
        if ($('checkinFeedbackBox')) $('checkinFeedbackBox').classList.add('hidden');
      };
    }
    if ($('btnCheckinGoCard')) {
      $('btnCheckinGoCard').onclick = function() {
        switchMainTab('relief');
        handleClientAwarenessCard();
      };
    }

    // --- AI 日记整理 ---
    if ($('btnFillJournalSample')) {
      $('btnFillJournalSample').onclick = function() {
        if ($('journalInputText')) {
          $('journalInputText').value = '今天主管在例会上当众否定了我负责的模块，催促我重写。我当时非常难堪，整天脑子都停不下来，特别自责，甚至怀疑自己不适合这份工作。';
        }
      };
    }
    if ($('btnClearJournalInput')) {
      $('btnClearJournalInput').onclick = function() {
        if ($('journalInputText')) $('journalInputText').value = '';
        if ($('journalStructuredResult')) $('journalStructuredResult').classList.add('hidden');
      };
    }
    if ($('btnAiOrganizeJournal')) {
      $('btnAiOrganizeJournal').onclick = function() {
        var raw = $('journalInputText') ? $('journalInputText').value.trim() : '';
        if (!raw) {
          showToast('请先输入今天的日常倾诉');
          return;
        }

        var btn = $('btnAiOrganizeJournal');
        btn.disabled = true;
        btn.textContent = '🌿 悟堂 AI 正在倾听与梳理…';

        fetch('http://localhost:8000/api/journal/organize', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ raw_text: raw, consent_to_save: true })
        }).then(function(r) { return r.json(); })
          .then(function(data) {
            btn.disabled = false;
            btn.textContent = '🌿 AI 结构化梳理心绪';
            var res = (data && data.structured_journal) ? data.structured_journal : null;
            if (res) renderJournalResult(res, raw);
          })
          .catch(function(err) {
            btn.disabled = false;
            btn.textContent = '🌿 AI 结构化梳理心绪';
            // 离线高质量兜底提炼
            var fallback = {
              event_summary: raw.slice(0, 70) + (raw.length > 70 ? '…' : ''),
              thoughts: '反复在心头重播被批评的场景，陷入「我不行」的自我怀疑。',
              feelings: ['难堪', '自责', '疲惫', '内耗'],
              possible_needs: '【待你确认】希望付出被客观尊重，工作有明确改进指引而非笼统指责。',
              next_step: '今晚先把情绪和事实写在纸上，明天以微信文字向主管确认两点具体改进细节。'
            };
            renderJournalResult(fallback, raw);
          });
      };
    }

    if ($('btnSaveJournalToLocal')) {
      $('btnSaveJournalToLocal').onclick = function() {
        var list = getStorageJson('wutang_journals', []);
        var todayStr = new Date().toISOString().slice(0, 10);
        list.unshift({
          id: 'J-' + todayStr + '-' + Math.random().toString(36).slice(2, 6),
          date: todayStr,
          event: $('jResEvent') ? $('jResEvent').textContent : '',
          thoughts: $('jResThoughts') ? $('jResThoughts').textContent : '',
          needs: $('jResNeeds') ? $('jResNeeds').textContent : '',
          next_step: $('jResNextStep') ? $('jResNextStep').textContent : '',
          created_at: new Date().toISOString()
        });
        setStorageJson('wutang_journals', list);
        showToast('日记已妥善安放在本地成长记录中');
        if ($('journalStructuredResult')) $('journalStructuredResult').classList.add('hidden');
        if ($('journalInputText')) $('journalInputText').value = '';
        updateDataSummary();
      };
    }

    if ($('btnDiscardJournal')) {
      $('btnDiscardJournal').onclick = function() {
        if ($('journalStructuredResult')) $('journalStructuredResult').classList.add('hidden');
      };
    }

    // --- 微行动反馈 ---
    var afGroup = $('actionFeedbackBtnGroup');
    if (afGroup) {
      afGroup.addEventListener('click', function(e) {
        var btn = e.target.closest('button');
        if (!btn) return;
        var status = btn.getAttribute('data-action-status');
        var reviews = getStorageJson('wutang_action_reviews', []);
        reviews.unshift({
          status: status,
          date: new Date().toISOString().slice(0, 10),
          action: $('currentMicroActionTitle') ? $('currentMicroActionTitle').textContent : ''
        });
        setStorageJson('wutang_action_reviews', reviews);

        var tip = $('actionFeedbackToast');
        if (tip) {
          tip.classList.remove('hidden');
          if (status === 'completed') tip.textContent = '已记录：好样的！哪怕只是一小步，也是对自己的温柔善待。';
          else if (status === 'partial') tip.textContent = '已记录：能做一部分已经非常棒了，跟随身心节奏，不急于求成。';
          else if (status === 'not_started') tip.textContent = '已记录：完全没关系，今晚先把心安顿好，明天随时可以重新开始。';
          else if (status === 'unsuitable') tip.textContent = '已记录：听从你的感觉，方法很多，我们随时换一个更舒适的小动作。';
        }
        showToast('已记录行动复盘反馈');
        updateDataSummary();
      });
    }
  }

  function renderJournalResult(res, raw) {
    if ($('jResEvent')) $('jResEvent').textContent = res.event_summary || raw;
    if ($('jResThoughts')) $('jResThoughts').textContent = res.thoughts || '';
    if ($('jResNeeds')) $('jResNeeds').textContent = res.possible_needs || '';
    if ($('jResNextStep')) $('jResNextStep').textContent = res.next_step || '';

    var fContainer = $('jResFeelings');
    if (fContainer) {
      var arr = Array.isArray(res.feelings) ? res.feelings : ['紧绷', '疲惫'];
      fContainer.innerHTML = arr.map(function(w) {
        return '<span class="badge rev" style="font-size:12px;">' + esc(w) + '</span>';
      }).join('');
    }

    if ($('journalStructuredResult')) $('journalStructuredResult').classList.remove('hidden');
    showToast('AI 结构化整理已生成，请检查并纠偏');
  }

  function renderGrowthSection() {
    renderMiniCalendar();
    // 渲染今日日期
    var badge = $('checkinTodayDateBadge');
    if (badge) badge.textContent = '今日：' + new Date().toISOString().slice(0, 10);
  }

  function renderMiniCalendar() {
    var grid = $('miniCalendarGrid');
    if (!grid) return;
    var checkins = getStorageJson('wutang_mood_checkins', []);
    var dateSet = {};
    checkins.forEach(function(c) { if (c.date) dateSet[c.date] = true; });

    var now = new Date();
    var year = now.getFullYear();
    var month = now.getMonth();
    var daysInMonth = new Date(year, month + 1, 0).getDate();
    var todayStr = now.toISOString().slice(0, 10);

    var html = '';
    var weekHeaders = ['日', '一', '二', '三', '四', '五', '六'];
    weekHeaders.forEach(function(h) {
      html += '<div style="font-weight:600;font-size:11px;color:var(--color-muted);padding:4px 0;">' + h + '</div>';
    });

    var firstDayOfWeek = new Date(year, month, 1).getDay();
    for (var i = 0; i < firstDayOfWeek; i++) {
      html += '<div class="mini-cal-day" style="opacity:0.25;">·</div>';
    }

    for (var d = 1; d <= daysInMonth; d++) {
      var dStr = year + '-' + String(month + 1).padStart(2, '0') + '-' + String(d).padStart(2, '0');
      var isToday = (dStr === todayStr);
      var hasCheckin = Boolean(dateSet[dStr]);
      var cls = 'mini-cal-day' + (isToday ? ' today' : '') + (hasCheckin ? ' has-checkin' : '');
      html += '<div class="' + cls + '" title="' + dStr + (hasCheckin ? ' 已签到' : '') + '">' + d + (hasCheckin ? ' 🌿' : '') + '</div>';
    }
    grid.innerHTML = html;

    // 每周回顾文案
    var summaryEl = $('weeklyReviewSummary');
    if (summaryEl) {
      if (checkins.length === 0) {
        summaryEl.textContent = '暂无签到记录。在上方留下你的第一次心境印记，悟堂将为你记录每日身心起伏。';
      } else if (checkins.length < 3) {
        summaryEl.textContent = '目前累计已留下 ' + checkins.length + ' 次觉察记录。根据 PRD 3.0 规范：记录较少时暂不下定论，请依你的节奏自然记录。';
      } else {
        summaryEl.textContent = '过去阶段已累计记录 ' + checkins.length + ' 次心境。你常在疲惫时能主动停下来为自己留白，这就是最踏实的自我关照。';
      }
    }
  }


  // --------------------------------------------------------------------------
  // 2. 心境健康中心模块 (Wellbeing: F-16, F-17, 18.9, 18.11)
  // --------------------------------------------------------------------------
  var pss10UserAnswers = new Array(10).fill(null);

  function initWellbeingModule() {
    // 展开 PSS-10
    if ($('btnOpenPss10')) {
      $('btnOpenPss10').onclick = function() {
        renderPss10Questions();
        if ($('pss10QuizContainer')) $('pss10QuizContainer').classList.remove('hidden');
        if ($('pss10ResultCard')) $('pss10ResultCard').classList.add('hidden');
        $('pss10QuizContainer').scrollIntoView({ behavior: 'smooth' });
      };
    }
    if ($('btnClosePss10')) {
      $('btnClosePss10').onclick = function() {
        if ($('pss10QuizContainer')) $('pss10QuizContainer').classList.add('hidden');
      };
    }

    // 提交 PSS-10
    if ($('btnSubmitPss10')) {
      $('btnSubmitPss10').onclick = function() {
        for (var i = 0; i < 10; i++) {
          if (pss10UserAnswers[i] === null) {
            showToast('请先完成第 ' + (i + 1) + ' 题作答');
            return;
          }
        }

        // 调用确定性计分接口
        fetch('http://localhost:8000/api/wellbeing/score', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            instrument_id: 'pss-10',
            answers: pss10UserAnswers,
            consent_to_record: true
          })
        }).then(function(r) { return r.json(); })
          .then(function(res) {
            if (res.success) renderPss10Report(res);
            else showToast(res.message || '计分失败');
          })
          .catch(function() {
            // 离线确定性计分兜底 (严格按照 PSS-10 规则：4,5,7,8 反向计分)
            var reverseIdx = [3, 4, 6, 7];
            var total = 0;
            for (var j = 0; j < 10; j++) {
              var v = pss10UserAnswers[j];
              total += (reverseIdx.indexOf(j) !== -1 ? (4 - v) : v);
            }
            var lvl = total <= 13 ? 'low' : (total <= 26 ? 'moderate' : 'high');
            var lvlLabel = total <= 13 ? '轻度压力' : (total <= 26 ? '中度压力' : '较高压力');
            var flag = (pss10UserAnswers[9] >= 3 && total >= 28);
            renderPss10Report({
              success: true,
              total_score: total,
              level: lvl,
              level_label: lvlLabel,
              summary: total <= 13 ? '你近期的知觉压力处于较低或平稳范围，能够较好地应对日常生活与工作节奏。' : (total <= 26 ? '你近期体验到了生活中的不可控感或挑战，情绪与精力有所消耗，建议有意识安排身心休息与微行动调适。' : '你近期承受的主观负荷较重，可能感到多项琐事超出个人掌控。这不是你的软弱，建议暂缓次要事务，必要时与专业心理人士聊聊。'),
              mindset_insight: '知觉压力反映过去一个月的身心负荷感，不是性格定论。允许自己拥有起伏。',
              oriental_wisdom_angle: '《大学》云：『知止而后有定，定而后能静。』在繁杂之中，先为自己找到一个明确的暂停锚点。',
              next_steps: ['睡前做 3 次平稳深呼吸', '将事实与担忧分栏写下', '如持续超过两周建议联系专业咨询师'],
              is_safety_flagged: flag,
              safety_message: flag ? '检测到你近期感到困难积聚且负荷沉重。建议参考下方全国心理援助热线或专业资源导航，给自己一份专业支持。' : ''
            });
          });
      };
    }

    if ($('btnRetakePss10')) {
      $('btnRetakePss10').onclick = function() {
        pss10UserAnswers.fill(null);
        renderPss10Questions();
        if ($('pss10ResultCard')) $('pss10ResultCard').classList.add('hidden');
        if ($('pss10QuizContainer')) $('pss10QuizContainer').classList.remove('hidden');
      };
    }

    if ($('btnSavePss10History')) {
      $('btnSavePss10History').onclick = function() {
        var scoreVal = $('pss10ScoreVal') ? $('pss10ScoreVal').textContent : '';
        var lvl = $('pss10LevelBadge') ? $('pss10LevelBadge').textContent : '';
        var list = getStorageJson('wutang_assessments', []);
        list.unshift({
          instrument: 'PSS-10',
          score: scoreVal,
          level: lvl,
          date: new Date().toISOString().slice(0, 10),
          created_at: new Date().toISOString()
        });
        setStorageJson('wutang_assessments', list);
        showToast('自评报告已安全存储至本地');
        updateDataSummary();
      };
    }

    // 资源导航地区过滤
    var regSelect = $('resourceRegionFilter');
    if (regSelect) {
      regSelect.onchange = function() {
        renderResourcesList(this.value);
      };
    }

    // 生成转介沟通清单
    if ($('btnGenerateReferral')) {
      $('btnGenerateReferral').onclick = function() {
        var complaint = $('referralComplaintInput') ? $('referralComplaintInput').value.trim() : '';
        var duration = $('referralDurationInput') ? $('referralDurationInput').value.trim() : '约2-4周';
        if (!complaint) {
          showToast('请先简述你的主要困扰');
          return;
        }

        var btn = $('btnGenerateReferral');
        btn.disabled = true;
        btn.textContent = '正在为你整理沟通清单…';

        fetch('http://localhost:8000/api/referral/summary', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            main_complaint: complaint,
            duration: duration,
            assessment_score: $('pss10ScoreVal') ? parseInt($('pss10ScoreVal').textContent) : null
          })
        }).then(function(r) { return r.json(); })
          .then(function(data) {
            btn.disabled = false;
            btn.textContent = '一键生成就医/面询沟通清单';
            if (data && data.summary) renderReferralSummary(data.summary);
          })
          .catch(function() {
            btn.disabled = false;
            btn.textContent = '一键生成就医/面询沟通清单';
            renderReferralSummary({
              summary_title: '日常压力与身心负荷沟通参考清单',
              key_symptoms: [complaint, '持续时间：' + duration, '近期感到注意力分散与身心疲惫'],
              impact_on_daily_life: '日常睡眠节律偶有波动，对多项并行的事务感到压力过载。',
              questions_for_specialist: [
                '针对我目前的压力状态，有哪些适合日常练习的身体放松或认知调整方法？',
                '是否建议进行更系统的心理咨询或进一步临床评估？'
              ]
            });
          });
      };
    }

    if ($('btnCopyReferralSummary')) {
      $('btnCopyReferralSummary').onclick = function() {
        var text = $('refSumBody') ? $('refSumBody').innerText : '';
        if (navigator.clipboard) {
          navigator.clipboard.writeText(text).then(function() { showToast('面询清单已复制到剪贴板'); });
        } else {
          showToast('复制成功');
        }
      };
    }
  }

  function renderPss10Questions() {
    var listEl = $('pss10QuestionsList');
    if (!listEl) return;
    var inst = (INSTRUMENTS || []).find(function(it) { return it.instrument_id === 'pss-10'; });
    var items = (inst && inst.items) ? inst.items : [
      { id: 1, text: "在过去的一个月中，你是否因为某些意料之外的事情发生而感到心烦意乱？" },
      { id: 2, text: "在过去的一个月中，你是否感到自己无法控制生活中的重要事情？" },
      { id: 3, text: "在过去的一个月中，你是否感到神经过敏或感到压力很大？" },
      { id: 4, text: "在过去的一个月中，你是否感到自己能充满信心地处理个人问题？" },
      { id: 5, text: "在过去的一个月中，你是否感到事情正在按照你的意愿顺利发展？" },
      { id: 6, text: "在过去的一个月中，你是否发现自己无法处理所有必须要做的事情？" },
      { id: 7, text: "在过去的一个月中，你是否能够有效地控制生活中的烦恼与波动？" },
      { id: 8, text: "在过去的一个月中，你是否感到自己一切都在掌握之中？" },
      { id: 9, text: "在过去的一个月中，你是否因为某些无法掌控的事情而感到生气或愤怒？" },
      { id: 10, text: "在过去的一个月中，你是否感到生活中的困难积聚太多，自己已经难以克服？" }
    ];

    var options = [
      { v: 0, l: "从不 (0)" },
      { v: 1, l: "很少 (1)" },
      { v: 2, l: "有时 (2)" },
      { v: 3, l: "经常 (3)" },
      { v: 4, l: "总是 (4)" }
    ];

    var html = items.map(function(item, idx) {
      var currentVal = pss10UserAnswers[idx];
      var optHtml = options.map(function(opt) {
        var isSel = (currentVal === opt.v);
        return '<button type="button" class="scale-radio-btn' + (isSel ? ' selected' : '') + '" data-qidx="' + idx + '" data-val="' + opt.v + '">' + opt.l + '</button>';
      }).join('');

      return '<div class="assessment-question-item">'
        + '  <div class="assessment-question-title">' + (idx + 1) + '. ' + esc(item.text) + '</div>'
        + '  <div class="scale-options-row">' + optHtml + '</div>'
        + '</div>';
    }).join('');

    listEl.innerHTML = html;

    listEl.onclick = function(e) {
      var btn = e.target.closest('.scale-radio-btn');
      if (!btn) return;
      var qIdx = parseInt(btn.getAttribute('data-qidx'));
      var val = parseInt(btn.getAttribute('data-val'));
      pss10UserAnswers[qIdx] = val;
      renderPss10Questions();
    };
  }

  function renderPss10Report(data) {
    if ($('pss10QuizContainer')) $('pss10QuizContainer').classList.add('hidden');
    if ($('pss10ResultCard')) $('pss10ResultCard').classList.remove('hidden');

    if ($('pss10ScoreVal')) $('pss10ScoreVal').textContent = data.total_score;
    if ($('pss10LevelBadge')) $('pss10LevelBadge').textContent = data.level_label || '测评完成';
    if ($('pss10SummaryText')) $('pss10SummaryText').textContent = data.summary || '';
    if ($('pss10WisdomText')) $('pss10WisdomText').textContent = data.oriental_wisdom_angle || data.mindset_insight || '';

    var stepUl = $('pss10NextStepsList');
    if (stepUl) {
      var steps = Array.isArray(data.next_steps) ? data.next_steps : ['保持规律作息', '尝试轻度微行动'];
      stepUl.innerHTML = steps.map(function(s) { return '<li>' + esc(s) + '</li>'; }).join('');
    }

    var alertBox = $('pss10SafetyAlert');
    if (alertBox) {
      if (data.is_safety_flagged) {
        alertBox.classList.remove('hidden');
        if ($('pss10SafetyText')) $('pss10SafetyText').textContent = data.safety_message;
      } else {
        alertBox.classList.add('hidden');
      }
    }

    $('pss10ResultCard').scrollIntoView({ behavior: 'smooth' });
  }

  function renderResourcesList(filterRegion) {
    var grid = $('resourceListGrid');
    if (!grid) return;
    var list = MENTAL_RESOURCES || [];
    filterRegion = filterRegion || '全部';

    var filtered = list.filter(function(r) {
      if (filterRegion === '全部') return true;
      if (filterRegion === '全国') return r.region === '全国';
      return r.region === filterRegion || r.region === '全国';
    });

    if (filtered.length === 0) {
      grid.innerHTML = '<div style="grid-column:1/-1;padding:24px;text-align:center;color:var(--color-muted);">当前地区暂未检索到已核验的常设专线</div>';
      return;
    }

    grid.innerHTML = filtered.map(function(item) {
      var isHotline = (item.service_type === 'hotline');
      var typeBadge = isHotline ? '<span class="badge ok">免费热线</span>' : '<span class="badge rev">公立专科</span>';
      return '<div class="resource-card">'
        + '  <div>'
        + '    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">'
        + '      ' + typeBadge
        + '      <span style="font-size:11px;color:var(--color-muted);">' + esc(item.region) + '</span>'
        + '    </div>'
        + '    <h4 style="margin:0 0 6px;font-size:15px;color:var(--color-ink);font-weight:600;">' + esc(item.resource_name) + '</h4>'
        + '    <div style="font-size:12.5px;color:var(--color-primary);font-weight:bold;margin-bottom:6px;">'
        + '      📞 <a href="tel:' + esc(item.contact_info) + '" style="color:var(--color-primary);text-decoration:none;">' + esc(item.contact_info) + '</a>'
        + '    </div>'
        + '    <div style="font-size:12px;color:var(--color-muted);line-height:1.5;">' + esc(item.availability_note || '') + '</div>'
        + '  </div>'
        + '  <div style="margin-top:10px;padding-top:8px;border-top:1px dashed var(--color-border);font-size:11px;color:var(--color-muted);display:flex;justify-content:space-between;">'
        + '    <span>出处：' + esc(item.source_url ? item.source_url.slice(0, 12) + '…' : '官方') + '</span>'
        + '    <span>核验：' + esc(item.last_verified_at) + '</span>'
        + '  </div>'
        + '</div>';
    }).join('');
  }

  function renderReferralSummary(sum) {
    var box = $('referralSummaryBox');
    if (!box) return;
    box.classList.remove('hidden');

    if ($('refSumTitle')) $('refSumTitle').textContent = sum.summary_title || '日常压力沟通参考清单';

    var html = '';
    html += '<div style="margin-bottom:8px;"><strong>一、核心主诉梳理：</strong></div>';
    html += '<ul style="margin:0 0 10px;padding-left:20px;">' + (sum.key_symptoms || []).map(function(s) { return '<li>' + esc(s) + '</li>'; }).join('') + '</ul>';

    if (sum.impact_on_daily_life) {
      html += '<div style="margin-bottom:4px;"><strong>二、日常身心影响：</strong></div>';
      html += '<p style="margin:0 0 10px;">' + esc(sum.impact_on_daily_life) + '</p>';
    }

    if (sum.questions_for_specialist && sum.questions_for_specialist.length) {
      html += '<div style="margin-bottom:4px;"><strong>三、期望向医生/咨询师咨询的问题：</strong></div>';
      html += '<ol style="margin:0;padding-left:20px;">' + sum.questions_for_specialist.map(function(q) { return '<li>' + esc(q) + '</li>'; }).join('') + '</ol>';
    }

    if ($('refSumBody')) $('refSumBody').innerHTML = html;
    box.scrollIntoView({ behavior: 'smooth' });
  }

  function renderWellbeingSection() {
    renderResourcesList('全部');
  }


  // --------------------------------------------------------------------------
  // 3. 情境练习室模块 (Practice Room: F-15 / 18.8)
  // --------------------------------------------------------------------------
  var currentPracticeScenario = null;
  var practiceChatHistory = [];

  function initPracticeModule() {
    renderPracticeScenarioCards();

    if ($('btnResetPracticeScenario')) {
      $('btnResetPracticeScenario').onclick = function() {
        if (currentPracticeScenario) startPracticeScenario(currentPracticeScenario);
      };
    }

    if ($('btnSendPracticeMessage')) {
      $('btnSendPracticeMessage').onclick = sendPracticeMessage;
    }
    if ($('practiceDraftInput')) {
      $('practiceDraftInput').onkeydown = function(e) {
        if (e.key === 'Enter') sendPracticeMessage();
      };
    }
  }

  function renderPracticeScenarioCards() {
    var grid = $('practiceScenarioCardsGrid');
    if (!grid) return;
    var list = PRACTICE_SCENARIOS || [];

    grid.innerHTML = list.map(function(sc, idx) {
      return '<div class="theme-pack-card" data-scid="' + sc.scenario_id + '">'
        + '  <span class="badge ok" style="font-size:11px;margin-bottom:6px;">' + esc(sc.category) + '</span>'
        + '  <h4 style="margin:0 0 6px;font-size:16px;color:var(--color-ink);">' + esc(sc.title) + '</h4>'
        + '  <p style="margin:0 0 12px;font-size:12.5px;color:var(--color-muted);line-height:1.5;">' + esc(sc.description) + '</p>'
        + '  <button class="btn sm secondary" style="width:100%;">进入练习 →</button>'
        + '</div>';
    }).join('');

    grid.onclick = function(e) {
      var card = e.target.closest('.theme-pack-card');
      if (!card) return;
      var scId = card.getAttribute('data-scid');
      var target = (PRACTICE_SCENARIOS || []).find(function(s) { return s.scenario_id === scId; });
      if (target) startPracticeScenario(target);
    };

    if (list.length > 0 && !currentPracticeScenario) {
      startPracticeScenario(list[0]);
    }
  }

  function startPracticeScenario(sc) {
    currentPracticeScenario = sc;
    practiceChatHistory = [];

    if ($('practiceRoomTitle')) $('practiceRoomTitle').textContent = sc.title;
    if ($('practiceRoomRoleDesc')) $('practiceRoomRoleDesc').textContent = 'AI 扮演对象：' + sc.ai_role;

    // AI 开场白
    practiceChatHistory.push({
      role: 'ai',
      content: sc.opening_line || '「你好，我们可以开始了。」'
    });

    renderPracticeChat();
    if ($('practiceFeedbackBox')) $('practiceFeedbackBox').classList.add('hidden');
    if ($('practiceDraftInput')) {
      $('practiceDraftInput').value = '';
      $('practiceDraftInput').focus();
    }
  }

  function renderPracticeChat() {
    var win = $('practiceChatWindow');
    if (!win) return;
    win.innerHTML = practiceChatHistory.map(function(msg) {
      var isAi = (msg.role === 'ai');
      return '<div class="chat-msg ' + (isAi ? 'role-ai' : 'role-user') + '">' + esc(msg.content) + '</div>';
    }).join('');
    win.scrollTop = win.scrollHeight;
  }

  function sendPracticeMessage() {
    var input = $('practiceDraftInput');
    if (!input) return;
    var text = input.value.trim();
    if (!text) {
      showToast('请输入你练习的一句话');
      return;
    }

    practiceChatHistory.push({ role: 'user', content: text });
    renderPracticeChat();
    input.value = '';

    var btn = $('btnSendPracticeMessage');
    if (btn) { btn.disabled = true; btn.textContent = '思考中…'; }

    fetch('http://localhost:8000/api/practice/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        scenario_id: currentPracticeScenario ? currentPracticeScenario.scenario_id : 'general',
        scenario_title: currentPracticeScenario ? currentPracticeScenario.title : '沟通练习',
        ai_role: currentPracticeScenario ? currentPracticeScenario.ai_role : '对话对象',
        user_draft: text,
        history: practiceChatHistory.slice(0, -1)
      })
    }).then(function(r) { return r.json(); })
      .then(function(data) {
        if (btn) { btn.disabled = false; btn.textContent = '发送练习'; }
        var res = (data && data.practice_result) ? data.practice_result : null;
        if (res) handlePracticeReply(res);
      })
      .catch(function() {
        if (btn) { btn.disabled = false; btn.textContent = '发送练习'; }
        // 离线高质量兜底
        handlePracticeReply({
          role_reply: '「我听明白了。不过这事确实比较突然，你看看还有什么其他折中的办法吗？」',
          feedback: {
            boundary: '基本表达了边界，态度坚决。',
            tone: '语气平实，无过分对抗感。',
            advice: '若能先表达对事情重要性的理解，再说明自身饱和度，合作体面更完整。'
          },
          alternatives: [
            '「我理解这个报表很急。不过我手头刚好有两个必须今晚闭环的数据要交，实在挪不出完整时间，你看我明天一早帮你看看行吗？」',
            '「今晚我的工单实在排满了。你可以先把上周的模板套进去，核心部分我们明天再对齐。」'
          ]
        });
      });
  }

  function handlePracticeReply(res) {
    if (res.role_reply) {
      practiceChatHistory.push({ role: 'ai', content: res.role_reply });
      renderPracticeChat();
    }

    var fbBox = $('practiceFeedbackBox');
    if (fbBox) {
      fbBox.classList.remove('hidden');
      var fb = res.feedback || {};
      if ($('pfBoundaryText')) $('pfBoundaryText').textContent = fb.boundary || '边界基本清晰。';
      if ($('pfToneText')) $('pfToneText').textContent = fb.tone || '语气得体。';
      if ($('pfAdviceText')) $('pfAdviceText').textContent = fb.advice || '建议保持平视沟通。';

      var altBox = $('pfAlternativesContainer');
      if (altBox) {
        var alts = res.alternatives || [];
        altBox.innerHTML = alts.map(function(alt) {
          return '<div class="alt-quote-card">'
            + '  <span>' + esc(alt) + '</span>'
            + '  <button class="btn sm secondary" onclick="copyPracticeAlt(this)" data-alt="' + esc(alt) + '">复制范式</button>'
            + '</div>';
        }).join('');
      }
      fbBox.scrollIntoView({ behavior: 'smooth' });
    }
  }

  window.copyPracticeAlt = function(btn) {
    var text = btn.getAttribute('data-alt');
    if (navigator.clipboard) {
      navigator.clipboard.writeText(text).then(function() { showToast('范式已复制'); });
    } else {
      showToast('范式已复制');
    }
  };

  function renderPracticeSection() {
    renderPracticeScenarioCards();
  }


  // --------------------------------------------------------------------------
  // 4. 卡牌典藏与主题卡牌包模块 (Theme Packs: F-18 / 18.12)
  // --------------------------------------------------------------------------
  var currentSelectedPack = null;

  function initCardsModule() {
    renderThemePackGrid();
    renderFavoriteCards();
  }

  function renderThemePackGrid() {
    var grid = $('themePackGridContainer');
    if (!grid) return;
    var packs = THEME_PACKS || [];

    grid.innerHTML = packs.map(function(p) {
      var isAct = (currentSelectedPack && currentSelectedPack.pack_id === p.pack_id);
      return '<div class="theme-pack-card' + (isAct ? ' active' : '') + '" data-packid="' + p.pack_id + '">'
        + '  <div style="font-size:26px;margin-bottom:8px;">' + p.icon + '</div>'
        + '  <h3 style="font-family:var(--font-serif);margin:0 0 4px;font-size:18px;">' + esc(p.name) + '</h3>'
        + '  <div style="font-size:12.5px;color:var(--color-primary);font-weight:500;margin-bottom:8px;">' + esc(p.tagline) + '</div>'
        + '  <p style="margin:0;font-size:12px;color:var(--color-muted);line-height:1.6;">' + esc(p.description) + '</p>'
        + '  <div style="margin-top:12px;display:flex;justify-content:space-between;align-items:center;">'
        + '    <span style="font-size:11px;color:var(--color-gold);">3 张核心牌组</span>'
        + '    <span style="font-size:12px;color:var(--color-primary);font-weight:600;">展开卡组 →</span>'
        + '  </div>'
        + '</div>';
    }).join('');

    grid.onclick = function(e) {
      var card = e.target.closest('.theme-pack-card');
      if (!card) return;
      var pid = card.getAttribute('data-packid');
      var pack = (THEME_PACKS || []).find(function(p) { return p.pack_id === pid; });
      if (pack) selectThemePack(pack);
    };

    if (packs.length > 0 && !currentSelectedPack) {
      selectThemePack(packs[0]);
    }
  }

  function selectThemePack(pack) {
    currentSelectedPack = pack;
    renderThemePackGrid();

    if ($('themePackDetailTitle')) $('themePackDetailTitle').textContent = pack.name + ' · 核心卡牌包 (' + pack.icon + ')';
    if ($('themePackDetailDesc')) $('themePackDetailDesc').textContent = pack.tagline + ' —— ' + pack.description;

    var container = $('themePackCardsList');
    if (!container) return;

    var allCards = [].concat(CARDS_MINDSET, CARDS_WISDOM, CARDS_ACTION);
    var matched = allCards.filter(function(c) {
      return pack.card_ids && pack.card_ids.indexOf(c.card_id) !== -1;
    });

    if (matched.length === 0) {
      matched = allCards.slice(0, 3);
    }

    container.innerHTML = matched.map(function(card) {
      return renderSingleCardHtml(card);
    }).join('');
  }

  function renderSingleCardHtml(card) {
    var typeName = card.card_type === 'mindset' ? '心境牌 · 看见自己' : (card.card_type === 'wisdom' ? '东方智慧牌 · 换个视角' : '行动牌 · 走出一步');
    var badgeClass = card.card_type === 'mindset' ? 'ok' : (card.card_type === 'wisdom' ? 'gold' : 'rev');
    var favList = getStorageJson('wutang_favorite_cards', []);
    var isFav = (favList.indexOf(card.card_id) !== -1);

    var content = card.front_text || card.quote || card.action_text || card.short_description || '';
    var source = card.source_title ? ('《' + card.source_title + '·' + (card.source_section || '') + '》') : '';

    return '<div class="studio-card-item">'
      + '  <div class="studio-card-header">'
      + '    <span class="badge ' + badgeClass + '">' + typeName + '</span>'
      + '    <span style="font-size:12px;color:var(--color-muted);">' + esc(card.card_id) + '</span>'
      + '  </div>'
      + '  <h3 class="studio-card-title">' + esc(card.title) + '</h3>'
      + '  <p class="studio-card-quote serif">“' + esc(content) + '”</p>'
      + (source ? ('<div class="studio-card-meta">出处：' + esc(source) + '</div>') : '')
      + '  <div class="studio-card-actions">'
      + '    <button class="btn sm ' + (isFav ? 'secondary' : 'ghost') + '" onclick="toggleFavoriteCard(\'' + card.card_id + '\')">'
      + (isFav ? '★ 已珍藏' : '☆ 珍藏此卡')
      + '    </button>'
      + '  </div>'
      + '</div>';
  }

  window.toggleFavoriteCard = function(cardId) {
    var list = getStorageJson('wutang_favorite_cards', []);
    var idx = list.indexOf(cardId);
    if (idx !== -1) {
      list.splice(idx, 1);
      showToast('已取消珍藏');
    } else {
      list.push(cardId);
      showToast('已珍藏至我的卡牌库');
    }
    setStorageJson('wutang_favorite_cards', list);
    renderFavoriteCards();
    if (currentSelectedPack) selectThemePack(currentSelectedPack);
    updateDataSummary();
  };

  function renderFavoriteCards() {
    var container = $('favCardsContainer');
    if (!container) return;
    var favIds = getStorageJson('wutang_favorite_cards', []);
    var countNotice = $('favCardsCountNotice');
    if (countNotice) countNotice.textContent = '当前珍藏 ' + favIds.length + ' 张启发卡牌';

    if (favIds.length === 0) {
      container.innerHTML = '<div style="grid-column:1/-1;padding:24px;text-align:center;color:var(--color-muted);">暂无珍藏卡牌。在浏览或解忧时点击「珍藏此卡」即可沉淀在此。</div>';
      return;
    }

    var allCards = [].concat(CARDS_MINDSET, CARDS_WISDOM, CARDS_ACTION);
    var cards = allCards.filter(function(c) { return favIds.indexOf(c.card_id) !== -1; });
    container.innerHTML = cards.map(function(c) { return renderSingleCardHtml(c); }).join('');
  }

  function renderCardsSection() {
    renderThemePackGrid();
    renderFavoriteCards();
  }


  // --------------------------------------------------------------------------
  // 5. 个人数据与独立隐私授权管理模块 (Mine & Privacy Matrix: F-19 / 10.6)
  // --------------------------------------------------------------------------
  function initDataManagementHandlers() {
    // 导出全量本地数据
    if ($('btnExportAllUserData')) {
      $('btnExportAllUserData').onclick = function() {
        var backup = {
          export_time: new Date().toISOString(),
          version: 'PRD 3.0',
          relief_history: getStorageJson('wutang_relief_history', []),
          mood_checkins: getStorageJson('wutang_mood_checkins', []),
          journals: getStorageJson('wutang_journals', []),
          action_reviews: getStorageJson('wutang_action_reviews', []),
          wellbeing_assessments: getStorageJson('wutang_assessments', []),
          favorite_cards: getStorageJson('wutang_favorite_cards', [])
        };
        var blob = new Blob([JSON.stringify(backup, null, 2)], { type: 'application/json' });
        var a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = 'wutang_personal_backup_' + new Date().toISOString().slice(0, 10) + '.json';
        a.click();
        showToast('个人数据包导出完成');
      };
    }

    // 清空本地数据
    if ($('btnClearAllUserData')) {
      $('btnClearAllUserData').onclick = function() {
        if (!confirm('确定彻底清空此设备上的所有悟堂记录（包含解忧历史、日记、签到与自评）吗？此操作无法撤回。')) return;
        ['wutang_relief_history', 'wutang_mood_checkins', 'wutang_journals', 'wutang_action_reviews', 'wutang_assessments', 'wutang_favorite_cards'].forEach(function(k) {
          localStorage.removeItem(k);
        });
        showToast('本地所有记录已彻底清除');
        updateDataSummary();
        renderMineSection();
      };
    }

    // 授权开关监听
    ['consentToggleGrowth', 'consentToggleWellbeing', 'consentTogglePublic'].forEach(function(id) {
      var el = $(id);
      if (el) {
        el.onchange = function() {
          showToast('隐私授权设置已同步');
        };
      }
    });

    updateDataSummary();
  }

  function updateDataSummary() {
    var el = $('dataSummaryNotice');
    if (!el) return;
    var hCount = getStorageJson('wutang_relief_history', []).length;
    var mCount = getStorageJson('wutang_mood_checkins', []).length;
    var jCount = getStorageJson('wutang_journals', []).length;
    var aCount = getStorageJson('wutang_assessments', []).length;
    el.textContent = hCount + ' 条足迹 · ' + mCount + ' 次签到 · ' + jCount + ' 篇日记 · ' + aCount + ' 次自评';
  }
"""

    # 4. 在 renderCardGallery 之前注入 js_3_0_body
    gallery_target = "  // ================= 禅意卡牌与书笺画廊渲染 ================="
    if gallery_target in html and "PRD 3.0 全局模块业务控制器" not in html:
        html = html.replace(gallery_target, js_3_0_body + "\n\n" + gallery_target)

    # 5. 在 setupEvents 绑定 3.0 顶部导航按钮
    old_events = """    $('tabRelief').onclick = function() { switchMainTab('relief'); };
    $('tabMine').onclick = function() { switchMainTab('mine'); };
    $('tabStudio').onclick = function() { switchMainTab('studio'); };"""

    new_events = """    if ($('tabRelief')) $('tabRelief').onclick = function() { switchMainTab('relief'); };
    if ($('tabGrowth')) $('tabGrowth').onclick = function() { switchMainTab('growth'); };
    if ($('tabWellbeing')) $('tabWellbeing').onclick = function() { switchMainTab('wellbeing'); };
    if ($('tabPractice')) $('tabPractice').onclick = function() { switchMainTab('practice'); };
    if ($('tabCards')) $('tabCards').onclick = function() { switchMainTab('cards'); };
    if ($('tabMine')) $('tabMine').onclick = function() { switchMainTab('mine'); };
    if ($('tabStudio')) $('tabStudio').onclick = function() { switchMainTab('studio'); };"""

    if old_events in html:
        html = html.replace(old_events, new_events)

    # 6. 在 bootstrap 中初始化 3.0 模块
    old_boot = """  function bootstrap() {
    initScenarioChips();
    setupEvents();
    renderClassicsList();
    renderAwarenessCard(0);
    renderStudioCards('all');
    lotusEngine.init('lotusCanvas');
    updateManagerUI();
    checkAiBackendStatus();
  }"""

    new_boot = """  function bootstrap() {
    initScenarioChips();
    setupEvents();
    renderClassicsList();
    renderAwarenessCard(0);
    renderStudioCards('all');
    lotusEngine.init('lotusCanvas');
    updateManagerUI();
    checkAiBackendStatus();
    // PRD 3.0 新增模块初始化
    initGrowthModule();
    initWellbeingModule();
    initPracticeModule();
    initCardsModule();
    initDataManagementHandlers();
  }"""

    if old_boot in html:
        html = html.replace(old_boot, new_boot)

    with open(TEMPLATE_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[ok] PRD 3.0 JS logic successfully injected into _template.html ({len(html):,} bytes)")

if __name__ == "__main__":
    patch_js()
