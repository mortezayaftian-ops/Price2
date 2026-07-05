import requests
import json
import os

BOT_TOKEN = os.environ["BOT_TOKEN"]
BRSAPI_KEY = os.environ["BRSAPI_KEY"]
CHAT_ID = "-1004297055826"
PRICE_FILE = "last_price.json"


def find_usd_price(data):
    """به‌صورت بازگشتی در ساختار JSON دنبال آیتم دلار آمریکا می‌گردد."""
    if isinstance(data, dict):
        symbol = str(data.get("symbol", "")).upper()
        name = str(data.get("name", "")) + str(data.get("name_en", ""))
        if symbol == "USD" or ("دلار" in name and "آمریک" in name):
            price = data.get("price")
            if price is not None:
                return price
        for value in data.values():
            result = find_usd_price(value)
            if result is not None:
                return result
    elif isinstance(data, list):
        for item in data:
            result = find_usd_price(item)
            if result is not None:
                return result
    return None


def get_dollar_price():
    """قیمت دلار بازار آزاد را از BrsApi می‌گیرد."""
    url = f"https://Api.BrsApi.ir/Market/Gold_Currency.php?key={BRSAPI_KEY}"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    price = find_usd_price(data)
    if price is None:
        print("قیمت دلار در پاسخ پیدا نشد. خروجی کامل API:")
        print(json.dumps(data, ensure_ascii=False, indent=2))
        raise ValueError("قیمت دلار در پاسخ API پیدا نشد.")

    return float(str(price).replace(",", ""))


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

    text = f"قیمت دلار بازار آزاد: {price:,.0f} تومان"
    send_message(text)
    save_price(price)
    print("پیام ارسال شد.")


if __name__ == "__main__":
    main()
