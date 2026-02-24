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

def get_candles(symbol="CYS-USDT"):
    path = "/openApi/swap/v3/quote/klines"
    # Берем 31 свечу: 30 для анализа + 1 текущая (которую отбросим)
    params = {"symbol": symbol, "interval": "15m", "limit": 31}
    try:
        res = requests.get(URL + path, params=params)
        data = res.json()
        if data.get("code") == 0:
            df = pd.DataFrame(data["data"], columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].astype(float)
            return df
    except:
        return None
    return None

def check_strategy():
    df = get_candles()
    if df is None or len(df) < 31: 
        return "WAIT", "Данных меньше 30"
    
    # Отбрасываем текущую незакрытую свечу
    closed_df = df.iloc[:-1].copy() 
    
    # Последняя закрытая свеча для проверки условий
    last_candle = closed_df.iloc[-1]
    
    # Lookback ровно 30 свечей ПЕРЕД последней закрытой
    # (То есть те самые 30 свечей, на основе которых строятся уровни)
    lookback_df = closed_df.iloc[-30:] 
    
    # УРОВНИ L1-L5
    L5 = lookback_df['high'].max()
    L1 = lookback_df['low'].min()
    L3 = (L5 + L1) / 2
    L2 = (L1 + L3) / 2
    L4 = (L5 + L3) / 2
    levels = [L1, L2, L3, L4, L5]

    # EMA 9
    ema_series = ta.ema(closed_df['close'], length=9)
    ema9 = ema_series.iloc[-1]

    # Параметры свечи
    o = last_candle['open']
    c = last_candle['close']
    h = last_candle['high']
    body = abs(c - o)
    upper_wick = h - max(o, c)
    is_green = c > o

    # УСЛОВИЯ (Как в Pine Script)
    is_level_broken = any(o < lvl < c for lvl in levels)
    is_ema_broken = o < ema9 < c
    is_wick_ok = upper_wick <= (body * 0.30)

    if is_green and is_level_broken and is_ema_broken and is_wick_ok and body > 0:
        return "BUY", "Условия выполнены"
    
    return "WAIT", "Нет сигнала"

def open_long_5usd(symbol="CYS-USDT"):
    # Получаем актуальную цену для расчета количества
    df = get_candles(symbol)
    price = df.iloc[-1]['close']
    qty = round(5.0 / price, 0) # Округляем до целого числа монет

    params = {
        "symbol": symbol,
        "side": "BUY",
        "positionSide": "LONG",
        "type": "MARKET",
        "quantity": qty,
        "timestamp": int(time.time() * 1000),
        "apiKey": API_KEY
    }
    
    query_string = urlencode(dict(sorted(params.items())))
    signature = get_signature(query_string)
    headers = {"X-BX-APIKEY": API_KEY}
    
    res = requests.post(f"{URL}/openApi/swap/v2/trade/order?{query_string}&signature={signature}", headers=headers)
    return res.json()
