import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from config import GUILD_ID

DATA_FILE = "modlogs.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

class ModerationLogs(commands.Cog):
    """Logs moderation actions in a specified channel"""

    def __init__(self, bot):
        self.bot = bot
        self.data = load_data()

    # --------------------
    # Set log channel
    # --------------------
    @app_commands.command(name="set_log_channel", description="Set the moderation log channel")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_log_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        guild_id = str(interaction.guild.id)
        self.data[guild_id] = {"log_channel": channel.id}
        save_data(self.data)
        await interaction.response.send_message(f"✅ Moderation log channel set to {channel.mention}")

    # --------------------
    # Helper to get log channel
    # --------------------
    def get_log_channel(self, guild: discord.Guild):
        guild_id = str(guild.id)
        channel_id = self.data.get(guild_id, {}).get("log_channel")
        if channel_id:
            return guild.get_channel(channel_id)
        return None

    # --------------------
    # Kick listener
    # --------------------
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        # Could be kick or leave; leave alone for now
        pass

    # --------------------
    # Ban listener
    # --------------------
    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        channel = self.get_log_channel(guild)
        if channel:
            embed = discord.Embed(title="🔨 User Banned", color=discord.Color.red())
            embed.add_field(name="User", value=f"{user} ({user.id})", inline=False)
            embed.add_field(name="Time", value=discord.utils.utcnow().strftime("%Y-%m-%d %H:%M:%S"), inline=False)
            await channel.send(embed=embed)

    # --------------------
    # Unban listener
    # --------------------
    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        channel = self.get_log_channel(guild)
        if channel:
            embed = discord.Embed(title="✅ User Unbanned", color=discord.Color.green())
            embed.add_field(name="User", value=f"{user} ({user.id})", inline=False)
            embed.add_field(name="Time", value=discord.utils.utcnow().strftime("%Y-%m-%d %H:%M:%S"), inline=False)
            await channel.send(embed=embed)

    # --------------------
    # Message delete listener
    # --------------------
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot:
            return
        channel = self.get_log_channel(message.guild)
        if channel:
            embed = discord.Embed(title="🗑️ Message Deleted", color=discord.Color.orange())
            embed.add_field(name="User", value=f"{message.author} ({message.author.id})", inline=False)
            embed.add_field(name="Channel", value=message.channel.mention, inline=False)
            embed.add_field(name="Content", value=message.content or "None", inline=False)
            embed.add_field(name="Time", value=discord.utils.utcnow().strftime("%Y-%m-%d %H:%M:%S"), inline=False)
            await channel.send(embed=embed)

    # --------------------
    # Message edit listener
    # --------------------
    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author.bot or before.content == after.content:
            return
        channel = self.get_log_channel(before.guild)
        if channel:
            embed = discord.Embed(title="✏️ Message Edited", color=discord.Color.blue())
            embed.add_field(name="User", value=f"{before.author} ({before.author.id})", inline=False)
            embed.add_field(name="Channel", value=before.channel.mention, inline=False)
            embed.add_field(name="Before", value=before.content or "None", inline=False)
            embed.add_field(name="After", value=after.content or "None", inline=False)
            embed.add_field(name="Time", value=discord.utils.utcnow().strftime("%Y-%m-%d %H:%M:%S"), inline=False)
            await channel.send(embed=embed)

    # --------------------
    # Role changes
    # --------------------
    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        channel = self.get_log_channel(before.guild)
        if not channel:
            return

        # Roles added
        added = [r for r in after.roles if r not in before.roles]
        removed = [r for r in before.roles if r not in after.roles]

        if added:
            embed = discord.Embed(title="➕ Role(s) Added", color=discord.Color.green())
            embed.add_field(name="User", value=f"{after} ({after.id})", inline=False)
            embed.add_field(name="Roles", value=", ".join([r.name for r in added]), inline=False)
            embed.add_field(name="Time", value=discord.utils.utcnow().strftime("%Y-%m-%d %H:%M:%S"), inline=False)
            await channel.send(embed=embed)

        if removed:
            embed = discord.Embed(title="➖ Role(s) Removed", color=discord.Color.red())
            embed.add_field(name="User", value=f"{after} ({after.id})", inline=False)
            embed.add_field(name="Roles", value=", ".join([r.name for r in removed]), inline=False)
            embed.add_field(name="Time", value=discord.utils.utcnow().strftime("%Y-%m-%d %H:%M:%S"), inline=False)
            await channel.send(embed=embed)

    # --------------------
    # Warn command
    # --------------------
    @app_commands.command(name="log_warn", description="Log a warning manually")
    @app_commands.checks.has_permissions(kick_members=True)
    async def log_warn(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        channel = self.get_log_channel(interaction.guild)
        if channel:
            embed = discord.Embed(title="⚠️ Warning Issued", color=discord.Color.orange())
            embed.add_field(name="User", value=f"{member} ({member.id})", inline=False)
            embed.add_field(name="Moderator", value=f"{interaction.user} ({interaction.user.id})", inline=False)
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Time", value=discord.utils.utcnow().strftime("%Y-%m-%d %H:%M:%S"), inline=False)
            await channel.send(embed=embed)
            await interaction.response.send_message(f"✅ Logged warning for {member.mention}", ephemeral=True)
        else:
            await interaction.response.send_message("❌ No log channel set.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(ModerationLogs(bot), guild=discord.Object(id=GUILD_ID))
