# -*- coding: utf-8 -*-
import requests, re, sys

BASE_URL = 'http://order.njmu.edu.cn:8088/cgyd'
s = requests.Session()

# Login
data = {'dlm': '24250125', 'mm': '285117', 'logintype': 'sno', 'yzm': '1'}
s.post(BASE_URL + '/login.html', data=data, timeout=15, allow_redirects=True)

# Visit show page first
r = s.get(BASE_URL + '/product/show.html?id=41', timeout=15)

# Check stock info
stocks = re.findall(r'sy_([^"]+).*?<small>.*? </small>(\d+)', r.text)
print('Stock info:')
for date, stock in stocks:
    print('  %s: %s remaining' % (date, stock))

# Also check what coordinatedes is in the page
coord_match = re.search(r'id="coordinatedes" value="([^"]*)"', r.text)
if coord_match:
    print('coordinatedes from page:', coord_match.group(1)[:100])

# Now try with the EXACT coordinate from the page
coord = coord_match.group(1) if coord_match else ''
changdi = chr(0x573a) + chr(0x5730)
coord2 = ','.join(['2_football_' + changdi + str(i) for i in range(1, 31)])

# Try both
for label, c in [('from_page', coord), ('generated', coord2)]:
    p = {'s_dates': '2026-06-11', 'serviceid': '41', 'coordinatedes': c}
    r2 = s.get(BASE_URL + '/product/getarea.html', params=p, timeout=15)
    locked = len(re.findall(r'lock', r2.text))
    spans = len(re.findall(r'<span', r2.text))
    print('getarea (%s): locked=%d spans=%d' % (label, locked, spans))
    
    # Check what class the cells have
    classes = set(re.findall(r'class="([^"]*)"', r2.text))
    print('  classes:', classes)
