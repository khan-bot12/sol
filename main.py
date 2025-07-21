import json
from fastapi import FastAPI, Request
import uvicorn
from bitget_trade import BitgetTrader

app = FastAPI()

trader = BitgetTrader()

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        print("[Webhook] Received:", data)

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

        return {"status": "ok"}

    except Exception as e:
        print("[Error] Exception while processing webhook:", e)
        return {"status": "error", "detail": str(e)}

if __name__ == "__main__":
    print("Starting FastAPI server on port 80...")
    uvicorn.run("main:app", host="0.0.0.0", port=80)
