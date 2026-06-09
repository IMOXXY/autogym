import requests
import json
import os
import sys
import re
from datetime import datetime, timedelta

BASE_URL = "http://order.njmu.edu.cn:8088/cgyd"
USERNAME = os.environ.get('GYM_USERNAME', '')
PASSWORD = os.environ.get('GYM_PASSWORD', '')
SERVICE_ID = '41'
COORDINATE_DES = ','.join([f'2_football_场地{i}' for i in range(1, 31)])

OPEN_DAYS = {1, 2, 4, 5, 6, 7}
session = requests.Session()

def login():
    data = {'dlm': USERNAME, 'mm': PASSWORD, 'logintype': 'sno'}
    r = session.post(f'{BASE_URL}/login.html', data=data, timeout=15, allow_redirects=True)
    print(f'[DEBUG] login status={r.status_code}, url={r.url}')
    if r.status_code != 200:
        return False
    if '\u767b\u5f55\u5931\u8d25' in r.text or '\u8bf7\u6c42\u5931\u8d25' in r.text:
        return False
    r2 = session.get(f'{BASE_URL}/', timeout=15)
    print(f'[DEBUG] index status={r2.status_code}, url={r2.url}')
    print('[+] \u767b\u5f55\u6210\u529f')
    return True

def get_slots(date):
    p = {'s_dates': date, 'serviceid': SERVICE_ID, 'coordinatedes': COORDINATE_DES}
    r = session.get(f'{BASE_URL}/product/getarea.html', params=p, timeout=15)
    if r.status_code != 200:
        return []
    m = re.search(r'<li data-row="9">(.*?)</li>', r.text, re.DOTALL)
    if not m:
        print('[-] \u672a\u627e\u5230 18:01-19:00')
        return []
    c = re.findall(r'<span[^>]*class="cell piece(?!.*?lock)"[^>]*data-stockid="(\d+)"[^>]*data-venue="([^"]*)"[^>]*data-id="([^"]*)"[^>]*>', m.group(1))
    avail = [{'sid': s, 'v': v, 'cid': c2} for s, v, c2 in c if s]
    print(f'[+] {date} \u53ef\u9884\u7ea6: {len(avail)}')
    for a in avail:
        print(f'    {a["v"]}')
    return avail

def book(slot):
    m = {'stockdetail': {slot['sid']: slot['cid']}, 'serviceid': SERVICE_ID, 'stockid': slot['sid'] + ',', 'remark': ''}
    r = session.post(f'{BASE_URL}/order/tobook.html', data={'param': json.dumps(m), 'num': '1'}, timeout=15)
    try:
        j = r.json()
        if j.get('result') == '1':
            print(f'[+] \u2705 \u6210\u529f! orderid={j["object"]["orderid"]}')
            return True
        else:
            print(f'[-] \u274c \u5931\u8d25: {j.get("message", "")}')
            return False
    except:
        print(f'[-] \u5f02\u5e38: {r.text[:200]}')
        return False

def main():
    if not USERNAME or not PASSWORD:
        print('[-] \u7f3a\u5c11 GYM_USERNAME/PASSWORD')
        sys.exit(1)
    date = sys.argv[1] if len(sys.argv) > 1 else (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    w = datetime.strptime(date, '%Y-%m-%d').isoweekday()
    if w not in OPEN_DAYS:
        print(f'[*] {date} \u5468{w} \u4f11\u606f\u8df3\u8fc7')
        return
    print(f'[*] {date} 18:01-19:00 (\u5468{w})')
    if not login():
        sys.exit(1)
    session.get(f'{BASE_URL}/product/show.html?id={SERVICE_ID}', timeout=15)
    slots = get_slots(date)
    if not slots:
        print('[-] \u6ca1\u6709\u53ef\u7528\u573a\u5730')
        return
    s = slots[0]
    print(f'[*] \u9009\u62e9: {s["v"]}')
    book(s)

if __name__ == '__main__':
    main()
