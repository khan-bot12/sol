import json
from fastapi import FastAPI, Request
from pydantic import BaseModel
from bitget_trade import BitgetTrader
import datetime

app = FastAPI()
trader = BitgetTrader()

class TradeSignal(BaseModel):
    action: str
    symbol: str
    quantity: float
    leverage: int

LOG_FILE = "/root/sol/webhook_logs.log"

def log_to_file(message: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

@app.post("/webhook")
async def webhook(request: Request):
    try:
        log_to_file("🚨 Webhook endpoint triggered")

        payload = await request.json()
        log_to_file(f"[INFO] Payload received: {payload}")

        required_fields = {"action", "symbol", "quantity", "leverage"}
        if not required_fields.issubset(payload.keys()):
            log_to_file("[ERROR] Missing required field in webhook")
            return {"error": "Missing required field in webhook"}

        action = payload["action"]
        symbol = payload["symbol"]
        quantity = payload["quantity"]
        leverage = payload["leverage"]

        if action == "buy":
            log_to_file(f"[ACTION] Opening LONG for {symbol} ({quantity} at {leverage}x)")
            trader.open_long(symbol, quantity, leverage)
        elif action == "sell":
            log_to_file(f"[ACTION] Opening SHORT for {symbol} ({quantity} at {leverage}x)")
            trader.open_short(symbol, quantity, leverage)
        elif action == "close_long":
            log_to_file(f"[ACTION] Closing LONG for {symbol}")
            trader.close_long(symbol)
        elif action == "close_short":
            log_to_file(f"[ACTION] Closing SHORT for {symbol}")
            trader.close_short(symbol)
        else:
            log_to_file(f"[ERROR] Unknown action: {action}")
            return {"error": "Invalid action"}

        log_to_file("[SUCCESS] Action executed")
        return {"status": "ok"}

    except Exception as e:
        error_msg = f"[ERROR] Exception: {str(e)}"
        log_to_file(error_msg)
        return {"error": str(e)}
