import requests
import json
import os
import sys
import re
from datetime import datetime, timedelta

BASE_URL = "http://order.njmu.edu.cn:8088/cgyd"
USERNAME = os.environ.get("GYM_USERNAME", "")
PASSWORD = os.environ.get("GYM_PASSWORD", "")
SERVICE_ID = "41"
COORDINATE_DES = ",".join([f"2_football_\u573a\u5730{i}" for i in range(1, 31)])

# \u5065\u8eab\u623f\u5f00\u653e\u65f6\u95f4\uff08\u5468\u4e09\u4f11\u606f\uff09
OPEN_DAYS = {1, 2, 4, 5, 6, 7}  # Mon=1, Tue=2, Wed=3, Thu=4, Fri=5, Sat=6, Sun=7

session = requests.Session()

def login():
    login_data = {"dlm": USERNAME, "mm": PASSWORD, "logintype": "sno"}
    resp = session.post(f"{BASE_URL}/login.html", data=login_data, timeout=15)
    if resp.status_code != 200:
        print(f"[-] \u767b\u5f55\u5931\u8d25 HTTP {resp.status_code}")
        return False
    if resp.url != f"{BASE_URL}/":
        print(f"[-] \u767b\u5f55\u5931\u8d25\uff0c\u8bf7\u68c0\u67e5\u8d26\u53f7\u5bc6\u7801")
        return False
    print(f"[+] \u767b\u5f55\u6210\u529f\uff01")
    return True

def get_available_slots(target_date):
    params = {"s_dates": target_date, "serviceid": SERVICE_ID, "coordinatedes": COORDINATE_DES}
    resp = session.get(f"{BASE_URL}/product/getarea.html", params=params, timeout=15)
    if resp.status_code != 200:
        print(f"[-] \u83b7\u53d6\u573a\u5730\u5931\u8d25 HTTP {resp.status_code}")
        return []

    # \u627e row=9 (18:01-19:00)
    m = re.search(r'<li data-row="9">(.*?)</li>', resp.text, re.DOTALL)
    if not m:
        print("[-] \u672a\u627e\u5230 18:01-19:00 \u65f6\u6bb5")
        return []

    cells = re.findall(
        r'<span[^>]*class="cell piece(?!.*?lock)"[^>]*data-stockid="(\d+)"[^>]*'
        r'data-venue="([^"]*)"[^>]*data-id="([^"]*)"[^>]*>',
        m.group(1)
    )
    available = [{"stockid": s, "venue": v, "cell_id": c} for s, v, c in cells if s]
    print(f"[+] {target_date} 18:01-19:00 \u53ef\u9884\u7ea6: {len(available)} \u573a\u5730")
    for a in available:
        print(f"    - {a['venue']}")
    return available

def book(available_slot):
    model = {
        "stockdetail": {available_slot["stockid"]: available_slot["cell_id"]},
        "serviceid": SERVICE_ID,
        "stockid": available_slot["stockid"] + ",",
        "remark": "",
    }
    resp = session.post(f"{BASE_URL}/order/tobook.html",
                        data={"param": json.dumps(model), "num": "1"}, timeout=15)
    try:
        result = resp.json()
        if result.get("result") == "1":
            oid = result.get("object", {}).get("orderid", "")
            print(f"[+] \u2705 \u9884\u7ea6\u6210\u529f\uff01\u8ba2\u5355 ID: {oid}")
            return True
        else:
            print(f"[-] \u274c \u9884\u7ea6\u5931\u8d25: {result.get('message', '\u672a\u77e5\u9519\u8bef')}")
            return False
    except Exception as e:
        print(f"[-] \u5f02\u5e38: {e}")
        return False

def main():
    if not USERNAME or not PASSWORD:
        print("[-] \u8bf7\u8bbe\u7f6e GYM_USERNAME \u548c GYM_PASSWORD \u73af\u5883\u53d8\u91cf")
        sys.exit(1)

    target_date = sys.argv[1] if len(sys.argv) > 1 else (datetime.now() + timedelta(days=0)).strftime("%Y-%m-%d")

    # \u68c0\u67e5\u5468\u51e0
    dt = datetime.strptime(target_date, "%Y-%m-%d")
    weekday = dt.isoweekday()
    if weekday not in OPEN_DAYS:
        print(f"[*] {target_date} \u662f\u5468{weekday}\uff0c\u5065\u8eab\u623f\u4f11\u606f\uff0c\u8df3\u8fc7")
        return

    print(f"[*] \u5f00\u59cb\u9884\u7ea6: {target_date} 18:01-19:00 (\u5468{weekday})")

    if not login():
        sys.exit(1)

    # \u8bbf\u95ee\u9884\u7ea6\u9875
    session.get(f"{BASE_URL}/product/show.html?id={SERVICE_ID}", timeout=15)

    available = get_available_slots(target_date)
    if not available:
        print("[-] \u6ca1\u6709\u53ef\u9884\u7ea6\u7684\u573a\u5730")
        return

    slot = available[0]
    print(f"[*] \u9009\u62e9: {slot['venue']}")
    book(slot)

if __name__ == "__main__":
    main()
