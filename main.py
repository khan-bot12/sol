from fastapi import FastAPI, Request
import uvicorn
import json
from bitget_trade import handle_trade

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        print("✅ Webhook received:", data)

        message = data.get("message") or data.get("alert") or ""
        if "UMLCB" in message:
            handle_trade(message.strip())
            return {"status": "executed"}
        else:
            print("❌ Invalid message format:", message)
            return {"status": "ignored", "reason": "Invalid format"}

    except Exception as e:
        print("❌ Error processing webhook:", e)
        return {"status": "error", "detail": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
