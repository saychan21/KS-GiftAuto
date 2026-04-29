import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.common.by import By

# -----------------------------
# 1. Google Sheets 연결
# -----------------------------
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

# service_account.json 파일 필요 (Google Cloud에서 발급)
creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(creds)

# 시트 열기
sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1c2QmtlaBNsQ32j7JWly-ayigbkmfireBUisUEzxaJTY/edit#gid=561406276")
worksheet = sheet.get_worksheet(0)

# Gift Code 리스트 가져오기 (A열)
gift_codes = worksheet.col_values(1)

# -----------------------------
# 2. Player ID 리스트 (여러 개)
# -----------------------------
player_ids = ["123456789", "987654321", "555555555"]

# -----------------------------
# 3. Selenium 브라우저 실행
# -----------------------------
driver = webdriver.Chrome()
driver.get("https://ks-giftcode.centurygame.com")

# -----------------------------
# 4. 자동화 루프
# -----------------------------
for pid in player_ids:
    # Player ID 입력
    player_id_box = driver.find_element(By.XPATH, '//*[@id="playerIdInput"]')
    player_id_box.clear()
    player_id_box.send_keys(pid)

    login_button = driver.find_element(By.XPATH, '//*[@id="loginButton"]')
    login_button.click()
    time.sleep(2)

    # Gift Code 입력 반복
    for code in gift_codes:
        gift_code_box = driver.find_element(By.XPATH, '//*[@id="giftCodeInput"]')
        gift_code_box.clear()
        gift_code_box.send_keys(code)

        confirm_button = driver.find_element(By.XPATH, '//*[@id="confirmButton"]')
        confirm_button.click()
        time.sleep(2)

print("✅ 모든 Player ID와 Gift Code 자동 입력 완료")
driver.quit()
