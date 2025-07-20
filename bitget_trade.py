import os
import requests
import time
import hmac
import hashlib
import json
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BITGET_API_KEY")
API_SECRET = os.getenv("BITGET_API_SECRET")
API_PASSPHRASE = os.getenv("BITGET_API_PASSPHRASE")

BASE_URL = "https://api.bitget.com"
SYMBOL = "SOLUSDT_UMCBL"
MARGIN_COIN = "USDT"
SIZE = "15"
LEVERAGE = 50

HEADERS = {
    "Content-Type": "application/json",
    "ACCESS-KEY": API_KEY,
    "ACCESS-PASSPHRASE": API_PASSPHRASE,
}

def get_server_time():
    response = requests.get(f"{BASE_URL}/api/mix/v1/market/time")
    return str(response.json()["data"])

def sign_request(timestamp, method, request_path, body=""):
    message = f"{timestamp}{method.upper()}{request_path}{body}"
    signature = hmac.new(API_SECRET.encode(), message.encode(), hashlib.sha256).hexdigest()
    return signature

def send_signed_request(method, endpoint, body=None):
    timestamp = get_server_time()
    body_str = json.dumps(body) if body else ""
    signature = sign_request(timestamp, method, endpoint, body_str)

    headers = HEADERS.copy()
    headers["ACCESS-TIMESTAMP"] = timestamp
    headers["ACCESS-SIGN"] = signature

    url = BASE_URL + endpoint
    if method.upper() == "POST":
        response = requests.post(url, headers=headers, data=body_str)
    else:
        response = requests.get(url, headers=headers, params=body)

    return response.json()

def get_positions():
    endpoint = f"/api/mix/v1/position/singlePosition"
    params = {
        "symbol": SYMBOL,
        "marginCoin": MARGIN_COIN
    }
    return send_signed_request("GET", endpoint, params)

def close_position(side):
    endpoint = "/api/mix/v1/order/close-position"
    body = {
        "symbol": SYMBOL,
        "marginCoin": MARGIN_COIN,
        "positionSide": "long" if side == "BUY" else "short"
    }
    return send_signed_request("POST", endpoint, body)

def place_order(side):
    # First close the opposite position
    print(f"🔁 Closing opposite position before placing {side} order...")
    if side == "BUY":
        close_position("SELL")
    else:
        close_position("BUY")

    endpoint = "/api/mix/v1/order/place-order"
    body = {
        "symbol": SYMBOL,
        "marginCoin": MARGIN_COIN,
        "size": SIZE,
        "price": "",  # Market order
        "side": "open_long" if side == "BUY" else "open_short",
        "orderType": "market"
    }
    return send_signed_request("POST", endpoint, body)

def handle_trade(message):
    print(f"📩 Received alert message: {message}")

    if message == "UMLCB:BUY":
        print("📈 Executing Long Entry...")
        result = place_order("BUY")
        print(result)
    elif message == "UMLCB:SELL":
        print("📉 Executing Short Entry...")
        result = place_order("SELL")
        print(result)
    elif message == "UMLCB:CLOSE_LONG":
        print("❌ Closing Long Position...")
        result = close_position("BUY")
        print(result)
    elif message == "UMLCB:CLOSE_SHORT":
        print("❌ Closing Short Position...")
        result = close_position("SELL")
        print(result)
    else:
        print("⚠️ Unknown alert message:", message)
