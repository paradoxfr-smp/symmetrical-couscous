import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import os
import datetime
import asyncio
from config import GUILD_ID

DATA_FILE = "utility.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

class Utility(commands.Cog):
    """Utility commands cog with 20 slash commands"""

    def __init__(self, bot):
        self.bot = bot
        self.data = load_data()
        self.reminder_loop.start()

    # ----------------------------
    # 1. /userinfo
    # ----------------------------
    @app_commands.command(name="userinfo", description="Get information about a user")
    async def userinfo(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        embed = discord.Embed(title=f"User Info - {member}", color=discord.Color.blue())
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
        embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
        embed.add_field(name="Top Role", value=member.top_role, inline=True)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        await interaction.response.send_message(embed=embed)

    # ----------------------------
    # 2. /serverinfo
    # ----------------------------
    @app_commands.command(name="serverinfo", description="Get information about the server")
    async def serverinfo(self, interaction: discord.Interaction):
        guild = interaction.guild
        embed = discord.Embed(title=f"Server Info - {guild.name}", color=discord.Color.green())
        embed.add_field(name="ID", value=guild.id)
        embed.add_field(name="Owner", value=guild.owner)
        embed.add_field(name="Member Count", value=guild.member_count)
        embed.add_field(name="Created At", value=guild.created_at.strftime("%Y-%m-%d %H:%M:%S"))
        embed.add_field(name="Boosts", value=guild.premium_subscription_count)
        embed.set_thumbnail(url=guild.icon.url if guild.icon else "")
        await interaction.response.send_message(embed=embed)

    # ----------------------------
    # 3. /avatar
    # ----------------------------
    @app_commands.command(name="avatar", description="Get user's avatar")
    async def avatar(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        await interaction.response.send_message(member.avatar.url if member.avatar else member.default_avatar.url)

    # ----------------------------
    # 4. /ping
    # ----------------------------
    @app_commands.command(name="ping", description="Bot latency")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"🏓 Pong! Latency: {round(self.bot.latency*1000)}ms")

    # ----------------------------
    # 5. /remind
    # ----------------------------
    @app_commands.command(name="remind", description="Set a reminder")
    async def remind(self, interaction: discord.Interaction, time: int, *, message: str):
        user_id = str(interaction.user.id)
        self.data.setdefault("reminders", []).append({
            "user": user_id,
            "message": message,
            "time": (datetime.datetime.utcnow() + datetime.timedelta(seconds=time)).isoformat()
        })
        save_data(self.data)
        await interaction.response.send_message(f"⏰ Reminder set in {time} seconds: {message}")

    # ----------------------------
    # 6. /uptime
    # ----------------------------
    @app_commands.command(name="uptime", description="Check bot uptime")
    async def uptime(self, interaction: discord.Interaction):
        if not hasattr(self.bot, "start_time"):
            self.bot.start_time = datetime.datetime.utcnow()
        delta = datetime.datetime.utcnow() - self.bot.start_time
        await interaction.response.send_message(f"⏱️ Uptime: {str(delta).split('.')[0]}")

    # ----------------------------
    # 7. /avatarinfo
    # ----------------------------
    @app_commands.command(name="avatarinfo", description="Show avatar info")
    async def avatarinfo(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        embed = discord.Embed(title=f"{member}'s Avatar", color=discord.Color.purple())
        embed.set_image(url=member.avatar.url if member.avatar else member.default_avatar.url)
        await interaction.response.send_message(embed=embed)

    # ----------------------------
    # 8. /roleinfo
    # ----------------------------
    @app_commands.command(name="roleinfo", description="Get information about a role")
    async def roleinfo(self, interaction: discord.Interaction, role: discord.Role):
        embed = discord.Embed(title=f"Role Info - {role.name}", color=role.color)
        embed.add_field(name="ID", value=role.id)
        embed.add_field(name="Mentionable", value=role.mentionable)
        embed.add_field(name="Members", value=len(role.members))
        embed.add_field(name="Created At", value=role.created_at.strftime("%Y-%m-%d %H:%M:%S"))
        await interaction.response.send_message(embed=embed)

    # ----------------------------
    # 9. /servericon
    # ----------------------------
    @app_commands.command(name="servericon", description="Show server icon")
    async def servericon(self, interaction: discord.Interaction):
        guild = interaction.guild
        await interaction.response.send_message(guild.icon.url if guild.icon else "No icon")

    # ----------------------------
    # 10. /time
    # ----------------------------
    @app_commands.command(name="time", description="Show current UTC time")
    async def time(self, interaction: discord.Interaction):
        now = datetime.datetime.utcnow()
        await interaction.response.send_message(f"🕒 Current UTC time: {now.strftime('%Y-%m-%d %H:%M:%S')}")

    # ----------------------------
    # 11. /avatarserver
    # ----------------------------
    @app_commands.command(name="avatarserver", description="Get server icon")
    async def avatarserver(self, interaction: discord.Interaction):
        guild = interaction.guild
        await interaction.response.send_message(guild.icon.url if guild.icon else "No icon")

    # ----------------------------
    # 12. /members
    # ----------------------------
    @app_commands.command(name="members", description="Show member count")
    async def members(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"👥 Members: {interaction.guild.member_count}")

    # ----------------------------
    # 13. /roles
    # ----------------------------
    @app_commands.command(name="roles", description="List all roles in server")
    async def roles(self, interaction: discord.Interaction):
        roles = [role.name for role in interaction.guild.roles if role.name != "@everyone"]
        await interaction.response.send_message(f"🏷️ Roles: {', '.join(roles)}")

    # ----------------------------
    # 14. /channels
    # ----------------------------
    @app_commands.command(name="channels", description="List all channels in server")
    async def channels(self, interaction: discord.Interaction):
        channels = [channel.name for channel in interaction.guild.channels]
        await interaction.response.send_message(f"📂 Channels: {', '.join(channels)}")

    # ----------------------------
    # 15. /emoji
    # ----------------------------
    @app_commands.command(name="emoji", description="Show emoji URL")
    async def emoji(self, interaction: discord.Interaction, emoji: discord.Emoji):
        await interaction.response.send_message(emoji.url)

    # ----------------------------
    # 16. /avatarbanner
    # ----------------------------
    @app_commands.command(name="avatarbanner", description="Show user's banner")
    async def avatarbanner(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        if member.banner:
            await interaction.response.send_message(member.banner.url)
        else:
            await interaction.response.send_message("❌ User has no banner.")

    # ----------------------------
    # 17. /botinfo
    # ----------------------------
    @app_commands.command(name="botinfo", description="Show bot info")
    async def botinfo(self, interaction: discord.Interaction):
        embed = discord.Embed(title=f"{self.bot.user} Info", color=discord.Color.teal())
        embed.add_field(name="ID", value=self.bot.user.id)
        embed.add_field(name="Latency", value=f"{round(self.bot.latency*1000)}ms")
        embed.add_field(name="Guilds", value=len(self.bot.guilds))
        await interaction.response.send_message(embed=embed)

    # ----------------------------
    # 18. /prefix
    # ----------------------------
    @app_commands.command(name="prefix", description="Show current prefix")
    async def prefix(self, interaction: discord.Interaction):
        await interaction.response.send_message("🔹 Current prefix is `/` (slash commands)")

    # ----------------------------
    # 19. /timer
    # ----------------------------
    @app_commands.command(name="timer", description="Set a timer in seconds")
    async def timer(self, interaction: discord.Interaction, seconds: int):
        if seconds <= 0:
            await interaction.response.send_message("❌ Time must be positive.")
            return
        await interaction.response.send_message(f"⏱️ Timer set for {seconds} seconds.")
        await asyncio.sleep(seconds)
        await interaction.followup.send(f"⏰ Time's up! {interaction.user.mention}")

    # ----------------------------
    # 20. /convert
    # ----------------------------
    @app_commands.command(name="convert", description="Convert seconds to HH:MM:SS")
    async def convert(self, interaction: discord.Interaction, seconds: int):
        if seconds < 0:
            await interaction.response.send_message("❌ Seconds must be positive.")
            return
        formatted = str(datetime.timedelta(seconds=seconds))
        await interaction.response.send_message(f"⏱️ {seconds} seconds = {formatted}")

    # ----------------------------
    # Background loop for reminders
    # ----------------------------
    @tasks.loop(seconds=5)
    async def reminder_loop(self):
        if "reminders" not in self.data:
            return
        now = datetime.datetime.utcnow()
        for reminder in self.data["reminders"][:]:
            time_remind = datetime.datetime.fromisoformat(reminder["time"])
            if now >= time_remind:
                user = self.bot.get_user(int(reminder["user"]))
                if user:
                    try:
                        await user.send(f"⏰ Reminder: {reminder['message']}")
                    except:
                        pass
                self.data["reminders"].remove(reminder)
        save_data(self.data)

async def setup(bot):
    await bot.add_cog(Utility(bot), guild=discord.Object(id=GUILD_ID))
