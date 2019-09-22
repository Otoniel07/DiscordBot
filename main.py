import os
import discord
import sqlite3
import config

# Open connection to SQLite DB
db = sqlite3.connect(os.path.join(os.path.dirname(__file__), config.DB_NAME))
db_cursor = db.cursor()
# Create `users` table if it does not exist
db_cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, level INTEGER, exp INTEGER, points INTEGER)''')

client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    # Do nothing if author is self
    if message.author == client.user:
        return
    # Do nothing if author is bot
    if message.author.bot:
        return

    # Fetch user info from database
    db_cursor.execute('SELECT * FROM users WHERE id=?', (str(message.author.id),) )
    query_response = db_cursor.fetchone()
    
    # Add new user to DB if they do not exist
    if not query_response:
        db_cursor.execute('INSERT INTO users VALUES (?,?,?,?)', (str(message.author.id), 1, 0, 0))
        db.commit()
        query_response = (str(message.author.id), 1, 0, 0)
    
    user_id, user_level, user_exp, user_points = query_response

client.run(config.TOKEN)
