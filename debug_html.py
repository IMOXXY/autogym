# -*- coding: utf-8 -*-
import requests, re, sys
from datetime import datetime, timedelta

BASE_URL = 'http://order.njmu.edu.cn:8088/cgyd'
s = requests.Session()

data = {'dlm': '24250125', 'mm': '285117', 'logintype': 'sno', 'yzm': '1'}
s.post(BASE_URL + '/login.html', data=data, timeout=15, allow_redirects=True)
s.get(BASE_URL + '/')

changdi = chr(0x573a) + chr(0x5730)
coord = ','.join(['2_football_' + changdi + str(i) for i in range(1, 31)])

r = s.get(BASE_URL + '/product/getarea.html', params={'s_dates': '2026-06-11', 'serviceid': '41', 'coordinatedes': coord}, timeout=15)

m = re.search(r'<li data-row="9">(.*?)</li>', r.text, re.DOTALL)
if m:
    html = m.group(1)
    # Print a few representative cells
    cells = re.findall(r'(<span[^>]*>.*?</span>)', html)
    print('Total cells in row 9:', len(cells))
    for i, c in enumerate(cells[:5]):
        print('  Cell %d: %s' % (i, c[:250]))
    print('  ...')
    # Check all unique class variants
    classes = set(re.findall(r'class="([^"]*)"', html))
    print('All unique classes:', classes)
    # Check stockid values
    stockids = re.findall(r'data-stockid="([^"]*)"', html)
    non_empty = [s for s in stockids if s]
    print('Non-empty stockids:', len(non_empty))
else:
    print('Row 9 not found!')
    rows = re.findall(r'data-row="(\d+)"', r.text)
    print('Available rows:', sorted(set(rows)))
