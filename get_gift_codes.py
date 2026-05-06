import requests

URL = "https://kingshot.net/api/gift-codes"

def get_active_codes():
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    res = requests.get(URL, headers=headers)

    print("STATUS:", res.status_code)
    print("TEXT:", res.text[:200])  # 🔥 중요

    try:
        data = res.json()
    except:
        print("❌ JSON 파싱 실패")
        return []

    return [
        item["code"]
        for item in data["data"]["giftCodes"]
        if item["expiresAt"] is None
    ]

def main():
    codes = get_active_codes()

    print("=== RESULT ===")
    print(codes)

if __name__ == "__main__":
    main()
