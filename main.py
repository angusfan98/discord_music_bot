import discord
from discord.ext import commands
import music
from dotenv import load_dotenv
import os

load_dotenv()

cogs = [music]

API_KEY = os.getenv("API_KEY")

client = commands.Bot(command_prefix='?', intents = discord.Intents.all())

@client.event
async def on_ready():
  print(":)")

for i in range(len(cogs)):
  cogs[i].setup(client)
  
client.run(API_KEY)

