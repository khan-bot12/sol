from fastapi import FastAPI, Request
import uvicorn
import logging
from bitget_trade import BitgetTrader

app = FastAPI()

# === Logging Setup ===
log_file_path = "/root/sol/webhook_logs.log"

logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        logging.info(f"📥 Received webhook data: {data}")

        # Initialize trader with symbol from the alert
        trader = BitgetTrader(symbol=data.get("symbol", "SOLUSDT"))

        action = data.get("action")
        quantity = data.get("quantity")

        if action == "buy":
            logging.info(f"🟢 Processing BUY for {quantity}")
            trader.close_short()
            trader.open_long(quantity)

        elif action == "sell":
            logging.info(f"🔴 Processing SELL for {quantity}")
            trader.close_long()
            trader.open_short(quantity)

        else:
            logging.warning(f"⚠️ Unknown action: {action}")

        return {"status": "success"}

    except Exception as e:
        logging.exception(f"❌ Error processing webhook: {e}")
        return {"status": "error", "message": str(e)}

# Run only if this script is executed directly (for local testing)
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=80)
