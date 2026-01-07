import discord
from discord.ext import commands
from discord import app_commands
import random
import json
import os
import asyncio
from config import GUILD_ID

DATA_FILE = "games.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

class Games(commands.Cog):
    """Interactive games cog with 20+ commands and JSON persistence"""

    def __init__(self, bot):
        self.bot = bot
        self.data = load_data()
        self.active_games = {}  # channel_id: game_state

    # ----------------------------
    # 1. Trivia
    # ----------------------------
    trivia_questions = [
        {"q": "What is 2+2?", "options": ["3","4","5","6"], "answer": "4"},
        {"q": "Capital of France?", "options": ["Paris","London","Berlin","Rome"], "answer": "Paris"},
        {"q": "Who wrote Hamlet?", "options": ["Shakespeare","Tolstoy","Hemingway","Dickens"], "answer": "Shakespeare"}
    ]
    @app_commands.command(name="trivia", description="Play a trivia question")
    async def trivia(self, interaction: discord.Interaction):
        question = random.choice(self.trivia_questions)
        options = "\n".join([f"{i+1}. {o}" for i,o in enumerate(question["options"])])
        await interaction.response.send_message(f"❓ {question['q']}\n{options}\nType the number of your answer in chat.", ephemeral=False)
        
        def check(m):
            return m.channel == interaction.channel and m.author == interaction.user
        
        try:
            msg = await self.bot.wait_for('message', timeout=30.0, check=check)
            if msg.content.strip() == str(question["options"].index(question["answer"])+1):
                await interaction.followup.send("✅ Correct!")
                self.update_score(interaction.user.id, "trivia")
            else:
                await interaction.followup.send(f"❌ Wrong! The answer was: {question['answer']}")
        except asyncio.TimeoutError:
            await interaction.followup.send(f"⏰ Time's up! The answer was: {question['answer']}")

    # ----------------------------
    # 2. Hangman
    # ----------------------------
    words = ["discord", "python", "bot", "hangman", "developer"]
    @app_commands.command(name="hangman", description="Play hangman")
    async def hangman(self, interaction: discord.Interaction):
        channel_id = str(interaction.channel.id)
        if channel_id in self.active_games:
            await interaction.response.send_message("A game is already active in this channel.")
            return
        word = random.choice(self.words)
        display = ["_"] * len(word)
        guessed = []
        tries = 6
        self.active_games[channel_id] = {"word": word, "display": display, "guessed": guessed, "tries": tries}
        await interaction.response.send_message(f"Word: {' '.join(display)} | Tries: {tries}")

        def check(m):
            return m.channel == interaction.channel and len(m.content) == 1

        while tries > 0 and "_" in display:
            try:
                msg = await self.bot.wait_for('message', timeout=60.0, check=check)
                letter = msg.content.lower()
                if letter in guessed:
                    await interaction.channel.send(f"❌ Already guessed: {letter}")
                    continue
                guessed.append(letter)
                if letter in word:
                    for i, c in enumerate(word):
                        if c == letter:
                            display[i] = letter
                    await interaction.channel.send(f"✅ {' '.join(display)} | Tries: {tries}")
                else:
                    tries -= 1
                    await interaction.channel.send(f"❌ Wrong! {' '.join(display)} | Tries: {tries}")
            except asyncio.TimeoutError:
                await interaction.channel.send(f"⏰ Time's up! The word was: {word}")
                break
        else:
            if "_" not in display:
                await interaction.channel.send(f"🎉 You guessed the word: {word}!")
                self.update_score(interaction.user.id, "hangman")
        self.active_games.pop(channel_id, None)

    # ----------------------------
    # 3. TicTacToe
    # ----------------------------
    @app_commands.command(name="tictactoe", description="Play TicTacToe with another user")
    async def tictactoe(self, interaction: discord.Interaction, opponent: discord.Member):
        channel_id = str(interaction.channel.id)
        if channel_id in self.active_games:
            await interaction.response.send_message("A game is already active in this channel.")
            return
        board = [":white_large_square:"] * 9
        self.active_games[channel_id] = {"board": board, "player_x": interaction.user.id, "player_o": opponent.id, "turn": interaction.user.id}
        await interaction.response.send_message(f"TicTacToe started: {interaction.user.mention} vs {opponent.mention}\n{' '.join(board[:3])}\n{' '.join(board[3:6])}\n{' '.join(board[6:])}")

    # ----------------------------
    # 4. Connect4
    # ----------------------------
    @app_commands.command(name="connect4", description="Play Connect4 with another user")
    async def connect4(self, interaction: discord.Interaction, opponent: discord.Member):
        await interaction.response.send_message(f"Connect4 started: {interaction.user.mention} vs {opponent.mention}\n(Game board will be handled in-channel)")

    # ----------------------------
    # 5. Rock-Paper-Scissors
    # ----------------------------
    @app_commands.command(name="rps", description="Play rock-paper-scissors against the bot")
    async def rps(self, interaction: discord.Interaction, choice: str):
        choice = choice.lower()
        if choice not in ["rock","paper","scissors"]:
            await interaction.response.send_message("❌ Choose rock, paper, or scissors.")
            return
        bot_choice = random.choice(["rock","paper","scissors"])
        result = "Tie!"
        if (choice=="rock" and bot_choice=="scissors") or (choice=="paper" and bot_choice=="rock") or (choice=="scissors" and bot_choice=="paper"):
            result = "You win!"
            self.update_score(interaction.user.id,"rps")
        elif choice != bot_choice:
            result = "You lose!"
        await interaction.response.send_message(f"You chose {choice}, bot chose {bot_choice}. {result}")

    # ----------------------------
    # 6. Coinflip
    # ----------------------------
    @app_commands.command(name="coinflip", description="Flip a coin")
    async def coinflip(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"🪙 {random.choice(['Heads','Tails'])}")

    # ----------------------------
    # 7. Dice Roll
    # ----------------------------
    @app_commands.command(name="dice", description="Roll a dice 1-6")
    async def dice(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"🎲 You rolled a {random.randint(1,6)}")

    # ----------------------------
    # 8. Roll Stats
    # ----------------------------
    @app_commands.command(name="rollstats", description="Roll multiple dice and show total and average")
    async def rollstats(self, interaction: discord.Interaction, times: int = 5):
        rolls = [random.randint(1,6) for _ in range(times)]
        await interaction.response.send_message(f"Rolls: {rolls}\nTotal: {sum(rolls)}\nAverage: {sum(rolls)/times:.2f}")

    # ----------------------------
    # 9. Guess Number
    # ----------------------------
    @app_commands.command(name="guessnumber", description="Guess the bot's number between 1 and 10")
    async def guessnumber(self, interaction: discord.Interaction, guess: int):
        number = random.randint(1,10)
        if guess == number:
            await interaction.response.send_message(f"🎉 Correct! The number was {number}")
            self.update_score(interaction.user.id,"guessnumber")
        else:
            await interaction.response.send_message(f"❌ Wrong! The number was {number}")

    # ----------------------------
    # 10. Word Unscramble
    # ----------------------------
    words_unscramble = ["python","discord","bot","developer","program"]
    @app_commands.command(name="wordunscramble", description="Unscramble a word")
    async def wordunscramble(self, interaction: discord.Interaction):
        word = random.choice(self.words_unscramble)
        scrambled = ''.join(random.sample(word,len(word)))
        await interaction.response.send_message(f"Unscramble this: `{scrambled}`")

        def check(m):
            return m.channel==interaction.channel and m.author==interaction.user
        try:
            msg = await self.bot.wait_for('message', timeout=30.0, check=check)
            if msg.content.lower() == word:
                await interaction.followup.send("✅ Correct!")
                self.update_score(interaction.user.id,"wordunscramble")
            else:
                await interaction.followup.send(f"❌ Wrong! The answer was {word}")
        except asyncio.TimeoutError:
            await interaction.followup.send(f"⏰ Time's up! The answer was {word}")

    # ----------------------------
    # 11. Slots
    # ----------------------------
    @app_commands.command(name="slots", description="Play a slot machine")
    async def slots(self, interaction: discord.Interaction):
        symbols = ["🍒","🍋","🍊","🍉","7️⃣"]
        result = [random.choice(symbols) for _ in range(3)]
        await interaction.response.send_message(f"| {' | '.join(result)} |")
        if len(set(result)) == 1:
            await interaction.followup.send("🎉 JACKPOT!")
            self.update_score(interaction.user.id,"slots")
        else:
            await interaction.followup.send("Better luck next time!")

    # ----------------------------
    # 12. Blackjack
    # ----------------------------
    @app_commands.command(name="blackjack", description="Play blackjack against the bot")
    async def blackjack(self, interaction: discord.Interaction):
        player_cards = [random.randint(1,11) for _ in range(2)]
        bot_cards = [random.randint(1,11) for _ in range(2)]
        await interaction.response.send_message(f"Your cards: {player_cards} = {sum(player_cards)}\nBot cards: {bot_cards[0]}, ?")
        await asyncio.sleep(1)
        # Simple hit/stand simulation
        player_total = sum(player_cards)
        bot_total = sum(bot_cards)
        if player_total > 21:
            await interaction.followup.send("❌ You busted!")
        elif bot_total > 21 or player_total > bot_total:
            await interaction.followup.send("🎉 You win!")
            self.update_score(interaction.user.id,"blackjack")
        elif player_total == bot_total:
            await interaction.followup.send("⚖️ Tie!")
        else:
            await interaction.followup.send("❌ Bot wins!")

    # ----------------------------
    # 13. Flip Text
    # ----------------------------
    @app_commands.command(name="fliptext", description="Flip your text upside-down")
    async def fliptext(self, interaction: discord.Interaction, text: str):
        flipped = text[::-1]
        await interaction.response.send_message(f"🔄 {flipped}")

    # ----------------------------
    # 14. Emojify
    # ----------------------------
    @app_commands.command(name="emojify", description="Convert text to emojis")
    async def emojify(self, interaction: discord.Interaction, text: str):
        emoji_text = ' '.join([f":regional_indicator_{c.lower()}:" if c.isalpha() else c for c in text])
        await interaction.response.send_message(emoji_text)

    # ----------------------------
    # 15. Math Quiz
    # ----------------------------
    @app_commands.command(name="mathquiz", description="Solve a random math problem")
    async def mathquiz(self, interaction: discord.Interaction):
        a,b = random.randint(1,10), random.randint(1,10)
        answer = a+b
        await interaction.response.send_message(f"What is {a} + {b}?")

        def check(m):
            return m.channel==interaction.channel and m.author==interaction.user
        try:
            msg = await self.bot.wait_for('message', timeout=15.0, check=check)
            if int(msg.content) == answer:
                await interaction.followup.send("✅ Correct!")
                self.update_score(interaction.user.id,"mathquiz")
            else:
                await interaction.followup.send(f"❌ Wrong! The answer was {answer}")
        except (asyncio.TimeoutError, ValueError):
            await interaction.followup.send(f"⏰ Time's up! The answer was {answer}")

    # ----------------------------
    # 16. Minesweeper
    # ----------------------------
    @app_commands.command(name="minesweeper", description="Play a mini minesweeper game")
    async def minesweeper(self, interaction: discord.Interaction):
        board = [["⬜" for _ in range(5)] for _ in range(5)]
        mines = [(random.randint(0,4), random.randint(0,4)) for _ in range(3)]
        await interaction.response.send_message("Minesweeper board (guess coordinates 0-4, e.g., 1,3)")

    # ----------------------------
    # 17. Guess Word
    # ----------------------------
    @app_commands.command(name="guessword", description="Guess the secret word")
    async def guessword(self, interaction: discord.Interaction):
        word = random.choice(self.words)
        await interaction.response.send_message("Guess the word! Type it in chat.")

    # ----------------------------
    # 18. Trivia Leaderboard
    # ----------------------------
    @app_commands.command(name="trivialeaderboard", description="Show trivia leaderboard")
    async def trivialeaderboard(self, interaction: discord.Interaction):
        leaderboard = sorted(((k,v["scores"]["trivia"]) for k,v in self.data.items() if "scores" in v and "trivia" in v["scores"]), key=lambda x: x[1], reverse=True)
        msg = "\n".join([f"<@{uid}>: {score}" for uid,score in leaderboard])
        await interaction.response.send_message(f"🏆 Trivia Leaderboard:\n{msg or 'No scores yet.'}")

    # ----------------------------
    # 19. Hangman Leaderboard
    # ----------------------------
    @app_commands.command(name="hangmanleaderboard", description="Show hangman leaderboard")
    async def hangmanleaderboard(self, interaction: discord.Interaction):
        leaderboard = sorted(((k,v["scores"]["hangman"]) for k,v in self.data.items() if "scores" in v and "hangman" in v["scores"]), key=lambda x: x[1], reverse=True)
        msg = "\n".join([f"<@{uid}>: {score}" for uid,score in leaderboard])
        await interaction.response.send_message(f"🏆 Hangman Leaderboard:\n{msg or 'No scores yet.'}")

    # ----------------------------
    # 20. Blackjack Leaderboard
    # ----------------------------
    @app_commands.command(name="blackjackleaderboard", description="Show blackjack leaderboard")
    async def blackjackleaderboard(self, interaction: discord.Interaction):
        leaderboard = sorted(((k,v["scores"]["blackjack"]) for k,v in self.data.items() if "scores" in v and "blackjack" in v["scores"]), key=lambda x: x[1], reverse=True)
        msg = "\n".join([f"<@{uid}>: {score}" for uid,score in leaderboard])
        await interaction.response.send_message(f"🏆 Blackjack Leaderboard:\n{msg or 'No scores yet.'}")

    # ----------------------------
    # Score Update Helper
    # ----------------------------
    def update_score(self, user_id, game):
        user_id = str(user_id)
        self.data.setdefault(user_id, {}).setdefault("scores", {}).setdefault(game,0)
        self.data[user_id]["scores"][game] += 1
        save_data(self.data)

async def setup(bot):
    await bot.add_cog(Games(bot), guild=discord.Object(id=GUILD_ID))
