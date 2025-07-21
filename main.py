import json
import logging
from fastapi import FastAPI, Request
from pydantic import BaseModel
from bitget_trade import BitgetTrader

# === Logging Setup ===
logging.basicConfig(
    filename="webhook_logs.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# === FastAPI App ===
app = FastAPI()

# === Pydantic model for webhook data ===
class TradeSignal(BaseModel):
    action: str
    symbol: str
    quantity: float
    leverage: int

# === Webhook Route ===
@app.post("/webhook")
async def webhook(request: Request):
    try:
        payload = await request.json()
        logging.info(f"Webhook received: {payload}")

        # Check required fields
        required = {"action", "symbol", "quantity", "leverage"}
        if not required.issubset(payload):
            logging.error("Missing required field in webhook")
            return {"error": "Missing required field in webhook"}

        action = payload["action"].lower()
        symbol = payload["symbol"].upper()
        quantity = float(payload["quantity"])
        leverage = int(payload["leverage"])

        # Create new trader instance for this symbol
        trader = BitgetTrader(symbol=symbol)

        # Action handling
        if action == "buy":
            trader.open_long(symbol, quantity, leverage)
        elif action == "sell":
            trader.open_short(symbol, quantity, leverage)
        elif action == "close_long":
            trader.close_long(symbol)
        elif action == "close_short":
            trader.close_short(symbol)
        else:
            logging.error(f"Invalid action: {action}")
            return {"error": "Invalid action type"}

        logging.info(f"Successfully processed: {action} {symbol} {quantity}@{leverage}x")
        return {"status": "ok"}

    except Exception as e:
        logging.exception(f"Exception in webhook handler: {str(e)}")
        return {"error": str(e)}
