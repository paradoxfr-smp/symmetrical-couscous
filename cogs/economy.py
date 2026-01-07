import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import random
import datetime
from config import GUILD_ID

DATA_FILE = "economy.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

SHOP_ITEMS = {
    "sword": 100,
    "shield": 150,
    "potion": 50,
    "car": 500,
    "house": 1000
}

class Economy(commands.Cog):
    """Economy cog with 20+ commands and JSON persistence"""

    def __init__(self, bot):
        self.bot = bot
        self.data = load_data()

    def ensure_user(self, user_id):
        user_id = str(user_id)
        self.data.setdefault(user_id, {
            "wallet": 100,
            "bank": 0,
            "inventory": [],
            "last_daily": None,
            "last_work": None
        })
        return user_id

    # 1. /balance
    @app_commands.command(name="balance", description="Check your balance")
    async def balance(self, interaction: discord.Interaction, member: discord.Member = None):
        user = member or interaction.user
        user_id = self.ensure_user(user.id)
        wallet = self.data[user_id]["wallet"]
        bank = self.data[user_id]["bank"]
        await interaction.response.send_message(f"💰 {user.mention}'s Balance:\nWallet: {wallet}\nBank: {bank}")

    # 2. /daily
    @app_commands.command(name="daily", description="Claim daily coins")
    async def daily(self, interaction: discord.Interaction):
        user_id = self.ensure_user(interaction.user.id)
        last_daily = self.data[user_id]["last_daily"]
        now = datetime.datetime.utcnow()
        if last_daily:
            last = datetime.datetime.fromisoformat(last_daily)
            if (now - last).total_seconds() < 86400:
                await interaction.response.send_message("⏳ You already claimed your daily reward.")
                return
        reward = random.randint(50, 150)
        self.data[user_id]["wallet"] += reward
        self.data[user_id]["last_daily"] = now.isoformat()
        save_data(self.data)
        await interaction.response.send_message(f"🎉 You received {reward} coins!")

    # 3. /work
    @app_commands.command(name="work", description="Work to earn coins")
    async def work(self, interaction: discord.Interaction):
        user_id = self.ensure_user(interaction.user.id)
        last_work = self.data[user_id]["last_work"]
        now = datetime.datetime.utcnow()
        if last_work:
            last = datetime.datetime.fromisoformat(last_work)
            if (now - last).total_seconds() < 3600:  # 1 hour cooldown
                await interaction.response.send_message("⏳ You can work again in 1 hour.")
                return
        reward = random.randint(20, 100)
        self.data[user_id]["wallet"] += reward
        self.data[user_id]["last_work"] = now.isoformat()
        save_data(self.data)
        await interaction.response.send_message(f"💼 You worked and earned {reward} coins!")

    # 4. /pay
    @app_commands.command(name="pay", description="Pay another user")
    async def pay(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        sender_id = self.ensure_user(interaction.user.id)
        receiver_id = self.ensure_user(member.id)
        if amount <= 0:
            await interaction.response.send_message("❌ Amount must be positive.")
            return
        if self.data[sender_id]["wallet"] < amount:
            await interaction.response.send_message("❌ You don't have enough coins.")
            return
        self.data[sender_id]["wallet"] -= amount
        self.data[receiver_id]["wallet"] += amount
        save_data(self.data)
        await interaction.response.send_message(f"💸 {interaction.user.mention} paid {member.mention} {amount} coins.")

    # 5. /beg
    @app_commands.command(name="beg", description="Beg for coins")
    async def beg(self, interaction: discord.Interaction):
        user_id = self.ensure_user(interaction.user.id)
        amount = random.randint(5, 50)
        self.data[user_id]["wallet"] += amount
        save_data(self.data)
        await interaction.response.send_message(f"🙏 Someone gave you {amount} coins!")

    # 6. /gamble
    @app_commands.command(name="gamble", description="Gamble your coins")
    async def gamble(self, interaction: discord.Interaction, amount: int):
        user_id = self.ensure_user(interaction.user.id)
        if amount <= 0:
            await interaction.response.send_message("❌ Amount must be positive.")
            return
        if self.data[user_id]["wallet"] < amount:
            await interaction.response.send_message("❌ You don't have enough coins.")
            return
        win = random.choice([True, False])
        if win:
            self.data[user_id]["wallet"] += amount
            save_data(self.data)
            await interaction.response.send_message(f"🎉 You won {amount} coins!")
        else:
            self.data[user_id]["wallet"] -= amount
            save_data(self.data)
            await interaction.response.send_message(f"❌ You lost {amount} coins.")

    # 7. /shop
    @app_commands.command(name="shop", description="Show the shop")
    async def shop(self, interaction: discord.Interaction):
        msg = "\n".join([f"{item}: {price} coins" for item,price in SHOP_ITEMS.items()])
        await interaction.response.send_message(f"🛒 Shop Items:\n{msg}")

    # 8. /buy
    @app_commands.command(name="buy", description="Buy an item from the shop")
    async def buy(self, interaction: discord.Interaction, item: str):
        user_id = self.ensure_user(interaction.user.id)
        item = item.lower()
        if item not in SHOP_ITEMS:
            await interaction.response.send_message("❌ Item not found.")
            return
        price = SHOP_ITEMS[item]
        if self.data[user_id]["wallet"] < price:
            await interaction.response.send_message("❌ Not enough coins.")
            return
        self.data[user_id]["wallet"] -= price
        self.data[user_id]["inventory"].append(item)
        save_data(self.data)
        await interaction.response.send_message(f"🛒 You bought **{item}** for {price} coins!")

    # 9. /inventory
    @app_commands.command(name="inventory", description="Show your inventory")
    async def inventory(self, interaction: discord.Interaction):
        user_id = self.ensure_user(interaction.user.id)
        inv = self.data[user_id]["inventory"]
        if not inv:
            await interaction.response.send_message("📦 Your inventory is empty.")
            return
        await interaction.response.send_message(f"📦 Inventory:\n{', '.join(inv)}")

    # 10. /deposit
    @app_commands.command(name="deposit", description="Deposit coins to your bank")
    async def deposit(self, interaction: discord.Interaction, amount: int):
        user_id = self.ensure_user(interaction.user.id)
        if amount <= 0 or self.data[user_id]["wallet"] < amount:
            await interaction.response.send_message("❌ Invalid amount or insufficient coins.")
            return
        self.data[user_id]["wallet"] -= amount
        self.data[user_id]["bank"] += amount
        save_data(self.data)
        await interaction.response.send_message(f"🏦 Deposited {amount} coins.")

    # 11. /withdraw
    @app_commands.command(name="withdraw", description="Withdraw coins from bank")
    async def withdraw(self, interaction: discord.Interaction, amount: int):
        user_id = self.ensure_user(interaction.user.id)
        if amount <= 0 or self.data[user_id]["bank"] < amount:
            await interaction.response.send_message("❌ Invalid amount or insufficient coins in bank.")
            return
        self.data[user_id]["wallet"] += amount
        self.data[user_id]["bank"] -= amount
        save_data(self.data)
        await interaction.response.send_message(f"🏦 Withdrew {amount} coins.")

    # 12. /leaderboard
    @app_commands.command(name="leaderboard", description="Show richest users")
    async def leaderboard(self, interaction: discord.Interaction):
        leaderboard = sorted(
            ((uid, data["wallet"] + data["bank"]) for uid,data in self.data.items()),
            key=lambda x: x[1],
            reverse=True
        )
        msg = "\n".join([f"<@{uid}>: {score}" for uid,score in leaderboard[:10]])
        await interaction.response.send_message(f"🏆 Richest Users:\n{msg or 'No data yet.'}")

    # 13. /workbonus
    @app_commands.command(name="workbonus", description="Random bonus coins for working")
    async def workbonus(self, interaction: discord.Interaction):
        user_id = self.ensure_user(interaction.user.id)
        bonus = random.randint(10, 50)
        self.data[user_id]["wallet"] += bonus
        save_data(self.data)
        await interaction.response.send_message(f"💰 You received a work bonus of {bonus} coins!")

    # 14. /lottery
    @app_commands.command(name="lottery", description="Enter the lottery")
    async def lottery(self, interaction: discord.Interaction):
        user_id = self.ensure_user(interaction.user.id)
        cost = 20
        if self.data[user_id]["wallet"] < cost:
            await interaction.response.send_message("❌ Not enough coins for lottery.")
            return
        self.data[user_id]["wallet"] -= cost
        win = random.randint(1,10) == 1
        if win:
            reward = 200
            self.data[user_id]["wallet"] += reward
            save_data(self.data)
            await interaction.response.send_message(f"🎉 You won the lottery! +{reward} coins")
        else:
            save_data(self.data)
            await interaction.response.send_message("❌ You lost the lottery.")

    # 15. /rob
    @app_commands.command(name="rob", description="Attempt to rob another user")
    async def rob(self, interaction: discord.Interaction, member: discord.Member):
        robber_id = self.ensure_user(interaction.user.id)
        victim_id = self.ensure_user(member.id)
        if self.data[victim_id]["wallet"] < 50:
            await interaction.response.send_message("❌ Victim has too little coins.")
            return
        win = random.choice([True, False])
        if win:
            stolen = random.randint(10, min(100, self.data[victim_id]["wallet"]))
            self.data[victim_id]["wallet"] -= stolen
            self.data[robber_id]["wallet"] += stolen
            save_data(self.data)
            await interaction.response.send_message(f"💰 You stole {stolen} coins from {member.mention}!")
        else:
            await interaction.response.send_message("❌ Robbery failed!")

    # 16. /coinflip
    @app_commands.command(name="coinflip", description="Flip a coin for fun")
    async def coinflip(self, interaction: discord.Interaction):
        result = random.choice(["Heads","Tails"])
        await interaction.response.send_message(f"🪙 Coin flip result: {result}")

    # 17. /dice
    @app_commands.command(name="dice", description="Roll a dice")
    async def dice(self, interaction: discord.Interaction):
        roll = random.randint(1,6)
        await interaction.response.send_message(f"🎲 You rolled a {roll}")

    # 18. /scratch
    @app_commands.command(name="scratch", description="Scratch card for coins")
    async def scratch(self, interaction: discord.Interaction):
        user_id = self.ensure_user(interaction.user.id)
        reward = random.choice([0,0,0,50,100])
        self.data[user_id]["wallet"] += reward
        save_data(self.data)
        await interaction.response.send_message(f"🎫 Scratch card: +{reward} coins")

    # 19. /stealbank
    @app_commands.command(name="stealbank", description="Steal coins from someone's bank")
    async def stealbank(self, interaction: discord.Interaction, member: discord.Member):
        thief_id = self.ensure_user(interaction.user.id)
        victim_id = self.ensure_user(member.id)
        if self.data[victim_id]["bank"] < 50:
            await interaction.response.send_message("❌ Victim has too little coins in bank.")
            return
        win = random.choice([True, False])
        if win:
            stolen = random.randint(10, min(100, self.data[victim_id]["bank"]))
            self.data[victim_id]["bank"] -= stolen
            self.data[thief_id]["wallet"] += stolen
            save_data(self.data)
            await interaction.response.send_message(f"🏦 You stole {stolen} coins from {member.mention}'s bank!")
        else:
            await interaction.response.send_message("❌ Bank robbery failed!")

    # 20. /worksteal
    @app_commands.command(name="worksteal", description="Attempt risky work for big reward")
    async def worksteal(self, interaction: discord.Interaction):
        user_id = self.ensure_user(interaction.user.id)
        success = random.choice([True, False, False])  # 33% chance
        if success:
            reward = random.randint(150, 300)
            self.data[user_id]["wallet"] += reward
            save_data(self.data)
            await interaction.response.send_message(f"💰 You succeeded! Earned {reward} coins!")
        else:
            loss = random.randint(20, 50)
            self.data[user_id]["wallet"] = max(0, self.data[user_id]["wallet"] - loss)
            save_data(self.data)
            await interaction.response.send_message(f"❌ Failed work! Lost {loss} coins.")

async def setup(bot):
    await bot.add_cog(Economy(bot), guild=discord.Object(id=GUILD_ID))
