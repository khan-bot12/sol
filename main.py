# main.py
import json
from fastapi import FastAPI, Request
from bitget_trade import BitgetTrader
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
trader = BitgetTrader()

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        print("[Webhook Received]:", data)

        action = data.get("action")
        symbol = data.get("symbol")
        quantity = data.get("quantity")
        leverage = data.get("leverage")

        if not all([action, symbol, quantity, leverage]):
            print("[Error] Missing required field in webhook")
            return {"status": "error", "message": "Missing required fields"}

        if action == "buy":
            trader.open_long(symbol, quantity, leverage)
        elif action == "sell":
            trader.open_short(symbol, quantity, leverage)
        elif action == "close_long":
            trader.close_long(symbol)
        elif action == "close_short":
            trader.close_short(symbol)
        else:
            print("[Error] Unknown action")
            return {"status": "error", "message": "Unknown action"}

        return {"status": "success"}

    except Exception as e:
        print(f"[Error] Exception while processing webhook: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
