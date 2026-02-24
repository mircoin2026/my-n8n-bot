import hmac
import time
import hashlib
import requests
import os

API_KEY = os.getenv('BINGX_API_KEY')
SECRET_KEY = os.getenv('BINGX_SECRET_KEY')
URL = "https://open-api.bingx.com"

def get_balance():
    path = "/openApi/swap/v2/user/balance"
    # Важно: BingX требует строгого порядка и чистоты строк
    timestamp = str(int(time.time() * 1000))
    params_str = f"apiKey={API_KEY}&timestamp={timestamp}"
    
    # Создаем подпись
    signature = hmac.new(
        SECRET_KEY.encode("utf-8"), 
        params_str.encode("utf-8"), 
        hashlib.sha256
    ).hexdigest()
    
    url = f"{URL}{path}?{params_str}&signature={signature}"
    headers = {"X-BX-APIKEY": API_KEY}
    
    response = requests.get(url, headers=headers)
    return response.json()

def check_server_time():
    # Простейший способ проверить связь с биржей без ключей
    path = "/openApi/swap/v2/server/time"
    res = requests.get(f"{URL}{path}")
    return res.json()
