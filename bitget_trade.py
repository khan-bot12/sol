import os
import time
import hmac
import hashlib
import base64
import requests
import logging
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BITGET_API_KEY")
API_SECRET = os.getenv("BITGET_API_SECRET")
API_PASSPHRASE = os.getenv("BITGET_API_PASSPHRASE")
BASE_URL = "https://api.bitget.com"

logging.basicConfig(filename='webhook_logs.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

HEADERS = {
    "Content-Type": "application/json",
    "ACCESS-KEY": API_KEY,
    "ACCESS-PASSPHRASE": API_PASSPHRASE,
}


def _get_timestamp():
    return str(int(time.time() * 1000))


def _sign(method, request_path, body=''):
    timestamp = _get_timestamp()
    prehash = timestamp + method.upper() + request_path + body
    signature = base64.b64encode(
        hmac.new(API_SECRET.encode(), prehash.encode(), hashlib.sha256).digest()
    ).decode()
    return signature, timestamp


def _send_request(method, path, body=''):
    body_str = body if isinstance(body, str) else json.dumps(body)
    signature, timestamp = _sign(method, path, body_str)

    headers = HEADERS.copy()
    headers.update({
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-SIGN": signature
    })

    url = BASE_URL + path
    response = requests.request(method, url, headers=headers, data=body_str)
    if response.status_code != 200:
        logging.error(f"Error: {response.status_code} - {response.text}")
    return response.json()


class BitgetTrader:
    def __init__(self, symbol: str):
        self.symbol = symbol.upper()  # e.g., SOLUSDT
        self.margin_coin = "USDT"
        self.leverage = 50
        self.symbol_full = f"{self.symbol}_UMCBL"

    def _place_order(self, action: str, quantity: float):
        """
        action: 'buy' (open long), 'sell' (open short), 'close_long', 'close_short'
        """
        side = "open"
        trade_side = "buy"

        if action == "buy":
            side = "open"
            trade_side = "buy"
        elif action == "sell":
            side = "open"
            trade_side = "sell"
        elif action == "close_long":
            side = "close"
            trade_side = "sell"
        elif action == "close_short":
            side = "close"
            trade_side = "buy"
        else:
            logging.error(f"Invalid action: {action}")
            return {"error": "Invalid action"}

        order = {
            "symbol": self.symbol_full,
            "marginCoin": self.margin_coin,
            "orderType": "market",
            "side": side,
            "tradeSide": trade_side,
            "size": str(quantity),
            "leverage": str(self.leverage)
        }

        logging.info(f"Placing order: {order}")
        path = "/api/mix/v1/order/placeOrder"
        result = _send_request("POST", path, json.dumps(order))
        logging.info(f"Order result: {result}")
        return result

    def execute_trade(self, action: str, quantity: float):
        logging.info(f"Executing action: {action} for {quantity} {self.symbol}")
        return self._place_order(action, quantity)
