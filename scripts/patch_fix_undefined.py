# -*- coding: utf-8 -*-
"""
Fix the 'undefined' bug in step 01 (听见了):
1. In assembleFourStep, cards.mindset does not have a .quote property (it has .front_text).
   Replace cards.mindset.quote with (cards.mindset.front_text || cards.mindset.quote || cards.mindset.short_description || '').
   Add strict guard against empty or 'undefined'.
2. In updateStreamingFourStep, support both '01 听见了' and PRD 4.0 '闻心' / '示道' / '笃行' / '法印'
   so that LLM streamed content updates stepText01/02/03/04 properly.
"""
import re
import os

TEMPLATE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', '_template.html')

with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix assembleFourStep mindset quote bug
old_mindset_code = """    var empathyText = generateEmpathy(scenario, text);

    if (cards && cards.mindset) {

      empathyText += ' 当下你所体会的，可能正如这句觉察：「' + cards.mindset.quote + '」。';

    }"""

new_mindset_code = """    var empathyText = generateEmpathy(scenario, text);

    if (cards && cards.mindset) {

      var mindsetText = (cards.mindset.front_text || cards.mindset.quote || cards.mindset.short_description || '').trim();

      if (mindsetText && mindsetText !== 'undefined') {

        empathyText += ' 当下你所体会的，可能正如这句觉察：「' + mindsetText + '」。';

      }

    }"""

if old_mindset_code in content:
    content = content.replace(old_mindset_code, new_mindset_code, 1)
    print("[1] assembleFourStep mindset front_text patched (undefined removed).")
else:
    # Try regex match
    pattern_m = re.compile(r'var empathyText = generateEmpathy\(scenario, text\);\s*if \(cards && cards\.mindset\) \{\s*empathyText \+= [^\n]*cards\.mindset\.quote[^\n]*;\s*\}')
    m = pattern_m.search(content)
    if m:
        content = content[:m.start()] + new_mindset_code + content[m.end():]
        print("[1] assembleFourStep mindset patched via regex.")
    else:
        raise SystemExit("Error: old_mindset_code pattern not found!")

# 2. Fix updateStreamingFourStep to match 闻心, 示道, 笃行, 法印
old_stream_match = """      if (l.indexOf('01 听见了') !== -1) { current = '01'; continue; }

      if (l.indexOf('02 古人有云') !== -1) { current = '02'; continue; }

      if (l.indexOf('03 试试这一招') !== -1) { current = '03'; continue; }

      if (l.indexOf('04 读这一段') !== -1) { current = '04'; continue; }"""

new_stream_match = """      if (l.indexOf('01 听见了') !== -1 || l.indexOf('闻心') !== -1) { current = '01'; continue; }

      if (l.indexOf('02 古人有云') !== -1 || l.indexOf('示道') !== -1) { current = '02'; continue; }

      if (l.indexOf('03 试试这一招') !== -1 || l.indexOf('笃行') !== -1) { current = '03'; continue; }

      if (l.indexOf('04 读这一段') !== -1 || l.indexOf('法印') !== -1) { current = '04'; continue; }"""

if old_stream_match in content:
    content = content.replace(old_stream_match, new_stream_match, 1)
    print("[2] updateStreamingFourStep enhanced for PRD 4.0 master sections.")
else:
    pattern_sm = re.compile(r'if \(l\.indexOf\(\'01 听见了\'\) !== -1\)[^}]*if \(l\.indexOf\(\'04 读这一段\'\) !== -1\) \{ current = \'04\'; continue; \}')
    m_sm = pattern_sm.search(content)
    if m_sm:
        content = content[:m_sm.start()] + new_stream_match + content[m_sm.end():]
        print("[2] updateStreamingFourStep enhanced via regex.")
    else:
        print("[2] Warning: updateStreamingFourStep pattern not matched directly.")

with open(TEMPLATE_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print("[SUCCESS] Patches applied to frontend/_template.html!")
