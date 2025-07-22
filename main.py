from fastapi import FastAPI, Request
import uvicorn
import json  # ✅ Correct import
from bitget_trade import smart_trade  # ✅ Your custom trading logic

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()  # ✅ Correct usage
        action = data["action"]
        symbol = data["symbol"]
        quantity = data["quantity"]
        leverage = data.get("leverage", 50)  # Default to 50x if not sent

        # Optional: Log to file (only if you want to tail logs)
        with open("/root/sol/webhook_logs.log", "a") as log_file:
            log_file.write(json.dumps(data) + "\n")

        # Execute the trade
        smart_trade(action=action, symbol=symbol, quantity=quantity, leverage=leverage)

        return {"status": "success", "message": "Trade executed"}
    
    except Exception as e:
        # Log errors too
        with open("/root/sol/webhook_logs.log", "a") as log_file:
            log_file.write(f"Error: {str(e)}\n")

        return {"status": "error", "message": str(e)}

# Entry point if running locally (optional for VPS systemd usage)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
