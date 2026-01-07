import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import os
from datetime import datetime, timedelta
from config import GUILD_ID

DATA_FILE = "birthdays.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

class Birthday(commands.Cog):
    """Birthday tracking and announcements"""

    def __init__(self, bot):
        self.bot = bot
        self.data = load_data()
        self.check_birthdays.start()

    def cog_unload(self):
        self.check_birthdays.cancel()

    # --------------------
    # Set birthday
    # --------------------
    @app_commands.command(name="set_birthday", description="Set your birthday (format: YYYY-MM-DD)")
    async def set_birthday(self, interaction: discord.Interaction, date: str):
        try:
            birthday = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            await interaction.response.send_message("❌ Invalid format! Use YYYY-MM-DD.", ephemeral=True)
            return

        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        self.data.setdefault(guild_id, {})[user_id] = date
        save_data(self.data)
        await interaction.response.send_message(f"🎉 Birthday set to {date} for {interaction.user.mention}!")

    # --------------------
    # View your birthday
    # --------------------
    @app_commands.command(name="my_birthday", description="View your birthday")
    async def my_birthday(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        birthday = self.data.get(guild_id, {}).get(user_id)
        if birthday:
            await interaction.response.send_message(f"🎂 Your birthday is on {birthday}.")
        else:
            await interaction.response.send_message("❌ You haven't set your birthday yet.", ephemeral=True)

    # --------------------
    # View all birthdays
    # --------------------
    @app_commands.command(name="birthdays", description="View all birthdays in this server")
    async def birthdays(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        guild_data = self.data.get(guild_id, {})
        if not guild_data:
            await interaction.response.send_message("No birthdays set in this server.")
            return

        embed = discord.Embed(title="🎉 Birthdays", color=discord.Color.blurple())
        for user_id, date in guild_data.items():
            member = interaction.guild.get_member(int(user_id))
            if member:
                embed.add_field(name=member.display_name, value=date, inline=False)

        await interaction.response.send_message(embed=embed)

    # --------------------
    # Birthday announcements
    # --------------------
    @tasks.loop(minutes=60)
    async def check_birthdays(self):
        now = datetime.utcnow()
        for guild in self.bot.guilds:
            guild_id = str(guild.id)
            for user_id, date_str in self.data.get(guild_id, {}).items():
                member = guild.get_member(int(user_id))
                if not member:
                    continue
                birthday = datetime.strptime(date_str, "%Y-%m-%d")
                # Check if birthday is today (month & day)
                if birthday.month == now.month and birthday.day == now.day:
                    channel = discord.utils.get(guild.text_channels, permissions__send_messages=True)
                    if channel:
                        await channel.send(f"🎉 Happy Birthday {member.mention}! 🎂")

    @check_birthdays.before_loop
    async def before_check_birthdays(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Birthday(bot), guild=discord.Object(id=GUILD_ID))
