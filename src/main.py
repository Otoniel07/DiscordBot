import config

import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='-')

@bot.command()
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension}')

@bot.command()
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Richard"))
    
bot.load_extension(f'cogs.levels')
bot.load_extension(f'cogs.fun')
bot.run(config.TOKEN)
