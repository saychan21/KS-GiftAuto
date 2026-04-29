import time
import yaml
import csv
import requests
from io import StringIO

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# 1. Load config
with open("config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

csv_url = config["google_sheets"]["csv_url"]
player_ids = config["player_ids"]
selectors = config["selectors"]
selenium_conf = config["selenium"]

# 2. Load Gift Codes from public Google Sheets (CSV)
response = requests.get(csv_url, timeout=30)
response.raise_for_status()

csv_data = csv.reader(StringIO(response.text))
gift_codes = [
    row[0].strip()
    for row in csv_data
    if row and row[0].strip().lower() != "gift_code"
]

print(f"✅ Gift Code {len(gift_codes)}개 로드 완료")

# 3. Chrome setup (Headless + UA)
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 30)

driver.get(selenium_conf["url"])
wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
time.sleep(5)

# 4. Automation
for pid in player_ids:
    print(f"▶ Player ID: {pid}")

    player_id_box = wait.until(
        EC.element_to_be_clickable((By.XPATH, selectors["player_id_input"]))
    )
    player_id_box.clear()
    player_id_box.send_keys(pid)

    login_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, selectors["login_button"]))
    )
    login_button.click()

    # wait for iframe after login
