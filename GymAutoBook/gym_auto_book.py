"""
Gym Auto Book - 自动预约健身房
"""
import json
import os
import sys
import logging
from datetime import datetime, timedelta

import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# ---------- Constants ----------
BASE_URL = "http://order.njmu.edu.cn:8088/cgyd"
SERVICE_ID = "41"
TARGET_TIME_SLOT = "18:01-19:00"
OPEN_DAYS = {1, 2, 4, 5, 6, 7}  # Monday=1 ... Sunday=7

# ---------- Logging ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


# ---------- Helper: create session ----------
def _create_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    return session


# ---------- Login ----------
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((requests.RequestException, ConnectionError)),
)
def login() -> requests.Session | None:
    """Login to the gym booking system."""
    session = _create_session()
    login_data = {
        "dlm": USERNAME,
        "mm": PASSWORD,
        "logintype": "sno",
        "yzm": "1",
    }
    resp = session.post(
        f"{BASE_URL}/login.html",
        data=login_data,
        timeout=15,
        allow_redirects=False,
    )
    if resp.status_code not in (301, 302, 200):
        log.error("Login failed, HTTP %d", resp.status_code)
        return None
    log.info("Login successful")
    return session


# ---------- Find available slots ----------
@retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=1, max=5),
    retry=retry_if_exception_type((requests.RequestException, json.JSONDecodeError)),
)
def find_slots(session: requests.Session, date_str: str) -> list[dict]:
    """Find available slots for the target time on a given date."""
    session.get(f"{BASE_URL}/product/show.html?id={SERVICE_ID}", timeout=15)
    resp = session.get(
        f"{BASE_URL}/product/findOkArea.html",
        params={"s_date": date_str, "serviceid": SERVICE_ID},
        timeout=15,
    )
    resp.raise_for_status()
    items = resp.json().get("object", [])
    return [
        item for item in items
        if item.get("stock", {}).get("time_no") == TARGET_TIME_SLOT
    ]


# ---------- Book a slot ----------
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((requests.RequestException, json.JSONDecodeError)),
)
def book(session: requests.Session, slot: dict) -> bool:
    """Book a specific time slot."""
    model = {
        "stockdetail": {str(slot["stockid"]): str(slot["id"])},
        "serviceid": SERVICE_ID,
        "stockid": f'{slot["stockid"]},',
        "remark": "",
        "users": "",
    }
    resp = session.post(
        f"{BASE_URL}/order/tobook.html",
        data={"param": json.dumps(model), "num": "1", "json": "true"},
        timeout=15,
    )
    resp.raise_for_status()
    result = resp.json()
    if result.get("result") == "1":
        order_id = result.get("object", {}).get("orderid", "")
        log.info("SUCCESS! Order ID: %s", order_id)
        return True
    else:
        log.warning("Booking failed: %s", result.get("message", "Unknown error"))
        return False


# ---------- Notification ----------
def send_notify(message: str):
    """Send notification via webhook if NOTIFY_URL is set."""
    notify_url = os.environ.get("NOTIFY_URL", "")
    if not notify_url:
        return
    try:
        requests.post(notify_url, json={"text": message}, timeout=10)
    except requests.RequestException:
        log.warning("Failed to send notification")


# ---------- Main ----------
def main():
    global USERNAME, PASSWORD
    USERNAME = os.environ.get("GYM_USERNAME", "")
    PASSWORD = os.environ.get("GYM_PASSWORD", "")

    if not USERNAME or not PASSWORD:
        log.error("Missing GYM_USERNAME or GYM_PASSWORD environment variables")
        sys.exit(1)

    # Parse target date (default: tomorrow)
    date_str = sys.argv[1] if len(sys.argv) > 1 else (
        datetime.now() + timedelta(days=1)
    ).strftime("%Y-%m-%d")

    # Check if gym is open on that day
    weekday = datetime.strptime(date_str, "%Y-%m-%d").isoweekday()
    if weekday not in OPEN_DAYS:
        log.info("SKIP: %s - gym closed (weekday %d)", date_str, weekday)
        return

    log.info("Booking %s %s", date_str, TARGET_TIME_SLOT)

    try:
        session = login()
        if not session:
            send_notify(f"? 健身房预约登录失败 ({date_str})")
            sys.exit(1)

        slots = find_slots(session, date_str)
        log.info("Available slots: %d", len(slots))

        if not slots:
            log.warning("No available slots for %s", date_str)
            return

        chosen = slots[0]
        log.info("Choosing: %s", chosen.get("sname", "Unknown"))

        if book(session, chosen):
            log.info("Booking completed successfully")
        else:
            send_notify(f"? 健身房预约失败 ({date_str})")
            sys.exit(1)

    except requests.RequestException as exc:
        log.error("Network error: %s", exc)
        send_notify(f"? 健身房预约网络异常 ({date_str}): {exc}")
        sys.exit(1)
    except (json.JSONDecodeError, KeyError, ValueError) as exc:
        log.error("Data parse error: %s", exc)
        send_notify(f"? 健身房预约数据异常 ({date_str}): {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
