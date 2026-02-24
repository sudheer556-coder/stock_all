import requests
import yfinance as yf
from datetime import datetime, time as dtime
import pytz
import os
import json

# ==========================
# CONFIGURATION
# ==========================

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1473479738302533703/Ln7OhZinKMIwX4X0lzaDKTHHhk9HIwcxdmNQbJjBHUylptiKdcGGG0a7z5I_jPIJeOGF"

STOCKS = {
    "MU": 12,
    "BE": 10,
    "APP": 20,
    "FIG": 2,
    "RDDT": 12,
    "HOOD": 4,
    "OKLO": 4,
    "MU": 20
}

ET = pytz.timezone("US/Eastern")

PREMARKET_START = dtime(4, 0)
MARKET_CLOSE = dtime(16, 0)

ALERT_FILE = "alerts.json"

# ==========================
# HELPERS
# ==========================

def is_market_hours():
    now = datetime.now(ET)
    weekday = now.weekday()
    current_time = now.time()

    if weekday >= 5:
        return False

    return PREMARKET_START <= current_time <= MARKET_CLOSE


def send_discord(message):
    requests.post(DISCORD_WEBHOOK, json={"content": message})


def load_alerts():
    if os.path.exists(ALERT_FILE):
        with open(ALERT_FILE, "r") as f:
            return json.load(f)
    return {}


def save_alerts(data):
    with open(ALERT_FILE, "w") as f:
        json.dump(data, f)


def check_stocks():
    today = str(datetime.now(ET).date())
    alerts = load_alerts()

    for symbol, threshold in STOCKS.items():
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d", interval="1m", prepost=True)

            if data.empty:
                continue

            today_high = data["High"].max()
            current_price = data["Close"].iloc[-1]

            drop = round(today_high - current_price, 2)

            print(symbol, "High:", today_high, "Current:", current_price, "Drop:", drop)

            if drop >= threshold:
                if alerts.get(symbol) == today:
                    continue  # already alerted today

                message = (
                    f"🚨 STOCK DROP ALERT\n\n"
                    f"{symbol}\n"
                    f"Today's High: ${round(today_high,2)}\n"
                    f"Current Price: ${round(current_price,2)}\n"
                    f"Drop: ${drop}"
                )

                send_discord(message)
                alerts[symbol] = today

        except Exception as e:
            print("Error:", symbol, e)

    save_alerts(alerts)


if __name__ == "__main__":
    check_stocks()





