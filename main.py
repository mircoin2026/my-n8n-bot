import discord
from discord.ext import commands, tasks
import os
import hmac
import time
import hashlib
import requests
import pandas as pd
import pandas_ta as ta
import asyncio
from datetime import datetime
from urllib.parse import urlencode

# --- НАСТРОЙКИ ---
TOKEN = os.getenv('DISCORD_TOKEN')
API_KEY = os.getenv('BINGX_API_KEY')
SECRET_KEY = os.getenv('BINGX_SECRET_KEY')
URL = "https://open-api.bingx.com"
SYMBOL = "CYS-USDT"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

# --- ФУНКЦИИ BINGX ---
def get_signature(query_string):
    return hmac.new(SECRET_KEY.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

def get_candles():
    path = "/openApi/swap/v3/quote/klines"
    params = {"symbol": SYMBOL, "interval": "15m", "limit": 31}
    try:
        res = requests.get(URL + path, params=params)
        data = res.json()
        if data.get("code") == 0:
            df = pd.DataFrame(data["data"], columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].astype(float)
            return df
    except: return None
    return None

def open_long_5usd():
    df = get_candles()
    if df is None: return "Ошибка получения цены"
    price = df.iloc[-1]['close']
    qty = round(5.0 / price, 0)
    
    params = {
        "symbol": SYMBOL, "side": "BUY", "positionSide": "LONG",
        "type": "MARKET", "quantity": qty,
        "timestamp": int(time.time() * 1000), "apiKey": API_KEY
    }
    query_string = urlencode(dict(sorted(params.items())))
    signature = get_signature(query_string)
    headers = {"X-BX-APIKEY": API_KEY}
    res = requests.post(f"{URL}/openApi/swap/v2/trade/order?{query_string}&signature={signature}", headers=headers)
    return res.json()

# --- СТРАТЕГИЯ (ТВОЯ, БЕЗ ИЗМЕНЕНИЙ) ---
def check_strategy():
    df = get_candles()
    if df is None or len(df) < 31: return False, "Мало данных"
    
    closed_df = df.iloc[:-1].copy()
    last_candle = closed_df.iloc[-1]
    lookback_df = closed_df.iloc[-30:] # Твои 30 свечей
    
    L5 = lookback_df['high'].max()
    L1 = lookback_df['low'].min()
    L3 = (L5 + L1) / 2
    L2 = (L1 + L3) / 2
    L4 = (L5 + L3) / 2
    levels = [L1, L2, L3, L4, L5]

    ema9 = ta.ema(closed_df['close'], length=9).iloc[-1]

    o, c, h = last_candle['open'], last_candle['close'], last_candle['high']
    body = abs(c - o)
    upper_wick = h - max(o, c)
    
    is_green = c > o
    level_broken = any(o < lvl < c for lvl in levels)
    ema_broken = o < ema9 < c
    wick_ok = upper_wick <= (body * 0.30)

    if is_green and level_broken and ema_broken and wick_ok and body > 0:
        return True, "СИГНАЛ НА ПОКУПКУ"
    return False, "Нет условий"

# --- ЦИКЛ РАБОТЫ ---
@tasks.loop(seconds=1) # Проверяем каждую секунду, чтобы не пропустить 02 сек
async def main_loop():
    now = datetime.now()
    
    # Срабатывает ровно в 00, 15, 30, 45 минут и 2 секунды
    if now.minute in [0, 15, 30, 45] and now.second == 2:
        print(f"--- АНАЛИЗ СВЕЧИ {now.strftime('%H:%M:%S')} ---")
        signal, reason = check_strategy()
        print(f"Результат: {reason}")
        
        if signal:
            res = open_long_5usd()
            print(f"Ордер: {res}")
        
        await asyncio.sleep(2) # Пауза, чтобы не сработало дважды в одну секунду

@bot.event
async def on_ready():
    print("================================")
    print(f"БОТ ЗАПУЩЕН! СЛЕДИТ ЗА {SYMBOL}")
    print("================================")
    if not main_loop.is_running():
        main_loop.start()

bot.run(TOKEN)
