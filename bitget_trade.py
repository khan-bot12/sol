# === bitget_trade.py ===
import os
import time
import hmac
import hashlib
import requests
import base64
import json
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BITGET_API_KEY")
API_SECRET = os.getenv("BITGET_API_SECRET")
API_PASSPHRASE = os.getenv("BITGET_API_PASSPHRASE")
BASE_URL = "https://api.bitget.com"

class BitgetTrader:
    def __init__(self):
        self.api_key = API_KEY
        self.api_secret = API_SECRET
        self.passphrase = API_PASSPHRASE

    def _get_headers(self, method, request_path, body):
        timestamp = str(int(time.time() * 1000))
        if body:
            body_str = json.dumps(body)
        else:
            body_str = ""
        prehash = f"{timestamp}{method}{request_path}{body_str}"
        sign = hmac.new(self.api_secret.encode(), prehash.encode(), hashlib.sha256).digest()
        sign_b64 = base64.b64encode(sign).decode()

        return {
            "ACCESS-KEY": self.api_key,
            "ACCESS-SIGN": sign_b64,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-PASSPHRASE": self.passphrase,
            "Content-Type": "application/json"
        }

    def execute_trade(self, action, symbol, quantity, leverage):
        # Set leverage
        leverage_endpoint = f"/api/mix/v1/account/setLeverage"
        leverage_body = {
            "symbol": symbol,
            "marginCoin": "USDT",
            "leverage": leverage,
            "holdSide": "long" if action == "buy" else "short"
        }
        headers = self._get_headers("POST", leverage_endpoint, leverage_body)
        requests.post(BASE_URL + leverage_endpoint, headers=headers, json=leverage_body)

        # Cancel opposite side
        self.close_position("short" if action == "buy" else "long", symbol, quantity)

        # Place order
        order_side = {
            "buy": "open_long",
            "sell": "open_short",
            "close_long": "close_long",
            "close_short": "close_short"
        }.get(action)

        if not order_side:
            return {"error": "Invalid action"}

        order_endpoint = "/api/mix/v1/order/placeOrder"
        order_body = {
            "symbol": symbol,
            "marginCoin": "USDT",
            "size": str(quantity),
            "side": order_side,
            "orderType": "market"
        }
        headers = self._get_headers("POST", order_endpoint, order_body)
        res = requests.post(BASE_URL + order_endpoint, headers=headers, json=order_body)

        return res.json()

    def close_position(self, side, symbol, quantity):
        endpoint = "/api/mix/v1/order/placeOrder"
        body = {
            "symbol": symbol,
            "marginCoin": "USDT",
            "size": str(quantity),
            "side": f"close_{side}",
            "orderType": "market"
        }
        headers = self._get_headers("POST", endpoint, body)
        requests.post(BASE_URL + endpoint, headers=headers, json=body)
