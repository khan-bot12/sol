from fastapi import FastAPI, Request
from bitget_trade import BitgetTrader
import uvicorn
import json

app = FastAPI()
trader = BitgetTrader()

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        print(f"[Webhook Received] Data: {data}")

        action = data.get("action")
        symbol = data.get("symbol")
        quantity = data.get("quantity")
        leverage = data.get("leverage", 50)

        if not action or not symbol or not quantity:
            print("[Error] Missing required fields in webhook.")
            return {"status": "error", "message": "Missing required fields."}

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
            print(f"[Error] Invalid action: {action}")
            return {"status": "error", "message": "Invalid action."}

        return {"status": "success"}

    except Exception as e:
        print(f"[Exception] Error processing webhook: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
