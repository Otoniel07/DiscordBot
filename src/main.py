import os
import discord
import datetime
import sqlite3


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
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="RichardBotV2"))
    
bot.load_extension(f'cogs.levels')
bot.run('NjE5NjcwMjA0NTA2NzAxODI5.XXLnDQ.uTTPbzdTICaJLT9GWFIik1i8IcQ')
