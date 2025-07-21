# main.py
from fastapi import FastAPI, Request
import uvicorn
import json
from bitget_trade import BitgetTrader
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

trader = BitgetTrader()

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        print("[Webhook Received]", data)

        action = data.get("action")
        symbol = data.get("symbol")
        quantity = data.get("quantity")
        leverage = data.get("leverage", 50)

        if action == "buy":
            trader.close_short(symbol)
            trader.open_long(symbol, quantity, leverage)

        elif action == "sell":
            trader.close_long(symbol)
            trader.open_short(symbol, quantity, leverage)

        elif action == "close_long":
            trader.close_long(symbol)

        elif action == "close_short":
            trader.close_short(symbol)

        else:
            print("[Error] Unknown action:", action)

    except Exception as e:
        print("[Error] exception while processing webhook:", str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
