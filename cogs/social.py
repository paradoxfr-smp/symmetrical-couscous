import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from config import GUILD_ID

DATA_FILE = "social_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

class Social(commands.Cog):
    """Social and interactive community commands"""

    def __init__(self, bot):
        self.bot = bot
        self.data = load_data()

    # --------------------
    # 1. /hug
    # --------------------
    @app_commands.command(name="hug", description="Hug another member")
    async def hug(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.send_message(f"🤗 {interaction.user.mention} hugged {member.mention}!")

    # --------------------
    # 2. /kiss
    # --------------------
    @app_commands.command(name="kiss", description="Kiss another member")
    async def kiss(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.send_message(f"😘 {interaction.user.mention} kissed {member.mention}!")

    # --------------------
    # 3. /slap
    # --------------------
    @app_commands.command(name="slap", description="Slap another member")
    async def slap(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.send_message(f"👋 {interaction.user.mention} slapped {member.mention}!")

    # --------------------
    # 4. /poke
    # --------------------
    @app_commands.command(name="poke", description="Poke another member")
    async def poke(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.send_message(f"👉 {interaction.user.mention} poked {member.mention}!")

    # --------------------
    # 5. /pat
    # --------------------
    @app_commands.command(name="pat", description="Pat another member")
    async def pat(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.send_message(f"🖐️ {interaction.user.mention} patted {member.mention}!")

    # --------------------
    # 6. /cuddle
    # --------------------
    @app_commands.command(name="cuddle", description="Cuddle with another member")
    async def cuddle(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.send_message(f"❤️ {interaction.user.mention} cuddled with {member.mention}!")

    # --------------------
    # 7. /highfive
    # --------------------
    @app_commands.command(name="highfive", description="High-five another member")
    async def highfive(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.send_message(f"✋ {interaction.user.mention} high-fived {member.mention}!")

    # --------------------
    # 8. /wink
    # --------------------
    @app_commands.command(name="wink", description="Wink at another member")
    async def wink(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.send_message(f"😉 {interaction.user.mention} winked at {member.mention}!")

    # --------------------
    # 9. /feed
    # --------------------
    @app_commands.command(name="feed", description="Feed another member")
    async def feed(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.send_message(f"🍎 {interaction.user.mention} fed {member.mention}!")

    # --------------------
    # 10. /slumber
    # --------------------
    @app_commands.command(name="slumber", description="Sleep together (fun)")
    async def slumber(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.send_message(f"😴 {interaction.user.mention} is sleeping next to {member.mention}!")

    # --------------------
    # 11. /compliment
    # --------------------
    @app_commands.command(name="compliment", description="Give a compliment to another member")
    async def compliment(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.send_message(f"🌟 {interaction.user.mention} says: {member.display_name}, you are amazing!")

    # --------------------
    # 12. /challenge
    # --------------------
    @app_commands.command(name="challenge", description="Challenge another member to a game")
    async def challenge(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.send_message(f"⚔️ {interaction.user.mention} challenged {member.mention} to a duel!")

    # --------------------
    # 13. /flirt
    # --------------------
    @app_commands.command(name="flirt", description="Flirt with another member")
    async def flirt(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.send_message(f"💌 {interaction.user.mention} flirted with {member.mention}!")

    # --------------------
    # 14. /share
    # --------------------
    @app_commands.command(name="share", description="Share an item or gift with another member")
    async def share(self, interaction: discord.Interaction, member: discord.Member, item: str):
        await interaction.response.send_message(f"🎁 {interaction.user.mention} shared {item} with {member.mention}!")

    # --------------------
    # 15. /trade
    # --------------------
    @app_commands.command(name="trade", description="Trade items with another member")
    async def trade(self, interaction: discord.Interaction, member: discord.Member, item: str):
        await interaction.response.send_message(f"🔄 {interaction.user.mention} traded {item} with {member.mention}!")

    # --------------------
    # 16. /invite_friend
    # --------------------
    @app_commands.command(name="invite_friend", description="Invite a member to an event or game")
    async def invite_friend(self, interaction: discord.Interaction, member: discord.Member, event: str):
        await interaction.response.send_message(f"📩 {interaction.user.mention} invited {member.mention} to {event}!")

    # --------------------
    # 17. /greet
    # --------------------
    @app_commands.command(name="greet", description="Greet another member")
    async def greet(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.send_message(f"👋 {interaction.user.mention} says hello to {member.mention}!")

    # --------------------
    # 18. /cheer
    # --------------------
    @app_commands.command(name="cheer", description="Cheer another member")
    async def cheer(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.send_message(f"🎉 {interaction.user.mention} cheers for {member.mention}!")

    # --------------------
    # 19. /support
    # --------------------
    @app_commands.command(name="support", description="Support another member")
    async def support(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.send_message(f"💪 {interaction.user.mention} supports {member.mention}!")

    # --------------------
    # 20. /friend_request
    # --------------------
    @app_commands.command(name="friend_request", description="Send a friend request to another member")
    async def friend_request(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.send_message(f"🤝 {interaction.user.mention} sent a friend request to {member.mention}!")


async def setup(bot):
    await bot.add_cog(Social(bot), guild=discord.Object(id=GUILD_ID))
