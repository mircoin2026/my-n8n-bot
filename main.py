import discord
import os
from discord.ext import commands

# 1. Получаем токен из переменных окружения Ботхоста
TOKEN = os.getenv('DISCORD_TOKEN')

# 2. Настраиваем права бота
intents = discord.Intents.default()
intents.message_content = True

# 3. Создаем самого бота (вот здесь рождается имя 'bot')
bot = commands.Bot(command_prefix='!', intents=intents)

# 4. Проверка запуска в консоли
@bot.event
async def on_ready():
    print(f'Успех! Бот запущен как {bot.user}')

# 5. Простая команда для проверки связи
@bot.command()
async def привет(ctx):
    await ctx.send('Привет! Я тебя слышу!')

# 6. Запуск (эта строка всегда должна быть В САМОМ КОНЦЕ)
bot.run(TOKEN)
