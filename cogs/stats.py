import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from config import GUILD_ID

DATA_FILE = "stats.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

class Stats(commands.Cog):
    """Server and user statistics commands"""

    def __init__(self, bot):
        self.bot = bot
        self.data = load_data()

    # --------------------
    # 1. /server_info
    # --------------------
    @app_commands.command(name="server_info", description="Get server information")
    async def server_info(self, interaction: discord.Interaction):
        guild = interaction.guild
        embed = discord.Embed(title=guild.name, color=discord.Color.blurple())
        embed.add_field(name="ID", value=guild.id)
        embed.add_field(name="Owner", value=guild.owner)
        embed.add_field(name="Members", value=guild.member_count)
        embed.add_field(name="Roles", value=len(guild.roles))
        embed.add_field(name="Text Channels", value=len(guild.text_channels))
        embed.add_field(name="Voice Channels", value=len(guild.voice_channels))
        await interaction.response.send_message(embed=embed)

    # --------------------
    # 2. /user_info
    # --------------------
    @app_commands.command(name="user_info", description="Get info about a user")
    async def user_info(self, interaction: discord.Interaction, member: discord.Member):
        embed = discord.Embed(title=member.name, color=discord.Color.green())
        embed.add_field(name="ID", value=member.id)
        embed.add_field(name="Status", value=str(member.status))
        embed.add_field(name="Top Role", value=member.top_role)
        embed.add_field(name="Joined", value=member.joined_at.strftime("%Y-%m-%d"))
        embed.add_field(name="Created", value=member.created_at.strftime("%Y-%m-%d"))
        await interaction.response.send_message(embed=embed)

    # --------------------
    # 3. /total_members
    # --------------------
    @app_commands.command(name="total_members", description="Get total members in server")
    async def total_members(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"👥 Total members: {interaction.guild.member_count}")

    # --------------------
    # 4. /online_members
    # --------------------
    @app_commands.command(name="online_members", description="Get online members count")
    async def online_members(self, interaction: discord.Interaction):
        online = sum(1 for m in interaction.guild.members if m.status != discord.Status.offline)
        await interaction.response.send_message(f"🟢 Online members: {online}")

    # --------------------
    # 5. /offline_members
    # --------------------
    @app_commands.command(name="offline_members", description="Get offline members count")
    async def offline_members(self, interaction: discord.Interaction):
        offline = sum(1 for m in interaction.guild.members if m.status == discord.Status.offline)
        await interaction.response.send_message(f"⚫ Offline members: {offline}")

    # --------------------
    # 6. /text_channels
    # --------------------
    @app_commands.command(name="text_channels", description="Number of text channels")
    async def text_channels(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"💬 Text channels: {len(interaction.guild.text_channels)}")

    # --------------------
    # 7. /voice_channels
    # --------------------
    @app_commands.command(name="voice_channels", description="Number of voice channels")
    async def voice_channels(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"🎤 Voice channels: {len(interaction.guild.voice_channels)}")

    # --------------------
    # 8. /roles_count
    # --------------------
    @app_commands.command(name="roles_count", description="Number of roles in server")
    async def roles_count(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"🎭 Total roles: {len(interaction.guild.roles)}")

    # --------------------
    # 9. /emoji_count
    # --------------------
    @app_commands.command(name="emoji_count", description="Number of emojis in server")
    async def emoji_count(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"😊 Total emojis: {len(interaction.guild.emojis)}")

    # --------------------
    # 10. /boost_count
    # --------------------
    @app_commands.command(name="boost_count", description="Server boost level and count")
    async def boost_count(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"🚀 Boost level: {interaction.guild.premium_tier}, Boosts: {interaction.guild.premium_subscription_count}")

    # --------------------
    # 11. /joined_at
    # --------------------
    @app_commands.command(name="joined_at", description="See when a member joined")
    async def joined_at(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.send_message(f"{member.display_name} joined on {member.joined_at.strftime('%Y-%m-%d')}")

    # --------------------
    # 12. /created_at
    # --------------------
    @app_commands.command(name="created_at", description="See when a user created their account")
    async def created_at(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.send_message(f"{member.display_name} created their account on {member.created_at.strftime('%Y-%m-%d')}")

    # --------------------
    # 13. /top_roles
    # --------------------
    @app_commands.command(name="top_roles", description="Show top roles in server")
    async def top_roles(self, interaction: discord.Interaction):
        roles = sorted(interaction.guild.roles, key=lambda r: r.position, reverse=True)
        roles_list = ", ".join([r.name for r in roles[:10]])
        await interaction.response.send_message(f"🎭 Top roles: {roles_list}")

    # --------------------
    # 14. /server_age
    # --------------------
    @app_commands.command(name="server_age", description="How old the server is")
    async def server_age(self, interaction: discord.Interaction):
        created = interaction.guild.created_at
        delta = (discord.utils.utcnow() - created).days
        await interaction.response.send_message(f"📅 Server age: {delta} days")

    # --------------------
    # 15. /member_status
    # --------------------
    @app_commands.command(name="member_status", description="Show number of members by status")
    async def member_status(self, interaction: discord.Interaction):
        statuses = {s: sum(1 for m in interaction.guild.members if m.status == s) for s in discord.Status}
        msg = "\n".join([f"{status.name}: {count}" for status, count in statuses.items()])
        await interaction.response.send_message(f"📊 Member statuses:\n{msg}")

    # --------------------
    # 16. /bots_count
    # --------------------
    @app_commands.command(name="bots_count", description="Number of bots in server")
    async def bots_count(self, interaction: discord.Interaction):
        bots = sum(1 for m in interaction.guild.members if m.bot)
        await interaction.response.send_message(f"🤖 Bots: {bots}")

    # --------------------
    # 17. /humans_count
    # --------------------
    @app_commands.command(name="humans_count", description="Number of human members in server")
    async def humans_count(self, interaction: discord.Interaction):
        humans = sum(1 for m in interaction.guild.members if not m.bot)
        await interaction.response.send_message(f"🧑 Humans: {humans}")

    # --------------------
    # 18. /largest_role
    # --------------------
    @app_commands.command(name="largest_role", description="Role with most members")
    async def largest_role(self, interaction: discord.Interaction):
        largest = max(interaction.guild.roles, key=lambda r: len(r.members))
        await interaction.response.send_message(f"🏅 Largest role: {largest.name} ({len(largest.members)} members)")

    # --------------------
    # 19. /smallest_role
    # --------------------
    @app_commands.command(name="smallest_role", description="Role with least members")
    async def smallest_role(self, interaction: discord.Interaction):
        smallest = min(interaction.guild.roles, key=lambda r: len(r.members))
        await interaction.response.send_message(f"🔹 Smallest role: {smallest.name} ({len(smallest.members)} members)")

    # --------------------
    # 20. /server_region
    # --------------------
    @app_commands.command(name="server_region", description="Show server region or location")
    async def server_region(self, interaction: discord.Interaction):
        region = getattr(interaction.guild, "region", "Automatic")
        await interaction.response.send_message(f"🌐 Server region: {region}")


async def setup(bot):
    await bot.add_cog(Stats(bot), guild=discord.Object(id=GUILD_ID))
