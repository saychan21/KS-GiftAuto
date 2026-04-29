import time
import json
import os
import random
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

GIFT_URL = "https://ks-giftcode.centurygame.com/"
CSV_URL = "https://docs.google.com/spreadsheets/d/1c2QmtlaBNsQ32j7JWly-ayigbkmfireBUisUEzxaJTY/export?format=csv"

PLAYERS = {
    "Ethereal": "17770771",
}

USED_CODES_FILE = "used_codes.json"
MAX_RETRY = 3

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def load_used_codes():
    if os.path.exists(USED_CODES_FILE):
        try:
            with open(USED_CODES_FILE, "r") as f:
                return set(json.load(f))
        except: return set()
    return set()

def save_used_codes(codes):
    with open(USED_CODES_FILE, "w") as f:
        json.dump(list(codes), f)

def get_active_codes():
    try:
        res = requests.get(CSV_URL, timeout=10)
        lines = res.text.splitlines()
        codes = [line.strip() for line in lines if line.strip()]
        log(f"가져온 코드 목록: {codes}")
        return list(set(codes))
    except:
        log("CSV 조회 실패")
        return []

def init_driver():
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    # GitHub Actions 환경 대응 (xvfb 사용 시 headless=False가 더 안정적)
    driver = uc.Chrome(options=options, headless=False)
    wait = WebDriverWait(driver, 20)
    return driver, wait

def apply_code(driver, wait, pid, name, code):
    for attempt in range(MAX_RETRY):
        try:
            driver.get(GIFT_URL)
            time.sleep(3)

            # 1. Player ID 입력
            id_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text'], .input-area input")))
            id_input.clear()
            id_input.send_keys(pid)
            
            # 2. Login 버튼 클릭 (정확한 텍스트 매칭)
            login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Login')]")))
            login_btn.click()
            log(f"[{name}] Login 클릭됨...")

            # 3. 중요: 로그인 처리 대기 및 기프트 코드 창 활성화 확인
            # 로그인 후 입력창의 placeholder가 'Enter Gift Code'로 바뀌거나 나타날 때까지 대기
            time.sleep(2) 
            code_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Enter Gift Code' or @placeholder='기프트 코드를 입력하세요']")))
            
            # 4. Gift Code 입력
            code_input.clear()
            code_input.send_keys(code)
            log(f"[{name}] Code 입력됨: {code}")

            # 5. Confirm 버튼 클릭
            confirm_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Confirm')]")))
            confirm_btn.click()
            
            # 결과 확인을 위한 짧은 대기
            time.sleep(3)
            driver.save_screenshot(f"result_{name}_{code}.png")
            
            log(f"SUCCESS: {name} / {code}")
            return True

        except Exception as e:
            driver.save_screenshot(f"error_{name}_{code}_{attempt}.png")
            log(f"RETRY {attempt+1}/{MAX_RETRY}: {name} / {code} (에러: {str(e)[:30]})")
            time.sleep(2)

    return False

def run():
    used_codes = load_used_codes()
    new_codes = get_active_codes()
    codes = [c for c in new_codes if c not in used_codes]

    if not codes:
        log("신규 코드 없음")
        return

    driver, wait = init_driver()

    try:
        for name, pid in PLAYERS.items():
            log(f"▶ {name} 작업 시작")
            for code in codes:
                if apply_code(driver, wait, pid, name, code):
                    used_codes.add(code)
                time.sleep(2)
    finally:
        driver.quit()
        save_used_codes(used_codes)
        log("모든 프로세스 종료")

if __name__ == "__main__":
    run()
