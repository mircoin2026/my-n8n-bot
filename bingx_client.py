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
    
    # BingX V2 требует только timestamp в параметрах для баланса
    params = {
        "timestamp": int(time.time() * 1000)
    }
    
    # 1. Склеиваем параметры в строку: "timestamp=12345678"
    query_string = f"timestamp={params['timestamp']}"
    
    # 2. Создаем подпись ТАК, как просит документация V2
    signature = hmac.new(
        SECRET_KEY.encode('utf-8'), 
        query_string.encode('utf-8'), 
        hashlib.sha256
    ).hexdigest()
    
    # 3. Собираем финальный URL
    full_url = f"{URL}{path}?{query_string}&signature={signature}"
    
    # 4. Ключ передаем ТОЛЬКО в заголовке
    headers = {
        "X-BX-APIKEY": API_KEY
    }
    
    try:
        response = requests.get(full_url, headers=headers)
        return response.json()
    except Exception as e:
        return {"code": -1, "msg": str(e)}

def debug_keys():
    # Проверка на наличие пустых строк или пробелов, которые мы не видим
    api = os.getenv('BINGX_API_KEY', '')
    sec = os.getenv('BINGX_SECRET_KEY', '')
    return f"Статус ключей:\nAPI: {len(api)} симв.\nSEC: {len(sec)} симв."
