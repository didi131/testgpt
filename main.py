import ccxt
import time
from datetime import datetime
from telegram import Bot
from keep_alive import keep_alive

telegram_token = "TON_TOKEN"
chat_id = "TON_CHAT_ID"
symbol = 'SOL/USDC'
amount_usdc = 10
buy_threshold = -0.5
sell_target = 1.0
interval = 300
holding = False
buy_price = None

api_key = "TA_CLE"
api_secret = "TON_SECRET"
api_passphrase = "TA_PASSPHRASE"

exchange = ccxt.kucoin({
    'apiKey': api_key,
    'secret': api_secret,
    'password': api_passphrase,
    'enableRateLimit': True
})

bot = Bot(token=telegram_token)
keep_alive()
bot.send_message(chat_id=chat_id, text="🚀 Bot actif sur KuCoin SOL/USDC")

while True:
    try:
        candles = exchange.fetch_ohlcv(symbol, '1m', limit=30)
        close_prices = [c[4] for c in candles]
        current_price = close_prices[-1]
        old_price = close_prices[0]
        change_percent = ((current_price - old_price) / old_price) * 100
        now = datetime.now().strftime('%H:%M:%S')

        bot.send_message(chat_id=chat_id, text=f"📊 [{now}] SOL = {current_price:.2f} | Δ30min = {change_percent:.2f}%")

        if not holding and change_percent <= buy_threshold:
            amount_sol = round(amount_usdc / current_price, 3)
            order = exchange.create_market_buy_order(symbol, amount_sol)
            buy_price = current_price
            holding = True
            bot.send_message(chat_id=chat_id, text=f"🟢 ACHAT à {buy_price:.2f} USDC ({amount_sol} SOL)")

        elif holding and ((current_price - buy_price) / buy_price) * 100 >= sell_target:
            amount_sol = round(amount_usdc / buy_price, 3)
            order = exchange.create_market_sell_order(symbol, amount_sol)
            gain = ((current_price - buy_price) / buy_price) * 100
            bot.send_message(chat_id=chat_id, text=f"🔴 VENTE à {current_price:.2f} | Gain ≈ {gain:.2f}%")
            holding = False
            buy_price = None

        time.sleep(interval)

    except Exception as e:
        bot.send_message(chat_id=chat_id, text=f"⚠️ Erreur : {type(e).__name__} - {str(e)}")
        time.sleep(60)
