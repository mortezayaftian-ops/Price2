import os
import json
import requests
from telegram import Bot

TOKEN = os.environ.get("TOKEN")
CHANNEL_ID = -1004297055826

bot = Bot(TOKEN)

FILE = "data.json"


# ---------- load / save ----------
def load_data():
    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except:
        return {
            "today": None,
            "yesterday": None,
            "week": []
        }


def save_data(data):
    with open(FILE, "w") as f:
        json.dump(data, f)


# ---------- قیمت دلار مبادله (با بکاپ) ----------
def get_dollar_price():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    # 🔥 منبع 1: TGJU
    try:
        url = "https://api.tgju.org/v1/data/sana.json"
        r = requests.get(url, headers=headers, timeout=10)

        if r.status_code == 200:
            data = r.json()
            price = data["sana"]["usd"]["price"]
            return int(price) // 10
    except:
        pass

    # 🔥 منبع 2: بکاپ
    try:
        url2 = "https://api.exchangerate.host/latest?base=USD&symbols=IRR"
        r2 = requests.get(url2, timeout=10)
        data2 = r2.json()
        return int(data2["rates"]["IRR"]) // 10
    except:
        return None


# ---------- main ----------
def main():
    data = load_data()

    price = get_dollar_price()

    if price is None:
        return

    # دیروز
    yesterday = data["today"]

    # امروز
    data["yesterday"] = yesterday
    data["today"] = price

    # هفته
    data["week"].append(price)
    data["week"] = data["week"][-7:]

    week_avg = sum(data["week"]) // len(data["week"])

    # تغییر روزانه
    if yesterday:
        diff = price - yesterday
        if diff > 0:
            diff_day = f"🟢 +{diff:,}"
        elif diff < 0:
            diff_day = f"🔴 {diff:,}"
        else:
            diff_day = "⚪ بدون تغییر"
    else:
        diff_day = "—"

    # پیام نهایی
    text = f"""
💵 گزارش دلار مبادله

━━━━━━━━━━━━━━
📅 قیمت امروز: {price:,} تومان
📊 تغییر نسبت به دیروز: {diff_day}

━━━━━━━━━━━━━━
📈 میانگین ۷ روزه: {week_avg:,} تومان

━━━━━━━━━━━━━━
#DOLLAR_REPORT
"""

    bot.send_message(chat_id=CHANNEL_ID, text=text)

    save_data(data)


if __name__ == "__main__":
    main()
