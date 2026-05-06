import requests

URL = "https://kingshot.net/api/gift-codes"

def get_active_codes():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json"
    }

    res = requests.get(URL, headers=headers)

    print("STATUS:", res.status_code)
    print("TEXT:", res.text[:200])  # 🔥 핵심

    try:
        data = res.json()
    except:
        print("❌ JSON 아님 → Cloudflare 차단됨")
        return []

    return [
        item["code"]
        for item in data["data"]["giftCodes"]
        if item["expiresAt"] is None
    ]
