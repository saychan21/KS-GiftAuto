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

# 🔥 CSV URL 사용 (이걸로 변경)
CSV_URL = "https://docs.google.com/spreadsheets/d/1c2QmtlaBNsQ32j7JWly-ayigbkmfireBUisUEzxaJTY/export?format=csv"

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


# 🔥 CSV에서 코드 가져오기 (핵심 변경)
def get_active_codes():
    try:
        res = requests.get(CSV_URL, timeout=10)

        print("STATUS:", res.status_code)
        print("TEXT:", res.text[:200])

        lines = res.text.splitlines()
        codes = [line.strip() for line in lines if line.strip()]

        print("CSV 코드:", codes)

        return list(set(codes))

    except Exception as e:
        print("CSV 조회 실패:", e)
        return []


# Selenium 설정
from selenium.webdriver.chrome.service import Service

def init_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0")

    # 🔥 GitHub에서 Chrome 위치 지정
    options.binary_location = "/usr/bin/google-chrome"

    service = Service()

    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 15)

    return driver, wait


# 코드 적용
def apply_code(driver, wait, pid, name, code):
    for attempt in range(MAX_RETRY):
        try:
            driver.get(GIFT_URL)

            player_input = wait.until(
                EC.presence_of_element_located((By.XPATH, '(//input[@type="text"])[1]'))
            )
            player_input.clear()
            player_input.send_keys(pid)

            driver.find_element(By.TAG_NAME, "button").click()

            code_input = wait.until(
                EC.presence_of_element_located((By.XPATH, '(//input[@type="text"])[2]'))
            )
            code_input.clear()
            code_input.send_keys(code)

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
