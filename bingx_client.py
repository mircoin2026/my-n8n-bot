import hmac
import time
import hashlib
import requests
import os
import pandas as pd
import pandas_ta as ta
from urllib.parse import urlencode

API_KEY = os.getenv('BINGX_API_KEY')
SECRET_KEY = os.getenv('BINGX_SECRET_KEY')
URL = "https://open-api.bingx.com"

def get_signature(query_string):
    return hmac.new(SECRET_KEY.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

# 1. Получение свечей (15м)
def get_candles(symbol="CYS-USDT", limit=50):
    path = "/openApi/swap/v3/quote/klines"
    params = {"symbol": symbol, "interval": "15m", "limit": limit}
    res = requests.get(URL + path, params=params)
    data = res.json()
    if data.get("code") == 0:
        df = pd.DataFrame(data["data"], columns=['time', 'open', 'high', 'low', 'close', 'volume'])
        df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].astype(float)
        return df
    return None

# 2. Открытие сделки (Market Long)
def place_market_order(symbol, side, amount):
    path = "/openApi/swap/v2/trade/order"
    timestamp = int(time.time() * 1000)
    params = {
        "symbol": symbol,
        "side": side,          # "BUY" для Long
        "positionSide": "LONG",
        "type": "MARKET",
        "quantity": amount,    # Кол-во монет (нужно будет рассчитать от 5$)
        "timestamp": timestamp,
        "apiKey": API_KEY
    }
    query_string = urlencode(dict(sorted(params.items())))
    signature = get_signature(query_string)
    url = f"{URL}{path}?{query_string}&signature={signature}"
    headers = {"X-BX-APIKEY": API_KEY}
    res = requests.post(url, headers=headers)
    return res.json()

# 3. Сама стратегия (Логика из Pine Script)
def check_strategy():
    df = get_candles()
    if df is None or len(df) < 31: return "Ошибка данных"
    
    # Берем данные (убираем текущую незаконченную свечу)
    closed_df = df.iloc[:-1].copy()
    last_candle = closed_df.iloc[-1]
    prev_candles = closed_df.iloc[-31:-1] # Lookback 30

    # Расчет уровней L1-L5
    l5 = prev_candles['high'].max()
    l1 = prev_candles['low'].min()
    l3 = (l5 + l1) / 2
    l2 = (l1 + l3) / 2
    l4 = (l5 + l3) / 2
    levels = [l1, l2, l3, l4, l5]

    # EMA 9
    ema9 = ta.ema(closed_df['close'], length=9).iloc[-1]

    # Параметры свечи
    c_open = last_candle['open']
    c_close = last_candle['close']
    c_high = last_candle['high']
    body = abs(c_close - c_open)
    upper_wick = c_high - max(c_open, c_close)
    is_green = c_close > c_open

    # Условия
    is_level_broken = any(c_open < lvl < c_close for lvl in levels)
    ema_broken = c_open < ema9 < c_close
    wick_ok = upper_wick <= (body * 0.30)

    if is_green and is_level_broken and ema_broken and wick_ok and body > 0:
        return "BUY"
    return "WAIT"
