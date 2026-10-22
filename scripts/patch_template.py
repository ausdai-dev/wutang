# patch finishToResult in frontend/_template.html
with open('frontend/_template.html', 'r', encoding='utf-8') as f:
    c = f.read()

target = "      saveConsultationHistory(text, pendingMeta.scenario, pendingMeta.cards, initialRes);\n\n      switchClientView('userResult');"

replacement = """      saveConsultationHistory(text, pendingMeta.scenario, pendingMeta.cards, initialRes);

      switchClientView('userResult');

      // 立即填充专属解脱之道卡牌与最契合的 96 觉察心象画卷（避免等待 SSE 结束时才显示或白屏）
      var w = (pendingMeta.cards && pendingMeta.cards.wisdom) ? pendingMeta.cards.wisdom : {};
      var ws = w.classic_source || {};
      var curTrack = pendingMeta.track || appState.selectedTrack || 'confucianism';
      var masterName = (appState.selectedMaster === 'laozi') ? '老子' : ((appState.selectedMaster === 'shakyamuni') ? '释迦牟尼' : ((appState.selectedMaster === 'all') ? '三圣合参' : '孔子'));
      var initialSig = {
        card_name: (w.name || (curTrack === 'daoism' ? '若水' : (curTrack === 'buddhism' ? '无住' : '克己'))).slice(0, 4),
        master: masterName,
        school: curTrack,
        aphorism: ws.quote || w.original_text || '君子求诸己，万般皆因行未至。',
        english_mantra: (curTrack === 'daoism' ? 'Flow like water, rest in quiet simplicity.' : (curTrack === 'buddhism' ? 'Abide nowhere to discover true peace.' : 'Self-discipline brings enduring dignity.')),
        classic_source: ws.book ? ('《' + ws.book + '·' + ws.chapter + '》（' + ws.author + '）') : '《论语·卫灵公》（春秋·孔子）',
        quote: ws.quote || '君子求诸己，小人求诸人。',
        interpretation: ws.translation || w.modern_interpretation || '把力气收回到自己身上，是瓦解内耗的唯一解药。',
        action_title: (pendingMeta.cards && pendingMeta.cards.action && pendingMeta.cards.action.title) ? pendingMeta.cards.action.title : '静坐调息，记录眼前可控之事',
        action_steps: (pendingMeta.cards && pendingMeta.cards.action && pendingMeta.cards.action.steps) ? pendingMeta.cards.action.steps : ['闭目静坐呼吸三次', '记录当下可控之事']
      };
      if (typeof updateLiberationCardView === 'function') {
        updateLiberationCardView(initialSig);
      }"""

if target in c:
    c = c.replace(target, replacement, 1)
    with open('frontend/_template.html', 'w', encoding='utf-8') as f:
        f.write(c)
    print("SUCCESS: frontend/_template.html updated successfully")
else:
    print("ERROR: Target not found")
