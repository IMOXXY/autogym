# -*- coding: utf-8 -*-
import requests, re, sys

BASE_URL = 'http://order.njmu.edu.cn:8088/cgyd'
s = requests.Session()

# Login
data = {'dlm': '24250125', 'mm': '285117', 'logintype': 'sno', 'yzm': '1'}
r = s.post(BASE_URL + '/login.html', data=data, timeout=15, allow_redirects=True)

# Extract JSESSIONID from URL if present
jsid = ''
m = re.search(r'jsessionid=([A-F0-9]+)', r.url, re.IGNORECASE)
if m:
    jsid = m.group(1)
    print('JSESSIONID: %s' % jsid)

# Visit show page
s.get(BASE_URL + '/product/show.html?id=41', timeout=15)

# Try getarea with jsessionid in URL
changdi = chr(0x573a) + chr(0x5730)
coord = ','.join(['2_football_' + changdi + str(i) for i in range(1, 31)])
p = {'s_dates': '2026-06-11', 'serviceid': '41', 'coordinatedes': coord}

if jsid:
    url = BASE_URL + '/product/getarea.html;jsessionid=' + jsid
else:
    url = BASE_URL + '/product/getarea.html'

r = s.get(url, params=p, timeout=15)
print('Status:', r.status_code)

# Count non-lock cells
non_lock = len(re.findall(r'class="cell piece[^"]*"[^>]*>ø…”√|<span[^>]*class="cell piece"[^>]*>', r.text))
locked = len(re.findall(r'lock', r.text))
print('Locked cells:', locked)

# Look for ANY cell without lock class
all_spans = re.findall(r'<span[^>]*class="cell piece[^"]*"[^>]*>.*?</span>', r.text)
for sp in all_spans[:3]:
    if 'lock' not in sp:
        print('UNLOCKED:', sp[:200])
    else:
        print('Locked:', sp[:150])
