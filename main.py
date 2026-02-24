import discord
import os
from discord.ext import commands
import bingx_client  # Убедись, что этот файл есть в репозитории!

# 1. Загрузка токена
TOKEN = os.getenv('DISCORD_TOKEN')

# 2. Настройка бота
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Бот ожил! Зашел как {bot.user}')

# Команда №1: Проверка связи
@bot.command()
async def привет(ctx):
    await ctx.send('Привет! Я на связи и готов к работе.')

# Команда №2: Проверка баланса
@bot.command()
async def баланс(ctx):
    res = bingx_client.get_balance()
    if res.get("code") == 0:
        data = res.get("data", {}).get("balance", {})
        val = data.get("balance", "0")
        await ctx.send(f"💰 Баланс: **{val} USDT**")
    else:
        await ctx.send(f"❌ Ошибка: {res.get('msg')}")

# Команда №3: Та самая диагностика ключей
@bot.command()
async def тест_ключей(ctx):
    info = bingx_client.debug_keys()
    await ctx.send(info)

# 3. Запуск
bot.run(TOKEN)
