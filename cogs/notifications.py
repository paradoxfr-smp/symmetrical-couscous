import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import os
from datetime import datetime, timedelta
import asyncio
from config import GUILD_ID

DATA_FILE = "notifications.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

class Notifications(commands.Cog):
    """Notification system with JSON persistence"""

    def __init__(self, bot):
        self.bot = bot
        self.data = load_data()
        self.check_notifications.start()

    def cog_unload(self):
        self.check_notifications.cancel()

    @tasks.loop(seconds=60)
    async def check_notifications(self):
        now = datetime.utcnow()
        changed = False
        for guild_id, users in list(self.data.items()):
            for user_id, notes in list(users.items()):
                for note in list(notes):
                    notify_time = datetime.fromisoformat(note["time"])
                    if now >= notify_time:
                        try:
                            user = self.bot.get_user(int(user_id))
                            if user:
                                await user.send(f"🔔 Notification: {note['message']}")
                        except:
                            pass
                        notes.remove(note)
                        changed = True
        if changed:
            save_data(self.data)

    # --------------------
    # 1. /notify_add
    # --------------------
    @app_commands.command(name="notify_add", description="Add a notification")
    async def notify_add(self, interaction: discord.Interaction, message: str, minutes: int):
        notify_time = datetime.utcnow() + timedelta(minutes=minutes)
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        self.data.setdefault(guild_id, {}).setdefault(user_id, []).append({
            "message": message,
            "time": notify_time.isoformat()
        })
        save_data(self.data)
        await interaction.response.send_message(f"✅ Notification set in {minutes} minutes: {message}")

    # --------------------
    # 2. /notify_list
    # --------------------
    @app_commands.command(name="notify_list", description="List your notifications")
    async def notify_list(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        notes = self.data.get(guild_id, {}).get(user_id, [])
        if not notes:
            await interaction.response.send_message("You have no notifications.", ephemeral=True)
            return
        msg = "\n".join([f"{i+1}. {n['message']} at {n['time']}" for i, n in enumerate(notes)])
        await interaction.response.send_message(msg)

    # --------------------
    # 3. /notify_delete
    # --------------------
    @app_commands.command(name="notify_delete", description="Delete a notification by index")
    async def notify_delete(self, interaction: discord.Interaction, index: int):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        notes = self.data.get(guild_id, {}).get(user_id, [])
        if 0 <= index-1 < len(notes):
            removed = notes.pop(index-1)
            save_data(self.data)
            await interaction.response.send_message(f"✅ Removed notification: {removed['message']}")
        else:
            await interaction.response.send_message("❌ Invalid index.", ephemeral=True)

    # --------------------
    # 4. /notify_clear
    # --------------------
    @app_commands.command(name="notify_clear", description="Clear all notifications")
    async def notify_clear(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        self.data.setdefault(guild_id, {})[user_id] = []
        save_data(self.data)
        await interaction.response.send_message("✅ All notifications cleared.")

    # --------------------
    # 5. /notify_edit
    # --------------------
    @app_commands.command(name="notify_edit", description="Edit a notification message")
    async def notify_edit(self, interaction: discord.Interaction, index: int, new_message: str):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        notes = self.data.get(guild_id, {}).get(user_id, [])
        if 0 <= index-1 < len(notes):
            notes[index-1]["message"] = new_message
            save_data(self.data)
            await interaction.response.send_message(f"✅ Notification {index} updated.")
        else:
            await interaction.response.send_message("❌ Invalid index.", ephemeral=True)

    # --------------------
    # 6. /notify_time
    # --------------------
    @app_commands.command(name="notify_time", description="Edit notification time")
    async def notify_time(self, interaction: discord.Interaction, index: int, minutes: int):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        notes = self.data.get(guild_id, {}).get(user_id, [])
        if 0 <= index-1 < len(notes):
            notes[index-1]["time"] = (datetime.utcnow() + timedelta(minutes=minutes)).isoformat()
            save_data(self.data)
            await interaction.response.send_message(f"✅ Notification {index} rescheduled to {minutes} minutes from now.")
        else:
            await interaction.response.send_message("❌ Invalid index.", ephemeral=True)

    # --------------------
    # 7. /notify_next
    # --------------------
    @app_commands.command(name="notify_next", description="Show your next notification")
    async def notify_next(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        notes = sorted(self.data.get(guild_id, {}).get(user_id, []), key=lambda n: n["time"])
        if notes:
            n = notes[0]
            await interaction.response.send_message(f"Next notification: {n['message']} at {n['time']}")
        else:
            await interaction.response.send_message("No notifications found.", ephemeral=True)

    # --------------------
    # 8. /notify_count
    # --------------------
    @app_commands.command(name="notify_count", description="Show number of notifications")
    async def notify_count(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        count = len(self.data.get(guild_id, {}).get(user_id, []))
        await interaction.response.send_message(f"You have {count} notifications.")

    # --------------------
    # 9. /notify_soon
    # --------------------
    @app_commands.command(name="notify_soon", description="Show notifications within X minutes")
    async def notify_soon(self, interaction: discord.Interaction, minutes: int):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        now = datetime.utcnow()
        soon = [n for n in self.data.get(guild_id, {}).get(user_id, []) if datetime.fromisoformat(n["time"]) <= now + timedelta(minutes=minutes)]
        if soon:
            msg = "\n".join([f"{n['message']} at {n['time']}" for n in soon])
            await interaction.response.send_message(f"Notifications within {minutes} minutes:\n{msg}")
        else:
            await interaction.response.send_message(f"No notifications within {minutes} minutes.", ephemeral=True)

    # --------------------
    # 10. /notify_search
    # --------------------
    @app_commands.command(name="notify_search", description="Search notifications by keyword")
    async def notify_search(self, interaction: discord.Interaction, keyword: str):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        results = [n for n in self.data.get(guild_id, {}).get(user_id, []) if keyword.lower() in n["message"].lower()]
        if results:
            msg = "\n".join([f"{n['message']} at {n['time']}" for n in results])
            await interaction.response.send_message(msg)
        else:
            await interaction.response.send_message("No matching notifications found.", ephemeral=True)

    # --------------------
    # 11. /notify_embed
    # --------------------
    @app_commands.command(name="notify_embed", description="Show notifications in an embed")
    async def notify_embed(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        notes = self.data.get(guild_id, {}).get(user_id, [])
        if not notes:
            await interaction.response.send_message("No notifications found.", ephemeral=True)
            return
        embed = discord.Embed(title="Your Notifications", color=discord.Color.random())
        for i, n in enumerate(notes, 1):
            embed.add_field(name=f"{i}. {n['message']}", value=f"Time: {n['time']}", inline=False)
        await interaction.response.send_message(embed=embed)

    # --------------------
    # 12-20: Additional convenience commands
    # --------------------
    @app_commands.command(name="notify_first", description="Show first notification")
    async def notify_first(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        notes = self.data.get(guild_id, {}).get(user_id, [])
        if notes:
            n = notes[0]
            await interaction.response.send_message(f"First notification: {n['message']} at {n['time']}")
        else:
            await interaction.response.send_message("No notifications found.", ephemeral=True)

    @app_commands.command(name="notify_last", description="Show last notification")
    async def notify_last(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        notes = self.data.get(guild_id, {}).get(user_id, [])
        if notes:
            n = notes[-1]
            await interaction.response.send_message(f"Last notification: {n['message']} at {n['time']}")
        else:
            await interaction.response.send_message("No notifications found.", ephemeral=True)

    @app_commands.command(name="notify_delete_by_message", description="Delete notifications by message")
    async def notify_delete_by_message(self, interaction: discord.Interaction, message: str):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        notes = self.data.get(guild_id, {}).get(user_id, [])
        removed = [n for n in notes if message.lower() in n["message"].lower()]
        self.data[guild_id][user_id] = [n for n in notes if message.lower() not in n["message"].lower()]
        save_data(self.data)
        if removed:
            await interaction.response.send_message(f"✅ Removed {len(removed)} notifications.")
        else:
            await interaction.response.send_message("No matching notifications found.", ephemeral=True)

    @app_commands.command(name="notify_random", description="Show a random notification")
    async def notify_random(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        notes = self.data.get(guild_id, {}).get(user_id, [])
        if notes:
            n = random.choice(notes)
            await interaction.response.send_message(f"Random notification: {n['message']} at {n['time']}")
        else:
            await interaction.response.send_message("No notifications found.", ephemeral=True)

    @app_commands.command(name="notify_reschedule_all", description="Reschedule all notifications by minutes")
    async def notify_reschedule_all(self, interaction: discord.Interaction, minutes: int):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        notes = self.data.get(guild_id, {}).get(user_id, [])
        for n in notes:
            n["time"] = (datetime.fromisoformat(n["time"]) + timedelta(minutes=minutes)).isoformat()
        save_data(self.data)
        await interaction.response.send_message(f"✅ Rescheduled all notifications by {minutes} minutes.")

    @app_commands.command(name="notify_edit_all", description="Edit all notifications to same message")
    async def notify_edit_all(self, interaction: discord.Interaction, new_message: str):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        notes = self.data.get(guild_id, {}).get(user_id, [])
        for n in notes:
            n["message"] = new_message
        save_data(self.data)
        await interaction.response.send_message(f"✅ All notifications updated.")

async def setup(bot):
    await bot.add_cog(Notifications(bot), guild=discord.Object(id=GUILD_ID))
