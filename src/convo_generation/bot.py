import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import openai

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OAI_ENDPOINT = os.getenv('OAI_ENDPOINT')
MODEL_DEPLOYMENT = os.getenv('MODEL_DEPLOYMENT')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

openai.api_key = OPENAI_API_KEY
openai.api_base = f"https://{OAI_ENDPOINT}.openai.azure.com/"
openai.api_version = '2023-05-15'

@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user}')

@bot.command(name='chat')
async def chat(ctx, *, message: str):
    response = openai.Completion.create(
        engine=MODEL_DEPLOYMENT,
        prompt=message,
        max_tokens=150
    )
    await ctx.send(response.choices[0].text.strip())

bot.run(DISCORD_TOKEN)
