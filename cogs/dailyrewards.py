import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from datetime import datetime, timedelta
from config import GUILD_ID

DATA_FILE = "daily_rewards.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

class DailyRewards(commands.Cog):
    """Daily rewards system for server members"""

    def __init__(self, bot):
        self.bot = bot
        self.data = load_data()

    # --------------------
    # Claim daily reward
    # --------------------
    @app_commands.command(name="daily", description="Claim your daily reward")
    async def daily(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)

        self.data.setdefault(guild_id, {}).setdefault(user_id, {})

        last_claim_str = self.data[guild_id][user_id].get("last_claim")
        last_claim = datetime.strptime(last_claim_str, "%Y-%m-%d %H:%M:%S") if last_claim_str else None
        now = datetime.utcnow()

        if last_claim and now - last_claim < timedelta(hours=24):
            next_claim = last_claim + timedelta(hours=24)
            delta = next_claim - now
            hours, remainder = divmod(int(delta.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            await interaction.response.send_message(
                f"⏳ You already claimed your daily reward! Come back in {hours}h {minutes}m {seconds}s.",
                ephemeral=True
            )
            return

        # Reward logic
        base_reward = 100  # base coins
        streak = self.data[guild_id][user_id].get("streak", 0)
        streak += 1
        bonus = min(streak * 10, 100)  # bonus caps at 100
        total_reward = base_reward + bonus

        # Update user data
        self.data[guild_id][user_id]["last_claim"] = now.strftime("%Y-%m-%d %H:%M:%S")
        self.data[guild_id][user_id]["streak"] = streak
        coins = self.data[guild_id][user_id].get("coins", 0) + total_reward
        self.data[guild_id][user_id]["coins"] = coins

        save_data(self.data)
        await interaction.response.send_message(
            f"💰 You claimed **{total_reward} coins**! (Streak: {streak} days) Total coins: {coins}"
        )

    # --------------------
    # Check streak
    # --------------------
    @app_commands.command(name="streak", description="Check your current daily streak")
    async def streak(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        streak = self.data.get(guild_id, {}).get(user_id, {}).get("streak", 0)
        await interaction.response.send_message(f"🔥 Your current streak is {streak} days.")

    # --------------------
    # Check coins
    # --------------------
    @app_commands.command(name="coins", description="Check your total coins")
    async def coins(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        coins = self.data.get(guild_id, {}).get(user_id, {}).get("coins", 0)
        await interaction.response.send_message(f"💰 You have {coins} coins.")

    # --------------------
    # Reset streak (admin only)
    # --------------------
    @app_commands.command(name="reset_streak", description="Reset a user's streak (Admin only)")
    @app_commands.checks.has_permissions(administrator=True)
    async def reset_streak(self, interaction: discord.Interaction, member: discord.Member):
        guild_id = str(interaction.guild.id)
        user_id = str(member.id)
        if guild_id in self.data and user_id in self.data[guild_id]:
            self.data[guild_id][user_id]["streak"] = 0
            save_data(self.data)
            await interaction.response.send_message(f"✅ {member.mention}'s daily streak has been reset.")
        else:
            await interaction.response.send_message(f"❌ {member.mention} has no streak data.", ephemeral=True)

    # --------------------
    # Reset coins (admin only)
    # --------------------
    @app_commands.command(name="reset_coins", description="Reset a user's coins (Admin only)")
    @app_commands.checks.has_permissions(administrator=True)
    async def reset_coins(self, interaction: discord.Interaction, member: discord.Member):
        guild_id = str(interaction.guild.id)
        user_id = str(member.id)
        if guild_id in self.data and user_id in self.data[guild_id]:
            self.data[guild_id][user_id]["coins"] = 0
            save_data(self.data)
            await interaction.response.send_message(f"✅ {member.mention}'s coins have been reset.")
        else:
            await interaction.response.send_message(f"❌ {member.mention} has no coin data.", ephemeral=True)

    # --------------------
    # Leaderboard
    # --------------------
    @app_commands.command(name="daily_leaderboard", description="Show top 10 users by coins")
    async def daily_leaderboard(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        guild_data = self.data.get(guild_id, {})
        sorted_users = sorted(guild_data.items(), key=lambda x: x[1].get("coins", 0), reverse=True)[:10]
        if not sorted_users:
            await interaction.response.send_message("No daily reward data yet!")
            return

        embed = discord.Embed(title="🏆 Daily Coins Leaderboard", color=discord.Color.gold())
        for i, (uid, info) in enumerate(sorted_users, start=1):
            member = interaction.guild.get_member(int(uid))
            if member:
                embed.add_field(name=f"{i}. {member.display_name}", value=f"Coins: {info.get('coins',0)} | Streak: {info.get('streak',0)}", inline=False)
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(DailyRewards(bot), guild=discord.Object(id=GUILD_ID))
