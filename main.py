import time
import json
import os
import random
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

GIFT_URL = "https://ks-giftcode.centurygame.com/"

# 👉 네가 준 URL 그대로 사용
GAS_URL = "https://script.google.com/macros/s/AKfycbwtsKZym8FNZMDBlwkMB3cEwAvJhIK3tdgU9AkCTsrF8Wx7RNynE1CVcOqBwVBA6GSV/exec"

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


def load_used_codes():
    if os.path.exists(USED_CODES_FILE):
        with open(USED_CODES_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_used_codes(codes):
    with open(USED_CODES_FILE, "w") as f:
        json.dump(list(codes), f)


# 🔥 GAS에서 코드 가져오기
def get_active_codes():
    try:
        res = requests.get(GAS_URL, timeout=10)

        print("STATUS:", res.status_code)
        print("TEXT:", res.text[:200])

        data = res.json()
        codes = data.get("codes", [])

        print("GAS 코드:", codes)

        return list(set(codes))

    except Exception as e:
        print("GAS 조회 실패:", e)
        return []


# Selenium 설정
def init_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0")

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 15)

    return driver, wait


# 코드 적용 (언어 무관 안정 버전)
def apply_code(driver, wait, pid, name, code):
    for attempt in range(MAX_RETRY):
        try:
            driver.get(GIFT_URL)

            # Player ID 입력
            player_input = wait.until(
                EC.presence_of_element_located((By.XPATH, '(//input[@type="text"])[1]'))
            )
            player_input.clear()
            player_input.send_keys(pid)

            # Login 버튼
            driver.find_element(By.TAG_NAME, "button").click()

            # Gift Code 입력
            code_input = wait.until(
                EC.presence_of_element_located((By.XPATH, '(//input[@type="text"])[2]'))
            )
            code_input.clear()
            code_input.send_keys(code)

            # Confirm 버튼 (마지막 버튼)
            buttons = driver.find_elements(By.TAG_NAME, "button")
            buttons[-1].click()

            log(f"SUCCESS: {name} ({pid}) / {code}")
            return True

        except Exception as e:
            log(f"RETRY {attempt+1}/{MAX_RETRY}: {code} / {e}")
            random_delay(2, 4)

    log(f"FAIL: {name} ({pid}) / {code}")
    return False


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
