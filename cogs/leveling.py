import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import random
from config import GUILD_ID

DATA_FILE = "leveling.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

class Leveling(commands.Cog):
    """Leveling system with 20+ slash commands"""

    def __init__(self, bot):
        self.bot = bot
        self.data = load_data()

    def ensure_user(self, user_id):
        user_id = str(user_id)
        self.data.setdefault(user_id, {"xp": 0, "level": 1})
        return user_id

    def xp_to_level(self, xp):
        # Simple leveling formula: level = int(xp**0.5)
        return int(xp ** 0.5)

    # 1. /rank
    @app_commands.command(name="rank", description="Show your rank")
    async def rank(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        user_id = self.ensure_user(member.id)
        xp = self.data[user_id]["xp"]
        level = self.data[user_id]["level"]
        await interaction.response.send_message(f"📊 {member.mention} is level {level} with {xp} XP")

    # 2. /top
    @app_commands.command(name="top", description="Show top 10 users")
    async def top(self, interaction: discord.Interaction):
        leaderboard = sorted(self.data.items(), key=lambda x: x[1]["xp"], reverse=True)
        msg = "\n".join([f"<@{uid}> - Level {info['level']} ({info['xp']} XP)" for uid,info in leaderboard[:10]])
        await interaction.response.send_message(f"🏆 Top 10 Users:\n{msg or 'No data yet.'}")

    # 3. /addxp
    @app_commands.command(name="addxp", description="Add XP to a user")
    async def addxp(self, interaction: discord.Interaction, member: discord.Member, xp: int):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Only admins can use this.", ephemeral=True)
            return
        user_id = self.ensure_user(member.id)
        self.data[user_id]["xp"] += xp
        self.data[user_id]["level"] = self.xp_to_level(self.data[user_id]["xp"])
        save_data(self.data)
        await interaction.response.send_message(f"✅ Added {xp} XP to {member.mention}")

    # 4. /removexp
    @app_commands.command(name="removexp", description="Remove XP from a user")
    async def removexp(self, interaction: discord.Interaction, member: discord.Member, xp: int):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Only admins can use this.", ephemeral=True)
            return
        user_id = self.ensure_user(member.id)
        self.data[user_id]["xp"] = max(0, self.data[user_id]["xp"] - xp)
        self.data[user_id]["level"] = self.xp_to_level(self.data[user_id]["xp"])
        save_data(self.data)
        await interaction.response.send_message(f"✅ Removed {xp} XP from {member.mention}")

    # 5. /setlevel
    @app_commands.command(name="setlevel", description="Set the level of a user")
    async def setlevel(self, interaction: discord.Interaction, member: discord.Member, level: int):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Only admins can use this.", ephemeral=True)
            return
        user_id = self.ensure_user(member.id)
        self.data[user_id]["level"] = level
        self.data[user_id]["xp"] = level**2
        save_data(self.data)
        await interaction.response.send_message(f"✅ Set {member.mention} to level {level}")

    # 6. /setxp
    @app_commands.command(name="setxp", description="Set XP of a user")
    async def setxp(self, interaction: discord.Interaction, member: discord.Member, xp: int):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Only admins can use this.", ephemeral=True)
            return
        user_id = self.ensure_user(member.id)
        self.data[user_id]["xp"] = xp
        self.data[user_id]["level"] = self.xp_to_level(xp)
        save_data(self.data)
        await interaction.response.send_message(f"✅ Set {member.mention} to {xp} XP")

    # 7. /xp
    @app_commands.command(name="xp", description="Check your XP")
    async def xp(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        user_id = self.ensure_user(member.id)
        await interaction.response.send_message(f"📈 {member.mention} has {self.data[user_id]['xp']} XP")

    # 8. /level
    @app_commands.command(name="level", description="Check your level")
    async def level(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        user_id = self.ensure_user(member.id)
        await interaction.response.send_message(f"⭐ {member.mention} is level {self.data[user_id]['level']}")

    # 9. /leaderboardxp
    @app_commands.command(name="leaderboardxp", description="Show top users by XP")
    async def leaderboardxp(self, interaction: discord.Interaction):
        leaderboard = sorted(self.data.items(), key=lambda x: x[1]["xp"], reverse=True)
        msg = "\n".join([f"<@{uid}> - {info['xp']} XP" for uid, info in leaderboard[:10]])
        await interaction.response.send_message(f"🏅 XP Leaderboard:\n{msg or 'No data'}")

    # 10. /leaderboardlevel
    @app_commands.command(name="leaderboardlevel", description="Show top users by level")
    async def leaderboardlevel(self, interaction: discord.Interaction):
        leaderboard = sorted(self.data.items(), key=lambda x: x[1]["level"], reverse=True)
        msg = "\n".join([f"<@{uid}> - Level {info['level']}" for uid, info in leaderboard[:10]])
        await interaction.response.send_message(f"🏅 Level Leaderboard:\n{msg or 'No data'}")

    # 11. /resetxp
    @app_commands.command(name="resetxp", description="Reset XP of a user")
    async def resetxp(self, interaction: discord.Interaction, member: discord.Member):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Only admins can use this.", ephemeral=True)
            return
        user_id = self.ensure_user(member.id)
        self.data[user_id]["xp"] = 0
        self.data[user_id]["level"] = 1
        save_data(self.data)
        await interaction.response.send_message(f"✅ Reset XP for {member.mention}")

    # 12. /resetlevel
    @app_commands.command(name="resetlevel", description="Reset level of a user")
    async def resetlevel(self, interaction: discord.Interaction, member: discord.Member):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Only admins can use this.", ephemeral=True)
            return
        user_id = self.ensure_user(member.id)
        self.data[user_id]["level"] = 1
        self.data[user_id]["xp"] = 0
        save_data(self.data)
        await interaction.response.send_message(f"✅ Reset level for {member.mention}")

    # 13. /awardxp
    @app_commands.command(name="awardxp", description="Award XP to all users")
    async def awardxp(self, interaction: discord.Interaction, xp: int):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Only admins can use this.", ephemeral=True)
            return
        for uid in self.data:
            self.data[uid]["xp"] += xp
            self.data[uid]["level"] = self.xp_to_level(self.data[uid]["xp"])
        save_data(self.data)
        await interaction.response.send_message(f"✅ Awarded {xp} XP to all users")

    # 14. /randomxp
    @app_commands.command(name="randomxp", description="Get random XP")
    async def randomxp(self, interaction: discord.Interaction):
        user_id = self.ensure_user(interaction.user.id)
        xp = random.randint(5, 25)
        self.data[user_id]["xp"] += xp
        self.data[user_id]["level"] = self.xp_to_level(self.data[user_id]["xp"])
        save_data(self.data)
        await interaction.response.send_message(f"🎲 You gained {xp} random XP!")

    # 15. /rankup
    @app_commands.command(name="rankup", description="Force a level up")
    async def rankup(self, interaction: discord.Interaction):
        user_id = self.ensure_user(interaction.user.id)
        self.data[user_id]["level"] += 1
        self.data[user_id]["xp"] = self.data[user_id]["level"]**2
        save_data(self.data)
        await interaction.response.send_message(f"⬆️ You ranked up to level {self.data[user_id]['level']}!")

    # 16. /leaderboardall
    @app_commands.command(name="leaderboardall", description="Top users by level + XP")
    async def leaderboardall(self, interaction: discord.Interaction):
        leaderboard = sorted(
            self.data.items(),
            key=lambda x: (x[1]["level"], x[1]["xp"]),
            reverse=True
        )
        msg = "\n".join([f"<@{uid}> - Level {info['level']} ({info['xp']} XP)" for uid, info in leaderboard[:10]])
        await interaction.response.send_message(f"🏆 Leaderboard:\n{msg or 'No data'}")

    # 17. /showxp
    @app_commands.command(name="showxp", description="Show your XP progress to next level")
    async def showxp(self, interaction: discord.Interaction):
        user_id = self.ensure_user(interaction.user.id)
        xp = self.data[user_id]["xp"]
        level = self.data[user_id]["level"]
        next_level_xp = (level+1)**2
        await interaction.response.send_message(f"📊 {interaction.user.mention} has {xp}/{next_level_xp} XP to next level")

    # 18. /showlevel
    @app_commands.command(name="showlevel", description="Show your current level")
    async def showlevel(self, interaction: discord.Interaction):
        user_id = self.ensure_user(interaction.user.id)
        await interaction.response.send_message(f"⭐ {interaction.user.mention} is level {self.data[user_id]['level']}")

    # 19. /resetall
    @app_commands.command(name="resetall", description="Reset all users' XP and levels")
    async def resetall(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Only admins can use this.", ephemeral=True)
            return
        for uid in self.data:
            self.data[uid]["xp"] = 0
            self.data[uid]["level"] = 1
        save_data(self.data)
        await interaction.response.send_message("✅ Reset XP and level for all users")

    # 20. /randomlevel
    @app_commands.command(name="randomlevel", description="Random level up yourself")
    async def randomlevel(self, interaction: discord.Interaction):
        user_id = self.ensure_user(interaction.user.id)
        gained = random.randint(0,2)
        self.data[user_id]["level"] += gained
        self.data[user_id]["xp"] = self.data[user_id]["level"]**2
        save_data(self.data)
        await interaction.response.send_message(f"🎲 You gained {gained} random level(s)! Now level {self.data[user_id]['level']}")

async def setup(bot):
    await bot.add_cog(Leveling(bot), guild=discord.Object(id=GUILD_ID))
