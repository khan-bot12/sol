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
        print("🔔 [WEBHOOK RECEIVED] Payload:", payload)

        # Validate required fields
        required_fields = {"action", "symbol", "quantity", "leverage"}
        if not required_fields.issubset(payload.keys()):
            print("❌ [ERROR] Missing required field(s) in webhook payload.")
            return {"error": "Missing required field in webhook"}

        action = payload["action"]
        symbol = payload["symbol"]
        quantity = payload["quantity"]
        leverage = payload["leverage"]

        # Handle signals
        if action == "buy":
            print(f"📈 [ACTION] Opening LONG on {symbol} with {quantity} @ {leverage}x")
            trader.open_long(symbol, quantity, leverage)
        elif action == "sell":
            print(f"📉 [ACTION] Opening SHORT on {symbol} with {quantity} @ {leverage}x")
            trader.open_short(symbol, quantity, leverage)
        elif action == "close_long":
            print(f"🔻 [ACTION] Closing LONG on {symbol}")
            trader.close_long(symbol)
        elif action == "close_short":
            print(f"🔺 [ACTION] Closing SHORT on {symbol}")
            trader.close_short(symbol)
        else:
            print(f"❌ [ERROR] Unknown action received: {action}")
            return {"error": "Invalid action"}

        return {"status": "ok"}

    except Exception as e:
        print("❗ [EXCEPTION] Error while processing webhook:", str(e))
        return {"error": str(e)}
