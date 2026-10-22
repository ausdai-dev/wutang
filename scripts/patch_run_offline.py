with open("frontend/_template.html", "r", encoding="utf-8") as f:
    content = f.read()

target = "switchClientView('userResult');\n\n  }"
replacement = """switchClientView('userResult');

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
  }"""

if target in content:
    content = content.replace(target, replacement, 1)
    with open("frontend/_template.html", "w", encoding="utf-8") as f:
        f.write(content)
    print("[ok] Injected updateLiberationCardView into runOfflineRelief!")
else:
    print("[x] Target not found")
