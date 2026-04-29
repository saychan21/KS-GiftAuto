import time
import json
import os
import random
import requests

import undetected_chromedriver as uc

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

GIFT_URL = "https://ks-giftcode.centurygame.com/"
CSV_URL = "https://docs.google.com/spreadsheets/d/1c2QmtlaBNsQ32j7JWly-ayigbkmfireBUisUEzxaJTY/export?format=csv"

PLAYERS = {
    "Ethereal": "17770771",
}

USED_CODES_FILE = "used_codes.json"
MAX_RETRY = 3


def log(msg):
    print(msg, flush=True)


def random_delay(a=1.5, b=3.0):
    time.sleep(random.uniform(a, b))


def load_used_codes():
    if os.path.exists(USED_CODES_FILE):
        with open(USED_CODES_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_used_codes(codes):
    with open(USED_CODES_FILE, "w") as f:
        json.dump(list(codes), f)


def get_active_codes():
    try:
        res = requests.get(CSV_URL, timeout=10)
        lines = res.text.splitlines()
        codes = [line.strip() for line in lines if line.strip()]
        log(f"코드: {codes}")
        return list(set(codes))
    except:
        log("CSV 조회 실패")
        return []


def init_driver():
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = uc.Chrome(
        options=options,
        headless=False,   # 🔥 여기만 수정됨
        version_main=147
    )

    wait = WebDriverWait(driver, 20)
    return driver, wait


def apply_code(driver, wait, pid, name, code):
    for attempt in range(MAX_RETRY):
        try:
            driver.get(GIFT_URL)
            time.sleep(3)

            # 🔥 STEP0: 무조건 스크린샷
            driver.save_screenshot(f"step0_{name}_{code}.png")

            # Player ID 입력
            player_input = wait.until(
                EC.presence_of_element_located((By.XPATH, '//input'))
            )
            player_input.clear()
            player_input.send_keys(pid)

            random_delay()

            # 🔥 Login 버튼 정확하게 찾기
            login_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"Login")]'))
            )

            ActionChains(driver).move_to_element(login_btn).click().perform()

            # 로그인 후 Gift input 등장 대기
            code_input = wait.until(
                EC.presence_of_element_located((By.XPATH, '(//input)[2]'))
            )

            random_delay()

            # Gift Code 입력
            code_input.clear()
            code_input.send_keys(code)

            # 🔥 Confirm 버튼 정확하게
            confirm_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"Confirm")]'))
            )

            ActionChains(driver).move_to_element(confirm_btn).click().perform()

            log(f"SUCCESS: {name} / {code}")
            return True

        except:
            # 🔥 에러 스크린샷
            driver.save_screenshot(f"error_{name}_{code}_{attempt}.png")

            log(f"RETRY {attempt+1}/{MAX_RETRY}: {name} / {code}")
            time.sleep(2)

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
        log(f"▶ {name}")

        for code in codes:
            success = apply_code(driver, wait, pid, name, code)

            if success:
                used_codes.add(code)

            random_delay()

    driver.quit()
    save_used_codes(used_codes)

    log("DONE")


if __name__ == "__main__":
    run()
