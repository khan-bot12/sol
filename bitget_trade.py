import time
import hmac
import hashlib
import json
import requests
import logging
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("BITGET_API_KEY")
API_SECRET = os.getenv("BITGET_API_SECRET")
API_PASSPHRASE = os.getenv("BITGET_API_PASSPHRASE")

BASE_URL = "https://api.bitget.com"
MARGIN_COIN = "USDT"

# === Logging ===
logging.basicConfig(
    filename="/root/sol/webhook_logs.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class BitgetTrader:

    def _get_timestamp(self):
        return str(int(time.time() * 1000))

    def _sign(self, timestamp, method, request_path, body=''):
        message = timestamp + method.upper() + request_path + body
        signature = hmac.new(
            API_SECRET.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature

    def _headers(self, method, path, body=""):
        timestamp = self._get_timestamp()
        sign = self._sign(timestamp, method, path, body)
        return {
            "ACCESS-KEY": API_KEY,
            "ACCESS-SIGN": sign,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-PASSPHRASE": API_PASSPHRASE,
            "Content-Type": "application/json"
        }

    def _post(self, endpoint, data):
        url = BASE_URL + endpoint
        body = json.dumps(data)
        headers = self._headers("POST", endpoint, body)
        logging.info(f"[REQUEST] {url} {body}")
        response = requests.post(url, headers=headers, data=body)
        logging.info(f"[RESPONSE] {response.status_code} {response.text}")
        return response.json()

    def open_long(self, symbol, size, leverage):
        data = {
            "symbol": symbol,
            "marginCoin": MARGIN_COIN,
            "side": "open_long",
            "orderType": "market",
            "size": str(size),
            "leverage": str(leverage)
        }
        return self._post("/api/mix/v1/order/placeOrder", data)

    def open_short(self, symbol, size, leverage):
        data = {
            "symbol": symbol,
            "marginCoin": MARGIN_COIN,
            "side": "open_short",
            "orderType": "market",
            "size": str(size),
            "leverage": str(leverage)
        }
        return self._post("/api/mix/v1/order/placeOrder", data)

    def close_long(self, symbol):
        data = {
            "symbol": symbol,
            "marginCoin": MARGIN_COIN,
            "side": "close_long",
            "orderType": "market",
            "size": "100"  # adjust as needed
        }
        return self._post("/api/mix/v1/order/placeOrder", data)

    def close_short(self, symbol):
        data = {
            "symbol": symbol,
            "marginCoin": MARGIN_COIN,
            "side": "close_short",
            "orderType": "market",
            "size": "100"  # adjust as needed
        }
        return self._post("/api/mix/v1/order/placeOrder", data)
