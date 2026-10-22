# -*- coding: utf-8 -*-
with open('frontend/_template.html', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Reset currentResonantZenCard on userLoading
t1 = "    // 正常困扰：进入 U-02 整理过渡状态（3D 莲花绽放旋转与沉淀）\n\n    switchClientView('userLoading');"
r1 = "    // 正常困扰：进入 U-02 整理过渡状态（3D 莲花绽放旋转与沉淀）\n    currentResonantZenCard = null;\n\n    switchClientView('userLoading');"
if t1 in c:
    c = c.replace(t1, r1, 1)
    print("Patch 1 applied: Reset on userLoading")
else:
    print("Warning: Patch 1 target not found")

# 2. In finishToResult, pass matched_zen_card
t2 = """        action_title: (pendingMeta.cards && pendingMeta.cards.action && pendingMeta.cards.action.title) ? pendingMeta.cards.action.title : '静坐调息，记录眼前可控之事',
        action_steps: (pendingMeta.cards && pendingMeta.cards.action && pendingMeta.cards.action.steps) ? pendingMeta.cards.action.steps : ['闭目静坐呼吸三次', '记录当下可控之事']
      };"""

r2 = """        action_title: (pendingMeta.cards && pendingMeta.cards.action && pendingMeta.cards.action.title) ? pendingMeta.cards.action.title : '静坐调息，记录眼前可控之事',
        action_steps: (pendingMeta.cards && pendingMeta.cards.action && pendingMeta.cards.action.steps) ? pendingMeta.cards.action.steps : ['闭目静坐呼吸三次', '记录当下可控之事'],
        matched_zen_card: (pendingMeta && pendingMeta.matched_zen_card) ? pendingMeta.matched_zen_card : null
      };"""
if t2 in c:
    c = c.replace(t2, r2, 1)
    print("Patch 2 applied: matched_zen_card passed in initialSig")
else:
    print("Warning: Patch 2 target not found")

# 3. In updateResonantZenCard, add anti-flicker lock
t3 = """  function updateResonantZenCard(matchedCard, sig) {
    var card = matchedCard;
    if (!card) {
      var userText = $('userTextarea') ? $('userTextarea').value.trim() : '';
      card = findClientResonantZenCard(userText, appState.selectedTrack, sig);
    }
    if (!card) return;

    currentResonantZenCard = card;"""

r3 = """  function updateResonantZenCard(matchedCard, sig, force) {
    var container = $('resonantZenCardContainer');
    if (!container) return;

    // 绝对防抖锁：如果本轮解忧已展示了卡牌且非强制换牌
    if (currentResonantZenCard && !force) {
      // 如果传入的新卡牌卡号与当前不同，坚决不进行画面替换，杜绝流式结束后图文突变
      if (matchedCard && matchedCard.card_id && currentResonantZenCard.card_id && matchedCard.card_id !== currentResonantZenCard.card_id) {
        return;
      }
      // 若卡号一致，仅平滑补全更细腻的契合之由（文本补充），不重刷图片与标题
      if (matchedCard && matchedCard.match_reason && $('rcReason')) {
        $('rcReason').textContent = matchedCard.match_reason;
      }
      return;
    }

    var card = matchedCard;
    if (!card) {
      var userText = $('userTextarea') ? $('userTextarea').value.trim() : '';
      card = findClientResonantZenCard(userText, appState.selectedTrack, sig);
    }
    if (!card) return;

    currentResonantZenCard = card;"""

if t3 in c:
    c = c.replace(t3, r3, 1)
    print("Patch 3 applied: Anti-flicker lock in updateResonantZenCard")
else:
    print("Warning: Patch 3 target not found")

with open('frontend/_template.html', 'w', encoding='utf-8') as f:
    f.write(c)

print("Template patching complete.")
