from fastapi import FastAPI, Request
from bitget_trade import BitgetTrader
import json  # ✅ Make sure this is at the top level

app = FastAPI()
trader = BitgetTrader()

@app.post("/webhook")
async def webhook(request: Request):
    try:
        payload = await request.body()
        data = json.loads(payload.decode())

        print(f"[Webhook Received] Payload: {data}")

        action = data.get("action")
        symbol = data.get("symbol")
        quantity = data.get("quantity", 15)
        leverage = data.get("leverage", 50)

        if action == "buy":
            trader.close_short(symbol)
            trader.open_long(symbol, quantity, leverage)
            return {"status": "Opened Long"}

        elif action == "sell":
            trader.close_long(symbol)
            trader.open_short(symbol, quantity, leverage)
            return {"status": "Opened Short"}

        elif action == "close_long":
            trader.close_long(symbol)
            return {"status": "Closed Long"}

        elif action == "close_short":
            trader.close_short(symbol)
            return {"status": "Closed Short"}

        else:
            return {"error": "Invalid action"}

    except Exception as e:
        print(f"[Error] Exception while processing webhook: {e}")
        return {"error": str(e)}
