import os
import time
import hmac
import json
import base64
import hashlib
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BITGET_API_KEY")
API_SECRET = os.getenv("BITGET_API_SECRET")
API_PASSPHRASE = os.getenv("BITGET_API_PASSPHRASE")
BASE_URL = "https://api.bitget.com"

class BitgetTrader:
    def __init__(self):
        if not API_KEY or not API_SECRET or not API_PASSPHRASE:
            raise Exception("Missing API credentials in .env")

    def _get_timestamp(self):
        return str(int(time.time() * 1000))

    def _sign(self, timestamp, method, request_path, body=""):
        message = f"{timestamp}{method.upper()}{request_path}{body}"
        signature = hmac.new(
            API_SECRET.encode("utf-8"),
            message.encode("utf-8"),
            digestmod=hashlib.sha256
        ).digest()
        return base64.b64encode(signature).decode()

    def _headers(self, method, request_path, body=""):
        timestamp = self._get_timestamp()
        sign = self._sign(timestamp, method, request_path, body)
        return {
            "ACCESS-KEY": API_KEY,
            "ACCESS-SIGN": sign,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-PASSPHRASE": API_PASSPHRASE,
            "Content-Type": "application/json"
        }

    def _request(self, method, path, data=None):
        url = BASE_URL + path
        body = json.dumps(data) if data else ""
        headers = self._headers(method, path, body)
        response = requests.request(method, url, headers=headers, data=body)
        print(f"[{method}] {url} >> {response.status_code} {response.text}")
        if response.status_code != 200:
            raise Exception(f"Bitget API error: {response.status_code} {response.text}")
        return response.json()

    def open_long(self, symbol, quantity, leverage):
        self._request("POST", "/api/mix/v1/order/placeOrder", {
            "symbol": symbol.replace("_UMCBL", ""),
            "marginCoin": "USDT",
            "orderType": "market",
            "side": "open_long",
            "size": quantity,
            "leverage": leverage,
            "productType": "umcbl"
        })

    def open_short(self, symbol, quantity, leverage):
        self._request("POST", "/api/mix/v1/order/placeOrder", {
            "symbol": symbol.replace("_UMCBL", ""),
            "marginCoin": "USDT",
            "orderType": "market",
            "side": "open_short",
            "size": quantity,
            "leverage": leverage,
            "productType": "umcbl"
        })

    def close_long(self, symbol):
        self._request("POST", "/api/mix/v1/order/closePositions", {
            "symbol": symbol.replace("_UMCBL", ""),
            "marginCoin": "USDT",
            "side": "close_long",
            "productType": "umcbl"
        })

    def close_short(self, symbol):
        self._request("POST", "/api/mix/v1/order/closePositions", {
            "symbol": symbol.replace("_UMCBL", ""),
            "marginCoin": "USDT",
            "side": "close_short",
            "productType": "umcbl"
        })
