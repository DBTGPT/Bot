import discord
import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get environment variables
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

# Set intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

# Create bot instance
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    logger.info(f'{bot.user} has connected to Discord!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('!hello'):
        await message.channel.send('Hello!')

    logger.info(f'Message from {message.author}: {message.content}')

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
