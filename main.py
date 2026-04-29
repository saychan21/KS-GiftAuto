import os
import time
import json
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- 설정 구간 ---
GIFT_URL = "https://ks-giftcode.centurygame.com/"
# 구글 시트 CSV 내보내기 URL (A열 데이터만 가져오기 위해 활용)
CSV_URL = "https://docs.google.com/spreadsheets/d/1c2QmtlaBNsQ32j7JWly-ayigbkmfireBUisUEzxaJTY/export?format=csv&gid=561406276"

# 여러 명의 플레이어 ID를 여기에 추가하세요
PLAYERS = [
    "17770771",
    # "추가ID_1",
    # "추가ID_2",
]

USED_CODES_FILE = "used_codes.json"

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def get_gift_codes():
    try:
        res = requests.get(CSV_URL, timeout=10)
        lines = res.text.splitlines()
        # A1~A3 등 첫 번째 컬럼의 데이터만 추출 (공백 제외)
        codes = [line.split(',')[0].strip() for line in lines if line.strip()]
        log(f"시트에서 가져온 코드: {codes}")
        return codes
    except Exception as e:
        log(f"시트 데이터 가져오기 실패: {e}")
        return []

def init_driver():
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    driver = uc.Chrome(options=options, headless=False) # xvfb 위에서 동작
    return driver

def run_redeem():
    codes = get_gift_codes()
    if not codes: return

    driver = init_driver()
    wait = WebDriverWait(driver, 20)

    try:
        for pid in PLAYERS:
            log(f"--- 플레이어 ID: {pid} 작업 시작 ---")
            
            for code in codes:
                try:
                    driver.get(GIFT_URL)
                    time.sleep(3)

                    # 1. Player ID 입력 (placeholder 기준)
                    id_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='ID']")))
                    id_input.clear()
                    id_input.send_keys(pid)
                    
                    # 2. Login 버튼 클릭 (엔터 대신 클릭)
                    login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Login')]")))
                    login_btn.click()
                    
                    # 3. 로그인 후 코드 입력창 활성화 대기 (중요)
                    # 로그인 성공 시 'Enter Gift Code' placeholder가 있는 input이 클릭 가능해질 때까지 대기
                    code_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Enter Gift Code']")))
                    code_input.clear()
                    code_input.send_keys(code)
                    
                    # 4. Confirm 버튼 클릭
                    confirm_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Confirm')]")))
                    confirm_btn.click()
                    
                    log(f"ID {pid} / Code {code}: 시도 완료")
                    time.sleep(2) # 연타 방지 대기
                    
                except Exception as e:
                    log(f"ID {pid} / Code {code} 처리 중 에러: {str(e)[:50]}")
                    driver.save_screenshot(f"error_{pid}_{code}.png")
                    continue

    finally:
        driver.quit()
        log("모든 작업 종료")

if __name__ == "__main__":
    run_redeem()
