import json
from fastapi import FastAPI, Request
from bitget_trade import BitgetTrader
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BITGET_API_KEY")
API_SECRET = os.getenv("BITGET_API_SECRET")
API_PASSPHRASE = os.getenv("BITGET_PASSPHRASE")

trader = BitgetTrader(API_KEY, API_SECRET, API_PASSPHRASE)

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        print(f"[INFO] Webhook received: {data}")

        # Required fields
        action = data.get("action")
        symbol = data.get("symbol")
        quantity = data.get("quantity")
        leverage = data.get("leverage")  # Optional for close actions

        if not action or not symbol or not quantity:
            print("[ERROR] Missing required field in webhook")
            return {"status": "error", "message": "Missing required field"}

        if action == "buy":
            trader.set_leverage(symbol, leverage)
            trader.close_short(symbol)
            trader.open_long(symbol, quantity)

        elif action == "sell":
            trader.set_leverage(symbol, leverage)
            trader.close_long(symbol)
            trader.open_short(symbol, quantity)

        elif action == "close_long":
            trader.close_long(symbol)

        elif action == "close_short":
            trader.close_short(symbol)

        else:
            print(f"[ERROR] Unknown action: {action}")
            return {"status": "error", "message": f"Unknown action: {action}"}

        return {"status": "success"}

    except Exception as e:
        print(f"[ERROR] Exception while processing webhook: {str(e)}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
