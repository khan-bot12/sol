# === bitget_trade.py ===
import os
import time
import hmac
import hashlib
import requests
import logging
from dotenv import load_dotenv

load_dotenv()

BITGET_API_KEY = os.getenv("BITGET_API_KEY")
BITGET_API_SECRET = os.getenv("BITGET_API_SECRET")
BITGET_API_PASSPHRASE = os.getenv("BITGET_API_PASSPHRASE")
BASE_URL = "https://api.bitget.com"

HEADERS = {
    "ACCESS-KEY": BITGET_API_KEY,
    "Content-Type": "application/json",
    "locale": "en-US"
}

class BitgetTrader:
    def __init__(self):
        if not all([BITGET_API_KEY, BITGET_API_SECRET, BITGET_API_PASSPHRASE]):
            raise ValueError("Missing API credentials")

    def _get_timestamp(self):
        return str(int(time.time() * 1000))

    def _sign(self, timestamp, method, request_path, body=""):
        message = f"{timestamp}{method}{request_path}{body}"
        signature = hmac.new(BITGET_API_SECRET.encode(), message.encode(), hashlib.sha256).hexdigest()
        return signature

    def _send_request(self, method, endpoint, body=""):
        timestamp = self._get_timestamp()
        request_path = f"/api/mix/v1{endpoint}"
        signature = self._sign(timestamp, method, request_path, body)

        HEADERS.update({
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-SIGN": signature,
            "ACCESS-PASSPHRASE": BITGET_API_PASSPHRASE
        })

        url = BASE_URL + request_path
        response = requests.request(method, url, headers=HEADERS, data=body)
        logging.info(f"[HTTP] {method} {url} - {response.status_code}: {response.text}")
        return response.json()

    def _place_order(self, symbol, size, leverage, side, positionSide):
        endpoint = "/order/placeOrder"
        body = json.dumps({
            "symbol": symbol,
            "marginCoin": "USDT",
            "size": str(size),
            "price": "",
            "side": side,
            "orderType": "market",
            "positionSide": positionSide,
            "leverage": str(leverage)
        })
        return self._send_request("POST", endpoint, body)

    def _close_position(self, symbol, side):
        endpoint = "/order/close-position"
        body = json.dumps({
            "symbol": symbol,
            "marginCoin": "USDT",
            "side": side
        })
        return self._send_request("POST", endpoint, body)

    def open_long(self, symbol, quantity, leverage):
        logging.info(f"[ORDER] Opening LONG: {symbol}, Qty: {quantity}, Leverage: {leverage}")
        self._close_position(symbol, "short")
        return self._place_order(symbol, quantity, leverage, "buy", "long")

    def open_short(self, symbol, quantity, leverage):
        logging.info(f"[ORDER] Opening SHORT: {symbol}, Qty: {quantity}, Leverage: {leverage}")
        self._close_position(symbol, "long")
        return self._place_order(symbol, quantity, leverage, "sell", "short")

    def close_long(self, symbol):
        logging.info(f"[ORDER] Closing LONG: {symbol}")
        return self._close_position(symbol, "long")

    def close_short(self, symbol):
        logging.info(f"[ORDER] Closing SHORT: {symbol}")
        return self._close_position(symbol, "short")
