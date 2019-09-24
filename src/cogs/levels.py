import os
import datetime
import sqlite3
import config

import discord
from discord.ext import commands

class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Open connection to SQLite DB
        # src_dir = os.path.join(os.path.dirname(__file__))
        src_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
        self.db = sqlite3.connect(os.path.join(src_dir, config.DB_NAME))
        self.db_cursor = self.db.cursor()
        # Create `users` table if it does not exist
        self.db_cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, level INTEGER, exp INTEGER, points INTEGER)''')
        # Create `monthly stats` 
        self.current_month = datetime.date.today().strftime("%B_%Y") # Format current time to Month-Year
        self.db_cursor.execute('''CREATE TABLE IF NOT EXISTS {} (id INTEGER PRIMARY KEY, exp_this_month INTEGER, points_this_month INTEGER)'''.format(self.current_month))
            
    @commands.Cog.listener()
    async def on_message(self, message):
        # Do nothing if author is self
        if message.author == self.bot.user:
            return
        # Do nothing if author is bot
        if message.author.bot:
            return

        await self.update_user_data(message)
        await self.update_monthly_data(message)

    async def update_monthly_data(self, message):
        # Fetch user info from database
        current_month = datetime.date.today().strftime("%B_%Y")
        self.db_cursor.execute('SELECT * FROM {} WHERE id=?'.format(current_month), (str(message.author.id), ))
        query_response = self.db_cursor.fetchone()
        
        # Add new user to DB if they do not exist
        if not query_response:
            self.db_cursor.execute('INSERT INTO {} VALUES (?,?,?)'.format(current_month), (str(message.author.id), 0, 0))
            self.db.commit()
            query_response = (str(message.author.id), 0, 0)
        
        user_id, user_exp, user_points = query_response
        user_exp += config.EXP_PER_MSG
        user_points += config.PTS_PER_MSG

        # Update the DB
        self.db_cursor.execute('UPDATE {} SET exp_this_month=?, points_this_month=? WHERE id=?'.format(current_month), (user_exp, user_points, str(message.author.id)))
        self.db.commit()
    
    async def update_user_data(self, message):
        # Fetch user info from database
        self.db_cursor.execute('SELECT * FROM users WHERE id=?', (str(message.author.id),) )
        query_response = self.db_cursor.fetchone()
        
        # Add new user to DB if they do not exist
        if not query_response:
            self.db_cursor.execute('INSERT INTO users VALUES (?,?,?,?)', (str(message.author.id), 1, 0, 0))
            self.db.commit()
            query_response = (str(message.author.id), 1, 0, 0)
        
        user_id, user_level, user_exp, user_points = query_response
        user_exp += config.EXP_PER_MSG
        user_points += config.PTS_PER_MSG

        actual_level = int(user_exp / 100 + 1)
        if user_level < actual_level:
            user_level = actual_level
            await message.channel.send('{} reached level {}!'.format(message.author.mention, user_level))
        
        # Update the DB
        self.db_cursor.execute('UPDATE users SET level=?, exp=?, points=? WHERE id=?', (user_level, user_exp, user_points, str(message.author.id)))
        self.db.commit()

    @commands.command()
    async def leaderboard(self, ctx):
        channel = ctx.message.channel
        print("Sending embed")
        current_month = datetime.date.today().strftime("%B_%Y")
        self.db_cursor.execute('SELECT * FROM {} ORDER BY exp_this_month DESC'.format(current_month))
        query_response = self.db_cursor.fetchmany(5)
        embed = discord.Embed(title="Top 5 exp leaders this month", color=0x0092ff)
        for user_info in query_response:
            user_id, user_exp, user_points = user_info
            embed.add_field(name=self.bot.get_user(user_id).name, value="{} exp gained".format(user_exp), inline=False)
        await channel.send(embed=embed)

def setup(bot):
    bot.add_cog(Levels(bot))