import discord
from discord.ext import commands
from discord import app_commands
from config import GUILD_ID, OWNER_ID

# In-memory anti-raid toggle; can be saved to JSON/db later
anti_raid_enabled = False

def owner_only():
    """Check if the user is the bot owner"""
    async def predicate(interaction: discord.Interaction):
        return interaction.user.id == OWNER_ID
    return app_commands.check(predicate)

class Admin(commands.Cog):
    """Fully functional admin commands"""

    def __init__(self, bot):
        self.bot = bot

    # ----------------------------
    # BOT MANAGEMENT
    # ----------------------------
    @app_commands.command(name="shutdown", description="Shut down the bot")
    @owner_only()
    async def shutdown(self, interaction: discord.Interaction):
        await interaction.response.send_message("🛑 Shutting down bot...", ephemeral=True)
        await self.bot.close()

    @app_commands.command(name="restart", description="Restart the bot (reconnects)")
    @owner_only()
    async def restart(self, interaction: discord.Interaction):
        await interaction.response.send_message("🔄 Restarting bot...", ephemeral=True)
        await self.bot.close()
        # Bot hosting service should handle auto-restart

    # ----------------------------
    # ROLE MANAGEMENT
    # ----------------------------
    @app_commands.command(name="createrole", description="Create a new role")
    @owner_only()
    async def createrole(self, interaction: discord.Interaction, name: str, color: discord.Color = discord.Color.default()):
        guild = interaction.guild
        role = await guild.create_role(name=name, color=color)
        await interaction.response.send_message(f"✅ Role `{role.name}` created.")

    @app_commands.command(name="deleterole", description="Delete a role")
    @owner_only()
    async def deleterole(self, interaction: discord.Interaction, role: discord.Role):
        await role.delete()
        await interaction.response.send_message(f"❌ Role `{role.name}` deleted.")

    @app_commands.command(name="giverole", description="Give a role to a member")
    @owner_only()
    async def giverole(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role):
        await member.add_roles(role)
        await interaction.response.send_message(f"✅ {member.mention} was given role `{role.name}`.")

    @app_commands.command(name="takerole", description="Remove a role from a member")
    @owner_only()
    async def takerole(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role):
        await member.remove_roles(role)
        await interaction.response.send_message(f"❌ {role.name} removed from {member.mention}.")

    # ----------------------------
    # CHANNEL MANAGEMENT
    # ----------------------------
    @app_commands.command(name="createchannel", description="Create a text or voice channel")
    @owner_only()
    async def createchannel(self, interaction: discord.Interaction, name: str, channel_type: str = "text"):
        guild = interaction.guild
        if channel_type.lower() == "text":
            channel = await guild.create_text_channel(name)
        elif channel_type.lower() == "voice":
            channel = await guild.create_voice_channel(name)
        else:
            await interaction.response.send_message("❌ Invalid channel type. Use `text` or `voice`.", ephemeral=True)
            return
        await interaction.response.send_message(f"✅ {channel_type.title()} channel `{name}` created.")

    @app_commands.command(name="deletechannel", description="Delete a channel")
    @owner_only()
    async def deletechannel(self, interaction: discord.Interaction, channel: discord.abc.GuildChannel):
        await channel.delete()
        await interaction.response.send_message(f"❌ Channel `{channel.name}` deleted.")

    @app_commands.command(name="renamechannel", description="Rename a channel")
    @owner_only()
    async def renamechannel(self, interaction: discord.Interaction, channel: discord.abc.GuildChannel, new_name: str):
        await channel.edit(name=new_name)
        await interaction.response.send_message(f"✏️ Channel renamed to `{new_name}`.")

    # ----------------------------
    # SERVER SETTINGS
    # ----------------------------
    @app_commands.command(name="setservername", description="Change server name")
    @owner_only()
    async def setservername(self, interaction: discord.Interaction, name: str):
        await interaction.guild.edit(name=name)
        await interaction.response.send_message(f"✅ Server name changed to `{name}`.")

    @app_commands.command(name="setservericon", description="Change server icon")
    @owner_only()
    async def setservericon(self, interaction: discord.Interaction, icon: discord.Attachment):
        icon_bytes = await icon.read()
        await interaction.guild.edit(icon=icon_bytes)
        await interaction.response.send_message("✅ Server icon updated.")

    @app_commands.command(name="setverificationlevel", description="Set server verification level (0-4)")
    @owner_only()
    async def setverificationlevel(self, interaction: discord.Interaction, level: int):
        if level < 0 or level > 4:
            await interaction.response.send_message("❌ Verification level must be 0-4", ephemeral=True)
            return
        await interaction.guild.edit(verification_level=discord.VerificationLevel(level))
        await interaction.response.send_message(f"✅ Server verification level set to `{level}`.")

    # ----------------------------
    # MODERATION
    # ----------------------------
    @app_commands.command(name="ban", description="Ban a member")
    @owner_only()
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        await member.ban(reason=reason)
        await interaction.response.send_message(f"🔨 Banned {member.mention} for: {reason}")

    @app_commands.command(name="kick", description="Kick a member")
    @owner_only()
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        await member.kick(reason=reason)
        await interaction.response.send_message(f"👢 Kicked {member.mention} for: {reason}")

    # ----------------------------
    # ANTI-RAID TOGGLE
    # ----------------------------
    @app_commands.command(name="antiraid", description="Enable or disable anti-raid")
    @owner_only()
    async def antiraid(self, interaction: discord.Interaction, status: bool):
        global anti_raid_enabled
        anti_raid_enabled = status
        await interaction.response.send_message(f"🛡️ Anti-raid protection is now `{status}`.")

async def setup(bot):
    await bot.add_cog(Admin(bot), guild=discord.Object(id=GUILD_ID))
