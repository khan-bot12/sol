import os
import requests
import time
import hmac
import hashlib
import json

class BitgetTrader:
    def __init__(self):
        self.API_KEY = os.getenv("BITGET_API_KEY")
        self.SECRET_KEY = os.getenv("BITGET_SECRET_KEY")
        self.PASSPHRASE = os.getenv("BITGET_PASSPHRASE")
        self.base_url = "https://api.bitget.com"
        self.headers = {
            "ACCESS-KEY": self.API_KEY,
            "ACCESS-PASSPHRASE": self.PASSPHRASE,
            "Content-Type": "application/json"
        }

    def _get_timestamp(self):
        return str(int(time.time() * 1000))

    def _sign(self, timestamp, method, request_path, body=""):
        message = f"{timestamp}{method}{request_path}{body}"
        signature = hmac.new(
            self.SECRET_KEY.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        return signature

    def _send_request(self, method, path, body_dict=None):
        url = self.base_url + path
        timestamp = self._get_timestamp()
        body = "" if body_dict is None else json.dumps(body_dict)
        sign = self._sign(timestamp, method.upper(), path, body)
        headers = self.headers.copy()
        headers["ACCESS-TIMESTAMP"] = timestamp
        headers["ACCESS-SIGN"] = sign

        response = requests.request(method, url, headers=headers, data=body)
        if response.status_code != 200:
            print("[ERROR]", response.text)
        return response.json()

    def close_long(self, symbol):
        print(f"[ACTION] Closing LONG position for {symbol}")
        body = {
            "symbol": symbol,
            "marginCoin": "USDT",
            "size": 0,
            "holdSide": "long"
        }
        self._send_request("POST", "/api/mix/v1/order/close-positions", body)

    def close_short(self, symbol):
        print(f"[ACTION] Closing SHORT position for {symbol}")
        body = {
            "symbol": symbol,
            "marginCoin": "USDT",
            "size": 0,
            "holdSide": "short"
        }
        self._send_request("POST", "/api/mix/v1/order/close-positions", body)

    def open_long(self, symbol, quantity, leverage=50):
        print(f"[ACTION] Opening LONG position for {symbol}, qty: {quantity}")
        body = {
            "symbol": symbol,
            "marginCoin": "USDT",
            "size": str(quantity),
            "side": "open_long",
            "orderType": "market",
            "leverage": str(leverage)
        }
        self._send_request("POST", "/api/mix/v1/order/place-order", body)

    def open_short(self, symbol, quantity, leverage=50):
        print(f"[ACTION] Opening SHORT position for {symbol}, qty: {quantity}")
        body = {
            "symbol": symbol,
            "marginCoin": "USDT",
            "size": str(quantity),
            "side": "open_short",
            "orderType": "market",
            "leverage": str(leverage)
        }
        self._send_request("POST", "/api/mix/v1/order/place-order", body)
