import discord
from discord.ext import commands, tasks
import os
import bingx_client
import asyncio
from datetime import datetime, timedelta

TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Бот-трейдер запущен! Актив: CYS-USDT')
    if not auto_trade_loop.is_running():
        auto_trade_loop.start()

@tasks.loop(seconds=10)  # Проверяем время каждые 10 секунд
async def auto_trade_loop():
    now = datetime.now()
    
    # Проверяем, наступил ли момент: 00, 15, 30 или 45 минут + 2 секунды
    if now.minute in [0, 15, 30, 45] and now.second == 2:
        print(f"--- Сигнал! Время: {now.strftime('%H:%M:%S')} ---")
        
        # 1. Запрашиваем анализ стратегии
        decision, reason = bingx_client.check_strategy()
        print(f"Результат анализа: {decision} ({reason})")
        
        if decision == "BUY":
            # 2. Открываем ордер на 5 USDT
            order_res = bingx_client.open_long_5usd("CYS-USDT")
            
            # Логируем результат в консоль и (по желанию) в Дискорд
            print(f"Ордер отправлен: {order_res}")
            
            # Находим канал, куда бот пришлет отчет (замени на свой ID или удали)
            # channel = bot.get_channel(ID_ТВОЕГО_КАНАЛА)
            # if channel: await channel.send(f"✅ Вход в лонг CYS-USDT! Ответ: {order_res}")
        
        # Чтобы бот не сработал несколько раз в одну и ту же секунду
        await asyncio.sleep(5)

# Запуск бота
bot.run(TOKEN)
