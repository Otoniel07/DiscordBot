import os
import discord
import datetime
import sqlite3
import config

from discord.ext import commands

bot = commands.Bot(command_prefix='-')

# Open connection to SQLite DB
src_dir = os.path.join(os.path.dirname(__file__))
db = sqlite3.connect(os.path.join(src_dir, config.DB_NAME))
db_cursor = db.cursor()
# Create `users` table if it does not exist
db_cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, level INTEGER, exp INTEGER, points INTEGER)''')
# Create `monthly stats` 
current_month = datetime.date.today().strftime("%B-%Y") # Format current time to Month-Year
db_cursor.execute('''CREATE TABLE IF NOT EXISTS ? (id INTEGER PRIMARY KEY, exp_this_month INTEGER, points_this_month INTEGER)''', (current_month, ))

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    await bot.change_presence(activity=discord.Streaming(name="RichardBotV2", url='https://github.com/richardyang/DiscordBot/'))

@bot.event
async def on_message(message):
    # Do nothing if author is self
    if message.author == bot.user:
        return
    # Do nothing if author is bot
    if message.author.bot:
        return
    
    await bot.process_commands(message)
    await update_user_data(message)
    await update_monthly_data(message)

async def update_monthly_data(message):
    # Fetch user info from database
    current_month = datetime.date.today().strftime("%B-%Y")
    db_cursor.execute('SELECT * FROM ? WHERE id=?', (current_month, str(message.author.id)) )
    query_response = db_cursor.fetchone()
    
    # Add new user to DB if they do not exist
    if not query_response:
        db_cursor.execute('INSERT INTO ? VALUES (?,?,?)', (current_month, str(message.author.id), 0, 0))
        db.commit()
        query_response = (str(message.author.id), 0, 0)
    
    user_id, user_exp, user_points = query_response
    user_exp += config.EXP_PER_MSG
    user_points += config.PTS_PER_MSG

    # Update the DB
    db_cursor.execute('UPDATE ? SET exp_this_month=?, points_this_month=? WHERE id=?', (current_month, user_exp, user_points, str(message.author.id)))
    db.commit()

async def update_user_data(message):
    # Fetch user info from database
    db_cursor.execute('SELECT * FROM users WHERE id=?', (str(message.author.id),) )
    query_response = db_cursor.fetchone()
    
    # Add new user to DB if they do not exist
    if not query_response:
        db_cursor.execute('INSERT INTO users VALUES (?,?,?,?)', (str(message.author.id), 1, 0, 0))
        db.commit()
        query_response = (str(message.author.id), 1, 0, 0)
    
    user_id, user_level, user_exp, user_points = query_response
    user_exp += config.EXP_PER_MSG
    user_points += config.PTS_PER_MSG

    actual_level = int(user_exp ** (0.45))
    if user_level < actual_level:
        user_level = actual_level
        await message.channel.send('{} reached level {}!'.format(message.author.mention, user_level))
    
    # Update the DB
    db_cursor.execute('UPDATE users SET level=?, exp=?, points=? WHERE id=?', (user_level, user_exp, user_points, str(message.author.id)))
    db.commit()


bot.run(config.TOKEN)
