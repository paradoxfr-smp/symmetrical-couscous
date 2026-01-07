import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import random
from config import GUILD_ID

class Memes(commands.Cog):
    """Memes cog using meme‑api.com for real memes"""

    def __init__(self, bot):
        self.bot = bot

    async def fetch_meme(self, subreddit: str = None):
        url = "https://meme-api.com/gimme"
        if subreddit:
            url += f"/{subreddit}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data
                return None

    # 1. /meme
    @app_commands.command(name="meme", description="Get a random meme")
    async def meme(self, interaction: discord.Interaction):
        data = await self.fetch_meme()
        if not data:
            await interaction.response.send_message("Failed to fetch meme 😢")
            return
        embed = discord.Embed(title=data.get("title"), color=discord.Color.random())
        embed.set_image(url=data.get("url"))
        await interaction.response.send_message(embed=embed)

    # 2. /meme_sub
    @app_commands.command(name="meme_sub", description="Get a meme from a specific subreddit")
    async def meme_sub(self, interaction: discord.Interaction, subreddit: str):
        data = await self.fetch_meme(subreddit)
        if not data or data.get("code") == 404:
            await interaction.response.send_message("Could not fetch from that subreddit 😕")
            return
        embed = discord.Embed(title=f"{data.get('title')} (r/{subreddit})", color=discord.Color.random())
        embed.set_image(url=data.get("url"))
        await interaction.response.send_message(embed=embed)

    # 3. /meme_random
    @app_commands.command(name="meme_random", description="Get multiple random memes")
    async def meme_random(self, interaction: discord.Interaction, count: int = 3):
        count = min(max(count, 1), 10)
        memes = []
        for _ in range(count):
            data = await self.fetch_meme()
            if data:
                memes.append(data.get("url"))
        if not memes:
            await interaction.response.send_message("No memes found.")
            return
        embeds = []
        for url in memes:
            e = discord.Embed(color=discord.Color.random())
            e.set_image(url=url)
            embeds.append(e)
        await interaction.response.send_message(embeds=embeds)

    # 4. /meme_title
    @app_commands.command(name="meme_title", description="Get meme title only")
    async def meme_title(self, interaction: discord.Interaction):
        data = await self.fetch_meme()
        await interaction.response.send_message(f"**Meme Title:** {data.get('title')}" if data else "Error fetching")

    # 5. /meme_info
    @app_commands.command(name="meme_info", description="Get meme info")
    async def meme_info(self, interaction: discord.Interaction):
        data = await self.fetch_meme()
        if not data:
            await interaction.response.send_message("Error fetching")
            return
        info = f"**Title:** {data.get('title')}\n**Author:** {data.get('author')}\n**Post Link:** {data.get('postLink')}"
        await interaction.response.send_message(info)

    # 6. /meme_author
    @app_commands.command(name="meme_author", description="Get a meme with author info")
    async def meme_author(self, interaction: discord.Interaction):
        data = await self.fetch_meme()
        if not data:
            await interaction.response.send_message("Error")
            return
        embed = discord.Embed(title=data.get("title"), description=f"By: {data.get('author')}", color=discord.Color.random())
        embed.set_image(url=data.get("url"))
        await interaction.response.send_message(embed=embed)

    # 7. /meme_random_subs
    @app_commands.command(name="meme_random_subs", description="Get meme from random popular subs")
    async def meme_random_subs(self, interaction: discord.Interaction):
        popular_subs = ["memes", "dankmemes", "funny", "wholesomememes", "programmerhumor"]
        sub = random.choice(popular_subs)
        data = await self.fetch_meme(sub)
        if not data:
            await interaction.response.send_message("Error fetching")
            return
        embed = discord.Embed(title=f"{data.get('title')} (r/{sub})", color=discord.Color.random())
        embed.set_image(url=data.get("url"))
        await interaction.response.send_message(embed=embed)

    # 8. /meme_link
    @app_commands.command(name="meme_link", description="Get direct meme link")
    async def meme_link(self, interaction: discord.Interaction):
        data = await self.fetch_meme()
        await interaction.response.send_message(data.get("url") if data else "Error fetching")

    # 9. /meme_embed
    @app_commands.command(name="meme_embed", description="Get meme with embed")
    async def meme_embed(self, interaction: discord.Interaction):
        data = await self.fetch_meme()
        if not data:
            await interaction.response.send_message("Error")
            return
        embed = discord.Embed(title="Here’s your Meme!", color=discord.Color.random())
        embed.set_image(url=data.get("url"))
        embed.set_footer(text=f"From r/{data.get('subreddit')}")
        await interaction.response.send_message(embed=embed)

    # 10. /meme_sub_info
    @app_commands.command(name="meme_sub_info", description="Get meme plus sub info")
    async def meme_sub_info(self, interaction: discord.Interaction, subreddit: str):
        data = await self.fetch_meme(subreddit)
        if not data:
            await interaction.response.send_message("Error")
            return
        info = f"**Sub:** {data.get('subreddit')}\n**Title:** {data.get('title')}"
        embed = discord.Embed(description=info, color=discord.Color.random())
        embed.set_image(url=data.get("url"))
        await interaction.response.send_message(embed=embed)

    # 11. /meme_sub_random
    @app_commands.command(name="meme_sub_random", description="Get random meme from random sub")
    async def meme_sub_random(self, interaction: discord.Interaction):
        random_subs = ["memes", "dankmemes", "AdviceAnimals", "PrequelMemes", "terriblefacebookmemes"]
        sub = random.choice(random_subs)
        data = await self.fetch_meme(sub)
        if not data:
            await interaction.response.send_message("Error")
            return
        embed = discord.Embed(title=f"Random Sub: r/{sub}", color=discord.Color.random())
        embed.set_image(url=data.get("url"))
        await interaction.response.send_message(embed=embed)

    # 12. /meme_subs
    @app_commands.command(name="meme_subs", description="List popular subs I can use")
    async def meme_subs(self, interaction: discord.Interaction):
        subs = ["memes", "dankmemes", "funny", "wholesomememes", "programmerhumor", "AdviceAnimals"]
        await interaction.response.send_message("Available subs: " + ", ".join(subs))

    # 13. /meme_random_title
    @app_commands.command(name="meme_random_title", description="Get just a meme title")
    async def meme_random_title(self, interaction: discord.Interaction):
        data = await self.fetch_meme()
        await interaction.response.send_message(data.get("title") if data else "Error")

    # 14. /meme_sub_random_title
    @app_commands.command(name="meme_sub_random_title", description="Get just a title from a sub")
    async def meme_sub_random_title(self, interaction: discord.Interaction, subreddit: str):
        data = await self.fetch_meme(subreddit)
        await interaction.response.send_message(data.get("title") if data else "Error")

    # 15. /meme_image_only
    @app_commands.command(name="meme_image_only", description="Get only the meme image URL")
    async def meme_image_only(self, interaction: discord.Interaction):
        data = await self.fetch_meme()
        await interaction.response.send_message(data.get("url") if data else "Error")

    # 16. /meme_sub_image
    @app_commands.command(name="meme_sub_image", description="Get only the image from a sub")
    async def meme_sub_image(self, interaction: discord.Interaction, subreddit: str):
        data = await self.fetch_meme(subreddit)
        await interaction.response.send_message(data.get("url") if data else "Error")

    # 17. /meme_sub_info_link
    @app_commands.command(name="meme_sub_info_link", description="Get title + post link from a sub")
    async def meme_sub_info_link(self, interaction: discord.Interaction, subreddit: str):
        data = await self.fetch_meme(subreddit)
        if not data:
            await interaction.response.send_message("Error")
            return
        await interaction.response.send_message(f"{data.get('title')}\n{data.get('postLink')}")

    # 18. /meme_post_link
    @app_commands.command(name="meme_post_link", description="Get meme with the post link")
    async def meme_post_link(self, interaction: discord.Interaction):
        data = await self.fetch_meme()
        if not data:
            await interaction.response.send_message("Error")
            return
        await interaction.response.send_message(f"{data.get('postLink')}")

    # 19. /meme_full
    @app_commands.command(name="meme_full", description="Full meme info")
    async def meme_full(self, interaction: discord.Interaction):
        data = await self.fetch_meme()
        if not data:
            await interaction.response.send_message("Error")
            return
        info = (
            f"**Title:** {data.get('title')}\n"
            f"**Author:** {data.get('author')}\n"
            f"**Subreddit:** {data.get('subreddit')}\n"
            f"**Post:** {data.get('postLink')}\n"
            f"**Image:** {data.get('url')}"
        )
        await interaction.response.send_message(info)

    # 20. /meme_info_embed
    @app_commands.command(name="meme_info_embed", description="Embed with full meme info")
    async def meme_info_embed(self, interaction: discord.Interaction):
        data = await self.fetch_meme()
        if not data:
            await interaction.response.send_message("Error")
            return
        embed = discord.Embed(
            title=data.get("title"),
            description=f"By {data.get('author')} | r/{data.get('subreddit')}",
            color=discord.Color.random()
        )
        embed.set_image(url=data.get("url"))
        embed.add_field(name="Post Link", value=data.get("postLink"))
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Memes(bot), guild=discord.Object(id=GUILD_ID))
