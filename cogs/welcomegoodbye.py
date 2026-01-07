import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from config import GUILD_ID

DATA_FILE = "welcome_goodbye.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

class WelcomeGoodbye(commands.Cog):
    """Welcome and goodbye system with JSON persistence"""

    def __init__(self, bot):
        self.bot = bot
        self.data = load_data()

    # ----------------------------
    # 1. /set_welcome_channel
    # ----------------------------
    @app_commands.command(name="set_welcome_channel", description="Set channel for welcome messages")
    async def set_welcome_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        guild_id = str(interaction.guild.id)
        self.data.setdefault(guild_id, {})["welcome_channel"] = channel.id
        save_data(self.data)
        await interaction.response.send_message(f"✅ Welcome channel set to {channel.mention}")

    # ----------------------------
    # 2. /set_goodbye_channel
    # ----------------------------
    @app_commands.command(name="set_goodbye_channel", description="Set channel for goodbye messages")
    async def set_goodbye_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        guild_id = str(interaction.guild.id)
        self.data.setdefault(guild_id, {})["goodbye_channel"] = channel.id
        save_data(self.data)
        await interaction.response.send_message(f"✅ Goodbye channel set to {channel.mention}")

    # ----------------------------
    # 3. /set_welcome_message
    # ----------------------------
    @app_commands.command(name="set_welcome_message", description="Set a custom welcome message")
    async def set_welcome_message(self, interaction: discord.Interaction, *, message: str):
        guild_id = str(interaction.guild.id)
        self.data.setdefault(guild_id, {})["welcome_message"] = message
        save_data(self.data)
        await interaction.response.send_message("✅ Welcome message set.")

    # ----------------------------
    # 4. /set_goodbye_message
    # ----------------------------
    @app_commands.command(name="set_goodbye_message", description="Set a custom goodbye message")
    async def set_goodbye_message(self, interaction: discord.Interaction, *, message: str):
        guild_id = str(interaction.guild.id)
        self.data.setdefault(guild_id, {})["goodbye_message"] = message
        save_data(self.data)
        await interaction.response.send_message("✅ Goodbye message set.")

    # ----------------------------
    # 5. /enable_welcome
    # ----------------------------
    @app_commands.command(name="enable_welcome", description="Enable welcome messages")
    async def enable_welcome(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        self.data.setdefault(guild_id, {})["welcome_enabled"] = True
        save_data(self.data)
        await interaction.response.send_message("✅ Welcome messages enabled.")

    # ----------------------------
    # 6. /disable_welcome
    # ----------------------------
    @app_commands.command(name="disable_welcome", description="Disable welcome messages")
    async def disable_welcome(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        self.data.setdefault(guild_id, {})["welcome_enabled"] = False
        save_data(self.data)
        await interaction.response.send_message("✅ Welcome messages disabled.")

    # ----------------------------
    # 7. /enable_goodbye
    # ----------------------------
    @app_commands.command(name="enable_goodbye", description="Enable goodbye messages")
    async def enable_goodbye(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        self.data.setdefault(guild_id, {})["goodbye_enabled"] = True
        save_data(self.data)
        await interaction.response.send_message("✅ Goodbye messages enabled.")

    # ----------------------------
    # 8. /disable_goodbye
    # ----------------------------
    @app_commands.command(name="disable_goodbye", description="Disable goodbye messages")
    async def disable_goodbye(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        self.data.setdefault(guild_id, {})["goodbye_enabled"] = False
        save_data(self.data)
        await interaction.response.send_message("✅ Goodbye messages disabled.")

    # ----------------------------
    # 9. /show_welcome_channel
    # ----------------------------
    @app_commands.command(name="show_welcome_channel", description="Show current welcome channel")
    async def show_welcome_channel(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        channel_id = self.data.get(guild_id, {}).get("welcome_channel")
        if channel_id:
            channel = self.bot.get_channel(channel_id)
            await interaction.response.send_message(f"Welcome channel: {channel.mention}")
        else:
            await interaction.response.send_message("No welcome channel set.", ephemeral=True)

    # ----------------------------
    # 10. /show_goodbye_channel
    # ----------------------------
    @app_commands.command(name="show_goodbye_channel", description="Show current goodbye channel")
    async def show_goodbye_channel(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        channel_id = self.data.get(guild_id, {}).get("goodbye_channel")
        if channel_id:
            channel = self.bot.get_channel(channel_id)
            await interaction.response.send_message(f"Goodbye channel: {channel.mention}")
        else:
            await interaction.response.send_message("No goodbye channel set.", ephemeral=True)

    # ----------------------------
    # 11. /show_welcome_message
    # ----------------------------
    @app_commands.command(name="show_welcome_message", description="Show current welcome message")
    async def show_welcome_message(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        message = self.data.get(guild_id, {}).get("welcome_message", "No message set.")
        await interaction.response.send_message(f"Welcome message: {message}")

    # ----------------------------
    # 12. /show_goodbye_message
    # ----------------------------
    @app_commands.command(name="show_goodbye_message", description="Show current goodbye message")
    async def show_goodbye_message(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        message = self.data.get(guild_id, {}).get("goodbye_message", "No message set.")
        await interaction.response.send_message(f"Goodbye message: {message}")

    # ----------------------------
    # 13. /reset_welcome_message
    # ----------------------------
    @app_commands.command(name="reset_welcome_message", description="Reset welcome message to default")
    async def reset_welcome_message(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        if "welcome_message" in self.data.get(guild_id, {}):
            self.data[guild_id].pop("welcome_message")
            save_data(self.data)
        await interaction.response.send_message("✅ Welcome message reset.")

    # ----------------------------
    # 14. /reset_goodbye_message
    # ----------------------------
    @app_commands.command(name="reset_goodbye_message", description="Reset goodbye message to default")
    async def reset_goodbye_message(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        if "goodbye_message" in self.data.get(guild_id, {}):
            self.data[guild_id].pop("goodbye_message")
            save_data(self.data)
        await interaction.response.send_message("✅ Goodbye message reset.")

    # ----------------------------
    # 15. /welcome_preview
    # ----------------------------
    @app_commands.command(name="welcome_preview", description="Preview your welcome message")
    async def welcome_preview(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        message = self.data.get(guild_id, {}).get("welcome_message", "Welcome {user}!")
        await interaction.response.send_message(message.replace("{user}", interaction.user.mention))

    # ----------------------------
    # 16. /goodbye_preview
    # ----------------------------
    @app_commands.command(name="goodbye_preview", description="Preview your goodbye message")
    async def goodbye_preview(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        message = self.data.get(guild_id, {}).get("goodbye_message", "Goodbye {user}!")
        await interaction.response.send_message(message.replace("{user}", interaction.user.mention))

    # ----------------------------
    # 17. /toggle_welcome_mentions
    # ----------------------------
    @app_commands.command(name="toggle_welcome_mentions", description="Toggle mention in welcome messages")
    async def toggle_welcome_mentions(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        current = self.data.get(guild_id, {}).get("welcome_mention", True)
        self.data.setdefault(guild_id, {})["welcome_mention"] = not current
        save_data(self.data)
        await interaction.response.send_message(f"✅ Welcome mentions {'enabled' if not current else 'disabled'}.")

    # ----------------------------
    # 18. /toggle_goodbye_mentions
    # ----------------------------
    @app_commands.command(name="toggle_goodbye_mentions", description="Toggle mention in goodbye messages")
    async def toggle_goodbye_mentions(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        current = self.data.get(guild_id, {}).get("goodbye_mention", True)
        self.data.setdefault(guild_id, {})["goodbye_mention"] = not current
        save_data(self.data)
        await interaction.response.send_message(f"✅ Goodbye mentions {'enabled' if not current else 'disabled'}.")

    # ----------------------------
    # 19. /show_status
    # ----------------------------
    @app_commands.command(name="show_status", description="Show current welcome/goodbye status")
    async def show_status(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        welcome_enabled = self.data.get(guild_id, {}).get("welcome_enabled", False)
        goodbye_enabled = self.data.get(guild_id, {}).get("goodbye_enabled", False)
        await interaction.response.send_message(f"Welcome messages: {welcome_enabled}\nGoodbye messages: {goodbye_enabled}")

    # ----------------------------
    # 20. /reset_all
    # ----------------------------
    @app_commands.command(name="reset_all", description="Reset all welcome/goodbye settings")
    async def reset_all(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        if guild_id in self.data:
            self.data.pop(guild_id)
            save_data(self.data)
        await interaction.response.send_message("✅ All welcome/goodbye settings reset.")

    # ----------------------------
    # Events for Join/Leave
    # ----------------------------
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild_id = str(member.guild.id)
        guild_data = self.data.get(guild_id, {})
        if guild_data.get("welcome_enabled", False):
            channel_id = guild_data.get("welcome_channel")
            message = guild_data.get("welcome_message", "Welcome {user}!")
            mention = guild_data.get("welcome_mention", True)
            if channel_id:
                channel = self.bot.get_channel(channel_id)
                if channel:
                    text = message.replace("{user}", member.mention if mention else member.name)
                    await channel.send(text)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        guild_id = str(member.guild.id)
        guild_data = self.data.get(guild_id, {})
        if guild_data.get("goodbye_enabled", False):
            channel_id = guild_data.get("goodbye_channel")
            message = guild_data.get("goodbye_message", "Goodbye {user}!")
            mention = guild_data.get("goodbye_mention", True)
            if channel_id:
                channel = self.bot.get_channel(channel_id)
                if channel:
                    text = message.replace("{user}", member.mention if mention else member.name)
                    await channel.send(text)

async def setup(bot):
    await bot.add_cog(WelcomeGoodbye(bot), guild=discord.Object(id=GUILD_ID))
