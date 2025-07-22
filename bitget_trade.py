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
        self.supported_symbols = ["SOLUSDT", "ETHUSDT", "BTCUSDT"]

    def _get_timestamp(self):
        return str(int(time.time() * 1000))

    def _sign(self, timestamp, method, request_path, body=''):
        prehash = f"{timestamp}{method.upper()}{request_path}{body}"
        signature = hmac.new(
            API_SECRET.encode(),
            prehash.encode(),
            hashlib.sha256
        ).digest()
        return base64.b64encode(signature).decode()

    def _headers(self, method, path, body=''):
        timestamp = self._get_timestamp()
        sign = self._sign(timestamp, method, path, body)
        return {
            "ACCESS-KEY": API_KEY,
            "ACCESS-SIGN": sign,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-PASSPHRASE": API_PASSPHRASE,
            "Content-Type": "application/json"
        }

    def _place_order(self, symbol, side, size, leverage):
        if symbol.upper() not in self.supported_symbols:
            print(f"[ERROR] Unsupported symbol: {symbol}")
            return

        path = "/api/mix/v1/order/placeOrder"
        url = BASE_URL + path

        body_dict = {
            "symbol": symbol.upper(),
            "marginCoin": "USDT",
            "productType": "UMCBL",
            "size": str(size),
            "side": side,
            "orderType": "market",
            "tradeSide": "open",
            "leverage": str(leverage)
        }

        body = json.dumps(body_dict)
        headers = self._headers("POST", path, body)

        response = requests.post(url, headers=headers, data=body)
        print("[INFO] Order Response:", response.text)

    def _close_order(self, symbol, side, size="0.1"):
        if symbol.upper() not in self.supported_symbols:
            print(f"[ERROR] Unsupported symbol: {symbol}")
            return

        path = "/api/mix/v1/order/placeOrder"
        url = BASE_URL + path

        body_dict = {
            "symbol": symbol.upper(),
            "marginCoin": "USDT",
            "productType": "UMCBL",
            "size": str(size),
            "side": side,
            "orderType": "market",
            "tradeSide": "close",
        }

        body = json.dumps(body_dict)
        headers = self._headers("POST", path, body)

        response = requests.post(url, headers=headers, data=body)
        print("[INFO] Close Order Response:", response.text)

    def open_long(self, symbol, size, leverage):
        print(f"[ACTION] Opening LONG: {symbol}, Qty: {size}, Lev: {leverage}")
        self._place_order(symbol, "buy", size, leverage)

    def open_short(self, symbol, size, leverage):
        print(f"[ACTION] Opening SHORT: {symbol}, Qty: {size}, Lev: {leverage}")
        self._place_order(symbol, "sell", size, leverage)

    def close_long(self, symbol):
        print(f"[ACTION] Closing LONG: {symbol}")
        self._close_order(symbol, "sell")

    def close_short(self, symbol):
        print(f"[ACTION] Closing SHORT: {symbol}")
        self._close_order(symbol, "buy")
