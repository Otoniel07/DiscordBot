import os
import discord
from discord.ext import commands

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.src_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
    
    @commands.command()
    async def billy(self, ctx):
        print("Press F for Billy")
        channel = ctx.message.channel
        file = discord.File(os.path.join(self.src_dir, 'cache/billy.gif'))
        msg = await channel.send("Press F to pay respects", file=file)
        await msg.add_reaction(emoji="🇫")

def setup(bot):
    bot.add_cog(Fun(bot))