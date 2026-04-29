import time
import yaml
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.common.by import By

# -----------------------------
# 1. YAML 설정 불러오기
# -----------------------------
with open("config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

sheet_url = config["google_sheets"]["url"]
cred_file = config["google_sheets"]["credentials"]
player_ids = config["player_ids"]
selectors = config["selectors"]
selenium_conf = config["selenium"]

# -----------------------------
# 2. Google Sheets 연결
# -----------------------------
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name(cred_file, scope)
client = gspread.authorize(creds)

worksheet = client.open_by_url(sheet_url).get_worksheet(0)
gift_codes = worksheet.col_values(1)  # A열 전체 읽기

# -----------------------------
# 3. Selenium 브라우저 실행
# -----------------------------
driver = webdriver.Chrome()
driver.get(selenium_conf["url"])

# -----------------------------
# 4. 자동화 루프
# -----------------------------
for pid in player_ids:
    # Player ID 입력
    player_id_box = driver.find_element(By.XPATH, selectors["player_id_input"])
    player_id_box.clear()
    player_id_box.send_keys(pid)

    login_button = driver.find_element(By.XPATH, selectors["login_button"])
    login_button.click()
    time.sleep(selenium_conf["wait_time"])

    # Gift Code 입력 반복
    for code in gift_codes:
        gift_code_box = driver.find_element(By.XPATH, selectors["gift_code_input"])
        gift_code_box.clear()
        gift_code_box.send_keys(code)

        confirm_button = driver.find_element(By.XPATH, selectors["confirm_button"])
        confirm_button.click()
        time.sleep(selenium_conf["wait_time"])

print("✅ 모든 Player ID와 Gift Code 자동 입력 완료")
driver.quit()
