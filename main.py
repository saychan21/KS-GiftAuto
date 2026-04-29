import os
import time
import requests
import subprocess
import re
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- [수정 포인트] 플레이어 ID를 리스트 형식으로 넣으세요 ---
PLAYERS = [
    "17770771",
    # "12345678", 여기에 추가 ID를 계속 넣을 수 있습니다.
]

GIFT_URL = "https://ks-giftcode.centurygame.com/"
CSV_URL = "https://docs.google.com/spreadsheets/d/1c2QmtlaBNsQ32j7JWly-ayigbkmfireBUisUEzxaJTY/export?format=csv&gid=561406276"

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def get_chrome_version():
    """시스템에 설치된 크롬 버전을 확인하여 메인 버전 숫자를 반환합니다."""
    try:
        output = subprocess.check_output(['google-chrome', '--version']).decode('utf-8')
        version = re.search(r'Google Chrome (\[0-9\]+)', output).group(1)
        return int(version)
    except:
        return None

def get_gift_codes():
    try:
        res = requests.get(CSV_URL, timeout=10)
        lines = res.text.splitlines()
        # A열 데이터 추출
        codes = [line.split(',')[0].strip() for line in lines if line.strip()]
        log(f"시트에서 가져온 코드: {codes}")
        return codes
    except Exception as e:
        log(f"시트 조회 실패: {e}")
        return []

def init_driver():
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    # 실행 환경의 크롬 버전을 자동으로 파악
    current_version = get_chrome_version()
    log(f"탐지된 크롬 버전: {current_version}")

    # 버전이 확인되면 해당 버전에 맞춰 실행, 실패 시 기본값으로 실행
    try:
        return uc.Chrome(options=options, headless=False, version_main=current_version)
    except:
        return uc.Chrome(options=options, headless=False)

def run():
    codes = get_gift_codes()
    if not codes: return

    driver = init_driver()
    wait = WebDriverWait(driver, 25)

    try:
        for pid in PLAYERS:
            log(f">>> 플레이어 [{pid}] 작업 시작")
            for code in codes:
                try:
                    driver.get(GIFT_URL)
                    time.sleep(4)

                    # 1. Player ID 입력
                    id_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='ID']")))
                    id_input.clear()
                    id_input.send_keys(pid)
                    
                    # 2. Login 클릭
                    login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Login')]")))
                    login_btn.click()
                    log(f"[{pid}] 로그인 클릭...")

                    # 3. Gift Code 입력창 활성화 대기 (로그인 응답 대기)
                    code_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Enter Gift Code']")))
                    code_input.clear()
                    code_input.send_keys(code)
                    
                    # 4. Confirm 클릭
                    confirm_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Confirm')]")))
                    confirm_btn.click()
                    
                    log(f"[{pid}] 코드 {code} 입력 완료")
                    time.sleep(2)
                    
                except Exception as e:
                    log(f"오류 발생 ({pid}/{code}): {str(e)[:50]}")
                    driver.save_screenshot(f"error_{pid}_{code}.png")
                    continue
    finally:
        driver.quit()
        log("모든 작업 종료")

if __name__ == "__main__":
    run()
