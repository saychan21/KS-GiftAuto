import cloudscraper

URL = "https://kingshot.net/api/gift-codes"

def get_active_codes():
    scraper = cloudscraper.create_scraper()

    res = scraper.get(URL)

    print("STATUS:", res.status_code)
    print("TEXT:", res.text[:200])  # 🔥 핵심

    try:
        data = res.json()
    except:
        print("❌ JSON 실패")
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
