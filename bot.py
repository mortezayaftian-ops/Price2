import os
import json
from telegram import Bot

TOKEN = os.environ.get("TOKEN")
CHANNEL_ID = -1004297055826

bot = Bot(TOKEN)

# 🔥 حالت تست
TEST = True

DATA_FILE = "data.json"

# ---------- load/save ----------
def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {
            "today": None,
            "yesterday": None,
            "week": [],
            "last_week_avg": None
        }

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# ---------- قیمت (تست یا واقعی) ----------
def get_price():
    if TEST:
        return 657000  # 👈 قیمت تستی
    else:
        import requests
        url = "https://api.exchangerate.host/latest?base=USD&symbols=IRR"
        r = requests.get(url, timeout=10)
        data = r.json()
        return int(data["rates"]["IRR"] / 10)

# ---------- main ----------
def main():
    data = load_data()

    price = get_price()

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
        diff_day = price - yesterday
        if diff_day > 0:
            diff_day = f"🟢 +{diff_day:,}"
        elif diff_day < 0:
            diff_day = f"🔴 {diff_day:,}"
        else:
            diff_day = "⚪ بدون تغییر"
    else:
        diff_day = "—"

    # تغییر هفته
    last_week_avg = data.get("last_week_avg")

    if last_week_avg:
        diff_week = week_avg - last_week_avg
        if diff_week > 0:
            diff_week = f"🟢 +{diff_week:,}"
        elif diff_week < 0:
            diff_week = f"🔴 {diff_week:,}"
        else:
            diff_week = "⚪ بدون تغییر"
    else:
        diff_week = "—"

    # ذخیره میانگین هفته
    if len(data["week"]) == 7:
        data["last_week_avg"] = week_avg
        data["week"] = []

    save_data(data)

    text = f"""
💵 گزارش تست دلار

📅 امروز: {price:,}
📊 دیروز: {yesterday if yesterday else '—'}
📉 تغییر روزانه: {diff_day}

━━━━━━━━━━
📈 میانگین هفته: {week_avg:,}
📊 تغییر هفته: {diff_week}

#TEST_MODE
"""

    bot.send_message(chat_id=CHANNEL_ID, text=text)

if __name__ == "__main__":
    main()
