import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import os
import random
from config import GUILD_ID

DATA_FILE = "trivia.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"questions": {}, "leaderboard": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

class Trivia(commands.Cog):
    """Trivia system with 20 commands"""

    def __init__(self, bot):
        self.bot = bot
        self.data = load_data()
        self.active_trivia = {}  # guild_id: question

    # ----------------------------
    # 1. /add_question
    # ----------------------------
    @app_commands.command(name="add_question", description="Add a trivia question")
    async def add_question(self, interaction: discord.Interaction, category: str, question: str, answer: str):
        guild_id = str(interaction.guild.id)
        self.data.setdefault("questions", {}).setdefault(guild_id, {}).setdefault(category, []).append({
            "question": question,
            "answer": answer
        })
        save_data(self.data)
        await interaction.response.send_message(f"✅ Question added to category `{category}`")

    # ----------------------------
    # 2. /remove_question
    # ----------------------------
    @app_commands.command(name="remove_question", description="Remove a trivia question by index")
    async def remove_question(self, interaction: discord.Interaction, category: str, index: int):
        guild_id = str(interaction.guild.id)
        questions = self.data.get("questions", {}).get(guild_id, {}).get(category, [])
        if 0 <= index-1 < len(questions):
            removed = questions.pop(index-1)
            save_data(self.data)
            await interaction.response.send_message(f"✅ Removed question: {removed['question']}")
        else:
            await interaction.response.send_message("❌ Invalid index.", ephemeral=True)

    # ----------------------------
    # 3. /list_questions
    # ----------------------------
    @app_commands.command(name="list_questions", description="List all questions in a category")
    async def list_questions(self, interaction: discord.Interaction, category: str):
        guild_id = str(interaction.guild.id)
        questions = self.data.get("questions", {}).get(guild_id, {}).get(category, [])
        if questions:
            msg = "\n".join(f"{i+1}. {q['question']}" for i, q in enumerate(questions))
            await interaction.response.send_message(f"Questions in `{category}`:\n{msg}")
        else:
            await interaction.response.send_message("No questions in this category.", ephemeral=True)

    # ----------------------------
    # 4. /start_trivia
    # ----------------------------
    @app_commands.command(name="start_trivia", description="Start a trivia round")
    async def start_trivia(self, interaction: discord.Interaction, category: str):
        guild_id = str(interaction.guild.id)
        questions = self.data.get("questions", {}).get(guild_id, {}).get(category, [])
        if not questions:
            await interaction.response.send_message("❌ No questions in this category.", ephemeral=True)
            return
        question = random.choice(questions)
        self.active_trivia[guild_id] = question
        await interaction.response.send_message(f"❓ Trivia Question: {question['question']}")

    # ----------------------------
    # 5. /answer
    # ----------------------------
    @app_commands.command(name="answer", description="Answer the active trivia question")
    async def answer(self, interaction: discord.Interaction, response: str):
        guild_id = str(interaction.guild.id)
        question = self.active_trivia.get(guild_id)
        if not question:
            await interaction.response.send_message("❌ No active trivia question.", ephemeral=True)
            return
        if response.lower() == question["answer"].lower():
            user_id = str(interaction.user.id)
            self.data.setdefault("leaderboard", {}).setdefault(guild_id, {}).setdefault(user_id, 0)
            self.data["leaderboard"][guild_id][user_id] += 1
            save_data(self.data)
            self.active_trivia.pop(guild_id)
            await interaction.response.send_message(f"✅ Correct! {interaction.user.mention} now has {self.data['leaderboard'][guild_id][user_id]} points.")
        else:
            await interaction.response.send_message("❌ Incorrect. Try again!")

    # ----------------------------
    # 6. /leaderboard
    # ----------------------------
    @app_commands.command(name="leaderboard", description="Show trivia leaderboard")
    async def leaderboard(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        leaderboard = self.data.get("leaderboard", {}).get(guild_id, {})
        if not leaderboard:
            await interaction.response.send_message("No leaderboard yet.", ephemeral=True)
            return
        sorted_board = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)
        msg = "\n".join(f"<@{user_id}>: {score} points" for user_id, score in sorted_board)
        await interaction.response.send_message(f"🏆 Trivia Leaderboard:\n{msg}")

    # ----------------------------
    # 7. /reset_leaderboard
    # ----------------------------
    @app_commands.command(name="reset_leaderboard", description="Reset trivia leaderboard")
    async def reset_leaderboard(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        self.data.setdefault("leaderboard", {})[guild_id] = {}
        save_data(self.data)
        await interaction.response.send_message("✅ Leaderboard reset.")

    # ----------------------------
    # 8. /categories
    # ----------------------------
    @app_commands.command(name="categories", description="List trivia categories")
    async def categories(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        categories = list(self.data.get("questions", {}).get(guild_id, {}).keys())
        if categories:
            await interaction.response.send_message(f"Categories: {', '.join(categories)}")
        else:
            await interaction.response.send_message("No categories available.", ephemeral=True)

    # ----------------------------
    # 9. /question_count
    # ----------------------------
    @app_commands.command(name="question_count", description="Show number of questions in a category")
    async def question_count(self, interaction: discord.Interaction, category: str):
        guild_id = str(interaction.guild.id)
        count = len(self.data.get("questions", {}).get(guild_id, {}).get(category, []))
        await interaction.response.send_message(f"Category `{category}` has {count} questions.")

    # ----------------------------
    # 10. /random_question
    # ----------------------------
    @app_commands.command(name="random_question", description="Get a random trivia question without starting a game")
    async def random_question(self, interaction: discord.Interaction, category: str):
        guild_id = str(interaction.guild.id)
        questions = self.data.get("questions", {}).get(guild_id, {}).get(category, [])
        if questions:
            question = random.choice(questions)
            await interaction.response.send_message(f"❓ {question['question']}")
        else:
            await interaction.response.send_message("No questions in this category.", ephemeral=True)

    # ----------------------------
    # 11. /show_active
    # ----------------------------
    @app_commands.command(name="show_active", description="Show current active trivia question")
    async def show_active(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        question = self.active_trivia.get(guild_id)
        if question:
            await interaction.response.send_message(f"Active question: {question['question']}")
        else:
            await interaction.response.send_message("No active question.", ephemeral=True)

    # ----------------------------
    # 12. /skip_question
    # ----------------------------
    @app_commands.command(name="skip_question", description="Skip the current trivia question")
    async def skip_question(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        if guild_id in self.active_trivia:
            self.active_trivia.pop(guild_id)
            await interaction.response.send_message("✅ Active question skipped.")
        else:
            await interaction.response.send_message("No active question.", ephemeral=True)

    # ----------------------------
    # 13. /add_category
    # ----------------------------
    @app_commands.command(name="add_category", description="Add a trivia category")
    async def add_category(self, interaction: discord.Interaction, category: str):
        guild_id = str(interaction.guild.id)
        self.data.setdefault("questions", {}).setdefault(guild_id, {}).setdefault(category, [])
        save_data(self.data)
        await interaction.response.send_message(f"✅ Category `{category}` added.")

    # ----------------------------
    # 14. /remove_category
    # ----------------------------
    @app_commands.command(name="remove_category", description="Remove a trivia category")
    async def remove_category(self, interaction: discord.Interaction, category: str):
        guild_id = str(interaction.guild.id)
        if category in self.data.get("questions", {}).get(guild_id, {}):
            self.data["questions"][guild_id].pop(category)
            save_data(self.data)
            await interaction.response.send_message(f"✅ Category `{category}` removed.")
        else:
            await interaction.response.send_message("❌ Category not found.", ephemeral=True)

    # ----------------------------
    # 15. /rename_category
    # ----------------------------
    @app_commands.command(name="rename_category", description="Rename a trivia category")
    async def rename_category(self, interaction: discord.Interaction, old: str, new: str):
        guild_id = str(interaction.guild.id)
        categories = self.data.get("questions", {}).get(guild_id, {})
        if old in categories:
            categories[new] = categories.pop(old)
            save_data(self.data)
            await interaction.response.send_message(f"✅ Category `{old}` renamed to `{new}`")
        else:
            await interaction.response.send_message("❌ Category not found.", ephemeral=True)

    # ----------------------------
    # 16. /show_answer
    # ----------------------------
    @app_commands.command(name="show_answer", description="Show the answer to the active trivia question")
    async def show_answer(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        question = self.active_trivia.get(guild_id)
        if question:
            await interaction.response.send_message(f"Answer: {question['answer']}")
        else:
            await interaction.response.send_message("No active question.", ephemeral=True)

    # ----------------------------
    # 17. /random_answer
    # ----------------------------
    @app_commands.command(name="random_answer", description="Get the answer to a random question in a category")
    async def random_answer(self, interaction: discord.Interaction, category: str):
        guild_id = str(interaction.guild.id)
        questions = self.data.get("questions", {}).get(guild_id, {}).get(category, [])
        if questions:
            question = random.choice(questions)
            await interaction.response.send_message(f"Question: {question['question']}\nAnswer: {question['answer']}")
        else:
            await interaction.response.send_message("No questions in this category.", ephemeral=True)

    # ----------------------------
    # 18. /reset_trivia
    # ----------------------------
    @app_commands.command(name="reset_trivia", description="Reset all trivia questions and leaderboard")
    async def reset_trivia(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        self.data["questions"][guild_id] = {}
        self.data["leaderboard"][guild_id] = {}
        save_data(self.data)
        self.active_trivia.pop(guild_id, None)
        await interaction.response.send_message("✅ Trivia reset.")

    # ----------------------------
    # 19. /show_question_count_all
    # ----------------------------
    @app_commands.command(name="show_question_count_all", description="Show number of questions in all categories")
    async def show_question_count_all(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        categories = self.data.get("questions", {}).get(guild_id, {})
        msg = "\n".join(f"{cat}: {len(questions)}" for cat, questions in categories.items())
        await interaction.response.send_message(msg if msg else "No questions available.")

    # ----------------------------
    # 20. /trivia_info
    # ----------------------------
    @app_commands.command(name="trivia_info", description="Show information about the trivia system")
    async def trivia_info(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        categories = self.data.get("questions", {}).get(guild_id, {})
        leaderboard = self.data.get("leaderboard", {}).get(guild_id, {})
        await interaction.response.send_message(f"Trivia info:\nCategories: {len(categories)}\nLeaderboard entries: {len(leaderboard)}")

async def setup(bot):
    await bot.add_cog(Trivia(bot), guild=discord.Object(id=GUILD_ID))
