import discord
import os
from discord.ext import commands
import bingx_client  # Импортируем твой новый файл с функциями биржи

TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Бот в сети! Ключи BingX подгружены.')

@bot.command()
async def баланс(ctx):
    # Вызываем функцию из второго файла
    data = bingx_client.get_balance()
    
    if data.get("code") == 0:
        # Если биржа ответила успешно, вытаскиваем баланс USDT
        balances = data.get("data", {}).get("balance", {})
        usdt_balance = balances.get("balance", "Не найден")
        await ctx.send(f"💰 Твой баланс на BingX: {usdt_balance} USDT")
    else:
        # Если биржа вернула ошибку (например, неверные ключи)
        error_msg = data.get("msg", "Неизвестная ошибка")
        await ctx.send(f"❌ Ошибка биржи: {error_msg}")

bot.run(TOKEN)
