import os
import time
import hmac
import hashlib
import requests
import json
from dotenv import load_dotenv

load_dotenv()

BITGET_API_KEY = os.getenv("BITGET_API_KEY")
BITGET_API_SECRET = os.getenv("BITGET_API_SECRET")
BITGET_API_PASSPHRASE = os.getenv("BITGET_API_PASSPHRASE")

BASE_URL = "https://api.bitget.com"

HEADERS = {
    "Content-Type": "application/json",
    "ACCESS-KEY": BITGET_API_KEY,
    "ACCESS-PASSPHRASE": BITGET_API_PASSPHRASE,
}

class BitgetTrader:
    def __init__(self):
        self.symbol = None

    def _get_timestamp(self):
        return str(int(time.time() * 1000))

    def _sign(self, timestamp, method, request_path, body=""):
        message = timestamp + method + request_path + body
        signature = hmac.new(
            BITGET_API_SECRET.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature

    def _send_request(self, method, endpoint, payload=None):
        timestamp = self._get_timestamp()
        body = json.dumps(payload) if payload else ""
        sign = self._sign(timestamp, method.upper(), endpoint, body)

        headers = HEADERS.copy()
        headers["ACCESS-TIMESTAMP"] = timestamp
        headers["ACCESS-SIGN"] = sign

        url = BASE_URL + endpoint

        response = requests.request(
            method.upper(), url, headers=headers, data=body
        )

        print(f"[DEBUG] {method} {url} => {response.status_code}: {response.text}")

        return response.json()

    def place_order(self, action, symbol, quantity, leverage):
        self.symbol = symbol

        # Close opposite side before opening new trade
        if action == "buy":
            self.close_short(symbol)
        elif action == "sell":
            self.close_long(symbol)

        endpoint = "/api/mix/v1/order/place"
        payload = {
            "symbol": symbol,
            "marginCoin": "USDT",
            "side": "open_long" if action == "buy" else "open_short",
            "orderType": "market",
            "size": str(quantity),
            "leverage": str(leverage),
            "tradeSide": "open"
        }

        return self._send_request("POST", endpoint, payload)

    def close_long(self, symbol):
        endpoint = "/api/mix/v1/order/close-position"
        payload = {
            "symbol": symbol,
            "marginCoin": "USDT",
            "side": "close_long"
        }
        return self._send_request("POST", endpoint, payload)

    def close_short(self, symbol):
        endpoint = "/api/mix/v1/order/close-position"
        payload = {
            "symbol": symbol,
            "marginCoin": "USDT",
            "side": "close_short"
        }
        return self._send_request("POST", endpoint, payload)
