# === main.py ===
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
        action = data.get("action")
        symbol = data.get("symbol")
        quantity = float(data.get("quantity", 0))
        leverage = int(data.get("leverage", 50))

        if not action or not symbol or not quantity:
            return {"error": "Missing required fields in alert message."}

        # Pass to trader
        result = trader.execute_trade(action, symbol, quantity, leverage)
        return {"message": "Trade executed", "result": result}

    except Exception as e:
        return {"error": f"Error processing webhook: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
