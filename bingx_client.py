import hmac
import time
import hashlib
import requests
import os

# Берем ключи из настроек хостинга
API_KEY = os.getenv('BINGX_API_KEY')
SECRET_KEY = os.getenv('BINGX_SECRET_KEY')
URL = "https://open-api.bingx.com"

def get_sign(payload):
    return hmac.new(SECRET_KEY.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()

def get_balance():
    path = "/openApi/swap/v2/user/balance"
    params = {
        "timestamp": int(time.time() * 1000),
        # API-ключ теперь не в params, а в заголовках ниже
    }
    
    # 1. Формируем строку параметров
    params_str = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
    
    # 2. Создаем подпись
    signature = get_sign(params_str)
    
    # 3. Добавляем ТЕ САМЫЕ ЗАГОЛОВКИ, которые просит биржа
    headers = {
        "X-BX-APIKEY": API_KEY,
        "Content-Type": "application/json"
    }
    
    # 4. Собираем полный URL
    full_url = f"{URL}{path}?{params_str}&signature={signature}"
    
    # 5. Делаем запрос с заголовками
    response = requests.get(full_url, headers=headers)
    return response.json()
