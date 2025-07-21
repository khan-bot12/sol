from fastapi import FastAPI, Request
import uvicorn
from bitget_trade import BitgetTrader

app = FastAPI()
trader = BitgetTrader()

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        print("[INFO] Received webhook data:", data)  # ✅ ADD THIS LINE TO SEE LOGS

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
            print("[ERROR] Unknown action:", action)
            return {"status": "error", "message": "Unknown action"}

        return {"status": "success"}

    except Exception as e:
        print("[ERROR] Exception while processing webhook:", e)
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
