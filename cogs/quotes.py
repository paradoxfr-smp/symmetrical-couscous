import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import aiohttp
from config import GUILD_ID

DATA_FILE = "quotes.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"quotes": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

class Quotes(commands.Cog):
    """Quotes system with 20 commands and API support"""

    def __init__(self, bot):
        self.bot = bot
        self.data = load_data()

    # 1. /add_quote
    @app_commands.command(name="add_quote", description="Add a custom quote")
    async def add_quote(self, interaction: discord.Interaction, *, quote: str):
        guild_id = str(interaction.guild.id)
        self.data.setdefault("quotes", {}).setdefault(guild_id, []).append(quote)
        save_data(self.data)
        await interaction.response.send_message("✅ Quote added.")

    # 2. /remove_quote
    @app_commands.command(name="remove_quote", description="Remove a quote by index")
    async def remove_quote(self, interaction: discord.Interaction, index: int):
        guild_id = str(interaction.guild.id)
        quotes = self.data.get("quotes", {}).get(guild_id, [])
        if 0 <= index-1 < len(quotes):
            removed = quotes.pop(index-1)
            save_data(self.data)
            await interaction.response.send_message(f"✅ Removed quote: {removed}")
        else:
            await interaction.response.send_message("❌ Invalid index.", ephemeral=True)

    # 3. /list_quotes
    @app_commands.command(name="list_quotes", description="List all quotes")
    async def list_quotes(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        quotes = self.data.get("quotes", {}).get(guild_id, [])
        if quotes:
            msg = "\n".join(f"{i+1}. {q}" for i, q in enumerate(quotes))
            await interaction.response.send_message(f"Quotes:\n{msg}")
        else:
            await interaction.response.send_message("No quotes found.", ephemeral=True)

    # 4. /random_quote
    @app_commands.command(name="random_quote", description="Get a random custom quote")
    async def random_quote(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        quotes = self.data.get("quotes", {}).get(guild_id, [])
        if quotes:
            quote = random.choice(quotes)
            await interaction.response.send_message(f"💬 {quote}")
        else:
            await interaction.response.send_message("No quotes available.", ephemeral=True)

    # 5. /clear_quotes
    @app_commands.command(name="clear_quotes", description="Delete all quotes")
    async def clear_quotes(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        self.data["quotes"][guild_id] = []
        save_data(self.data)
        await interaction.response.send_message("✅ All quotes cleared.")

    # 6. /quote_count
    @app_commands.command(name="quote_count", description="Show number of quotes")
    async def quote_count(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        count = len(self.data.get("quotes", {}).get(guild_id, []))
        await interaction.response.send_message(f"Total quotes: {count}")

    # 7. /get_quote
    @app_commands.command(name="get_quote", description="Get a specific quote by index")
    async def get_quote(self, interaction: discord.Interaction, index: int):
        guild_id = str(interaction.guild.id)
        quotes = self.data.get("quotes", {}).get(guild_id, [])
        if 0 <= index-1 < len(quotes):
            await interaction.response.send_message(quotes[index-1])
        else:
            await interaction.response.send_message("❌ Invalid index.", ephemeral=True)

    # 8. /edit_quote
    @app_commands.command(name="edit_quote", description="Edit a quote by index")
    async def edit_quote(self, interaction: discord.Interaction, index: int, *, new_text: str):
        guild_id = str(interaction.guild.id)
        quotes = self.data.get("quotes", {}).get(guild_id, [])
        if 0 <= index-1 < len(quotes):
            quotes[index-1] = new_text
            save_data(self.data)
            await interaction.response.send_message(f"✅ Quote {index} updated.")
        else:
            await interaction.response.send_message("❌ Invalid index.", ephemeral=True)

    # 9. /search_quotes
    @app_commands.command(name="search_quotes", description="Search quotes by keyword")
    async def search_quotes(self, interaction: discord.Interaction, keyword: str):
        guild_id = str(interaction.guild.id)
        quotes = self.data.get("quotes", {}).get(guild_id, [])
        found = [q for q in quotes if keyword.lower() in q.lower()]
        if found:
            await interaction.response.send_message("\n".join(found))
        else:
            await interaction.response.send_message("No quotes found.", ephemeral=True)

    # 10. /random_api_quote
    @app_commands.command(name="random_api_quote", description="Get a random inspirational quote from API")
    async def random_api_quote(self, interaction: discord.Interaction):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.quotable.io/random") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    await interaction.response.send_message(f"💬 \"{data['content']}\" — {data['author']}")
                else:
                    await interaction.response.send_message("Failed to fetch API quote.")

    # 11. /quote_info
    @app_commands.command(name="quote_info", description="Show info of a quote by index")
    async def quote_info(self, interaction: discord.Interaction, index: int):
        guild_id = str(interaction.guild.id)
        quotes = self.data.get("quotes", {}).get(guild_id, [])
        if 0 <= index-1 < len(quotes):
            quote = quotes[index-1]
            await interaction.response.send_message(f"Quote {index}: {quote}")
        else:
            await interaction.response.send_message("❌ Invalid index.", ephemeral=True)

    # 12. /quote_embed
    @app_commands.command(name="quote_embed", description="Show a quote in an embed")
    async def quote_embed(self, interaction: discord.Interaction, index: int):
        guild_id = str(interaction.guild.id)
        quotes = self.data.get("quotes", {}).get(guild_id, [])
        if 0 <= index-1 < len(quotes):
            embed = discord.Embed(description=quotes[index-1], color=discord.Color.random())
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ Invalid index.", ephemeral=True)

    # 13. /quote_random_embed
    @app_commands.command(name="quote_random_embed", description="Show a random quote in an embed")
    async def quote_random_embed(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        quotes = self.data.get("quotes", {}).get(guild_id, [])
        if quotes:
            embed = discord.Embed(description=random.choice(quotes), color=discord.Color.random())
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("No quotes available.", ephemeral=True)

    # 14. /import_quotes
    @app_commands.command(name="import_quotes", description="Import quotes from JSON string")
    async def import_quotes(self, interaction: discord.Interaction, *, json_text: str):
        guild_id = str(interaction.guild.id)
        try:
            quotes = json.loads(json_text)
            if isinstance(quotes, list):
                self.data.setdefault("quotes", {}).setdefault(guild_id, []).extend(quotes)
                save_data(self.data)
                await interaction.response.send_message(f"✅ Imported {len(quotes)} quotes.")
            else:
                await interaction.response.send_message("❌ Invalid JSON.", ephemeral=True)
        except:
            await interaction.response.send_message("❌ Invalid JSON.", ephemeral=True)

    # 15. /export_quotes
    @app_commands.command(name="export_quotes", description="Export all quotes as JSON")
    async def export_quotes(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        quotes = self.data.get("quotes", {}).get(guild_id, [])
        await interaction.response.send_message(f"```json\n{json.dumps(quotes, indent=2)}\n```" if quotes else "No quotes to export.")

    # 16. /quote_first
    @app_commands.command(name="quote_first", description="Get the first quote")
    async def quote_first(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        quotes = self.data.get("quotes", {}).get(guild_id, [])
        await interaction.response.send_message(quotes[0] if quotes else "No quotes available.")

    # 17. /quote_last
    @app_commands.command(name="quote_last", description="Get the last quote")
    async def quote_last(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        quotes = self.data.get("quotes", {}).get(guild_id, [])
        await interaction.response.send_message(quotes[-1] if quotes else "No quotes available.")

    # 18. /quote_search_api
    @app_commands.command(name="quote_search_api", description="Get a quote containing keyword from API")
    async def quote_search_api(self, interaction: discord.Interaction, keyword: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.quotable.io/quotes?query={keyword}") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    results = data.get("results", [])
                    if results:
                        quote = random.choice(results)
                        await interaction.response.send_message(f"💬 \"{quote['content']}\" — {quote['author']}")
                        return
                await interaction.response.send_message("No quotes found from API.")

    # 19. /quote_random_api_embed
    @app_commands.command(name="quote_random_api_embed", description="Random API quote in embed")
    async def quote_random_api_embed(self, interaction: discord.Interaction):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.quotable.io/random") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    embed = discord.Embed(description=f"\"{data['content']}\" — {data['author']}", color=discord.Color.random())
                    await interaction.response.send_message(embed=embed)
                else:
                    await interaction.response.send_message("Failed to fetch API quote.")

    # 20. /quote_random_combined
    @app_commands.command(name="quote_random_combined", description="Random quote from API or custom")
    async def quote_random_combined(self, interaction: discord.Interaction):
        import random
        guild_id = str(interaction.guild.id)
        quotes = self.data.get("quotes", {}).get(guild_id, [])
        use_api = random.choice([True, False])
        if use_api:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.quotable.io/random") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        await interaction.response.send_message(f"💬 \"{data['content']}\" — {data['author']}")
                        return
        if quotes:
            await interaction.response.send_message(f"💬 {random.choice(quotes)}")
        else:
            await interaction.response.send_message("No quotes available.")

async def setup(bot):
    await bot.add_cog(Quotes(bot), guild=discord.Object(id=GUILD_ID))
