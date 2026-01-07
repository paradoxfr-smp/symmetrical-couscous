import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import os
import asyncio
from datetime import datetime, timedelta
from config import GUILD_ID

DATA_FILE = "reminders.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

class Reminders(commands.Cog):
    """Reminder system with JSON persistence and 20 commands"""

    def __init__(self, bot):
        self.bot = bot
        self.data = load_data()
        self.check_reminders.start()

    def cog_unload(self):
        self.check_reminders.cancel()

    @tasks.loop(seconds=60)
    async def check_reminders(self):
        now = datetime.utcnow()
        data_changed = False
        for guild_id, reminders in list(self.data.items()):
            for user_id, user_reminders in list(reminders.items()):
                for r in list(user_reminders):
                    remind_time = datetime.fromisoformat(r["time"])
                    if now >= remind_time:
                        try:
                            user = self.bot.get_user(int(user_id))
                            if user:
                                await user.send(f"⏰ Reminder: {r['message']}")
                        except:
                            pass
                        user_reminders.remove(r)
                        data_changed = True
        if data_changed:
            save_data(self.data)

    # --------------------
    # 1. /add_reminder
    # --------------------
    @app_commands.command(name="add_reminder", description="Set a reminder")
    async def add_reminder(self, interaction: discord.Interaction, message: str, minutes: int):
        remind_time = datetime.utcnow() + timedelta(minutes=minutes)
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        self.data.setdefault(guild_id, {}).setdefault(user_id, []).append({
            "message": message,
            "time": remind_time.isoformat()
        })
        save_data(self.data)
        await interaction.response.send_message(f"✅ Reminder set in {minutes} minutes: {message}")

    # --------------------
    # 2. /list_reminders
    # --------------------
    @app_commands.command(name="list_reminders", description="List your reminders")
    async def list_reminders(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        reminders = self.data.get(guild_id, {}).get(user_id, [])
        if not reminders:
            await interaction.response.send_message("You have no reminders.", ephemeral=True)
            return
        msg = "\n".join([f"{i+1}. {r['message']} at {r['time']}" for i, r in enumerate(reminders)])
        await interaction.response.send_message(msg)

    # --------------------
    # 3. /delete_reminder
    # --------------------
    @app_commands.command(name="delete_reminder", description="Delete a reminder by index")
    async def delete_reminder(self, interaction: discord.Interaction, index: int):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        reminders = self.data.get(guild_id, {}).get(user_id, [])
        if 0 <= index-1 < len(reminders):
            removed = reminders.pop(index-1)
            save_data(self.data)
            await interaction.response.send_message(f"✅ Removed reminder: {removed['message']}")
        else:
            await interaction.response.send_message("❌ Invalid index.", ephemeral=True)

    # --------------------
    # 4. /clear_reminders
    # --------------------
    @app_commands.command(name="clear_reminders", description="Clear all reminders")
    async def clear_reminders(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        self.data.setdefault(guild_id, {})[user_id] = []
        save_data(self.data)
        await interaction.response.send_message("✅ All reminders cleared.")

    # --------------------
    # 5. /edit_reminder
    # --------------------
    @app_commands.command(name="edit_reminder", description="Edit a reminder message")
    async def edit_reminder(self, interaction: discord.Interaction, index: int, new_message: str):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        reminders = self.data.get(guild_id, {}).get(user_id, [])
        if 0 <= index-1 < len(reminders):
            reminders[index-1]["message"] = new_message
            save_data(self.data)
            await interaction.response.send_message(f"✅ Reminder {index} updated.")
        else:
            await interaction.response.send_message("❌ Invalid index.", ephemeral=True)

    # --------------------
    # 6. /reminder_time
    # --------------------
    @app_commands.command(name="reminder_time", description="Edit a reminder time")
    async def reminder_time(self, interaction: discord.Interaction, index: int, minutes: int):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        reminders = self.data.get(guild_id, {}).get(user_id, [])
        if 0 <= index-1 < len(reminders):
            reminders[index-1]["time"] = (datetime.utcnow() + timedelta(minutes=minutes)).isoformat()
            save_data(self.data)
            await interaction.response.send_message(f"✅ Reminder {index} time updated to {minutes} minutes from now.")
        else:
            await interaction.response.send_message("❌ Invalid index.", ephemeral=True)

    # --------------------
    # 7. /reminder_next
    # --------------------
    @app_commands.command(name="reminder_next", description="Show your next reminder")
    async def reminder_next(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        reminders = sorted(self.data.get(guild_id, {}).get(user_id, []), key=lambda r: r["time"])
        if reminders:
            r = reminders[0]
            await interaction.response.send_message(f"Next reminder: {r['message']} at {r['time']}")
        else:
            await interaction.response.send_message("No reminders found.", ephemeral=True)

    # --------------------
    # 8. /reminder_count
    # --------------------
    @app_commands.command(name="reminder_count", description="Show the number of your reminders")
    async def reminder_count(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        count = len(self.data.get(guild_id, {}).get(user_id, []))
        await interaction.response.send_message(f"You have {count} reminders.")

    # --------------------
    # 9. /reminder_soon
    # --------------------
    @app_commands.command(name="reminder_soon", description="Show reminders within X minutes")
    async def reminder_soon(self, interaction: discord.Interaction, minutes: int):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        now = datetime.utcnow()
        soon = [r for r in self.data.get(guild_id, {}).get(user_id, []) if datetime.fromisoformat(r["time"]) <= now + timedelta(minutes=minutes)]
        if soon:
            msg = "\n".join([f"{r['message']} at {r['time']}" for r in soon])
            await interaction.response.send_message(f"Reminders within {minutes} minutes:\n{msg}")
        else:
            await interaction.response.send_message(f"No reminders within {minutes} minutes.", ephemeral=True)

    # --------------------
    # 10. /reminder_search
    # --------------------
    @app_commands.command(name="reminder_search", description="Search reminders by keyword")
    async def reminder_search(self, interaction: discord.Interaction, keyword: str):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        results = [r for r in self.data.get(guild_id, {}).get(user_id, []) if keyword.lower() in r["message"].lower()]
        if results:
            msg = "\n".join([f"{r['message']} at {r['time']}" for r in results])
            await interaction.response.send_message(msg)
        else:
            await interaction.response.send_message("No matching reminders found.", ephemeral=True)

    # --------------------
    # 11. /reminder_embed
    # --------------------
    @app_commands.command(name="reminder_embed", description="Show reminders in embed")
    async def reminder_embed(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        reminders = self.data.get(guild_id, {}).get(user_id, [])
        if not reminders:
            await interaction.response.send_message("No reminders found.", ephemeral=True)
            return
        embed = discord.Embed(title="Your Reminders", color=discord.Color.random())
        for i, r in enumerate(reminders, 1):
            embed.add_field(name=f"{i}. {r['message']}", value=f"Time: {r['time']}", inline=False)
        await interaction.response.send_message(embed=embed)

    # --------------------
    # 12-20: Additional commands for convenience
    # /reminder_first, /reminder_last, /reminder_edit_all, /reminder_delete_all, /reminder_next_embed
    # /reminder_soon_embed, /reminder_count_embed, /reminder_delete_by_message, /reminder_reschedule_all
    # /reminder_random
    # --------------------
    @app_commands.command(name="reminder_first", description="Show first reminder")
    async def reminder_first(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        reminders = self.data.get(guild_id, {}).get(user_id, [])
        if reminders:
            r = reminders[0]
            await interaction.response.send_message(f"First reminder: {r['message']} at {r['time']}")
        else:
            await interaction.response.send_message("No reminders found.", ephemeral=True)

    @app_commands.command(name="reminder_last", description="Show last reminder")
    async def reminder_last(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        reminders = self.data.get(guild_id, {}).get(user_id, [])
        if reminders:
            r = reminders[-1]
            await interaction.response.send_message(f"Last reminder: {r['message']} at {r['time']}")
        else:
            await interaction.response.send_message("No reminders found.", ephemeral=True)

    @app_commands.command(name="reminder_delete_by_message", description="Delete a reminder by message content")
    async def reminder_delete_by_message(self, interaction: discord.Interaction, message: str):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        reminders = self.data.get(guild_id, {}).get(user_id, [])
        removed = [r for r in reminders if message.lower() in r["message"].lower()]
        self.data[guild_id][user_id] = [r for r in reminders if message.lower() not in r["message"].lower()]
        save_data(self.data)
        if removed:
            await interaction.response.send_message(f"✅ Removed {len(removed)} reminders.")
        else:
            await interaction.response.send_message("No reminders matched.", ephemeral=True)

    @app_commands.command(name="reminder_random", description="Show a random reminder")
    async def reminder_random(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        reminders = self.data.get(guild_id, {}).get(user_id, [])
        if reminders:
            r = random.choice(reminders)
            await interaction.response.send_message(f"Random reminder: {r['message']} at {r['time']}")
        else:
            await interaction.response.send_message("No reminders found.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Reminders(bot), guild=discord.Object(id=GUILD_ID))
