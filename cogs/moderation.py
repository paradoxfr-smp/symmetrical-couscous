import discord
from discord.ext import commands
from discord import app_commands
from config import GUILD_ID
import json
import datetime
import asyncio
import os

DATA_FILE = "moderation.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

class Moderation(commands.Cog):
    """Full moderation cog with 20+ slash commands and JSON persistence"""

    def __init__(self, bot):
        self.bot = bot
        self.data = load_data()

    # ----------------------------
    # 1. Kick
    # ----------------------------
    @app_commands.command(name="kick", description="Kick a member")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        await member.kick(reason=reason)
        await self.log_action(interaction.guild.id, f"Kicked {member} for: {reason}", str(interaction.user))
        await interaction.response.send_message(f"👢 Kicked {member.mention} for: {reason}")

    # ----------------------------
    # 2. Ban
    # ----------------------------
    @app_commands.command(name="ban", description="Ban a member")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        await member.ban(reason=reason)
        await self.log_action(interaction.guild.id, f"Banned {member} for: {reason}", str(interaction.user))
        await interaction.response.send_message(f"🔨 Banned {member.mention} for: {reason}")

    # ----------------------------
    # 3. Softban
    # ----------------------------
    @app_commands.command(name="softban", description="Softban a member (ban and unban to delete messages)")
    @app_commands.checks.has_permissions(ban_members=True)
    async def softban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        await member.ban(reason=reason)
        await member.unban(reason="Softban expired")
        await self.log_action(interaction.guild.id, f"Softbanned {member} for: {reason}", str(interaction.user))
        await interaction.response.send_message(f"🟠 Softbanned {member.mention} for: {reason}")

    # ----------------------------
    # 4. Warn
    # ----------------------------
    @app_commands.command(name="warn", description="Warn a member")
    @app_commands.checks.has_permissions(kick_members=True)
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        guild_id = str(interaction.guild.id)
        user_id = str(member.id)
        self.data.setdefault(guild_id, {}).setdefault(user_id, {}).setdefault("warns", [])
        warn_entry = {
            "reason": reason,
            "moderator": str(interaction.user),
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
        self.data[guild_id][user_id]["warns"].append(warn_entry)
        save_data(self.data)
        await self.log_action(guild_id, f"Warned {member} for: {reason}", str(interaction.user))
        await interaction.response.send_message(f"⚠️ {member.mention} has been warned for: {reason}")

    # ----------------------------
    # 5. Check Warns
    # ----------------------------
    @app_commands.command(name="warns", description="Check warns of a member")
    @app_commands.checks.has_permissions(kick_members=True)
    async def warns(self, interaction: discord.Interaction, member: discord.Member):
        guild_id = str(interaction.guild.id)
        user_id = str(member.id)
        warns = self.data.get(guild_id, {}).get(user_id, {}).get("warns", [])
        if not warns:
            await interaction.response.send_message(f"{member.mention} has no warnings.")
            return
        embed = discord.Embed(title=f"Warnings for {member}", color=discord.Color.orange())
        for i, w in enumerate(warns, start=1):
            embed.add_field(name=f"Warn {i}", value=f"Reason: {w['reason']}\nModerator: {w['moderator']}\nTime: {w['timestamp']}", inline=False)
        await interaction.response.send_message(embed=embed)

    # ----------------------------
    # 6. Clear Warns
    # ----------------------------
    @app_commands.command(name="clearwarns", description="Clear all warnings of a member")
    @app_commands.checks.has_permissions(kick_members=True)
    async def clearwarns(self, interaction: discord.Interaction, member: discord.Member):
        guild_id = str(interaction.guild.id)
        user_id = str(member.id)
        if guild_id in self.data and user_id in self.data[guild_id]:
            self.data[guild_id][user_id]["warns"] = []
            save_data(self.data)
            await interaction.response.send_message(f"✅ Cleared all warnings for {member.mention}.")
        else:
            await interaction.response.send_message(f"{member.mention} has no warnings.")

    # ----------------------------
    # 7. Mute
    # ----------------------------
    @app_commands.command(name="mute", description="Mute a member (temporary or permanent)")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def mute(self, interaction: discord.Interaction, member: discord.Member, duration: int = 0, reason: str = "No reason provided"):
        guild = interaction.guild
        mute_role = discord.utils.get(guild.roles, name="Muted")
        if not mute_role:
            mute_role = await guild.create_role(name="Muted", color=discord.Color.dark_gray())
            for channel in guild.channels:
                await channel.set_permissions(mute_role, speak=False, send_messages=False, add_reactions=False)
        await member.add_roles(mute_role, reason=reason)
        guild_id = str(guild.id)
        user_id = str(member.id)
        self.data.setdefault(guild_id, {}).setdefault(user_id, {})["mute"] = {
            "reason": reason,
            "moderator": str(interaction.user),
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "duration": duration
        }
        save_data(self.data)
        msg = f"🔇 {member.mention} has been muted"
        if duration > 0:
            msg += f" for {duration} minutes"
        await interaction.response.send_message(msg + f". Reason: {reason}")
        if duration > 0:
            await asyncio.sleep(duration * 60)
            # Reload data in case of restart
            data = load_data()
            if data.get(guild_id, {}).get(user_id, {}).get("mute", None):
                if mute_role in member.roles:
                    await member.remove_roles(mute_role, reason="Temporary mute expired")
                    del data[guild_id][user_id]["mute"]
                    save_data(data)

    # ----------------------------
    # 8. Unmute
    # ----------------------------
    @app_commands.command(name="unmute", description="Unmute a member")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def unmute(self, interaction: discord.Interaction, member: discord.Member):
        guild = interaction.guild
        mute_role = discord.utils.get(guild.roles, name="Muted")
        if mute_role and mute_role in member.roles:
            await member.remove_roles(mute_role, reason="Unmuted by staff")
            guild_id = str(guild.id)
            user_id = str(member.id)
            if guild_id in self.data and user_id in self.data[guild_id]:
                self.data[guild_id][user_id].pop("mute", None)
                save_data(self.data)
            await interaction.response.send_message(f"🔊 {member.mention} has been unmuted.")
        else:
            await interaction.response.send_message(f"{member.mention} is not muted.", ephemeral=True)

    # ----------------------------
    # 9. Clear Messages
    # ----------------------------
    @app_commands.command(name="clear", description="Clear a number of messages")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, amount: int):
        await interaction.channel.purge(limit=amount)
        await interaction.response.send_message(f"🧹 Cleared {amount} messages.", ephemeral=True)

    # ----------------------------
    # 10. Role Give
    # ----------------------------
    @app_commands.command(name="giverole", description="Give a role to a member")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def giverole(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role):
        await member.add_roles(role, reason=f"Role given by {interaction.user}")
        await interaction.response.send_message(f"✅ {role.name} given to {member.mention}.")

    # ----------------------------
    # 11. Role Remove
    # ----------------------------
    @app_commands.command(name="removerole", description="Remove a role from a member")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def removerole(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role):
        await member.remove_roles(role, reason=f"Role removed by {interaction.user}")
        await interaction.response.send_message(f"✅ {role.name} removed from {member.mention}.")

    # ----------------------------
    # 12. Lock Channel
    # ----------------------------
    @app_commands.command(name="lock", description="Lock the current channel")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def lock(self, interaction: discord.Interaction):
        overwrites = interaction.channel.overwrites_for(interaction.guild.default_role)
        overwrites.send_messages = False
        await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrites)
        await interaction.response.send_message(f"🔒 {interaction.channel.mention} is now locked.")

    # ----------------------------
    # 13. Unlock Channel
    # ----------------------------
    @app_commands.command(name="unlock", description="Unlock the current channel")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def unlock(self, interaction: discord.Interaction):
        overwrites = interaction.channel.overwrites_for(interaction.guild.default_role)
        overwrites.send_messages = True
        await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrites)
        await interaction.response.send_message(f"🔓 {interaction.channel.mention} is now unlocked.")

    # ----------------------------
    # 14. Temp Ban
    # ----------------------------
    @app_commands.command(name="tempban", description="Temporarily ban a member (minutes)")
    @app_commands.checks.has_permissions(ban_members=True)
    async def tempban(self, interaction: discord.Interaction, member: discord.Member, duration: int, reason: str = "No reason provided"):
        await member.ban(reason=reason)
        await interaction.response.send_message(f"⏳ {member.mention} has been temporarily banned for {duration} minutes. Reason: {reason}")
        await asyncio.sleep(duration * 60)
        await member.unban(reason="Temporary ban expired")

    # ----------------------------
    # 15. Kick History
    # ----------------------------
    @app_commands.command(name="kicklog", description="View kick history of a member")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kicklog(self, interaction: discord.Interaction, member: discord.Member):
        guild_id = str(interaction.guild.id)
        history = self.data.get(guild_id, {}).get(str(member.id), {}).get("kicks", [])
        if not history:
            await interaction.response.send_message(f"{member.mention} has no kick history.")
            return
        embed = discord.Embed(title=f"Kick History for {member}", color=discord.Color.red())
        for i, entry in enumerate(history, start=1):
            embed.add_field(name=f"{i}. {entry['reason']}", value=f"By {entry['moderator']} at {entry['timestamp']}", inline=False)
        await interaction.response.send_message(embed=embed)

    # ----------------------------
    # 16. Ban History
    # ----------------------------
    @app_commands.command(name="banlog", description="View ban history of a member")
    @app_commands.checks.has_permissions(ban_members=True)
    async def banlog(self, interaction: discord.Interaction, member: discord.Member):
        guild_id = str(interaction.guild.id)
        history = self.data.get(guild_id, {}).get(str(member.id), {}).get("bans", [])
        if not history:
            await interaction.response.send_message(f"{member.mention} has no ban history.")
            return
        embed = discord.Embed(title=f"Ban History for {member}", color=discord.Color.dark_red())
        for i, entry in enumerate(history, start=1):
            embed.add_field(name=f"{i}. {entry['reason']}", value=f"By {entry['moderator']} at {entry['timestamp']}", inline=False)
        await interaction.response.send_message(embed=embed)

    # ----------------------------
    # 17. Mass Kick
    # ----------------------------
    @app_commands.command(name="masskick", description="Kick multiple members (owner only)")
    async def masskick(self, interaction: discord.Interaction, members: str):
        if interaction.user.id != interaction.guild.owner_id:
            await interaction.response.send_message("❌ Only the server owner can mass kick.", ephemeral=True)
            return
        user_ids = [int(x.strip()) for x in members.split(",")]
        for uid in user_ids:
            member = interaction.guild.get_member(uid)
            if member:
                await member.kick(reason="Mass kick by owner")
        await interaction.response.send_message("✅ Mass kick completed.")

    # ----------------------------
    # 18. Mass Ban
    # ----------------------------
    @app_commands.command(name="massban", description="Ban multiple members (owner only)")
    async def massban(self, interaction: discord.Interaction, members: str):
        if interaction.user.id != interaction.guild.owner_id:
            await interaction.response.send_message("❌ Only the server owner can mass ban.", ephemeral=True)
            return
        user_ids = [int(x.strip()) for x in members.split(",")]
        for uid in user_ids:
            member = interaction.guild.get_member(uid)
            if member:
                await member.ban(reason="Mass ban by owner")
        await interaction.response.send_message("✅ Mass ban completed.")

    # ----------------------------
    # 19. Anti-Raid Toggle
    # ----------------------------
    @app_commands.command(name="antiraid", description="Toggle anti-raid protection on/off")
    @app_commands.checks.has_permissions(administrator=True)
    async def antiraid(self, interaction: discord.Interaction, state: bool):
        guild_id = str(interaction.guild.id)
        self.data.setdefault(guild_id, {})["antiraid"] = state
        save_data(self.data)
        await interaction.response.send_message(f"🛡️ Anti-raid protection is now {'ON' if state else 'OFF'}.")

    # ----------------------------
    # 20. Moderation Logs
    # ----------------------------
    @app_commands.command(name="modlogs", description="View moderation logs")
    @app_commands.checks.has_permissions(administrator=True)
    async def modlogs(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        logs = self.data.get(guild_id, {}).get("modlog", [])
        if not logs:
            await interaction.response.send_message("No moderation logs found.")
            return
        embed = discord.Embed(title="Moderation Logs", color=discord.Color.blurple())
        for i, entry in enumerate(logs, start=1):
            embed.add_field(name=f"{i}. {entry['action']}", value=f"By {entry['moderator']} at {entry['timestamp']}", inline=False)
        await interaction.response.send_message(embed=embed)

    # ----------------------------
    # Logging Helper
    # ----------------------------
    async def log_action(self, guild_id, action, moderator):
        guild_id = str(guild_id)
        self.data.setdefault(guild_id, {}).setdefault("modlog", [])
        self.data[guild_id]["modlog"].append({
            "action": action,
            "moderator": moderator,
            "timestamp": datetime.datetime.utcnow().isoformat()
        })
        save_data(self.data)

async def setup(bot):
    await bot.add_cog(Moderation(bot), guild=discord.Object(id=GUILD_ID))
