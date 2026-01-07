import discord
from discord.ext import commands
from discord import app_commands
from config import GUILD_ID
import datetime

class Info(commands.Cog):
    """Info cog with 20 slash commands"""

    def __init__(self, bot):
        self.bot = bot

    # ----------------------------
    # 1. /userinfo
    # ----------------------------
    @app_commands.command(name="userinfo", description="Get detailed info about a user")
    async def userinfo(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        embed = discord.Embed(title=f"User Info - {member}", color=discord.Color.blue())
        embed.add_field(name="ID", value=member.id)
        embed.add_field(name="Username", value=str(member))
        embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"))
        embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"))
        embed.add_field(name="Top Role", value=member.top_role)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        await interaction.response.send_message(embed=embed)

    # ----------------------------
    # 2. /serverinfo
    # ----------------------------
    @app_commands.command(name="serverinfo", description="Get detailed info about the server")
    async def serverinfo(self, interaction: discord.Interaction):
        guild = interaction.guild
        embed = discord.Embed(title=f"Server Info - {guild.name}", color=discord.Color.green())
        embed.add_field(name="ID", value=guild.id)
        embed.add_field(name="Owner", value=guild.owner)
        embed.add_field(name="Member Count", value=guild.member_count)
        embed.add_field(name="Boosts", value=guild.premium_subscription_count)
        embed.add_field(name="Created At", value=guild.created_at.strftime("%Y-%m-%d %H:%M:%S"))
        embed.set_thumbnail(url=guild.icon.url if guild.icon else "")
        await interaction.response.send_message(embed=embed)

    # ----------------------------
    # 3. /roleinfo
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
    # 4. /botinfo
    # ----------------------------
    @app_commands.command(name="botinfo", description="Show information about the bot")
    async def botinfo(self, interaction: discord.Interaction):
        embed = discord.Embed(title=f"{self.bot.user} Info", color=discord.Color.teal())
        embed.add_field(name="ID", value=self.bot.user.id)
        embed.add_field(name="Latency", value=f"{round(self.bot.latency*1000)}ms")
        embed.add_field(name="Guilds", value=len(self.bot.guilds))
        embed.add_field(name="Users", value=len(self.bot.users))
        await interaction.response.send_message(embed=embed)

    # ----------------------------
    # 5. /avatar
    # ----------------------------
    @app_commands.command(name="avatar", description="Get a user's avatar")
    async def avatar(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        await interaction.response.send_message(member.avatar.url if member.avatar else member.default_avatar.url)

    # ----------------------------
    # 6. /servericon
    # ----------------------------
    @app_commands.command(name="servericon", description="Show the server icon")
    async def servericon(self, interaction: discord.Interaction):
        guild = interaction.guild
        await interaction.response.send_message(guild.icon.url if guild.icon else "No icon")

    # ----------------------------
    # 7. /emojilist
    # ----------------------------
    @app_commands.command(name="emojilist", description="Show all emojis in the server")
    async def emojilist(self, interaction: discord.Interaction):
        emojis = [str(e) for e in interaction.guild.emojis]
        await interaction.response.send_message(" ".join(emojis) if emojis else "No emojis in this server.")

    # ----------------------------
    # 8. /members
    # ----------------------------
    @app_commands.command(name="members", description="Show total member count")
    async def members(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"👥 Members: {interaction.guild.member_count}")

    # ----------------------------
    # 9. /channels
    # ----------------------------
    @app_commands.command(name="channels", description="Show all channels in the server")
    async def channels(self, interaction: discord.Interaction):
        channels = [channel.name for channel in interaction.guild.channels]
        await interaction.response.send_message(f"📂 Channels: {', '.join(channels)}")

    # ----------------------------
    # 10. /boosts
    # ----------------------------
    @app_commands.command(name="boosts", description="Show server boost info")
    async def boosts(self, interaction: discord.Interaction):
        guild = interaction.guild
        await interaction.response.send_message(f"✨ Boosts: {guild.premium_subscription_count}, Level: {guild.premium_tier}")

    # ----------------------------
    # 11. /joined
    # ----------------------------
    @app_commands.command(name="joined", description="Show when a user joined the server")
    async def joined(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        await interaction.response.send_message(f"{member.mention} joined on {member.joined_at.strftime('%Y-%m-%d %H:%M:%S')}")

    # ----------------------------
    # 12. /created
    # ----------------------------
    @app_commands.command(name="created", description="Show when a user's account was created")
    async def created(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        await interaction.response.send_message(f"{member.mention}'s account created on {member.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

    # ----------------------------
    # 13. /roles
    # ----------------------------
    @app_commands.command(name="roles", description="List all roles of a user")
    async def roles(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        roles = [role.name for role in member.roles if role.name != "@everyone"]
        await interaction.response.send_message(f"🏷️ Roles: {', '.join(roles)}")

    # ----------------------------
    # 14. /isbot
    # ----------------------------
    @app_commands.command(name="isbot", description="Check if user is a bot")
    async def isbot(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        await interaction.response.send_message(f"{member.mention} is a bot: {member.bot}")

    # ----------------------------
    # 15. /status
    # ----------------------------
    @app_commands.command(name="status", description="Get user's online status")
    async def status(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        await interaction.response.send_message(f"{member.mention} is currently {member.status}")

    # ----------------------------
    # 16. /activity
    # ----------------------------
    @app_commands.command(name="activity", description="Show user's activity")
    async def activity(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        activity = member.activity.name if member.activity else "No activity"
        await interaction.response.send_message(f"{member.mention} is doing: {activity}")

    # ----------------------------
    # 17. /nickname
    # ----------------------------
    @app_commands.command(name="nickname", description="Show user's nickname")
    async def nickname(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        nickname = member.nick if member.nick else member.name
        await interaction.response.send_message(f"{member.mention}'s nickname: {nickname}")

    # ----------------------------
    # 18. /botservers
    # ----------------------------
    @app_commands.command(name="botservers", description="Show number of servers the bot is in")
    async def botservers(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"🤖 Bot is in {len(self.bot.guilds)} servers")

    # ----------------------------
    # 19. /toprole
    # ----------------------------
    @app_commands.command(name="toprole", description="Show the top role of a user")
    async def toprole(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        await interaction.response.send_message(f"{member.mention}'s top role: {member.top_role}")

    # ----------------------------
    # 20. /avatarbanner
    # ----------------------------
    @app_commands.command(name="avatarbanner", description="Show user's banner")
    async def avatarbanner(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        if member.banner:
            await interaction.response.send_message(member.banner.url)
        else:
            await interaction.response.send_message("❌ User has no banner.")

async def setup(bot):
    await bot.add_cog(Info(bot), guild=discord.Object(id=GUILD_ID))
