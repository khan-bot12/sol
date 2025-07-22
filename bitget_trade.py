import time
import hmac
import hashlib
import requests
import uuid
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("BitgetTrader")

class BitgetTrader:
    def __init__(self):
        self.api_key = os.getenv("BITGET_API_KEY")
        self.api_secret = os.getenv("BITGET_API_SECRET")
        self.api_passphrase = os.getenv("BITGET_API_PASSPHRASE")
        self.base_url = "https://api.bitget.com"

    def _headers(self, method, path, body=""):
        timestamp = str(int(time.time() * 1000))
        prehash = timestamp + method.upper() + path + body
        sign = hmac.new(
            self.api_secret.encode("utf-8"),
            prehash.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        return {
            "ACCESS-KEY": self.api_key,
            "ACCESS-SIGN": sign,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-PASSPHRASE": self.api_passphrase,
            "Content-Type": "application/json"
        }

    def place_order(self, symbol, side, position_side, quantity=None, leverage=None):
        logger.info(f"Placing order: {side.upper()} {position_side} {quantity} {symbol}")

        if leverage:
            self.set_leverage(symbol, leverage)

        # Close logic
        if position_side == "close_long":
            side = "sell"
            pos_side = "long"
            order_type = "market"
        elif position_side == "close_short":
            side = "buy"
            pos_side = "short"
            order_type = "market"
        # Open logic
        elif position_side == "long":
            pos_side = "long"
            order_type = "market"
        elif position_side == "short":
            pos_side = "short"
            order_type = "market"
        else:
            raise ValueError("Invalid position_side")

        path = "/api/mix/v1/order/place"
        url = self.base_url + path
        body = {
            "symbol": symbol,
            "marginCoin": "USDT",
            "side": side,
            "orderType": order_type,
            "posSide": pos_side,
            "size": str(quantity) if quantity else "0",
            "leverage": str(leverage) if leverage else "50",
            "clientOid": str(uuid.uuid4()),
            "tradeSide": position_side  # Optional field for clarification
        }

        import json
        headers = self._headers("POST", path, json.dumps(body))

        response = requests.post(url, headers=headers, json=body)

        if response.status_code == 200:
            logger.info(f"Order response: {response.json()}")
        else:
            logger.error(f"Order failed: {response.status_code} {response.text}")

    def set_leverage(self, symbol, leverage):
        logger.info(f"Setting leverage: {leverage}x for {symbol}")
        path = "/api/mix/v1/account/setLeverage"
        url = self.base_url + path
        body = {
            "symbol": symbol,
            "marginCoin": "USDT",
            "leverage": str(leverage),
            "holdSide": "long"
        }

        import json
        headers = self._headers("POST", path, json.dumps(body))
        response = requests.post(url, headers=headers, json=body)

        if response.status_code == 200:
            logger.info(f"Leverage response: {response.json()}")
        else:
            logger.error(f"Leverage set failed: {response.status_code} {response.text}")

    # ✅ Add these two methods to support main.py
    def close_long(self, symbol):
        self.place_order(symbol, "sell", "close_long")

    def close_short(self, symbol):
        self.place_order(symbol, "buy", "close_short")
