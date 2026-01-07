import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
from config import GUILD_ID

# For trivia and hangman, we’ll use in-memory state for simplicity.
# You can later move to JSON for persistence.

class Fun(commands.Cog):
    """Fun and games commands for Discord"""

    def __init__(self, bot):
        self.bot = bot
        self.trivia_questions = [
            {"question": "What is the capital of France?", "options": ["Paris", "London", "Rome", "Berlin"], "answer": "Paris"},
            {"question": "What is 2 + 2?", "options": ["3", "4", "5", "6"], "answer": "4"},
            {"question": "Who wrote Hamlet?", "options": ["Shakespeare", "Tolstoy", "Hemingway", "Dickens"], "answer": "Shakespeare"}
        ]
        self.hangman_games = {}  # channel_id: {word, display, guessed_letters, tries}
        self.tictactoe_games = {}  # channel_id: {board, player_x, player_o, turn}

    # ----------------------------
    # 1. Ping
    # ----------------------------
    @app_commands.command(name="ping", description="Check bot latency")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"🏓 Pong! {round(self.bot.latency * 1000)}ms")

    # ----------------------------
    # 2. Meme
    # ----------------------------
    memes = [
        "https://i.redd.it/abcd1234.png",
        "https://i.redd.it/efgh5678.png",
        "https://i.redd.it/ijkl9012.png"
    ]
    @app_commands.command(name="meme", description="Get a random meme")
    async def meme(self, interaction: discord.Interaction):
        url = random.choice(self.memes)
        embed = discord.Embed(title="Random Meme", color=discord.Color.random())
        embed.set_image(url=url)
        await interaction.response.send_message(embed=embed)

    # ----------------------------
    # 3. Joke
    # ----------------------------
    jokes = [
        "Why did the scarecrow win an award? Because he was outstanding in his field!",
        "I told my computer I needed a break, and it said 'No problem – I’ll go to sleep.'",
        "Why don’t skeletons fight each other? They don’t have the guts."
    ]
    @app_commands.command(name="joke", description="Tell a random joke")
    async def joke(self, interaction: discord.Interaction):
        await interaction.response.send_message(random.choice(self.jokes))

    # ----------------------------
    # 4. Quote
    # ----------------------------
    quotes = [
        "The best way to get started is to quit talking and begin doing. – Walt Disney",
        "Don’t let yesterday take up too much of today. – Will Rogers",
        "It’s not whether you get knocked down, it’s whether you get up. – Vince Lombardi"
    ]
    @app_commands.command(name="quote", description="Get an inspirational quote")
    async def quote(self, interaction: discord.Interaction):
        await interaction.response.send_message(random.choice(self.quotes))

    # ----------------------------
    # 5. Roll
    # ----------------------------
    @app_commands.command(name="roll", description="Roll a dice")
    async def roll(self, interaction: discord.Interaction, max_number: int = 100):
        await interaction.response.send_message(f"🎲 You rolled: {random.randint(1, max_number)}")

    # ----------------------------
    # 6. Say
    # ----------------------------
    @app_commands.command(name="say", description="Bot repeats your message")
    async def say(self, interaction: discord.Interaction, message: str):
        await interaction.response.send_message(message)

    # ----------------------------
    # 7. 8ball
    # ----------------------------
    eight_ball = ["Yes", "No", "Maybe", "Definitely", "Absolutely not", "Ask again later"]
    @app_commands.command(name="8ball", description="Ask the magic 8-ball")
    async def eightball(self, interaction: discord.Interaction, question: str):
        await interaction.response.send_message(f"🎱 {random.choice(self.eight_ball)}")

    # ----------------------------
    # 8. Coinflip
    # ----------------------------
    @app_commands.command(name="coinflip", description="Flip a coin")
    async def coinflip(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"🪙 {random.choice(['Heads', 'Tails'])}")

    # ----------------------------
    # 9. Choose
    # ----------------------------
    @app_commands.command(name="choose", description="Choose between multiple options")
    async def choose(self, interaction: discord.Interaction, options: str):
        choices = [o.strip() for o in options.split(",")]
        await interaction.response.send_message(f"🎯 I choose: {random.choice(choices)}")

    # ----------------------------
    # 10. Rock Paper Scissors
    # ----------------------------
    rps_choices = ["rock", "paper", "scissors"]
    @app_commands.command(name="rps", description="Play Rock Paper Scissors")
    async def rps(self, interaction: discord.Interaction, choice: str):
        choice = choice.lower()
        if choice not in self.rps_choices:
            await interaction.response.send_message("❌ Choose rock, paper, or scissors.")
            return
        bot_choice = random.choice(self.rps_choices)
        result = "Tie!"
        if (choice == "rock" and bot_choice == "scissors") or \
           (choice == "paper" and bot_choice == "rock") or \
           (choice == "scissors" and bot_choice == "paper"):
            result = "You win!"
        elif choice != bot_choice:
            result = "You lose!"
        await interaction.response.send_message(f"🖐 You chose {choice}, I chose {bot_choice}. {result}")

    # ----------------------------
    # 11. Trivia (real interactive)
    # ----------------------------
    @app_commands.command(name="trivia", description="Play a trivia question")
    async def trivia(self, interaction: discord.Interaction):
        question = random.choice(self.trivia_questions)
        options = "\n".join([f"{i+1}. {o}" for i, o in enumerate(question["options"])])
        await interaction.response.send_message(f"❓ {question['question']}\n{options}\n(Type the number of your answer in chat)")

    # ----------------------------
    # 12. Hangman (interactive)
    # ----------------------------
    @app_commands.command(name="hangman", description="Play hangman")
    async def hangman(self, interaction: discord.Interaction):
        channel_id = interaction.channel.id
        if channel_id in self.hangman_games:
            await interaction.response.send_message("A hangman game is already running here!")
            return
        word = random.choice(["discord", "python", "bot", "hangman"])
        display = ["_"] * len(word)
        self.hangman_games[channel_id] = {"word": word, "display": display, "guessed_letters": [], "tries": 6}
        await interaction.response.send_message(f"Word: {' '.join(display)}\nTries left: 6")

    # ----------------------------
    # 13. TicTacToe (2 players)
    # ----------------------------
    @app_commands.command(name="tictactoe", description="Play TicTacToe with another user")
    async def tictactoe(self, interaction: discord.Interaction, opponent: discord.Member):
        channel_id = interaction.channel.id
        if channel_id in self.tictactoe_games:
            await interaction.response.send_message("A TicTacToe game is already running here!")
            return
        board = [":white_large_square:"] * 9
        self.tictactoe_games[channel_id] = {"board": board, "player_x": interaction.user.id, "player_o": opponent.id, "turn": interaction.user.id}
        await interaction.response.send_message(f"TicTacToe started between {interaction.user.mention} and {opponent.mention}\n" +
                                                f"{' '.join(board[:3])}\n{' '.join(board[3:6])}\n{' '.join(board[6:])}")

    # ----------------------------
    # 14. Word count
    # ----------------------------
    @app_commands.command(name="wordcount", description="Count words in a sentence")
    async def wordcount(self, interaction: discord.Interaction, sentence: str):
        count = len(sentence.split())
        await interaction.response.send_message(f"📝 Word count: {count}")

    # ----------------------------
    # 15. Reverse
    # ----------------------------
    @app_commands.command(name="reverse", description="Reverse a message")
    async def reverse(self, interaction: discord.Interaction, text: str):
        await interaction.response.send_message(text[::-1])

    # ----------------------------
    # 16. Avatar
    # ----------------------------
    @app_commands.command(name="avatar", description="Get a user's avatar")
    async def avatar(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        embed = discord.Embed(title=f"{member}'s Avatar", color=discord.Color.random())
        embed.set_image(url=member.avatar.url)
        await interaction.response.send_message(embed=embed)

    # ----------------------------
    # 17. Roll stats
    # ----------------------------
    @app_commands.command(name="rollstats", description="Roll multiple dice")
    async def rollstats(self, interaction: discord.Interaction, times: int = 5, max_number: int = 100):
        rolls = [random.randint(1, max_number) for _ in range(times)]
        await interaction.response.send_message(f"🎲 Rolls: {rolls}\nTotal: {sum(rolls)}\nAverage: {sum(rolls)/times:.2f}")

    # ----------------------------
    # 18. Compliment
    # ----------------------------
    compliments = ["You are amazing!", "You have a great sense of humor!", "You're awesome!"]
    @app_commands.command(name="compliment", description="Send a random compliment")
    async def compliment(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"💖 {random.choice(self.compliments)}")

    # ----------------------------
    # 19. Insult
    # ----------------------------
    insults = ["You're funny… but in a bad way!", "You're like a cloud. When you disappear, it's a beautiful day."]
    @app_commands.command(name="insult", description="Send a random playful insult")
    async def insult(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"😈 {random.choice(self.insults)}")

    # ----------------------------
    # 20. Random number
    # ----------------------------
    @app_commands.command(name="randomnumber", description="Generate a random number in a range")
    async def randomnumber(self, interaction: discord.Interaction, min_num: int = 1, max_num: int = 100):
        await interaction.response.send_message(f"🎲 Random number: {random.randint(min_num, max_num)}")

async def setup(bot):
    await bot.add_cog(Fun(bot), guild=discord.Object(id=GUILD_ID))
