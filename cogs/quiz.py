import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import random
from config import GUILD_ID

DATA_FILE = "quiz_scores.json"
QUESTIONS_FILE = "quiz_questions.json"

# Load user scores
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Load questions
def load_questions():
    if os.path.exists(QUESTIONS_FILE):
        with open(QUESTIONS_FILE, "r") as f:
            return json.load(f)
    # Example questions if file does not exist
    sample_questions = [
        {"question": "What is the capital of France?", "options": ["Paris", "London", "Berlin", "Madrid"], "answer": "Paris"},
        {"question": "2 + 2 * 2 = ?", "options": ["4", "6", "8", "2"], "answer": "6"},
        {"question": "Which planet is known as the Red Planet?", "options": ["Mars", "Earth", "Venus", "Jupiter"], "answer": "Mars"}
    ]
    with open(QUESTIONS_FILE, "w") as f:
        json.dump(sample_questions, f, indent=4)
    return sample_questions

class Quiz(commands.Cog):
    """Interactive quiz game with score tracking"""

    def __init__(self, bot):
        self.bot = bot
        self.scores = load_data()
        self.questions = load_questions()

    # --------------------
    # Start a quiz
    # --------------------
    @app_commands.command(name="quiz", description="Start a quiz")
    async def quiz(self, interaction: discord.Interaction):
        question = random.choice(self.questions)
        options = question["options"]
        random.shuffle(options)

        embed = discord.Embed(title="❓ Quiz Time!", description=question["question"], color=discord.Color.blue())
        for i, option in enumerate(options, start=1):
            embed.add_field(name=f"Option {i}", value=option, inline=False)
        embed.set_footer(text="Reply with the option number (1-4) in chat.")

        await interaction.response.send_message(embed=embed)

        def check(m: discord.Message):
            return m.author == interaction.user and m.channel == interaction.channel and m.content in ["1", "2", "3", "4"]

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=30)
        except:
            await interaction.followup.send("⏰ Time's up! You didn't answer in time.", ephemeral=True)
            return

        choice = int(msg.content) - 1
        selected_option = options[choice]
        correct_answer = question["answer"]

        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        self.scores.setdefault(guild_id, {}).setdefault(user_id, {"score": 0})

        if selected_option == correct_answer:
            self.scores[guild_id][user_id]["score"] += 1
            save_data(self.scores)
            await interaction.followup.send(f"✅ Correct! Your score: {self.scores[guild_id][user_id]['score']}")
        else:
            await interaction.followup.send(f"❌ Incorrect. The correct answer was: **{correct_answer}**. Your score: {self.scores[guild_id][user_id]['score']}")

    # --------------------
    # Check score
    # --------------------
    @app_commands.command(name="quiz_score", description="Check your quiz score")
    async def quiz_score(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        score = self.scores.get(guild_id, {}).get(user_id, {}).get("score", 0)
        await interaction.response.send_message(f"📝 {interaction.user.mention}, your quiz score is {score}.")

    # --------------------
    # Quiz leaderboard
    # --------------------
    @app_commands.command(name="quiz_leaderboard", description="Show top 10 quiz scorers")
    async def quiz_leaderboard(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        guild_scores = self.scores.get(guild_id, {})
        if not guild_scores:
            await interaction.response.send_message("No quiz scores yet!")
            return
        sorted_scores = sorted(guild_scores.items(), key=lambda x: x[1]["score"], reverse=True)[:10]
        embed = discord.Embed(title="🏆 Quiz Leaderboard", color=discord.Color.gold())
        for i, (uid, info) in enumerate(sorted_scores, start=1):
            member = interaction.guild.get_member(int(uid))
            if member:
                embed.add_field(name=f"{i}. {member.display_name}", value=f"Score: {info['score']}", inline=False)
        await interaction.response.send_message(embed=embed)

    # --------------------
    # Reset score (admin)
    # --------------------
    @app_commands.command(name="quiz_reset", description="Reset a user's quiz score (Admin only)")
    @app_commands.checks.has_permissions(administrator=True)
    async def quiz_reset(self, interaction: discord.Interaction, member: discord.Member):
        guild_id = str(interaction.guild.id)
        user_id = str(member.id)
        if guild_id in self.scores and user_id in self.scores[guild_id]:
            self.scores[guild_id][user_id]["score"] = 0
            save_data(self.scores)
            await interaction.response.send_message(f"✅ {member.mention}'s quiz score has been reset.")
        else:
            await interaction.response.send_message(f"❌ {member.mention} has no quiz score.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Quiz(bot), guild=discord.Object(id=GUILD_ID))
