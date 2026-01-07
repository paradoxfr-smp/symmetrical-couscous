import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import os
from config import GUILD_ID

DATA_FILE = "logging.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

class Logging(commands.Cog):
    """Logging system with 20 slash commands and JSON persistence"""

    def __init__(self, bot):
        self.bot = bot
        self.data = load_data()

    # ----------------------------
    # 1. /setlog
    # ----------------------------
    @app_commands.command(name="setlog", description="Set the logging channel")
    async def setlog(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Only admins can set log channels.", ephemeral=True)
            return
        self.data[str(interaction.guild.id)] = {"log_channel": channel.id}
        save_data(self.data)
        await interaction.response.send_message(f"✅ Logging channel set to {channel.mention}")

    # ----------------------------
    # 2. /showlog
    # ----------------------------
    @app_commands.command(name="showlog", description="Show the current logging channel")
    async def showlog(self, interaction: discord.Interaction):
        guild_data = self.data.get(str(interaction.guild.id), {})
        log_id = guild_data.get("log_channel")
        if log_id:
            channel = interaction.guild.get_channel(log_id)
            await interaction.response.send_message(f"📑 Current log channel: {channel.mention}")
        else:
            await interaction.response.send_message("❌ No logging channel set.")

    # ----------------------------
    # 3. /logmessage
    # ----------------------------
    @app_commands.command(name="logmessage", description="Log a custom message")
    async def logmessage(self, interaction: discord.Interaction, message: str):
        log_channel_id = self.data.get(str(interaction.guild.id), {}).get("log_channel")
        if log_channel_id:
            channel = interaction.guild.get_channel(log_channel_id)
            await channel.send(f"📝 {message}")
            await interaction.response.send_message("✅ Message logged.")
        else:
            await interaction.response.send_message("❌ Logging channel not set.")

    # ----------------------------
    # 4. /loguser
    # ----------------------------
    @app_commands.command(name="loguser", description="Log a user's info")
    async def loguser(self, interaction: discord.Interaction, member: discord.Member):
        log_channel_id = self.data.get(str(interaction.guild.id), {}).get("log_channel")
        if log_channel_id:
            channel = interaction.guild.get_channel(log_channel_id)
            await channel.send(f"👤 User logged: {member} (ID: {member.id})")
            await interaction.response.send_message(f"✅ Logged {member.mention}")
        else:
            await interaction.response.send_message("❌ Logging channel not set.")

    # ----------------------------
    # 5. /enablejoinlog
    # ----------------------------
    @app_commands.command(name="enablejoinlog", description="Enable join/leave logs")
    async def enablejoinlog(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        self.data.setdefault(guild_id, {})["join_leave"] = True
        save_data(self.data)
        await interaction.response.send_message("✅ Join/Leave logging enabled.")

    # ----------------------------
    # 6. /disablejoinlog
    # ----------------------------
    @app_commands.command(name="disablejoinlog", description="Disable join/leave logs")
    async def disablejoinlog(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        self.data.setdefault(guild_id, {})["join_leave"] = False
        save_data(self.data)
        await interaction.response.send_message("❌ Join/Leave logging disabled.")

    # ----------------------------
    # 7. /enablemessageeditlog
    # ----------------------------
    @app_commands.command(name="enablemessageeditlog", description="Enable message edit logs")
    async def enablemessageeditlog(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        self.data.setdefault(guild_id, {})["message_edit"] = True
        save_data(self.data)
        await interaction.response.send_message("✅ Message edit logging enabled.")

    # ----------------------------
    # 8. /disablemessageeditlog
    # ----------------------------
    @app_commands.command(name="disablemessageeditlog", description="Disable message edit logs")
    async def disablemessageeditlog(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        self.data.setdefault(guild_id, {})["message_edit"] = False
        save_data(self.data)
        await interaction.response.send_message("❌ Message edit logging disabled.")

    # ----------------------------
    # 9. /enablemessagedeletelog
    # ----------------------------
    @app_commands.command(name="enablemessagedeletelog", description="Enable message delete logs")
    async def enablemessagedeletelog(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        self.data.setdefault(guild_id, {})["message_delete"] = True
        save_data(self.data)
        await interaction.response.send_message("✅ Message delete logging enabled.")

    # ----------------------------
    # 10. /disablemessagedeletelog
    # ----------------------------
    @app_commands.command(name="disablemessagedeletelog", description="Disable message delete logs")
    async def disablemessagedeletelog(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        self.data.setdefault(guild_id, {})["message_delete"] = False
        save_data(self.data)
        await interaction.response.send_message("❌ Message delete logging disabled.")

    # ----------------------------
    # 11. /logban
    # ----------------------------
    @app_commands.command(name="logban", description="Log a ban event manually")
    async def logban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
        log_channel_id = self.data.get(str(interaction.guild.id), {}).get("log_channel")
        if log_channel_id:
            channel = interaction.guild.get_channel(log_channel_id)
            await channel.send(f"🔨 {member} was banned. Reason: {reason}")
            await interaction.response.send_message(f"✅ {member.mention} ban logged")
        else:
            await interaction.response.send_message("❌ Logging channel not set.")

    # ----------------------------
    # 12. /logkick
    # ----------------------------
    @app_commands.command(name="logkick", description="Log a kick event manually")
    async def logkick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
        log_channel_id = self.data.get(str(interaction.guild.id), {}).get("log_channel")
        if log_channel_id:
            channel = interaction.guild.get_channel(log_channel_id)
            await channel.send(f"👢 {member} was kicked. Reason: {reason}")
            await interaction.response.send_message(f"✅ {member.mention} kick logged")
        else:
            await interaction.response.send_message("❌ Logging channel not set.")

    # ----------------------------
    # 13. /logroleadd
    # ----------------------------
    @app_commands.command(name="logroleadd", description="Log a role add manually")
    async def logroleadd(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role):
        log_channel_id = self.data.get(str(interaction.guild.id), {}).get("log_channel")
        if log_channel_id:
            channel = interaction.guild.get_channel(log_channel_id)
            await channel.send(f"➕ Role {role.name} added to {member}")
            await interaction.response.send_message("✅ Role add logged")
        else:
            await interaction.response.send_message("❌ Logging channel not set.")

    # ----------------------------
    # 14. /logroleremove
    # ----------------------------
    @app_commands.command(name="logroleremove", description="Log a role remove manually")
    async def logroleremove(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role):
        log_channel_id = self.data.get(str(interaction.guild.id), {}).get("log_channel")
        if log_channel_id:
            channel = interaction.guild.get_channel(log_channel_id)
            await channel.send(f"➖ Role {role.name} removed from {member}")
            await interaction.response.send_message("✅ Role remove logged")
        else:
            await interaction.response.send_message("❌ Logging channel not set.")

    # ----------------------------
    # 15. /logchannelcreate
    # ----------------------------
    @app_commands.command(name="logchannelcreate", description="Log a channel creation manually")
    async def logchannelcreate(self, interaction: discord.Interaction, channel: discord.abc.GuildChannel):
        log_channel_id = self.data.get(str(interaction.guild.id), {}).get("log_channel")
        if log_channel_id:
            ch = interaction.guild.get_channel(log_channel_id)
            await ch.send(f"📂 Channel created: {channel.name} ({channel.id})")
            await interaction.response.send_message("✅ Channel creation logged")
        else:
            await interaction.response.send_message("❌ Logging channel not set.")

    # ----------------------------
    # 16. /logchanneldelete
    # ----------------------------
    @app_commands.command(name="logchanneldelete", description="Log a channel deletion manually")
    async def logchanneldelete(self, interaction: discord.Interaction, channel_name: str):
        log_channel_id = self.data.get(str(interaction.guild.id), {}).get("log_channel")
        if log_channel_id:
            ch = interaction.guild.get_channel(log_channel_id)
            await ch.send(f"🗑️ Channel deleted: {channel_name}")
            await interaction.response.send_message("✅ Channel deletion logged")
        else:
            await interaction.response.send_message("❌ Logging channel not set.")

    # ----------------------------
    # 17. /logrolecreate
    # ----------------------------
    @app_commands.command(name="logrolecreate", description="Log a role creation manually")
    async def logrolecreate(self, interaction: discord.Interaction, role: discord.Role):
        log_channel_id = self.data.get(str(interaction.guild.id), {}).get("log_channel")
        if log_channel_id:
            ch = interaction.guild.get_channel(log_channel_id)
            await ch.send(f"➕ Role created: {role.name} ({role.id})")
            await interaction.response.send_message("✅ Role creation logged")
        else:
            await interaction.response.send_message("❌ Logging channel not set.")

    # ----------------------------
    # 18. /logroleremoveevent
    # ----------------------------
    @app_commands.command(name="logroleremoveevent", description="Log a role deletion manually")
    async def logroleremoveevent(self, interaction: discord.Interaction, role_name: str):
        log_channel_id = self.data.get(str(interaction.guild.id), {}).get("log_channel")
        if log_channel_id:
            ch = interaction.guild.get_channel(log_channel_id)
            await ch.send(f"➖ Role deleted: {role_name}")
            await interaction.response.send_message("✅ Role deletion logged")
        else:
            await interaction.response.send_message("❌ Logging channel not set.")

    # ----------------------------
    # 19. /logbanlist
    # ----------------------------
    @app_commands.command(name="logbanlist", description="Log all banned users")
    async def logbanlist(self, interaction: discord.Interaction):
        bans = await interaction.guild.bans()
        log_channel_id = self.data.get(str(interaction.guild.id), {}).get("log_channel")
        if log_channel_id:
            ch = interaction.guild.get_channel(log_channel_id)
            for ban_entry in bans:
                await ch.send(f"🔨 Banned: {ban_entry.user} | Reason: {ban_entry.reason}")
            await interaction.response.send_message("✅ Ban list logged")
        else:
            await interaction.response.send_message("❌ Logging channel not set.")

    # ----------------------------
    # 20. /logall
    # ----------------------------
    @app_commands.command(name="logall", description="Log all current server info")
    async def logall(self, interaction: discord.Interaction):
        guild = interaction.guild
        log_channel_id = self.data.get(str(interaction.guild.id), {}).get("log_channel")
        if not log_channel_id:
            await interaction.response.send_message("❌ Logging channel not set.")
            return
        ch = interaction.guild.get_channel(log_channel_id)
        embed = discord.Embed(title=f"{guild.name} Full Log", color=discord.Color.orange())
        embed.add_field(name="Members", value=guild.member_count)
        embed.add_field(name="Channels", value=len(guild.channels))
        embed.add_field(name="Roles", value=len(guild.roles))
        embed.add_field(name="Boost Level", value=guild.premium_tier)
        await ch.send(embed=embed)
        await interaction.response.send_message("✅ Full server info logged")

async def setup(bot):
    await bot.add_cog(Logging(bot), guild=discord.Object(id=GUILD_ID))
