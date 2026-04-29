import time
import yaml
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

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
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    cred_file, scope
)
client = gspread.authorize(creds)

worksheet = client.open_by_url(sheet_url).get_worksheet(0)

# Gift Code 정제
gift_codes = [
    code.strip()
    for code in worksheet.col_values(1)
    if code.strip() and code.lower() != "gift_code"
]

print(f"✅ Gift Code {len(gift_codes)}개 로드 완료")

# -----------------------------
# 3. Headless Selenium 브라우저 실행 ✅
# -----------------------------
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 10)

driver.get(selenium_conf["url"])

# -----------------------------
# 4. 자동화 루프
# -----------------------------
for pid in player_ids:
    print(f"\n▶ Player ID 처리 시작: {pid}")

    # Player ID 입력
    player_id_box = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, selectors["player_id_input"])
        )
    )
    player_id_box.clear()
    player_id_box.send_keys(pid)

    login_button = driver.find_element(
        By.XPATH, selectors["login_button"]
    )
    login_button.click()

    time.sleep(selenium_conf["wait_time"])

    # Gift Code 입력 반복
    for code in gift_codes:
        try:
            gift_code_box = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, selectors["gift_code_input"])
                )
            )
            gift_code_box.clear()
            gift_code_box.send_keys(code)

            confirm_button = driver.find_element(
                By.XPATH, selectors["confirm_button"]
            )
            confirm_button.click()

            print(f"✅ 성공 시도: {code}")
            time.sleep(selenium_conf["wait_time"])

        except Exception as e:
            print(f"❌ 실패: {code} / 이유: {e}")
            continue

print("\n✅ 모든 Player ID와 Gift Code 자동 입력 완료")
driver.quit()
