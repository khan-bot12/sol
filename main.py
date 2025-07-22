from fastapi import FastAPI, Request
import uvicorn
import json
from bitget_trade import smart_trade

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        action = data.get("action")
        symbol = data.get("symbol")
        quantity = data.get("quantity")
        leverage = data.get("leverage", 50)

        # Log full payload and values
        with open("/root/sol/webhook_logs.log", "a") as f:
            f.write("\n====== NEW ALERT ======\n")
            f.write(f"Raw data: {json.dumps(data)}\n")
            f.write(f"Action: {action} | Symbol: {symbol} | Quantity: {quantity} | Leverage: {leverage}\n")

        smart_trade(action=action, symbol=symbol, quantity=quantity, leverage=leverage)

        return {"status": "success", "message": "Trade executed"}

    except Exception as e:
        with open("/root/sol/webhook_logs.log", "a") as f:
            f.write(f"[ERROR] {str(e)}\n")
        return {"status": "error", "message": str(e)}

# Optional if testing manually
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
