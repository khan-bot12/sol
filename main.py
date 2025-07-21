from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from bitget_trade import BitgetTrader
import uvicorn
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
trader = BitgetTrader()

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        print(f"[INFO] Received webhook data: {data}")
    except Exception as e:
        print(f"[ERROR] Failed to parse JSON: {e}")
        return JSONResponse(content={"error": "Invalid JSON"}, status_code=400)

    action = data.get("action")
    symbol = data.get("symbol")
    quantity = data.get("quantity")
    leverage = data.get("leverage", 50)  # default to 50 if not provided

    if not action or not symbol or not quantity:
        print(f"[ERROR] Missing required field in webhook: {data}")
        return JSONResponse(content={"error": "Missing required field"}, status_code=400)

    try:
        if action == "buy":
            print("[ACTION] Executing LONG")
            trader.open_long(symbol, quantity, leverage)
        elif action == "sell":
            print("[ACTION] Executing SHORT")
            trader.open_short(symbol, quantity, leverage)
        elif action == "close_long":
            print("[ACTION] Closing LONG")
            trader.close_long(symbol)
        elif action == "close_short":
            print("[ACTION] Closing SHORT")
            trader.close_short(symbol)
        else:
            print(f"[ERROR] Unknown action: {action}")
            return JSONResponse(content={"error": "Unknown action"}, status_code=400)

        return JSONResponse(content={"status": "success"}, status_code=200)

    except Exception as e:
        print(f"[ERROR] Exception while processing webhook: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=80)
