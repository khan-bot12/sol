import os
import time
import hmac
import hashlib
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BITGET_API_KEY")
API_SECRET = os.getenv("BITGET_API_SECRET")
API_PASSPHRASE = os.getenv("BITGET_API_PASSPHRASE")
BASE_URL = "https://api.bitget.com"

HEADERS = {
    "ACCESS-KEY": API_KEY,
    "ACCESS-PASSPHRASE": API_PASSPHRASE,
    "Content-Type": "application/json"
}

class BitgetTrader:
    def __init__(self):
        self.session = requests.Session()

    def _get_timestamp(self):
        return str(int(time.time() * 1000))

    def _sign(self, timestamp, method, request_path, body=''):
        pre_hash = f"{timestamp}{method.upper()}{request_path}{body}"
        return hmac.new(
            API_SECRET.encode(),
            pre_hash.encode(),
            hashlib.sha256
        ).hexdigest()

    def _send_request(self, method, path, body_dict=None):
        timestamp = self._get_timestamp()
        body = json.dumps(body_dict) if body_dict else ''
        sign = self._sign(timestamp, method, path, body)

        headers = HEADERS.copy()
        headers["ACCESS-TIMESTAMP"] = timestamp
        headers["ACCESS-SIGN"] = sign

        url = BASE_URL + path
        try:
            if method == "POST":
                response = self.session.post(url, headers=headers, data=body)
            else:
                response = self.session.get(url, headers=headers)

            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[Error] Failed to send request: {e}")
            return None

    def _place_order(self, symbol, side, size, leverage):
        # Ensure leverage is set
        self._set_leverage(symbol, leverage)

        order = {
            "symbol": symbol,
            "marginCoin": "USDT",
            "size": str(size),
            "side": side,
            "orderType": "market",
            "force": "gtc",
            "tradeSide": "open" if "open" in side.lower() else "close"
        }

        return self._send_request("POST", "/api/mix/v1/order/place-order", order)

    def _close_position(self, symbol, side):
        close_side = "close_long" if side == "long" else "close_short"
        path = "/api/mix/v1/order/close-position"
        body = {
            "symbol": symbol,
            "marginCoin": "USDT",
            "side": close_side
        }

        return self._send_request("POST", path, body)

    def _set_leverage(self, symbol, leverage):
        path = "/api/mix/v1/account/set-leverage"
        body = {
            "symbol": symbol,
            "marginCoin": "USDT",
            "leverage": str(leverage),
            "holdSide": "long_short"
        }
        return self._send_request("POST", path, body)

    def open_long(self, symbol, size, leverage):
        print(f"[TRADE] Opening LONG on {symbol} with size {size}")
        return self._place_order(symbol, "open_long", size, leverage)

    def open_short(self, symbol, size, leverage):
        print(f"[TRADE] Opening SHORT on {symbol} with size {size}")
        return self._place_order(symbol, "open_short", size, leverage)

    def close_long(self, symbol):
        print(f"[TRADE] Closing LONG on {symbol}")
        return self._close_position(symbol, "long")

    def close_short(self, symbol):
        print(f"[TRADE] Closing SHORT on {symbol}")
        return self._close_position(symbol, "short")
