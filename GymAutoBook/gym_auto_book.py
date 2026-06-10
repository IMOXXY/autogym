import requests, json, os, sys
from datetime import datetime, timedelta

B = "http://order.njmu.edu.cn:8088/cgyd"
U = os.environ.get("GYM_USERNAME", "")
P = os.environ.get("GYM_PASSWORD", "")
OPEN_DAYS = {1, 2, 4, 5, 6, 7}

session = requests.Session()

def login():
    r = session.post(B + "/login.html", data={"dlm":U,"mm":P,"logintype":"sno","yzm":"1"}, timeout=15, allow_redirects=False)
    if r.status_code not in (301, 302, 200):
        print("Login failed:", r.status_code)
        return False
    s2 = requests.Session()
    s2.cookies.update(session.cookies)
    global session
    session = s2
    return True

def find_slots(date_str):
    session.get(B + "/product/show.html?id=41", timeout=15)
    r = session.get(B + "/product/findOkArea.html", params={"s_date":date_str,"serviceid":"41"}, timeout=15)
    items = r.json().get("object", [])
    return [it for it in items if it.get("stock",{}).get("time_no")=="18:01-19:00"]

def book(slot):
    model = {
        "stockdetail": {str(slot["stockid"]): str(slot["id"])},
        "serviceid": "41",
        "stockid": str(slot["stockid"]) + ",",
        "remark": "",
        "users": ""
    }
    r = session.post(B + "/order/tobook.html", data={"param": json.dumps(model), "num": "1", "json": "true"}, timeout=15)
    res = r.json()
    if res.get("result") == "1":
        oid = res.get("object", {}).get("orderid", "")
        print("SUCCESS! Order ID:", oid)
        return True
    else:
        print("FAILED:", res.get("message", "Unknown error"))
        return False

def main():
    if not U or not P:
        print("Missing GYM_USERNAME or GYM_PASSWORD")
        sys.exit(1)
    date_str = sys.argv[1] if len(sys.argv) > 1 else (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    w = datetime.strptime(date_str, "%Y-%m-%d").isoweekday()
    if w not in OPEN_DAYS:
        print("SKIP:", date_str, "gym closed")
        return
    print("Booking", date_str, "18:01-19:00")
    if not login():
        sys.exit(1)
    print("Login OK")
    slots = find_slots(date_str)
    print("Available:", len(slots))
    if not slots:
        print("No available slots")
        return
    s = slots[0]
    print("Choosing:", s["sname"])
    book(s)

if __name__ == "__main__":
    main()