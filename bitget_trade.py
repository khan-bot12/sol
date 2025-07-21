import os
import time
import logging
import hmac
import hashlib
import base64
import json
import requests
from dotenv import load_dotenv

load_dotenv()

# === Logging Setup ===
logging.basicConfig(
    filename="/root/sol/webhook_logs.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class BitgetTrader:
    def __init__(self):
        self.api_key = os.getenv("BITGET_API_KEY")
        self.secret_key = os.getenv("BITGET_API_SECRET")
        self.passphrase = os.getenv("BITGET_API_PASSPHRASE")
        self.base_url = "https://api.bitget.com"
        self.headers = {
            "Content-Type": "application/json",
            "ACCESS-KEY": self.api_key,
            "ACCESS-PASSPHRASE": self.passphrase
        }

    def _get_timestamp(self):
        return str(int(time.time() * 1000))

    def _sign(self, timestamp, method, request_path, body=""):
        message = f"{timestamp}{method}{request_path}{body}"
        signature = hmac.new(self.secret_key.encode(), message.encode(), hashlib.sha256).digest()
        return base64.b64encode(signature).decode()

    def _request(self, method, endpoint, body=""):
        timestamp = self._get_timestamp()
        body_str = json.dumps(body) if body else ""
        sign = self._sign(timestamp, method.upper(), endpoint, body_str)

        headers = self.headers.copy()
        headers.update({
            "ACCESS-SIGN": sign,
            "ACCESS-TIMESTAMP": timestamp
        })

        url = self.base_url + endpoint

        try:
            if method.upper() == "POST":
                response = requests.post(url, headers=headers, data=body_str)
            else:
                response = requests.get(url, headers=headers, params=body)

            response.raise_for_status()
            logging.info(f"[RESPONSE] {response.status_code} {response.text}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"[ERROR] Request failed: {e}")
            return None

    def set_leverage(self, symbol, leverage):
        body = {
            "symbol": symbol,
            "marginCoin": "USDT",
            "leverage": str(leverage),
            "holdSide": "long"
        }
        self._request("POST", "/api/mix/v1/account/setLeverage", body)

    def close_long(self, symbol):
        logging.info(f"[CLOSE] Closing LONG position on {symbol}")
        self._close_position(symbol, "close_long")

    def close_short(self, symbol):
        logging.info(f"[CLOSE] Closing SHORT position on {symbol}")
        self._close_position(symbol, "close_short")

    def _close_position(self, symbol, side):
        side_map = {
            "close_long": "close_long",
            "close_short": "close_short"
        }
        order_side = "close_long" if side == "close_long" else "close_short"
        hold_side = "long" if side == "close_long" else "short"

        body = {
            "symbol": symbol,
            "marginCoin": "USDT",
            "size": "100%",  # full close
            "side": "close",
            "holdSide": hold_side
        }

        logging.info(f"[ORDER] Sending {side} order for {symbol}")
        self._request("POST", "/api/mix/v1/order/close-position", body)

    def open_long(self, symbol, quantity, leverage):
        logging.info(f"[OPEN] Opening LONG on {symbol} Qty: {quantity} Lev: {leverage}")
        self.set_leverage(symbol, leverage)
        self._place_order(symbol, quantity, "open_long")

    def open_short(self, symbol, quantity, leverage):
        logging.info(f"[OPEN] Opening SHORT on {symbol} Qty: {quantity} Lev: {leverage}")
        self.set_leverage(symbol, leverage)
        self._place_order(symbol, quantity, "open_short")

    def _place_order(self, symbol, quantity, side):
        side_type = "buy" if side == "open_long" else "sell"
        hold_side = "long" if side == "open_long" else "short"

        body = {
            "symbol": symbol,
            "marginCoin": "USDT",
            "size": str(quantity),
            "side": side_type,
            "orderType": "market",
            "holdSide": hold_side
        }

        logging.info(f"[ORDER] Placing {side.upper()} market order: {body}")
        self._request("POST", "/api/mix/v1/order/place-order", body)
