import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import random
from config import GUILD_ID

class Jokes(commands.Cog):
    """Jokes system with 20 commands using JokeAPI"""

    def __init__(self, bot):
        self.bot = bot

    async def fetch_joke(self, category: str = "Any", blacklist: str = None, type_: str = None):
        url = f"https://v2.jokeapi.dev/joke/{category}"
        params = {}
        if blacklist:
            params["blacklistFlags"] = blacklist
        if type_:
            params["type"] = type_
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data
        return None

    # 1. /joke
    @app_commands.command(name="joke", description="Get a random joke")
    async def joke(self, interaction: discord.Interaction):
        data = await self.fetch_joke()
        if not data:
            await interaction.response.send_message("❌ Failed to fetch joke")
            return
        if data["type"] == "single":
            await interaction.response.send_message(data["joke"])
        else:
            await interaction.response.send_message(f"{data['setup']}\n||{data['delivery']}||")  # Spoiler delivery

    # 2. /joke_category
    @app_commands.command(name="joke_category", description="Get joke from a specific category")
    async def joke_category(self, interaction: discord.Interaction, category: str):
        data = await self.fetch_joke(category)
        if not data:
            await interaction.response.send_message("❌ No joke found")
            return
        if data["type"] == "single":
            await interaction.response.send_message(data["joke"])
        else:
            await interaction.response.send_message(f"{data['setup']}\n||{data['delivery']}||")

    # 3. /joke_single
    @app_commands.command(name="joke_single", description="Get only single-line jokes")
    async def joke_single(self, interaction: discord.Interaction):
        data = await self.fetch_joke(type_="single")
        if not data:
            await interaction.response.send_message("❌ No joke found")
            return
        await interaction.response.send_message(data["joke"])

    # 4. /joke_twopart
    @app_commands.command(name="joke_twopart", description="Get only two-part jokes")
    async def joke_twopart(self, interaction: discord.Interaction):
        data = await self.fetch_joke(type_="twopart")
        if not data:
            await interaction.response.send_message("❌ No joke found")
            return
        await interaction.response.send_message(f"{data['setup']}\n||{data['delivery']}||")

    # 5. /joke_safe
    @app_commands.command(name="joke_safe", description="Get safe jokes")
    async def joke_safe(self, interaction: discord.Interaction):
        data = await self.fetch_joke(blacklist="nsfw,religious,political,racist,sexist")
        if not data:
            await interaction.response.send_message("❌ No joke found")
            return
        if data["type"] == "single":
            await interaction.response.send_message(data["joke"])
        else:
            await interaction.response.send_message(f"{data['setup']}\n||{data['delivery']}||")

    # 6. /joke_embed
    @app_commands.command(name="joke_embed", description="Get a joke in an embed")
    async def joke_embed(self, interaction: discord.Interaction):
        data = await self.fetch_joke()
        if not data:
            await interaction.response.send_message("❌ Failed")
            return
        embed = discord.Embed(color=discord.Color.random())
        if data["type"] == "single":
            embed.description = data["joke"]
        else:
            embed.description = f"{data['setup']}\n||{data['delivery']}||"
        await interaction.response.send_message(embed=embed)

    # 7. /joke_random_multiple
    @app_commands.command(name="joke_random_multiple", description="Get multiple random jokes")
    async def joke_random_multiple(self, interaction: discord.Interaction, count: int = 3):
        count = min(max(count,1),10)
        jokes = []
        for _ in range(count):
            data = await self.fetch_joke()
            if data:
                if data["type"] == "single":
                    jokes.append(data["joke"])
                else:
                    jokes.append(f"{data['setup']} ||{data['delivery']}||")
        if jokes:
            await interaction.response.send_message("\n\n".join(jokes))
        else:
            await interaction.response.send_message("❌ No jokes found")

    # 8. /joke_category_safe
    @app_commands.command(name="joke_category_safe", description="Safe joke from specific category")
    async def joke_category_safe(self, interaction: discord.Interaction, category: str):
        data = await self.fetch_joke(category, blacklist="nsfw,religious,political,racist,sexist")
        if not data:
            await interaction.response.send_message("❌ No joke found")
            return
        if data["type"] == "single":
            await interaction.response.send_message(data["joke"])
        else:
            await interaction.response.send_message(f"{data['setup']} ||{data['delivery']}||")

    # 9. /joke_info
    @app_commands.command(name="joke_info", description="Show info about a joke")
    async def joke_info(self, interaction: discord.Interaction):
        data = await self.fetch_joke()
        if not data:
            await interaction.response.send_message("❌ Failed")
            return
        info = f"Category: {data['category']}\nType: {data['type']}\nFlags: {', '.join([k for k,v in data['flags'].items() if v])}"
        await interaction.response.send_message(info)

    # 10. /joke_random_embed_multiple
    @app_commands.command(name="joke_random_embed_multiple", description="Multiple jokes in embeds")
    async def joke_random_embed_multiple(self, interaction: discord.Interaction, count: int = 3):
        count = min(max(count,1),5)
        embeds = []
        for _ in range(count):
            data = await self.fetch_joke()
            if data:
                embed = discord.Embed(color=discord.Color.random())
                if data["type"] == "single":
                    embed.description = data["joke"]
                else:
                    embed.description = f"{data['setup']} ||{data['delivery']}||"
                embeds.append(embed)
        await interaction.response.send_message(embeds=embeds if embeds else None)

    # 11. /joke_random_safe_multiple
    @app_commands.command(name="joke_random_safe_multiple", description="Multiple safe jokes")
    async def joke_random_safe_multiple(self, interaction: discord.Interaction, count: int = 3):
        count = min(max(count,1),5)
        jokes = []
        for _ in range(count):
            data = await self.fetch_joke(blacklist="nsfw,religious,political,racist,sexist")
            if data:
                if data["type"] == "single":
                    jokes.append(data["joke"])
                else:
                    jokes.append(f"{data['setup']} ||{data['delivery']}||")
        if jokes:
            await interaction.response.send_message("\n\n".join(jokes))
        else:
            await interaction.response.send_message("❌ No jokes found")

    # 12. /joke_random_category
    @app_commands.command(name="joke_random_category", description="Random joke from a random category")
    async def joke_random_category(self, interaction: discord.Interaction):
        categories = ["Programming","Misc","Pun","Spooky","Christmas"]
        category = random.choice(categories)
        data = await self.fetch_joke(category)
        if not data:
            await interaction.response.send_message("❌ No joke found")
            return
        if data["type"] == "single":
            await interaction.response.send_message(f"[{category}] {data['joke']}")
        else:
            await interaction.response.send_message(f"[{category}] {data['setup']} ||{data['delivery']}||")

    # 13. /joke_random_flag
    @app_commands.command(name="joke_random_flag", description="Joke excluding certain flags")
    async def joke_random_flag(self, interaction: discord.Interaction, flags: str):
        data = await self.fetch_joke(blacklist=flags)
        if not data:
            await interaction.response.send_message("❌ No joke found")
            return
        if data["type"] == "single":
            await interaction.response.send_message(data["joke"])
        else:
            await interaction.response.send_message(f"{data['setup']} ||{data['delivery']}||")

    # 14. /joke_random_programming
    @app_commands.command(name="joke_random_programming", description="Random programming joke")
    async def joke_random_programming(self, interaction: discord.Interaction):
        data = await self.fetch_joke("Programming")
        if not data:
            await interaction.response.send_message("❌ No joke found")
            return
        if data["type"] == "single":
            await interaction.response.send_message(data["joke"])
        else:
            await interaction.response.send_message(f"{data['setup']} ||{data['delivery']}||")

    # 15. /joke_random_misc
    @app_commands.command(name="joke_random_misc", description="Random miscellaneous joke")
    async def joke_random_misc(self, interaction: discord.Interaction):
        data = await self.fetch_joke("Misc")
        if not data:
            await interaction.response.send_message("❌ No joke found")
            return
        if data["type"] == "single":
            await interaction.response.send_message(data["joke"])
        else:
            await interaction.response.send_message(f"{data['setup']} ||{data['delivery']}||")

    # 16. /joke_random_pun
    @app_commands.command(name="joke_random_pun", description="Random pun joke")
    async def joke_random_pun(self, interaction: discord.Interaction):
        data = await self.fetch_joke("Pun")
        if not data:
            await interaction.response.send_message("❌ No joke found")
            return
        if data["type"] == "single":
            await interaction.response.send_message(data["joke"])
        else:
            await interaction.response.send_message(f"{data['setup']} ||{data['delivery']}||")

    # 17. /joke_random_spooky
    @app_commands.command(name="joke_random_spooky", description="Random spooky joke")
    async def joke_random_spooky(self, interaction: discord.Interaction):
        data = await self.fetch_joke("Spooky")
        if not data:
            await interaction.response.send_message("❌ No joke found")
            return
        if data["type"] == "single":
            await interaction.response.send_message(data["joke"])
        else:
            await interaction.response.send_message(f"{data['setup']} ||{data['delivery']}||")

    # 18. /joke_random_christmas
    @app_commands.command(name="joke_random_christmas", description="Random Christmas joke")
    async def joke_random_christmas(self, interaction: discord.Interaction):
        data = await self.fetch_joke("Christmas")
        if not data:
            await interaction.response.send_message("❌ No joke found")
            return
        if data["type"] == "single":
            await interaction.response.send_message(data["joke"])
        else:
            await interaction.response.send_message(f"{data['setup']} ||{data['delivery']}||")

    # 19. /joke_random_safe_embed
    @app_commands.command(name="joke_random_safe_embed", description="Random safe joke in embed")
    async def joke_random_safe_embed(self, interaction: discord.Interaction):
        data = await self.fetch_joke(blacklist="nsfw,religious,political,racist,sexist")
        if not data:
            await interaction.response.send_message("❌ No joke found")
            return
        embed = discord.Embed(color=discord.Color.random())
        if data["type"] == "single":
            embed.description = data["joke"]
        else:
            embed.description = f"{data['setup']} ||{data['delivery']}||"
        await interaction.response.send_message(embed=embed)

    # 20. /joke_random_combined
    @app_commands.command(name="joke_random_combined", description="Random joke from any category and type")
    async def joke_random_combined(self, interaction: discord.Interaction):
        categories = ["Programming","Misc","Pun","Spooky","Christmas"]
        category = random.choice(categories)
        data = await self.fetch_joke(category)
        if not data:
            await interaction.response.send_message("❌ No joke found")
            return
        if data["type"] == "single":
            await interaction.response.send_message(f"[{category}] {data['joke']}")
        else:
            await interaction.response.send_message(f"[{category}] {data['setup']} ||{data['delivery']}||")

async def setup(bot):
    await bot.add_cog(Jokes(bot), guild=discord.Object(id=GUILD_ID))
