with open("frontend/_template.html", "r", encoding="utf-8") as f:
    content = f.read()

OLD_TAB = '<button class="mode-tab" id="tabCards" title="卡牌典藏与主题卡牌包">卡牌典藏</button>'
NEW_TAB = '<button class="mode-tab" id="tabCards" title="儒释道卡牌人生与百八常道图鉴">卡牌人生</button>'

if OLD_TAB in content:
    content = content.replace(OLD_TAB, NEW_TAB, 1)
    print("Updated tabCards button label!")

# Update runOfflineRelief to synthesize liberation card signature
OLD_OFFLINE = """  function runOfflineRelief(caseId, sc, text, presetMindsetCard) {
    var cards = matchReliefCards(sc, text, presetMindsetCard);
    appState.currentCards = cards;
    var res = assembleFourStep(caseId, sc, text, cards);
    appState.currentResult = res;
    renderResultView(res);
    saveConsultationHistory(text, sc, cards, res);
    switchClientView('userResult');
  }"""

NEW_OFFLINE = """  function runOfflineRelief(caseId, sc, text, presetMindsetCard) {
    var cards = matchReliefCards(sc, text, presetMindsetCard);
    appState.currentCards = cards;
    var res = assembleFourStep(caseId, sc, text, cards);
    appState.currentResult = res;
    renderResultView(res);
    saveConsultationHistory(text, sc, cards, res);

    var w = cards.wisdom || {};
    var ws = w.classic_source || {};
    var masterName = (appState.selectedMaster === 'laozi') ? '老子' : ((appState.selectedMaster === 'shakyamuni') ? '释迦牟尼' : ((appState.selectedMaster === 'all') ? '三圣合参' : '孔子'));
    var fallbackSig = {
      card_name: (w.name || (appState.selectedTrack === 'daoism' ? '若水' : (appState.selectedTrack === 'buddhism' ? '无住' : '克己'))).slice(0, 2),
      master: masterName,
      school: appState.selectedTrack || 'confucianism',
      aphorism: ws.quote || w.original_text || '君子求诸己，万般皆因行未至。',
      english_mantra: (appState.selectedTrack === 'daoism' ? 'Flow like water, rest in quiet simplicity.' : (appState.selectedTrack === 'buddhism' ? 'Abide nowhere to discover true peace.' : 'Self-discipline brings enduring dignity.')),
      classic_source: ws.book ? ('《' + ws.book + '·' + ws.chapter + '》（' + ws.author + '）') : '《论语·卫灵公》（春秋·孔子）',
      quote: ws.quote || '君子求诸己，小人求诸人。',
      interpretation: ws.translation || w.modern_interpretation || '把力气收回到自己身上，是瓦解内耗的唯一解药。',
      action_title: (cards.action && cards.action.title) ? cards.action.title : '静坐调息，记录眼前可控之事',
      action_steps: (cards.action && cards.action.steps) ? cards.action.steps : ['闭目静坐呼吸三次', '记录当下可控之事']
    };
    updateLiberationCardView(fallbackSig);

    switchClientView('userResult');
  }"""

if OLD_OFFLINE in content:
    content = content.replace(OLD_OFFLINE, NEW_OFFLINE, 1)
    print("Updated runOfflineRelief to invoke updateLiberationCardView!")

with open("frontend/_template.html", "w", encoding="utf-8") as f:
    f.write(content)

print("Saved frontend/_template.html!")
