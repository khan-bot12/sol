from fastapi import FastAPI, Request
import uvicorn
from bitget_trade import smart_trade

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        action = data["action"].lower()
        symbol = data["symbol"]
        quantity = float(data["quantity"])
        leverage = int(data.get("leverage", 50))

        print(f"==== NEW ALERT ==== \nRaw data: {data}")

        if action in ["buy", "sell", "close_long", "close_short"]:
            result = smart_trade(action, symbol, quantity, leverage)
            return {"status": "success", "detail": result}
        else:
            error_msg = f"invalid action received: {action}"
            print(f"[Error] {error_msg}")
            return {"status": "error", "detail": error_msg}
    except Exception as e:
        print(f"[Exception] {e}")
        return {"status": "error", "detail": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
