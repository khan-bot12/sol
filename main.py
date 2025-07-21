from fastapi import FastAPI, Request
import uvicorn
import json
from bitget_trade import BitgetTrader

app = FastAPI()
trader = BitgetTrader()

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.body()
        print("Webhook data received:", data)

        payload = json.loads(data)
        print("Parsed JSON:", payload)

        action = payload.get("action")
        symbol = payload.get("symbol")
        quantity = payload.get("quantity")
        leverage = payload.get("leverage", 50)

        if not action or not symbol or not quantity:
            return {"error": "Missing required fields"}

        print(f"Processing signal → Action: {action}, Symbol: {symbol}, Qty: {quantity}, Leverage: {leverage}")

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
            return {"error": "Unknown action type"}

        return {"status": "Order processed successfully"}

    except json.JSONDecodeError as je:
        print("[JSON ERROR] Could not decode payload:", je)
        return {"error": "Invalid JSON format"}
    except Exception as e:
        print("[Error] Exception while processing webhook:", e)
        return {"error": str(e)}
