from fastapi import FastAPI, Request
import uvicorn
from bitget_trade import process_trade
import hmac
import hashlib
import os

app = FastAPI()

# Optional security key from TradingView (if you use a secret)
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")  # leave empty if not using

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()

        # Optional: Validate webhook secret
        if WEBHOOK_SECRET:
            if "secret" not in data or data["secret"] != WEBHOOK_SECRET:
                return {"status": "unauthorized"}

        signal = data.get("signal", "").upper()
        size = float(data.get("size", 15))  # Default size = 15 SOL
        process_trade(signal, size)
        return {"status": "ok", "message": f"{signal} order received"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
