from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
import logging
from bitget_trade import smart_trade

# Setup basic logging
logging.basicConfig(
    filename="/root/sol/webhook_logs.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        action = data["action"]
        symbol = data["symbol"]
        quantity = data["quantity"]
        leverage = data.get("leverage", 20)

        logging.info(f"🚀 Webhook received: {data}")
        result = smart_trade(action, symbol, quantity, leverage)
        logging.info(f"✅ Trade result: {result}")

        return JSONResponse(content={"status": "ok", "result": result})

    except Exception as e:
        logging.error(f"❌ Error processing webhook: {e}")
        return JSONResponse(content={"status": "error", "message": str(e)})

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=80)
