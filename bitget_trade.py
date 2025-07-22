import requests
import time
import hmac
import hashlib
import base64
import json
import os

# === Load from environment or hardcoded ===
API_KEY = os.getenv("BITGET_API_KEY", "your_api_key_here")
API_SECRET = os.getenv("BITGET_API_SECRET", "your_api_secret_here")
API_PASSPHRASE = os.getenv("BITGET_API_PASSPHRASE", "your_passphrase_here")
BASE_URL = "https://api.bitget.com"

HEADERS = {
    "ACCESS-KEY": API_KEY,
    "ACCESS-PASSPHRASE": API_PASSPHRASE,
    "Content-Type": "application/json"
}


def get_server_time():
    response = requests.get(BASE_URL + "/api/v2/public/time")
    return str(response.json()['data'])


def sign_request(timestamp, method, request_path, body=""):
    message = f"{timestamp}{method}{request_path}{body}"
    mac = hmac.new(bytes(API_SECRET, encoding='utf8'),
                   bytes(message, encoding='utf8'),
                   digestmod=hashlib.sha256)
    d = mac.digest()
    return base64.b64encode(d).decode()


def place_order(symbol, side, size, leverage):
    timestamp = get_server_time()
    path = "/api/v2/mix/order/place"
    url = BASE_URL + path

    body = {
        "symbol": symbol,
        "marginCoin": "USDT",
        "orderType": "market",
        "side": side,
        "size": str(size),
        "leverage": str(leverage),
        "presetTakeProfitPrice": None,
        "presetStopLossPrice": None,
        "tradeSide": "open",
        "productType": "umcbl"
    }

    body_json = json.dumps(body)
    sign = sign_request(timestamp, "POST", path, body_json)

    headers = HEADERS.copy()
    headers["ACCESS-TIMESTAMP"] = timestamp
    headers["ACCESS-SIGN"] = sign

    response = requests.post(url, headers=headers, data=body_json)
    print(f"Place order response: {response.text}")
    return response.json()


def close_position(symbol, side):
    timestamp = get_server_time()
    path = "/api/v2/mix/order/close-position"
    url = BASE_URL + path

    body = {
        "symbol": symbol,
        "marginCoin": "USDT",
        "side": side,
        "productType": "umcbl"
    }

    body_json = json.dumps(body)
    sign = sign_request(timestamp, "POST", path, body_json)

    headers = HEADERS.copy()
    headers["ACCESS-TIMESTAMP"] = timestamp
    headers["ACCESS-SIGN"] = sign

    response = requests.post(url, headers=headers, data=body_json)
    print(f"Close position response: {response.text}")
    return response.json()


def smart_trade(action, symbol, quantity, leverage=50):
    # Determine sides
    if action.lower() == "buy":
        close_position(symbol, "short")
        time.sleep(0.5)
        place_order(symbol, "open_long", quantity, leverage)
    elif action.lower() == "sell":
        close_position(symbol, "long")
        time.sleep(0.5)
        place_order(symbol, "open_short", quantity, leverage)
    else:
        print("Invalid action. Must be 'buy' or 'sell'")
