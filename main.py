import json
import logging
from fastapi import FastAPI, Request
from pydantic import BaseModel
from bitget_trade import BitgetTrader

# Setup logging
logging.basicConfig(
    filename="/root/sol/webhook_logs.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
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
        logging.info(f"Webhook received: {payload}")

        required_fields = {"action", "symbol", "quantity", "leverage"}
        if not required_fields.issubset(payload.keys()):
            logging.error("Missing required field in webhook")
            return {"error": "Missing required field in webhook"}

        action = payload["action"]
        symbol = payload["symbol"]
        quantity = payload["quantity"]
        leverage = payload["leverage"]

        if action == "buy":
            logging.info("Executing open_long()")
            trader.open_long(symbol, quantity, leverage)
        elif action == "sell":
            logging.info("Executing open_short()")
            trader.open_short(symbol, quantity, leverage)
        elif action == "close_long":
            logging.info("Executing close_long()")
            trader.close_long(symbol)
        elif action == "close_short":
            logging.info("Executing close_short()")
            trader.close_short(symbol)
        else:
            logging.error(f"Unknown action: {action}")
            return {"error": "Invalid action"}

        logging.info("Webhook processed successfully")
        return {"status": "ok"}

    except Exception as e:
        logging.exception("Exception while processing webhook")
        return {"error": str(e)}
