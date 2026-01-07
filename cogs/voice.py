import discord
from discord.ext import commands, tasks
from discord import app_commands, ui
import json
import os
from datetime import datetime, timedelta
from config import GUILD_ID

DATA_FILE = "voice_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

class Voice(commands.Cog):
    """Full-featured voice management, tracking, and VC panel system"""

    def __init__(self, bot):
        self.bot = bot
        self.data = load_data()
        self.temp_channels = {}  # guild_id: {channel_id: owner_id}
        self.track_voice.start()
        self.cleanup.start()

    def cog_unload(self):
        self.track_voice.cancel()
        self.cleanup.cancel()

    # --------------------
    # Track voice time
    # --------------------
    @tasks.loop(seconds=60)
    async def track_voice(self):
        for guild in self.bot.guilds:
            guild_id = str(guild.id)
            for member in guild.members:
                if member.voice and member.voice.channel:
                    user_id = str(member.id)
                    self.data.setdefault(guild_id, {}).setdefault(user_id, {}).setdefault("voice_time", 0)
                    self.data[guild_id][user_id]["voice_time"] += 1
        save_data(self.data)

    # --------------------
    # Cleanup empty temp channels
    # --------------------
    @tasks.loop(seconds=60)
    async def cleanup(self):
        for guild_id, channels in list(self.temp_channels.items()):
            for channel_id, owner_id in list(channels.items()):
                guild = self.bot.get_guild(int(guild_id))
                if not guild:
                    continue
                channel = guild.get_channel(channel_id)
                if not channel:
                    self.temp_channels[guild_id].pop(channel_id)
                    continue
                if len(channel.members) == 0:
                    await channel.delete()
                    self.temp_channels[guild_id].pop(channel_id)

    @cleanup.before_loop
    async def before_cleanup(self):
        await self.bot.wait_until_ready()

    # --------------------
    # VC Panel Command
    # --------------------
    @app_commands.command(name="vc_panel", description="Send the VC panel")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def vc_panel(self, interaction: discord.Interaction):
        view = VCPanelView(self.bot)
        embed = discord.Embed(
            title="🎵 Voice Channel Panel",
            description="Click the button below to create your own temporary VC!",
            color=discord.Color.blurple()
        )
        await interaction.response.send_message(embed=embed, view=view)

    # --------------------
    # VC Stats & Leaderboard
    # --------------------
    @app_commands.command(name="vc_stats", description="Show your VC time")
    async def vc_stats(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        time_min = self.data.get(guild_id, {}).get(user_id, {}).get("voice_time", 0)
        await interaction.response.send_message(f"⏱️ You have spent {time_min} minutes in VC")

    @app_commands.command(name="vc_top", description="Show top VC users")
    async def vc_top(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        users = self.data.get(guild_id, {})
        sorted_users = sorted(users.items(), key=lambda x: x[1].get("voice_time", 0), reverse=True)[:10]
        msg = "\n".join([f"{interaction.guild.get_member(int(uid))}: {u['voice_time']} min" for uid,u in sorted_users])
        await interaction.response.send_message(f"🏆 Top VC users:\n{msg}")

    # --------------------
    # Voice management commands
    # --------------------
    @app_commands.command(name="vc_mute", description="Mute a user in VC")
    async def vc_mute(self, interaction: discord.Interaction, member: discord.Member):
        if member.voice:
            await member.edit(mute=True)
            await interaction.response.send_message(f"🔇 {member.display_name} muted")
        else:
            await interaction.response.send_message(f"{member.display_name} is not in VC", ephemeral=True)

    @app_commands.command(name="vc_unmute", description="Unmute a user in VC")
    async def vc_unmute(self, interaction: discord.Interaction, member: discord.Member):
        if member.voice:
            await member.edit(mute=False)
            await interaction.response.send_message(f"🔊 {member.display_name} unmuted")
        else:
            await interaction.response.send_message(f"{member.display_name} is not in VC", ephemeral=True)

    @app_commands.command(name="vc_deaf", description="Deafen a user in VC")
    async def vc_deaf(self, interaction: discord.Interaction, member: discord.Member):
        if member.voice:
            await member.edit(deafen=True)
            await interaction.response.send_message(f"🛑 {member.display_name} deafened")
        else:
            await interaction.response.send_message(f"{member.display_name} is not in VC", ephemeral=True)

    @app_commands.command(name="vc_undeaf", description="Undeafen a user in VC")
    async def vc_undeaf(self, interaction: discord.Interaction, member: discord.Member):
        if member.voice:
            await member.edit(deafen=False)
            await interaction.response.send_message(f"✅ {member.display_name} undeafened")
        else:
            await interaction.response.send_message(f"{member.display_name} is not in VC", ephemeral=True)

    @app_commands.command(name="vc_move", description="Move a member to a VC")
    async def vc_move(self, interaction: discord.Interaction, member: discord.Member, channel: discord.VoiceChannel):
        if member.voice:
            await member.move_to(channel)
            await interaction.response.send_message(f"✅ Moved {member.display_name} to {channel.name}")
        else:
            await interaction.response.send_message(f"{member.display_name} is not in VC", ephemeral=True)

    @app_commands.command(name="vc_lock", description="Lock a VC (deny connect)")
    async def vc_lock(self, interaction: discord.Interaction, channel: discord.VoiceChannel):
        await channel.set_permissions(interaction.guild.default_role, connect=False)
        await interaction.response.send_message(f"🔒 Locked VC {channel.name}")

    @app_commands.command(name="vc_unlock", description="Unlock a VC")
    async def vc_unlock(self, interaction: discord.Interaction, channel: discord.VoiceChannel):
        await channel.set_permissions(interaction.guild.default_role, connect=True)
        await interaction.response.send_message(f"🔓 Unlocked VC {channel.name}")

    @app_commands.command(name="vc_rename", description="Rename a VC")
    async def vc_rename(self, interaction: discord.Interaction, channel: discord.VoiceChannel, new_name: str):
        await channel.edit(name=new_name)
        await interaction.response.send_message(f"✅ VC renamed to {new_name}")

    @app_commands.command(name="vc_limit", description="Set user limit for VC")
    async def vc_limit(self, interaction: discord.Interaction, channel: discord.VoiceChannel, limit: int):
        await channel.edit(user_limit=limit)
        await interaction.response.send_message(f"✅ VC {channel.name} user limit set to {limit}")

    @app_commands.command(name="vc_all_mute", description="Mute all members in VC")
    async def vc_all_mute(self, interaction: discord.Interaction, channel: discord.VoiceChannel):
        for member in channel.members:
            await member.edit(mute=True)
        await interaction.response.send_message(f"🔇 All members muted in {channel.name}")

    @app_commands.command(name="vc_all_unmute", description="Unmute all members in VC")
    async def vc_all_unmute(self, interaction: discord.Interaction, channel: discord.VoiceChannel):
        for member in channel.members:
            await member.edit(mute=False)
        await interaction.response.send_message(f"🔊 All members unmuted in {channel.name}")

    @app_commands.command(name="vc_disconnect_all", description="Disconnect all members from VC")
    async def vc_disconnect_all(self, interaction: discord.Interaction, channel: discord.VoiceChannel):
        for member in channel.members:
            await member.move_to(None)
        await interaction.response.send_message(f"✅ All members disconnected from {channel.name}")


# --------------------
# VC Panel View
# --------------------
class VCPanelView(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @ui.button(label="Create Temporary VC", style=discord.ButtonStyle.green, custom_id="create_vc")
    async def create_vc(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        # Create temp VC
        channel_name = f"{interaction.user.display_name}'s VC"
        temp_channel = await guild.create_voice_channel(channel_name)
        # Save channel owner
        cog: Voice = self.bot.get_cog("Voice")
        cog.temp_channels.setdefault(str(guild.id), {})[temp_channel.id] = interaction.user.id
        # Move user into VC
        if interaction.user.voice:
            await interaction.user.move_to(temp_channel)
        await interaction.response.send_message(f"✅ Temporary VC `{channel_name}` created!", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Voice(bot), guild=discord.Object(id=GUILD_ID))
