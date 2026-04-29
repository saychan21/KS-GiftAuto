import time
import json
import os
import random
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

GIFT_URL = "https://ks-giftcode.centurygame.com/"

CSV_URL = "https://docs.google.com/spreadsheets/d/1c2QmtlaBNsQ32j7JWly-ayigbkmfireBUisUEzxaJTY/export?format=csv"

PLAYERS = {
    "Ethereal": "17770771",
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


# CSV 코드 가져오기
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
def init_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0")
    options.binary_location = "/usr/bin/google-chrome"

    service = Service()
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 20)

    return driver, wait


# 🔥 로그인 (완전 안정 버전)
def login(driver, wait, pid, name):
    driver.get(GIFT_URL)
    time.sleep(5)  # 🔥 중요 (렌더링 대기)

    driver.save_screenshot(f"login_page_{name}.png")

    # 🔥 input 2개 확보
    inputs = wait.until(lambda d: d.find_elements(By.TAG_NAME, "input"))

    if len(inputs) < 1:
        raise Exception("input 없음")

    inputs[0].clear()
    inputs[0].send_keys(pid)

    driver.save_screenshot(f"login_input_{name}.png")

    # 🔥 button 확보
    buttons = wait.until(lambda d: d.find_elements(By.TAG_NAME, "button"))

    if len(buttons) < 1:
        raise Exception("button 없음")

    buttons[0].click()

    time.sleep(3)

    driver.save_screenshot(f"login_done_{name}.png")


# 🔥 코드 적용 (완전 안정 버전)
def apply_code(driver, wait, name, code):
    for attempt in range(MAX_RETRY):
        try:
            time.sleep(2)

            inputs = wait.until(lambda d: d.find_elements(By.TAG_NAME, "input"))

            if len(inputs) < 2:
                raise Exception("gift input 없음")

            inputs[1].clear()
            inputs[1].send_keys(code)

            driver.save_screenshot(f"code_input_{name}_{code}.png")

            buttons = wait.until(lambda d: d.find_elements(By.TAG_NAME, "button"))

            if len(buttons) < 2:
                raise Exception("confirm 버튼 없음")

            buttons[-1].click()

            time.sleep(2)

            driver.save_screenshot(f"code_confirm_{name}_{code}.png")

            log(f"SUCCESS: {name} / {code}")
            return True

        except Exception as e:
            print("ERROR:", e)
            driver.save_screenshot(f"error_{name}_{code}_{attempt}.png")
            random_delay(2, 4)

    log(f"FAIL: {name} / {code}")
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

        login(driver, wait, pid, name)

        for code in codes:
            success = apply_code(driver, wait, name, code)

            if success:
                used_codes.add(code)

            random_delay()

    driver.quit()
    save_used_codes(used_codes)

    log("=== DONE ===")


if __name__ == "__main__":
    run()
