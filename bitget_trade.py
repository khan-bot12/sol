import os
import time
import hmac
import base64
import hashlib
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BITGET_API_KEY")
API_SECRET = os.getenv("BITGET_API_SECRET")
API_PASSPHRASE = os.getenv("BITGET_API_PASSPHRASE")
BASE_URL = "https://api.bitget.com"

HEADERS = {
    "Content-Type": "application/json",
    "ACCESS-KEY": API_KEY,
    "ACCESS-PASSPHRASE": API_PASSPHRASE,
}

def get_timestamp():
    return str(int(time.time() * 1000))

def sign_request(timestamp, method, request_path, body=''):
    message = f"{timestamp}{method}{request_path}{body}"
    mac = hmac.new(API_SECRET.encode(), message.encode(), hashlib.sha256)
    d = mac.digest()
    return base64.b64encode(d).decode()

def send_request(method, endpoint, payload=None):
    timestamp = get_timestamp()
    body = '' if payload is None else json.dumps(payload)
    signature = sign_request(timestamp, method.upper(), endpoint, body)

    headers = HEADERS.copy()
    headers["ACCESS-TIMESTAMP"] = timestamp
    headers["ACCESS-SIGN"] = signature

    url = BASE_URL + endpoint
    response = requests.request(method, url, headers=headers, data=body)

    if response.status_code != 200:
        print(f"[HTTP Error] {response.status_code} - {response.text}")
    return response.json()

def get_position(symbol):
    endpoint = f"/api/mix/v1/position/singlePosition?symbol={symbol}&marginCoin=USDT"
    return send_request("GET", endpoint)

def close_position(symbol, side, quantity):
    order_side = "close_long" if side == "long" else "close_short"
    payload = {
        "symbol": symbol,
        "marginCoin": "USDT",
        "size": str(quantity),
        "side": order_side,
        "orderType": "market"
    }
    return send_request("POST", "/api/mix/v1/order/close-position", payload)

def place_order(symbol, side, quantity, leverage):
    payload = {
        "symbol": symbol,
        "marginCoin": "USDT",
        "size": str(quantity),
        "side": side,
        "orderType": "market",
        "leverage": str(leverage)
    }
    return send_request("POST", "/api/mix/v1/order/place-order", payload)

def smart_trade(action, symbol, quantity, leverage):
    pos = get_position(symbol)
    side = pos.get("data", {}).get("holdSide")
    
    result = []

    if action == "buy":
        if side == "short":
            result.append(close_position(symbol, "short", quantity))
        result.append(place_order(symbol, "open_long", quantity, leverage))

    elif action == "sell":
        if side == "long":
            result.append(close_position(symbol, "long", quantity))
        result.append(place_order(symbol, "open_short", quantity, leverage))

    elif action == "close_long":
        if side == "long":
            result.append(close_position(symbol, "long", quantity))
        else:
            result.append("No long position to close.")

    elif action == "close_short":
        if side == "short":
            result.append(close_position(symbol, "short", quantity))
        else:
            result.append("No short position to close.")

    else:
        result.append(f"Invalid action: {action}")

    return result
