import json
import logging
from datetime import datetime
from fastapi import FastAPI, Request
from pydantic import BaseModel
from bitget_trade import BitgetTrader

# === Setup Logging ===
logging.basicConfig(
    filename="/root/sol/webhook_logs.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI()
trader = BitgetTrader()

class TradeSignal(BaseModel):
    action: str
    symbol: str
    quantity: float
    leverage: int

@app.post("/webhook")
async def webhook(request: Request):
    try:
        payload = await request.json()
        log_msg = f"[WEBHOOK RECEIVED] {payload}"
        print(log_msg)
        logging.info(log_msg)

        # Validate required fields
        required_fields = {"action", "symbol", "quantity", "leverage"}
        if not required_fields.issubset(payload.keys()):
            error_msg = "[ERROR] Missing required field in webhook"
            print(error_msg)
            logging.error(error_msg)
            return {"error": error_msg}

        action = payload["action"]
        symbol = payload["symbol"]
        quantity = payload["quantity"]
        leverage = payload["leverage"]

        # Handle signals
        if action == "buy":
            logging.info(f"[ACTION] Opening LONG on {symbol} with {quantity} @ {leverage}x")
            trader.open_long(symbol, quantity, leverage)

        elif action == "sell":
            logging.info(f"[ACTION] Opening SHORT on {symbol} with {quantity} @ {leverage}x")
            trader.open_short(symbol, quantity, leverage)

        elif action == "close_long":
            logging.info(f"[ACTION] Closing LONG on {symbol}")
            trader.close_long(symbol)

        elif action == "close_short":
            logging.info(f"[ACTION] Closing SHORT on {symbol}")
            trader.close_short(symbol)

        else:
            error_msg = f"[ERROR] Unknown action: {action}"
            print(error_msg)
            logging.error(error_msg)
            return {"error": error_msg}

        return {"status": "ok"}

    except Exception as e:
        error_msg = f"[ERROR] Exception while processing webhook: {str(e)}"
        print(error_msg)
        logging.error(error_msg)
        return {"error": str(e)}
