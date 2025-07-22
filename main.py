from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from bitget_trade import BitgetTrader
import uvicorn
import logging
import json

app = FastAPI()

# Setup logging
logging.basicConfig(filename="/root/sol/webhook_logs.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        logging.info(f"Received alert: {json.dumps(data)}")

        # Validate required fields
        symbol = data.get("symbol")
        action = data.get("action")
        quantity = data.get("quantity")

        if not symbol or not action or not quantity:
            error_msg = "Missing required field in webhook (symbol, action, quantity)"
            logging.error(error_msg)
            return JSONResponse(content={"error": error_msg}, status_code=400)

        trader = BitgetTrader(symbol)
        result = trader.execute_trade(action, float(quantity))

        return JSONResponse(content={"message": "Trade executed", "result": result})

    except Exception as e:
        logging.exception("Exception in webhook")
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=80)
