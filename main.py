import time
import json
import os
import random
import requests
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

GIFT_URL = "https://ks-giftcode.centurygame.com/"

# =========================
# 👉 여기만 수정하면 됨
# =========================
PLAYERS = {
    "Ethereal": "17770771",
    "Wireshark": "37281298",
}

USED_CODES_FILE = "used_codes.json"
MAX_RETRY = 3


def log(msg):
    print(msg, flush=True)


def random_delay(a=1.5, b=3.5):
    time.sleep(random.uniform(a, b))


# =========================
# 중복 코드 관리
# =========================
def load_used_codes():
    if os.path.exists(USED_CODES_FILE):
        with open(USED_CODES_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_used_codes(codes):
    with open(USED_CODES_FILE, "w") as f:
        json.dump(list(codes), f)


# =========================
# 🔥 HTML 파싱 방식 (핵심)
# =========================
def get_active_codes():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        url = "https://kingshot.net/gift-codes"
        res = requests.get(url, headers=headers, timeout=10)

        print("STATUS:", res.status_code)

        html = res.text

        match = re.search(r"Active Gift Codes([\s\S]*?)Expired Gift Codes", html)
        if not match:
            print("Active 코드 영역 못 찾음")
            return []

        active_section = match.group(1)

        raw_codes = re.findall(r"\b[A-Z0-9]{6,16}\b", active_section)

        blacklist = {"COPY", "CODE", "REDEEM", "NOW", "SHARE", "LINK", "ACTIVE"}

        codes = list(set([c for c in raw_codes if c not in blacklist]))

        print("추출된 코드:", codes)

        return codes

    except Exception as e:
        print("코드 파싱 실패:", e)
        return []


# =========================
# Selenium 설정
# =========================
def init_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 15)

    return driver, wait


# =========================
# 코드 적용
# =========================
def apply_code(driver, wait, pid, name, code):
    for attempt in range(MAX_RETRY):
        try:
            driver.get(GIFT_URL)

            player_input = wait.until(
                EC.presence_of_element_located((By.XPATH, '//input[@placeholder="플레이어 ID"]'))
            )
            player_input.clear()
            player_input.send_keys(pid)

            driver.find_element(By.CLASS_NAME, "login_btn").click()

            code_input = wait.until(
                EC.presence_of_element_located((By.XPATH, '//input[@placeholder="교환 코드를 입력해 주세요"]'))
            )
            code_input.clear()
            code_input.send_keys(code)

            driver.find_element(By.CLASS_NAME, "exchange_btn").click()

            log(f"SUCCESS: {name} ({pid}) / {code}")
            return True

        except Exception as e:
            log(f"RETRY {attempt+1}/{MAX_RETRY}: {code} / {e}")
            random_delay(2, 4)

    log(f"FAIL: {name} ({pid}) / {code}")
    return False


# =========================
# 실행
# =========================
def run():
    used_codes = load_used_codes()
    new_codes = get_active_codes()

    codes = [c for c in new_codes if c not in used_codes]

    if not codes:
        log("신규 코드 없음")
        return

    driver, wait = init_driver()

    for name, pid in PLAYERS.items():
        log(f"▶ {name} ({pid})")

        for code in codes:
            success = apply_code(driver, wait, pid, name, code)

            if success:
                used_codes.add(code)

            random_delay()

    driver.quit()
    save_used_codes(used_codes)

    log("=== DONE ===")


if __name__ == "__main__":
    run()
