# bitget_trade.py
import os
import time
import hmac
import hashlib
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

class BitgetTrader:
    def __init__(self):
        self.api_key = os.getenv("BITGET_API_KEY")
        self.api_secret = os.getenv("BITGET_API_SECRET")
        self.passphrase = os.getenv("BITGET_API_PASSPHRASE")
        self.base_url = "https://api.bitget.com"

    def _headers(self, method, request_path, body=''):
        timestamp = str(int(time.time() * 1000))
        prehash = timestamp + method + request_path + body
        signature = base64.b64encode(
            hmac.new(self.api_secret.encode(), prehash.encode(), hashlib.sha256).digest()
        ).decode()

        return {
            'ACCESS-KEY': self.api_key,
            'ACCESS-SIGN': signature,
            'ACCESS-TIMESTAMP': timestamp,
            'ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        }

    def _place_order(self, symbol, side, quantity, leverage):
        print(f"[Order] Placing {side} order for {symbol} with qty {quantity}")
        endpoint = "/api/mix/v1/order/place-order"
        url = self.base_url + endpoint
        body = {
            "symbol": symbol,
            "marginCoin": "USDT",
            "side": side,
            "orderType": "market",
            "size": str(quantity),
            "leverage": str(leverage),
            "marketCode": "UMCBL",
        }
        body_json = json.dumps(body)
        headers = self._headers("POST", endpoint, body_json)

        response = requests.post(url, headers=headers, data=body_json)
        print("[Order Response]", response.text)
        return response.json()

    def _close_position(self, symbol, side):
        print(f"[Close] Closing {side} position for {symbol}")
        endpoint = "/api/mix/v1/position/close-position"
        url = self.base_url + endpoint
        body = {
            "symbol": symbol,
            "marginCoin": "USDT",
            "holdSide": side
        }
        body_json = json.dumps(body)
        headers = self._headers("POST", endpoint, body_json)

        response = requests.post(url, headers=headers, data=body_json)
        print("[Close Response]", response.text)
        return response.json()

    def open_long(self, symbol, quantity, leverage):
        return self._place_order(symbol, "open_long", quantity, leverage)

    def open_short(self, symbol, quantity, leverage):
        return self._place_order(symbol, "open_short", quantity, leverage)

    def close_long(self, symbol):
        return self._close_position(symbol, "long")

    def close_short(self, symbol):
        return self._close_position(symbol, "short")
