import json
import logging
import sys
from fastapi import FastAPI, Request
from pydantic import BaseModel
from bitget_trade import BitgetTrader

# === Setup logging ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("/root/sol/webhook_logs.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

app = FastAPI()
trader = BitgetTrader()

class TradeSignal(BaseModel):
    action: str
    symbol: str
    quantity: float = 0  # Optional for close actions
    leverage: int = 0    # Optional for close actions

@app.post("/webhook")
async def webhook(request: Request):
    try:
        payload = await request.json()
        logging.info(f"Webhook received: {payload}")

        action = payload.get("action")
        symbol = payload.get("symbol")

        if not action or not symbol:
            logging.error("Missing required field 'action' or 'symbol'")
            return {"error": "Missing required field"}

        # Handle trade actions
        if action == "buy":
            quantity = payload.get("quantity")
            leverage = payload.get("leverage")
            if quantity is None or leverage is None:
                logging.error("Missing 'quantity' or 'leverage' for buy action")
                return {"error": "Missing quantity or leverage"}
            trader.open_long(symbol, quantity, leverage)
            logging.info(f"Executed buy for {symbol}")
        
        elif action == "sell":
            quantity = payload.get("quantity")
            leverage = payload.get("leverage")
            if quantity is None or leverage is None:
                logging.error("Missing 'quantity' or 'leverage' for sell action")
                return {"error": "Missing quantity or leverage"}
            trader.open_short(symbol, quantity, leverage)
            logging.info(f"Executed sell for {symbol}")
        
        elif action == "close_long":
            trader.close_long(symbol)
            logging.info(f"Closed long for {symbol}")
        
        elif action == "close_short":
            trader.close_short(symbol)
            logging.info(f"Closed short for {symbol}")
        
        else:
            logging.error(f"Invalid action: {action}")
            return {"error": "Invalid action"}

        return {"status": "ok"}

    except Exception as e:
        logging.exception(f"Exception while processing webhook: {str(e)}")
        return {"error": str(e)}
