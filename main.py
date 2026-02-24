@bot.command()
async def тест_ключей(ctx):
    info = bingx_client.debug_keys()
    await ctx.send(info)
