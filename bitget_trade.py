import os
import time
import hmac
import json
import hashlib
import requests
from dotenv import load_dotenv

load_dotenv()

class BitgetTrader:
    def __init__(self):
        self.api_key = os.getenv("BITGET_API_KEY")
        self.api_secret = os.getenv("BITGET_API_SECRET")
        self.api_passphrase = os.getenv("BITGET_API_PASSPHRASE")
        self.base_url = "https://api.bitget.com"

    def _sign(self, timestamp, method, request_path, body=""):
        message = f"{timestamp}{method}{request_path}{body}"
        mac = hmac.new(self.api_secret.encode(), message.encode(), hashlib.sha256)
        return mac.hexdigest()

    def _send_request(self, method, endpoint, body=""):
        url = self.base_url + endpoint
        timestamp = str(int(time.time() * 1000))
        body_str = json.dumps(body) if body else ""
        signature = self._sign(timestamp, method.upper(), endpoint, body_str)

        headers = {
            "ACCESS-KEY": self.api_key,
            "ACCESS-SIGN": signature,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-PASSPHRASE": self.api_passphrase,
            "Content-Type": "application/json"
        }

        response = requests.request(method, url, headers=headers, data=body_str)
        try:
            print(f"[Bitget API] {method} {endpoint} → {response.status_code}")
            print(f"[Response] {response.text}")
            return response.json()
        except Exception as e:
            print(f"[Error] Failed to parse response: {e}")
            return None

    def set_leverage(self, symbol, leverage):
        body = {
            "symbol": symbol,
            "marginCoin": "USDT",
            "leverage": str(leverage),
            "holdSide": "long"
        }
        self._send_request("POST", "/api/mix/v1/account/setLeverage", body)

    def close_long(self, symbol):
        print(f"[Action] Closing LONG on {symbol}")
        self._place_order(symbol, "close_long")

    def close_short(self, symbol):
        print(f"[Action] Closing SHORT on {symbol}")
        self._place_order(symbol, "close_short")

    def open_long(self, symbol, quantity):
        print(f"[Action] Opening LONG on {symbol} with {quantity}")
        self._place_order(symbol, "open_long", quantity)

    def open_short(self, symbol, quantity):
        print(f"[Action] Opening SHORT on {symbol} with {quantity}")
        self._place_order(symbol, "open_short", quantity)

    def _place_order(self, symbol, side, quantity=0):
        side_map = {
            "open_long": ("buy", "open_long"),
            "open_short": ("sell", "open_short"),
            "close_long": ("sell", "close_long"),
            "close_short": ("buy", "close_short")
        }

        if side not in side_map:
            print(f"[Error] Invalid order side: {side}")
            return

        side_type, pos_side = side_map[side]

        body = {
            "symbol": symbol,
            "marginCoin": "USDT",
            "size": str(quantity),
            "price": "",
            "side": side_type,
            "orderType": "market",
            "posSide": pos_side
        }

        self._send_request("POST", "/api/mix/v1/order/placeOrder", body)
