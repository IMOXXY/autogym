# -*- coding: utf-8 -*-
import requests
import json
import os
import sys
import re
from datetime import datetime, timedelta

BASE_URL = 'http://order.njmu.edu.cn:8088/cgyd'
USERNAME = os.environ.get('GYM_USERNAME', '')
PASSWORD = os.environ.get('GYM_PASSWORD', '')
SERVICE_ID = '41'

# Gym closed on Wednesday (3), open other days
OPEN_DAYS = {1, 2, 4, 5, 6, 7}

# 30 venues
changdi = chr(0x573a) + chr(0x5730)
COORD = ','.join(['2_football_' + changdi + str(i) for i in range(1, 31)])

session = requests.Session()

def login():
    s = session
    # Login - yzm=1 means no captcha needed for first 5 attempts
    data = {'dlm': USERNAME, 'mm': PASSWORD, 'logintype': 'sno', 'yzm': '1'}
    r = s.post(BASE_URL + '/login.html', data=data, timeout=15, allow_redirects=True)
    print('LOGIN: status=%d, url=%s' % (r.status_code, r.url))
    
    if r.status_code != 200:
        print('ERROR: Login failed (HTTP %d)' % r.status_code)
        return False
    
    # Verify by visiting home page
    r2 = s.get(BASE_URL + '/', timeout=15)
    print('HOME: status=%d, url=%s' % (r2.status_code, r2.url))
    print('SUCCESS: Logged in')
    return True

def get_available_slots(date_str):
    s = session
    # First visit the show page
    s.get(BASE_URL + '/product/show.html?id=' + SERVICE_ID, timeout=15)
    
    # Then get area data
    params = {'s_dates': date_str, 'serviceid': SERVICE_ID, 'coordinatedes': COORD}
    r = s.get(BASE_URL + '/product/getarea.html', params=params, timeout=15)
    
    if r.status_code != 200:
        print('ERROR: getarea failed (HTTP %d)' % r.status_code)
        return []
    
    # Find row 9 (18:01-19:00)
    m = re.search(r'<li data-row="9">(.*?)</li>', r.text, re.DOTALL)
    if not m:
        print('WARN: No row 9 found for 18:01-19:00')
        # Show available rows for debugging
        rows = re.findall(r'data-row="(\d+)"', r.text)
        print('Available rows:', sorted(set(rows)))
        return []
    
    row_html = m.group(1)
    
    # Find cells that are NOT locked (i.e., available for booking)
    # Match: class="cell piece ..." without "lock", with a non-empty data-stockid
    pattern = r'class="cell piece (?!.*?lock)"[^>]*data-stockid="(\d+)"[^>]*data-venue="([^"]*)"[^>]*data-id="([^"]*)"[^>]*>'
    cells = re.findall(pattern, row_html)
    
    available = []
    for stockid, venue, cell_id in cells:
        if stockid:
            available.append({'stockid': stockid, 'venue': venue, 'cell_id': cell_id})
    
    print('AVAILABLE: %d venues at 18:01-19:00' % len(available))
    for a in available:
        print('  - %s' % a['venue'])
    
    return available

def book(slot):
    s = session
    model = {
        'stockdetail': {slot['stockid']: slot['cell_id']},
        'serviceid': SERVICE_ID,
        'stockid': slot['stockid'] + ',',
        'remark': ''
    }
    r = s.post(
        BASE_URL + '/order/tobook.html',
        data={'param': json.dumps(model), 'num': '1'},
        timeout=15
    )
    try:
        result = r.json()
        if result.get('result') == '1':
            oid = result.get('object', {}).get('orderid', '')
            print('SUCCESS: Booked! Order ID: %s' % oid)
            return True
        else:
            print('FAILED: %s' % result.get('message', 'Unknown error'))
            return False
    except Exception as e:
        print('ERROR: %s - Response: %s' % (e, r.text[:200]))
        return False

def main():
    if not USERNAME or not PASSWORD:
        print('ERROR: Missing GYM_USERNAME or GYM_PASSWORD environment variables')
        sys.exit(1)
    
    # Target date = tomorrow
    date_str = sys.argv[1] if len(sys.argv) > 1 else (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Check if gym is open on this day
    dt = datetime.strptime(date_str, '%Y-%m-%d')
    weekday = dt.isoweekday()
    if weekday not in OPEN_DAYS:
        print('SKIP: %s is day %d (gym closed on Wednesdays)' % (date_str, weekday))
        return
    
    print('START: Booking for %s 18:01-19:00 (day %d)' % (date_str, weekday))
    
    if not login():
        sys.exit(1)
    
    slots = get_available_slots(date_str)
    if not slots:
        print('NO SLOTS: No available venues for %s 18:01-19:00' % date_str)
        return
    
    chosen = slots[0]
    print('CHOOSING: %s' % chosen['venue'])
    book(chosen)

if __name__ == '__main__':
    main()
