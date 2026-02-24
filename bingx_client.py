import os

def debug_keys():
    api_key = os.getenv('BINGX_API_KEY')
    sec_key = os.getenv('BINGX_SECRET_KEY')
    
    # Проверяем, не пустые ли они
    if not api_key or not sec_key:
        return "❌ Ключи вообще не найдены в настройках хостинга!"
    
    # Проверяем длину (стандартный Secret обычно около 40+ символов)
    # И проверяем на наличие пробелов
    res = f"Ключи найдены! \nДлина API Key: {len(api_key)}\nДлина Secret: {len(sec_key)}"
    if api_key.strip() != api_key or sec_key.strip() != sec_key:
        res += "\n⚠️ ВНИМАНИЕ: В ключах обнаружены лишние пробелы в начале или конце!"
    
    return res
