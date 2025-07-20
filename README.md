# sol

# Sol Auto Scalping Bot

Automated SOLUSDT futures trading bot using Bitget and FastAPI.

## Setup
1. Clone the repo
2. Create a `.env` file with API credentials
3. Run the bot using `uvicorn main:app --host 0.0.0.0 --port 80`

## Webhook Alert Format
Send alerts from TradingView as:
```json
{"signal": "BUY", "size": 15}
