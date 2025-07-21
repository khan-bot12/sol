import json
from fastapi import FastAPI, Request
from pydantic import BaseModel
from bitget_trade import BitgetTrader

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
        print("[INFO] Webhook received:", payload)

        # Validate required fields
        required_fields = {"action", "symbol", "quantity", "leverage"}
        if not required_fields.issubset(payload.keys()):
            print("[ERROR] Missing required field in webhook")
            return {"error": "Missing required field in webhook"}

        action = payload["action"]
        symbol = payload["symbol"]
        quantity = payload["quantity"]
        leverage = payload["leverage"]

        # Handle signals
        if action == "buy":
            trader.open_long(symbol, quantity, leverage)
        elif action == "sell":
            trader.open_short(symbol, quantity, leverage)
        elif action == "close_long":
            trader.close_long(symbol)
        elif action == "close_short":
            trader.close_short(symbol)
        else:
            print(f"[ERROR] Unknown action: {action}")
            return {"error": "Invalid action"}

        return {"status": "ok"}

    except Exception as e:
        print("[ERROR] Exception while processing webhook:", str(e))
        return {"error": str(e)}
