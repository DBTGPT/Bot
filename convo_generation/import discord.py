import discord
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Set up intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

# Create the bot client
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    logging.info(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    # Prevent the bot from replying to itself
    if message.author == client.user:
        return

    logging.info(f'Received message: {message.content} from {message.author}')

    # Respond to "hello" messages
    if message.content.lower().startswith('hello'):
        await message.channel.send('Hello! How can I assist you today?')

# Run the bot with the token from environment variables
token = os.getenv('DISCORD_TOKEN')
client.run(token)
