import requests

URL = "https://kingshot.net/api/gift-codes"

def get_active_codes():
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    res = requests.get(URL, headers=headers)
    data = res.json()

    return [
        item["code"]
        for item in data["data"]["giftCodes"]
        if item["expiresAt"] is None
    ]

def main():
    codes = get_active_codes()

    print("=== ACTIVE CODES ===")
    for code in codes:
        print(code)

if __name__ == "__main__":
    main()
