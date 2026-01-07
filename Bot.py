import discord
from discord.ext import commands
import os
from config import GUILD_ID

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents)  # prefix here is ignored for slash commands

@bot.event
async def on_ready():
    guild = discord.Object(id=GUILD_ID)
    await bot.tree.sync(guild=guild)
    print(f"✅ Logged in as {bot.user}")

async def load_cogs():
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            await bot.load_extension(f"cogs.{file[:-3]}")

@bot.event
async def setup_hook():
    await load_cogs()

bot.run("YOUR_BOT_TOKEN")
