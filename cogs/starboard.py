import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from config import GUILD_ID

DATA_FILE = "starboard.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

class Starboard(commands.Cog):
    """Starboard system with 20 functional commands"""

    def __init__(self, bot):
        self.bot = bot
        self.data = load_data()

    # ----------------------------
    # 1. /set_starboard_channel
    # ----------------------------
    @app_commands.command(name="set_starboard_channel", description="Set the starboard channel")
    async def set_starboard_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        guild_id = str(interaction.guild.id)
        self.data.setdefault(guild_id, {})["channel_id"] = channel.id
        save_data(self.data)
        await interaction.response.send_message(f"✅ Starboard channel set to {channel.mention}")

    # ----------------------------
    # 2. /set_star_emoji
    # ----------------------------
    @app_commands.command(name="set_star_emoji", description="Set the emoji for starboard")
    async def set_star_emoji(self, interaction: discord.Interaction, emoji: str):
        guild_id = str(interaction.guild.id)
        self.data.setdefault(guild_id, {})["emoji"] = emoji
        save_data(self.data)
        await interaction.response.send_message(f"✅ Starboard emoji set to {emoji}")

    # ----------------------------
    # 3. /set_star_threshold
    # ----------------------------
    @app_commands.command(name="set_star_threshold", description="Set number of reactions required for starboard")
    async def set_star_threshold(self, interaction: discord.Interaction, count: int):
        guild_id = str(interaction.guild.id)
        self.data.setdefault(guild_id, {})["threshold"] = count
        save_data(self.data)
        await interaction.response.send_message(f"✅ Starboard threshold set to {count}")

    # ----------------------------
    # 4. /enable_starboard
    # ----------------------------
    @app_commands.command(name="enable_starboard", description="Enable starboard")
    async def enable_starboard(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        self.data.setdefault(guild_id, {})["enabled"] = True
        save_data(self.data)
        await interaction.response.send_message("✅ Starboard enabled")

    # ----------------------------
    # 5. /disable_starboard
    # ----------------------------
    @app_commands.command(name="disable_starboard", description="Disable starboard")
    async def disable_starboard(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        self.data.setdefault(guild_id, {})["enabled"] = False
        save_data(self.data)
        await interaction.response.send_message("✅ Starboard disabled")

    # ----------------------------
    # 6. /show_starboard_channel
    # ----------------------------
    @app_commands.command(name="show_starboard_channel", description="Show current starboard channel")
    async def show_starboard_channel(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        channel_id = self.data.get(guild_id, {}).get("channel_id")
        if channel_id:
            channel = self.bot.get_channel(channel_id)
            await interaction.response.send_message(f"Starboard channel: {channel.mention}")
        else:
            await interaction.response.send_message("No starboard channel set.", ephemeral=True)

    # ----------------------------
    # 7. /show_star_emoji
    # ----------------------------
    @app_commands.command(name="show_star_emoji", description="Show current starboard emoji")
    async def show_star_emoji(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        emoji = self.data.get(guild_id, {}).get("emoji", "⭐")
        await interaction.response.send_message(f"Current starboard emoji: {emoji}")

    # ----------------------------
    # 8. /show_threshold
    # ----------------------------
    @app_commands.command(name="show_threshold", description="Show current starboard threshold")
    async def show_threshold(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        threshold = self.data.get(guild_id, {}).get("threshold", 3)
        await interaction.response.send_message(f"Starboard threshold: {threshold}")

    # ----------------------------
    # 9. /reset_starboard
    # ----------------------------
    @app_commands.command(name="reset_starboard", description="Reset all starboard settings")
    async def reset_starboard(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        if guild_id in self.data:
            self.data.pop(guild_id)
            save_data(self.data)
        await interaction.response.send_message("✅ Starboard settings reset")

    # ----------------------------
    # 10. /preview_star
    # ----------------------------
    @app_commands.command(name="preview_star", description="Preview how a message would appear on starboard")
    async def preview_star(self, interaction: discord.Interaction, message: str):
        await interaction.response.send_message(f"{self.data.get(str(interaction.guild.id), {}).get('emoji', '⭐')} {message}")

    # ----------------------------
    # 11. /list_starred
    # ----------------------------
    @app_commands.command(name="list_starred", description="List recently starred messages")
    async def list_starred(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        starred = self.data.get(guild_id, {}).get("messages", [])
        if starred:
            await interaction.response.send_message("\n".join(starred))
        else:
            await interaction.response.send_message("No messages have been starred yet.")

    # ----------------------------
    # 12. /clear_starred
    # ----------------------------
    @app_commands.command(name="clear_starred", description="Clear all starred messages")
    async def clear_starred(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        self.data.setdefault(guild_id, {})["messages"] = []
        save_data(self.data)
        await interaction.response.send_message("✅ Cleared all starred messages")

    # ----------------------------
    # 13. /manual_star
    # ----------------------------
    @app_commands.command(name="manual_star", description="Manually add a message to starboard")
    async def manual_star(self, interaction: discord.Interaction, message: str):
        guild_id = str(interaction.guild.id)
        self.data.setdefault(guild_id, {}).setdefault("messages", []).append(message)
        save_data(self.data)
        await interaction.response.send_message(f"✅ Manually added to starboard: {message}")

    # ----------------------------
    # 14. /remove_star
    # ----------------------------
    @app_commands.command(name="remove_star", description="Remove a message from starboard")
    async def remove_star(self, interaction: discord.Interaction, message: str):
        guild_id = str(interaction.guild.id)
        messages = self.data.get(guild_id, {}).get("messages", [])
        if message in messages:
            messages.remove(message)
            save_data(self.data)
            await interaction.response.send_message(f"✅ Removed message from starboard: {message}")
        else:
            await interaction.response.send_message("Message not found.", ephemeral=True)

    # ----------------------------
    # 15. /toggle_star_notifications
    # ----------------------------
    @app_commands.command(name="toggle_star_notifications", description="Toggle notifications when someone stars a message")
    async def toggle_star_notifications(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        current = self.data.get(guild_id, {}).get("notify", True)
        self.data.setdefault(guild_id, {})["notify"] = not current
        save_data(self.data)
        await interaction.response.send_message(f"✅ Star notifications {'enabled' if not current else 'disabled'}")

    # ----------------------------
    # 16. /starboard_status
    # ----------------------------
    @app_commands.command(name="starboard_status", description="Check current starboard status")
    async def starboard_status(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        enabled = self.data.get(guild_id, {}).get("enabled", False)
        await interaction.response.send_message(f"Starboard enabled: {enabled}")

    # ----------------------------
    # 17. /show_all_settings
    # ----------------------------
    @app_commands.command(name="show_all_settings", description="Show all starboard settings")
    async def show_all_settings(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        settings = self.data.get(guild_id, {})
        await interaction.response.send_message(f"Starboard settings: {settings}")

    # ----------------------------
    # 18. /reset_messages
    # ----------------------------
    @app_commands.command(name="reset_messages", description="Clear all starboard messages but keep config")
    async def reset_messages(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        self.data.setdefault(guild_id, {})["messages"] = []
        save_data(self.data)
        await interaction.response.send_message("✅ Cleared all starred messages but kept config")

    # ----------------------------
    # 19. /starboard_preview_embed
    # ----------------------------
    @app_commands.command(name="starboard_preview_embed", description="Preview starboard embed")
    async def starboard_preview_embed(self, interaction: discord.Interaction, message: str):
        embed = discord.Embed(title="⭐ Starred Message", description=message, color=discord.Color.gold())
        await interaction.response.send_message(embed=embed)

    # ----------------------------
    # 20. /manual_star_embed
    # ----------------------------
    @app_commands.command(name="manual_star_embed", description="Manually add an embed to starboard")
    async def manual_star_embed(self, interaction: discord.Interaction, title: str, description: str):
        embed = discord.Embed(title=title, description=description, color=discord.Color.gold())
        guild_id = str(interaction.guild.id)
        self.data.setdefault(guild_id, {}).setdefault("messages", []).append(f"{title}: {description}")
        save_data(self.data)
        await interaction.response.send_message(embed=embed)

    # ----------------------------
    # Event Listener
    # ----------------------------
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return
        guild_id = str(reaction.message.guild.id)
        guild_data = self.data.get(guild_id, {})
        if not guild_data.get("enabled", False):
            return
        emoji = guild_data.get("emoji", "⭐")
        threshold = guild_data.get("threshold", 3)
        if str(reaction.emoji) == emoji and reaction.count >= threshold:
            channel_id = guild_data.get("channel_id")
            if channel_id:
                channel = self.bot.get_channel(channel_id)
                if channel:
                    embed = discord.Embed(title="⭐ Starred Message", description=reaction.message.content, color=discord.Color.gold())
                    embed.set_author(name=reaction.message.author.display_name, icon_url=reaction.message.author.display_avatar.url)
                    await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Starboard(bot), guild=discord.Object(id=GUILD_ID))
