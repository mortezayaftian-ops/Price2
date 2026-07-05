import requests
import json
import os
import re

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = "-1004297055826"
PRICE_FILE = "last_price.json"

def get_dollar_price():
    """قیمت دلار بازار آزاد را از TGJU استخراج می‌کند."""
    url = "https://www.tgju.org/profile/price_dollar_rl"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    html = resp.text

    match = re.search(r'data-last="(\d+)"', html)
    if not match:
        raise ValueError("قیمت در صفحه پیدا نشد؛ ساختار سایت تغییر کرده است.")
    return int(match.group(1))

def load_last_price():
    if os.path.exists(PRICE_FILE):
        with open(PRICE_FILE, "r") as f:
            return json.load(f).get("price")
    return None

def save_price(price):
    with open(PRICE_FILE, "w") as f:
        json.dump({"price": price}, f)

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    r = requests.post(url, data=payload, timeout=15)
    r.raise_for_status()

def main():
    price = get_dollar_price()
    last_price = load_last_price()

    if price == last_price:
        print("قیمت تغییر نکرده، پیامی ارسال نشد.")
        return

    price_toman = price // 10
    text = f"قیمت دلار بازار آزاد: {price_toman:,} تومان"
    send_message(text)
    save_price(price)
    print("پیام ارسال شد.")

if __name__ == "__main__":
    main()
