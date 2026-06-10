# -*- coding: utf-8 -*-
import requests, re, sys

BASE_URL = 'http://order.njmu.edu.cn:8088/cgyd'
s = requests.Session()

data = {'dlm': '24250125', 'mm': '285117', 'logintype': 'sno', 'yzm': '1'}
s.post(BASE_URL + '/login.html', data=data, timeout=15, allow_redirects=True)
s.get(BASE_URL + '/')

changdi = chr(0x573a) + chr(0x5730)
coord = ','.join(['2_football_' + changdi + str(i) for i in range(1, 31)])

r = s.get(BASE_URL + '/product/getarea.html', params={'s_dates': '2026-06-11', 'serviceid': '41', 'coordinatedes': coord}, timeout=15)

# Check all rows
for row_num in range(1, 12):
    m = re.search(r'<li data-row="%d">(.*?)</li>' % row_num, r.text, re.DOTALL)
    if m:
        html = m.group(1)
        locked = len(re.findall(r'lock', html))
        total = len(re.findall(r'<span', html))
        stockids = [s for s in re.findall(r'data-stockid="([^"]*)"', html) if s]
        sample_time = re.search(r'data-timer="([^"]*)"', html)
        time = sample_time.group(1) if sample_time else '??'
        print('Row %d (%s): total=%d locked=%d available=%d' % (row_num, time, total, locked, total-locked))
    else:
        print('Row %d: NOT FOUND' % row_num)
