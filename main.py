import os
import time
import json
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ... (상단 설정 및 함수들은 이전과 동일) ...

def init_driver():
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    
    # GitHub Actions 환경에서 브라우저 창 크기가 작으면 요소가 안 보일 수 있음
    options.add_argument("--window-size=1920,1080")

    try:
        # 버전 갈등을 피하기 위해 browser_executable_path를 명시적으로 줄 수 있습니다.
        # 보통 Ubuntu Actions 환경의 경로는 /usr/bin/google-chrome 입니다.
        driver = uc.Chrome(
            options=options,
            headless=False,  # xvfb를 사용하므로 False 유지
            use_subprocess=True
        )
        wait = WebDriverWait(driver, 25)
        return driver, wait
    except Exception as e:
        print(f"Driver Init Error: {e}")
        # 예외 발생 시 드라이버 없이 종료되지 않도록 처리
        raise e

def apply_code(driver, wait, pid, name, code):
    try:
        driver.get(GIFT_URL)
        log(f"페이지 접속 완료: {name}")
        
        # 1. Player ID 입력 (스크린샷 기준 placeholder 타겟팅)
        # 해당 사이트는 렌더링 시간이 걸리므로 넉넉히 대기
        time.sleep(5)
        
        id_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']")))
        id_input.clear()
        id_input.send_keys(pid)
        
        # 2. Login 버튼 클릭
        login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Login')]")))
        login_btn.click()
        log("Login 버튼 클릭함")

        # 3. Gift Code 입력창 활성화 대기 (로그인 후 나타남)
        # 'Enter Gift Code' 텍스트가 포함된 input이 나타날 때까지 대기
        time.sleep(3)
        code_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Enter Gift Code']")))
        code_input.clear()
        code_input.send_keys(code)
        
        # 4. Confirm 버튼 클릭
        confirm_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Confirm')]")))
        confirm_btn.click()
        
        log(f"성공 리포트: {name} / {code}")
        time.sleep(2)
        return True
    except Exception as e:
        log(f"실패 리포트: {name} / {code} -> {str(e)}")
        driver.save_screenshot(f"fail_{name}_{code}.png")
        return False

# ... (이하 run 함수 등은 이전과 동일) ...
