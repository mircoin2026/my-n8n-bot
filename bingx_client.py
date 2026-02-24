import hmac
import time
import hashlib
import requests
import os

API_KEY = os.getenv('BINGX_API_KEY')
SECRET_KEY = os.getenv('BINGX_SECRET_KEY')
URL = "https://open-api.bingx.com"

def get_sign(payload):
    return hmac.new(SECRET_KEY.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()

def get_balance():
    path = "/openApi/swap/v2/user/balance"
    method = "GET"
    params = {
        "timestamp": int(time.time() * 1000),
        "apiKey": API_KEY,
    }
    
    # Формируем строку запроса
    params_str = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
    signature = get_sign(params_str)
    full_url = f"{URL}{path}?{params_str}&signature={signature}"
    
    response = requests.get(full_url)
    return response.json()
