# -*- coding: utf-8 -*-
import io

content = io.open(r'd:\BaiduSyncdisk\02-DEV\悟堂\frontend\index.html', encoding='utf-8').read()

print('--- practice scenarios ---')
for pid in ['sc-refuse-request', 'sc-express-need', 'sc-handle-feedback',
            'sc-different-opinion', 'sc-crucial-prep']:
    print(pid, content.count(pid))

print('--- mindset scenarios ---')
for k in ['"key":"work"', '"key":"relation"', '"key":"night"',
          '"key":"growth"', '"key":"communication"']:
    print(k, content.count(k))

print('--- practice room UI title ---')
print('情境练习室', content.count('情境练习室'))
