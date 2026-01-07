import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from datetime import datetime
from config import GUILD_ID
import aiohttp
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

DATA_FILE = "images.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

class Images(commands.Cog):
    """Image commands with 20 functional slash commands"""

    def __init__(self, bot):
        self.bot = bot
        self.data = load_data()

    # ----------------------------
    # 1. /avatar
    # ----------------------------
    @app_commands.command(name="avatar", description="Show user's avatar")
    async def avatar(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        await interaction.response.send_message(f"{member.mention}'s avatar:", embed=discord.Embed().set_image(url=member.avatar.url))

    # ----------------------------
    # 2. /pixelate
    # ----------------------------
    @app_commands.command(name="pixelate", description="Pixelate a user's avatar")
    async def pixelate(self, interaction: discord.Interaction, member: discord.Member = None, size: int = 10):
        member = member or interaction.user
        async with aiohttp.ClientSession() as session:
            async with session.get(str(member.avatar.url)) as resp:
                img_bytes = await resp.read()
        image = Image.open(BytesIO(img_bytes)).convert("RGB")
        image_small = image.resize((size, size), resample=Image.BILINEAR)
        image = image_small.resize(image.size, Image.NEAREST)
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)
        await interaction.response.send_message(file=discord.File(fp=buffer, filename="pixelate.png"))

    # ----------------------------
    # 3. /invert
    # ----------------------------
    @app_commands.command(name="invert", description="Invert a user's avatar colors")
    async def invert(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        async with aiohttp.ClientSession() as session:
            async with session.get(str(member.avatar.url)) as resp:
                img_bytes = await resp.read()
        image = Image.open(BytesIO(img_bytes)).convert("RGB")
        inverted = Image.eval(image, lambda x: 255 - x)
        buffer = BytesIO()
        inverted.save(buffer, format="PNG")
        buffer.seek(0)
        await interaction.response.send_message(file=discord.File(fp=buffer, filename="invert.png"))

    # ----------------------------
    # 4. /grayscale
    # ----------------------------
    @app_commands.command(name="grayscale", description="Convert a user's avatar to grayscale")
    async def grayscale(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        async with aiohttp.ClientSession() as session:
            async with session.get(str(member.avatar.url)) as resp:
                img_bytes = await resp.read()
        image = Image.open(BytesIO(img_bytes)).convert("L")
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)
        await interaction.response.send_message(file=discord.File(fp=buffer, filename="grayscale.png"))

    # ----------------------------
    # 5. /blur
    # ----------------------------
    @app_commands.command(name="blur", description="Apply blur to a user's avatar")
    async def blur(self, interaction: discord.Interaction, member: discord.Member = None, radius: int = 5):
        from PIL import ImageFilter
        member = member or interaction.user
        async with aiohttp.ClientSession() as session:
            async with session.get(str(member.avatar.url)) as resp:
                img_bytes = await resp.read()
        image = Image.open(BytesIO(img_bytes)).convert("RGB")
        image = image.filter(ImageFilter.GaussianBlur(radius))
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)
        await interaction.response.send_message(file=discord.File(fp=buffer, filename="blur.png"))

    # ----------------------------
    # 6. /rotate
    # ----------------------------
    @app_commands.command(name="rotate", description="Rotate a user's avatar")
    async def rotate(self, interaction: discord.Interaction, member: discord.Member = None, degrees: int = 90):
        member = member or interaction.user
        async with aiohttp.ClientSession() as session:
            async with session.get(str(member.avatar.url)) as resp:
                img_bytes = await resp.read()
        image = Image.open(BytesIO(img_bytes)).convert("RGBA")
        rotated = image.rotate(degrees, expand=True)
        buffer = BytesIO()
        rotated.save(buffer, format="PNG")
        buffer.seek(0)
        await interaction.response.send_message(file=discord.File(fp=buffer, filename="rotate.png"))

    # ----------------------------
    # 7. /textimage
    # ----------------------------
    @app_commands.command(name="textimage", description="Create an image with custom text")
    async def textimage(self, interaction: discord.Interaction, text: str):
        image = Image.new("RGB", (600, 200), color=(73, 109, 137))
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()
        draw.text((10, 80), text, fill=(255, 255, 255), font=font)
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)
        await interaction.response.send_message(file=discord.File(fp=buffer, filename="text.png"))

    # ----------------------------
    # 8. /flip
    # ----------------------------
    @app_commands.command(name="flip", description="Flip a user's avatar horizontally")
    async def flip(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        async with aiohttp.ClientSession() as session:
            async with session.get(str(member.avatar.url)) as resp:
                img_bytes = await resp.read()
        image = Image.open(BytesIO(img_bytes))
        flipped = image.transpose(Image.FLIP_LEFT_RIGHT)
        buffer = BytesIO()
        flipped.save(buffer, format="PNG")
        buffer.seek(0)
        await interaction.response.send_message(file=discord.File(fp=buffer, filename="flip.png"))

    # ----------------------------
    # 9. /mirror
    # ----------------------------
    @app_commands.command(name="mirror", description="Mirror a user's avatar vertically")
    async def mirror(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        async with aiohttp.ClientSession() as session:
            async with session.get(str(member.avatar.url)) as resp:
                img_bytes = await resp.read()
        image = Image.open(BytesIO(img_bytes))
        mirrored = image.transpose(Image.FLIP_TOP_BOTTOM)
        buffer = BytesIO()
        mirrored.save(buffer, format="PNG")
        buffer.seek(0)
        await interaction.response.send_message(file=discord.File(fp=buffer, filename="mirror.png"))

    # ----------------------------
    # 10. /circleavatar
    # ----------------------------
    @app_commands.command(name="circleavatar", description="Make avatar circular")
    async def circleavatar(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        async with aiohttp.ClientSession() as session:
            async with session.get(str(member.avatar.url)) as resp:
                img_bytes = await resp.read()
        image = Image.open(BytesIO(img_bytes)).convert("RGBA")
        size = image.size
        mask = Image.new("L", size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=255)
        output = Image.new("RGBA", size)
        output.paste(image, mask=mask)
        buffer = BytesIO()
        output.save(buffer, format="PNG")
        buffer.seek(0)
        await interaction.response.send_message(file=discord.File(fp=buffer, filename="circle.png"))

    # ----------------------------
    # 11. /sharpen
    # ----------------------------
    @app_commands.command(name="sharpen", description="Sharpen a user's avatar")
    async def sharpen(self, interaction: discord.Interaction, member: discord.Member = None):
        from PIL import ImageFilter
        member = member or interaction.user
        async with aiohttp.ClientSession() as session:
            async with session.get(str(member.avatar.url)) as resp:
                img_bytes = await resp.read()
        image = Image.open(BytesIO(img_bytes))
        sharp = image.filter(ImageFilter.SHARPEN)
        buffer = BytesIO()
        sharp.save(buffer, format="PNG")
        buffer.seek(0)
        await interaction.response.send_message(file=discord.File(fp=buffer, filename="sharpen.png"))

    # ----------------------------
    # 12. /sepia
    # ----------------------------
    @app_commands.command(name="sepia", description="Apply sepia filter to avatar")
    async def sepia(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        async with aiohttp.ClientSession() as session:
            async with session.get(str(member.avatar.url)) as resp:
                img_bytes = await resp.read()
        image = Image.open(BytesIO(img_bytes)).convert("RGB")
        sepia_image = Image.new("RGB", image.size)
        pixels = image.load()
        for x in range(image.width):
            for y in range(image.height):
                r, g, b = pixels[x, y]
                tr = int(0.393*r + 0.769*g + 0.189*b)
                tg = int(0.349*r + 0.686*g + 0.168*b)
                tb = int(0.272*r + 0.534*g + 0.131*b)
                sepia_image.putpixel((x, y), (min(tr,255), min(tg,255), min(tb,255)))
        buffer = BytesIO()
        sepia_image.save(buffer, format="PNG")
        buffer.seek(0)
        await interaction.response.send_message(file=discord.File(fp=buffer, filename="sepia.png"))

    # ----------------------------
    # 13. /sketch
    # ----------------------------
    @app_commands.command(name="sketch", description="Sketch effect on avatar")
    async def sketch(self, interaction: discord.Interaction, member: discord.Member = None):
        from PIL import ImageFilter
        member = member or interaction.user
        async with aiohttp.ClientSession() as session:
            async with session.get(str(member.avatar.url)) as resp:
                img_bytes = await resp.read()
        image = Image.open(BytesIO(img_bytes)).convert("L")
        sketch = image.filter(ImageFilter.CONTOUR)
        buffer = BytesIO()
        sketch.save(buffer, format="PNG")
        buffer.seek(0)
        await interaction.response.send_message(file=discord.File(fp=buffer, filename="sketch.png"))

    # ----------------------------
    # 14. /thumbnail
    # ----------------------------
    @app_commands.command(name="thumbnail", description="Create a 128x128 thumbnail of avatar")
    async def thumbnail(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        async with aiohttp.ClientSession() as session:
            async with session.get(str(member.avatar.url)) as resp:
                img_bytes = await resp.read()
        image = Image.open(BytesIO(img_bytes))
        image.thumbnail((128,128))
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)
        await interaction.response.send_message(file=discord.File(fp=buffer, filename="thumbnail.png"))

    # ----------------------------
    # 15. /banner
    # ----------------------------
    @app_commands.command(name="banner", description="Show user's banner if available")
    async def banner(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        user = await interaction.client.fetch_user(member.id)
        if user.banner:
            await interaction.response.send_message(file=discord.File(BytesIO(await user.banner.read()), filename="banner.png"))
        else:
            await interaction.response.send_message("❌ User has no banner", ephemeral=True)

    # ----------------------------
    # 16. /frameavatar
    # ----------------------------
    @app_commands.command(name="frameavatar", description="Add a red frame to avatar")
    async def frameavatar(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        async with aiohttp.ClientSession() as session:
            async with session.get(str(member.avatar.url)) as resp:
                img_bytes = await resp.read()
        image = Image.open(BytesIO(img_bytes)).convert("RGBA")
        draw = ImageDraw.Draw(image)
        draw.rectangle([0,0,image.width-1,image.height-1], outline="red", width=10)
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)
        await interaction.response.send_message(file=discord.File(fp=buffer, filename="frame.png"))

    # ----------------------------
    # 17. /resize
    # ----------------------------
    @app_commands.command(name="resize", description="Resize avatar to width and height")
    async def resize(self, interaction: discord.Interaction, member: discord.Member = None, width: int = 256, height: int = 256):
        member = member or interaction.user
        async with aiohttp.ClientSession() as session:
            async with session.get(str(member.avatar.url)) as resp:
                img_bytes = await resp.read()
        image = Image.open(BytesIO(img_bytes))
        image = image.resize((width, height))
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)
        await interaction.response.send_message(file=discord.File(fp=buffer, filename="resize.png"))

    # ----------------------------
    # 18. /textoverlay
    # ----------------------------
    @app_commands.command(name="textoverlay", description="Overlay text on avatar")
    async def textoverlay(self, interaction: discord.Interaction, text: str, member: discord.Member = None):
        member = member or interaction.user
        async with aiohttp.ClientSession() as session:
            async with session.get(str(member.avatar.url)) as resp:
                img_bytes = await resp.read()
        image = Image.open(BytesIO(img_bytes)).convert("RGBA")
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()
        draw.text((10,10), text, fill=(255,255,255), font=font)
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)
        await interaction.response.send_message(file=discord.File(fp=buffer, filename="overlay.png"))

    # ----------------------------
    # 19. /combineavatars
    # ----------------------------
    @app_commands.command(name="combineavatars", description="Combine two user avatars side by side")
    async def combineavatars(self, interaction: discord.Interaction, member1: discord.Member, member2: discord.Member):
        async with aiohttp.ClientSession() as session:
            async with session.get(str(member1.avatar.url)) as resp:
                img1 = Image.open(BytesIO(await resp.read())).convert("RGBA")
            async with session.get(str(member2.avatar.url)) as resp:
                img2 = Image.open(BytesIO(await resp.read())).convert("RGBA")
        width = img1.width + img2.width
        height = max(img1.height, img2.height)
        new_img = Image.new("RGBA", (width, height))
        new_img.paste(img1, (0,0))
        new_img.paste(img2, (img1.width,0))
        buffer = BytesIO()
        new_img.save(buffer, format="PNG")
        buffer.seek(0)
        await interaction.response.send_message(file=discord.File(fp=buffer, filename="combine.png"))

    # ----------------------------
    # 20. /saveimage
    # ----------------------------
    @app_commands.command(name="saveimage", description="Save an image URL to JSON record")
    async def saveimage(self, interaction: discord.Interaction, url: str):
        user_id = str(interaction.user.id)
        self.data.setdefault(user_id, {}).setdefault("images", []).append(url)
        save_data(self.data)
        await interaction.response.send_message("✅ Image saved to your record")

async def setup(bot):
    await bot.add_cog(Images(bot), guild=discord.Object(id=GUILD_ID))
