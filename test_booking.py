import requests, re, urllib.parse

BASE_URL = 'http://order.njmu.edu.cn:8088/cgyd'
s = requests.Session()

data = {'dlm': '24250125', 'mm': '285117', 'logintype': 'sno', 'yzm': '1'}
r = s.post(BASE_URL + '/login.html', data=data, timeout=15, allow_redirects=True)
print('Login OK')

s.get(BASE_URL + '/product/show.html?id=41', timeout=15)

cd = chr(0x573a) + chr(0x5730)
coord_raw = ','.join(['2_football_' + cd + str(i) for i in range(1, 31)])
coord_encoded = urllib.parse.quote(coord_raw, safe=',')

query = 's_dates=2026-06-11&serviceid=41&coordinatedes=' + coord_encoded
url = BASE_URL + '/product/getarea.html?' + query
print('URL:', url[:150])

r = s.get(url, timeout=15)
print('Status:', r.status_code)

locked = len(re.findall(r'lock', r.text))
spans = len(re.findall(r'<span', r.text))
print('Locked:', locked, 'Total spans:', spans)

m = re.search(r'<li data-row=
