import time
import requests
import hmac
import hashlib
import base64
import os

# Load your Bitget API credentials
API_KEY = os.getenv("BITGET_API_KEY")
API_SECRET = os.getenv("BITGET_API_SECRET")
API_PASSPHRASE = os.getenv("BITGET_API_PASSPHRASE")
BASE_URL = "https://api.bitget.com"

SYMBOL = "SOLUSDT_UMCBL"  # USDT-margined Futures

HEADERS = {
    "Content-Type": "application/json",
    "ACCESS-KEY": API_KEY,
    "ACCESS-PASSPHRASE": API_PASSPHRASE,
}


def get_timestamp():
    return str(int(time.time() * 1000))


def sign(message):
    return base64.b64encode(
        hmac.new(API_SECRET.encode(), message.encode(), hashlib.sha256).digest()
    ).decode()


def auth_headers(method, path, body=""):
    timestamp = get_timestamp()
    message = f"{timestamp}{method}{path}{body}"
    signature = sign(message)
    headers = HEADERS.copy()
    headers.update({
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-SIGN": signature,
    })
    return headers


def cancel_all_orders():
    path = f"/api/mix/v1/order/cancel-all-orders"
    url = BASE_URL + path
    payload = {
        "symbol": SYMBOL,
        "marginCoin": "USDT"
    }
    headers = auth_headers("POST", path, json.dumps(payload))
    requests.post(url, headers=headers, json=payload)


def get_position():
    path = f"/api/mix/v1/position/single-position"
    url = BASE_URL + path + f"?symbol={SYMBOL}&marginCoin=USDT"
    headers = auth_headers("GET", path + f"?symbol={SYMBOL}&marginCoin=USDT")
    response = requests.get(url, headers=headers)
    data = response.json()
    pos = data.get("data", {})
    side = pos.get("holdSide", "")
    return side if pos else "NONE"


def place_order(side, size):
    path = "/api/mix/v1/order/place-order"
    url = BASE_URL + path
    payload = {
        "symbol": SYMBOL,
        "marginCoin": "USDT",
        "size": str(size),
        "price": "",  # market order
        "side": side,
        "orderType": "market",
        "tradeSide": "open",
        "positionSide": "long" if side == "buy" else "short",
        "force": True
    }
    headers = auth_headers("POST", path, json.dumps(payload))
    response = requests.post(url, headers=headers, json=payload)
    print(f"Order response: {response.text}")
    return response.json()


def close_position(current_side):
    side = "sell" if current_side == "long" else "buy"
    path = "/api/mix/v1/order/place-order"
    url = BASE_URL + path
    payload = {
        "symbol": SYMBOL,
        "marginCoin": "USDT",
        "size": "15",  # fixed size to close
        "price": "",
        "side": side,
        "orderType": "market",
        "tradeSide": "close",
        "positionSide": current_side,
        "force": True
    }
    headers = auth_headers("POST", path, json.dumps(payload))
    response = requests.post(url, headers=headers, json=payload)
    print(f"Close response: {response.text}")
    return response.json()


def process_trade(signal, size):
    current_pos = get_position()
    print(f"Current Position: {current_pos}")

    if signal == "BUY":
        if current_pos == "short":
            close_position("short")
        place_order("buy", size)

    elif signal == "SELL":
        if current_pos == "long":
            close_position("long")
        place_order("sell", size)
