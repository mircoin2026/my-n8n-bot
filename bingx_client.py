import hmac
import time
import hashlib
import requests
import os
from urllib.parse import urlencode

API_KEY = os.getenv('BINGX_API_KEY')
SECRET_KEY = os.getenv('BINGX_SECRET_KEY')
URL = "https://open-api.bingx.com"

def get_balance():
    path = "/openApi/swap/v2/user/balance"
    
    # 1. Создаем параметры
    params = {
        "timestamp": int(time.time() * 1000),
        "apiKey": API_KEY
    }
    
    # 2. Формируем строку запроса (Query String)
    # urlencode гарантирует, что все символы будут правильными
    query_string = urlencode(params)
    
    # 3. Создаем подпись (HMAC SHA256)
    signature = hmac.new(
        SECRET_KEY.encode('utf-8'), 
        query_string.encode('utf-8'), 
        hashlib.sha256
    ).hexdigest()
    
    # 4. Собираем полный URL
    full_url = f"{URL}{path}?{query_string}&signature={signature}"
    
    # 5. Заголовки (BingX просит передавать ключ здесь)
    headers = {
        "X-BX-APIKEY": API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(full_url, headers=headers)
        return response.json()
    except Exception as e:
        return {"code": -1, "msg": str(e)}

# Эту функцию оставляем для диагностики
def debug_keys():
    api = os.getenv('BINGX_API_KEY', '')
    sec = os.getenv('BINGX_SECRET_KEY', '')
    return f"Ключи в системе: \nAPI: {len(api)} симв. \nSEC: {len(sec)} симв."
