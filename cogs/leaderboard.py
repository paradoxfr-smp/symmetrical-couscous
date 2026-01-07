import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from config import GUILD_ID

# Load JSON data files
LEVEL_FILE = "leveling.json"
ECON_FILE = "economy.json"
VOICE_FILE = "voice_data.json"
SOCIAL_FILE = "social_data.json"

def load_json(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return {}

class Leaderboard(commands.Cog):
    """Server-wide leaderboards"""

    def __init__(self, bot):
        self.bot = bot

    # --------------------
    # Leveling leaderboard
    # --------------------
    @app_commands.command(name="level_leaderboard", description="Show top 10 users by level")
    async def level_leaderboard(self, interaction: discord.Interaction):
        data = load_json(LEVEL_FILE).get(str(interaction.guild.id), {})
        sorted_users = sorted(data.items(), key=lambda x: x[1].get("level", 0), reverse=True)[:10]
        if not sorted_users:
            await interaction.response.send_message("No leveling data yet!")
            return
        embed = discord.Embed(title="🏆 Level Leaderboard", color=discord.Color.gold())
        for i, (uid, info) in enumerate(sorted_users, start=1):
            member = interaction.guild.get_member(int(uid))
            if member:
                embed.add_field(name=f"{i}. {member.display_name}", value=f"Level: {info.get('level',0)} XP: {info.get('xp',0)}", inline=False)
        await interaction.response.send_message(embed=embed)

    # --------------------
    # Economy leaderboard
    # --------------------
    @app_commands.command(name="money_leaderboard", description="Top 10 richest users")
    async def money_leaderboard(self, interaction: discord.Interaction):
        data = load_json(ECON_FILE).get(str(interaction.guild.id), {})
        sorted_users = sorted(data.items(), key=lambda x: x[1].get("balance", 0), reverse=True)[:10]
        if not sorted_users:
            await interaction.response.send_message("No economy data yet!")
            return
        embed = discord.Embed(title="💰 Money Leaderboard", color=discord.Color.green())
        for i, (uid, info) in enumerate(sorted_users, start=1):
            member = interaction.guild.get_member(int(uid))
            if member:
                embed.add_field(name=f"{i}. {member.display_name}", value=f"Balance: {info.get('balance',0)}", inline=False)
        await interaction.response.send_message(embed=embed)

    # --------------------
    # Voice leaderboard
    # --------------------
    @app_commands.command(name="vc_leaderboard", description="Top 10 users by voice time")
    async def vc_leaderboard(self, interaction: discord.Interaction):
        data = load_json(VOICE_FILE).get(str(interaction.guild.id), {})
        sorted_users = sorted(data.items(), key=lambda x: x[1].get("voice_time", 0), reverse=True)[:10]
        if not sorted_users:
            await interaction.response.send_message("No voice data yet!")
            return
        embed = discord.Embed(title="🎧 VC Leaderboard", color=discord.Color.blurple())
        for i, (uid, info) in enumerate(sorted_users, start=1):
            member = interaction.guild.get_member(int(uid))
            if member:
                minutes = info.get("voice_time", 0)
                embed.add_field(name=f"{i}. {member.display_name}", value=f"Time: {minutes} min", inline=False)
        await interaction.response.send_message(embed=embed)

    # --------------------
    # Social leaderboard
    # --------------------
    @app_commands.command(name="social_leaderboard", description="Top 10 users by social interactions")
    async def social_leaderboard(self, interaction: discord.Interaction):
        data = load_json(SOCIAL_FILE).get(str(interaction.guild.id), {})
        sorted_users = sorted(data.items(), key=lambda x: x[1].get("interactions", 0), reverse=True)[:10]
        if not sorted_users:
            await interaction.response.send_message("No social data yet!")
            return
        embed = discord.Embed(title="🌐 Social Leaderboard", color=discord.Color.purple())
        for i, (uid, info) in enumerate(sorted_users, start=1):
            member = interaction.guild.get_member(int(uid))
            if member:
                embed.add_field(name=f"{i}. {member.display_name}", value=f"Interactions: {info.get('interactions',0)}", inline=False)
        await interaction.response.send_message(embed=embed)

    # --------------------
    # Combined leaderboard
    # --------------------
    @app_commands.command(name="combined_leaderboard", description="Top 10 users by total points (level + money + VC time + social)")
    async def combined_leaderboard(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        leveling = load_json(LEVEL_FILE).get(guild_id, {})
        economy = load_json(ECON_FILE).get(guild_id, {})
        voice = load_json(VOICE_FILE).get(guild_id, {})
        social = load_json(SOCIAL_FILE).get(guild_id, {})

        scores = {}
        for uid in set(list(leveling.keys()) + list(economy.keys()) + list(voice.keys()) + list(social.keys())):
            lvl = leveling.get(uid, {}).get("level", 0)
            money = economy.get(uid, {}).get("balance", 0)
            vc_time = voice.get(uid, {}).get("voice_time", 0)
            social_int = social.get(uid, {}).get("interactions", 0)
            scores[uid] = lvl + money + vc_time + social_int

        sorted_users = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:10]
        if not sorted_users:
            await interaction.response.send_message("No leaderboard data yet!")
            return
        embed = discord.Embed(title="🏆 Combined Leaderboard", color=discord.Color.gold())
        for i, (uid, score) in enumerate(sorted_users, start=1):
            member = interaction.guild.get_member(int(uid))
            if member:
                embed.add_field(name=f"{i}. {member.display_name}", value=f"Total Score: {score}", inline=False)
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Leaderboard(bot), guild=discord.Object(id=GUILD_ID))
