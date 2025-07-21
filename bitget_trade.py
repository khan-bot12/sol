import time
import hmac
import hashlib
import requests
import json
import os

API_KEY = os.getenv("BITGET_API_KEY")
API_SECRET = os.getenv("BITGET_API_SECRET")
API_PASSPHRASE = os.getenv("BITGET_API_PASSPHRASE")

BASE_URL = "https://api.bitget.com"

class BitgetTrader:
    def __init__(self, symbol="SOLUSDT"):
        self.symbol = symbol
        self.product_type = "umcbl"
        self.margin_mode = "crossed"
        self.leverage = 50

    def _get_timestamp(self):
        return str(int(time.time() * 1000))

    def _sign(self, timestamp, method, request_path, body=""):
        prehash = f"{timestamp}{method.upper()}{request_path}{body}"
        return hmac.new(API_SECRET.encode(), prehash.encode(), hashlib.sha256).hexdigest()

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

    def _request(self, method, path, body=None):
        url = BASE_URL + path
        body_str = json.dumps(body) if body else ""
        headers = self._headers(method, path, body_str)
        response = requests.request(method, url, headers=headers, data=body_str)
        return response.json()

    def get_positions(self):
        path = f"/api/mix/v1/position/singlePosition?productType={self.product_type}&symbol={self.symbol}"
        return self._request("GET", path)

    def close_position(self, side):
        order_side = "close_long" if side == "long" else "close_short"
        position_data = self.get_positions()
        size = position_data.get("data", {}).get("total", "0")

        if float(size) == 0:
            return {"message": f"No {side} position to close."}

        body = {
            "symbol": self.symbol,
            "marginCoin": "USDT",
            "size": size,
            "side": "close_long" if side == "long" else "close_short",
            "orderType": "market",
            "productType": self.product_type
        }
        return self._request("POST", "/api/mix/v1/order/placeOrder", body)

    def open_position(self, side, quantity):
        body = {
            "symbol": self.symbol,
            "marginCoin": "USDT",
            "size": str(quantity),
            "side": "open_long" if side == "buy" else "open_short",
            "orderType": "market",
            "leverage": str(self.leverage),
            "marginMode": self.margin_mode,
            "productType": self.product_type
        }
        return self._request("POST", "/api/mix/v1/order/placeOrder", body)

    def smart_trade(self, action, quantity):
        if action == "buy":
            self.close_position("short")
            return self.open_position("buy", quantity)
        elif action == "sell":
            self.close_position("long")
            return self.open_position("sell", quantity)
        else:
            return {"error": "Invalid action. Use 'buy' or 'sell'."}
