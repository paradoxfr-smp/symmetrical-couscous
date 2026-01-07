import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from googletrans import Translator
from config import GUILD_ID

DATA_FILE = "translation.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

translator = Translator()

class Translation(commands.Cog):
    """Translation commands with 20 functional slash commands"""

    def __init__(self, bot):
        self.bot = bot
        self.data = load_data()

    # ----------------------------
    # 1. /translate
    # ----------------------------
    @app_commands.command(name="translate", description="Translate text to a target language")
    async def translate(self, interaction: discord.Interaction, text: str, target: str):
        translated = translator.translate(text, dest=target)
        await interaction.response.send_message(f"**Original:** {text}\n**Translated ({target}):** {translated.text}")

    # ----------------------------
    # 2. /detect
    # ----------------------------
    @app_commands.command(name="detect", description="Detect language of text")
    async def detect(self, interaction: discord.Interaction, text: str):
        detected = translator.detect(text)
        await interaction.response.send_message(f"Detected language: `{detected.lang}` | Confidence: `{detected.confidence}`")

    # ----------------------------
    # 3. /translate_auto
    # ----------------------------
    @app_commands.command(name="translate_auto", description="Auto-detect and translate to English")
    async def translate_auto(self, interaction: discord.Interaction, text: str):
        translated = translator.translate(text, dest="en")
        await interaction.response.send_message(f"**Original:** {text}\n**Translated (en):** {translated.text}")

    # ----------------------------
    # 4. /setlang
    # ----------------------------
    @app_commands.command(name="setlang", description="Set your preferred target language")
    async def setlang(self, interaction: discord.Interaction, lang: str):
        user_id = str(interaction.user.id)
        self.data.setdefault(user_id, {})["lang"] = lang
        save_data(self.data)
        await interaction.response.send_message(f"✅ Your preferred language set to `{lang}`")

    # ----------------------------
    # 5. /mylang
    # ----------------------------
    @app_commands.command(name="mylang", description="Check your preferred language")
    async def mylang(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        lang = self.data.get(user_id, {}).get("lang", "en")
        await interaction.response.send_message(f"Your preferred language: `{lang}`")

    # ----------------------------
    # 6. /translate_user
    # ----------------------------
    @app_commands.command(name="translate_user", description="Translate a message from a user")
    async def translate_user(self, interaction: discord.Interaction, member: discord.Member, target: str):
        last_msg = None
        async for msg in interaction.channel.history(limit=100):
            if msg.author.id == member.id:
                last_msg = msg.content
                break
        if last_msg:
            translated = translator.translate(last_msg, dest=target)
            await interaction.response.send_message(f"**Original ({member.display_name}):** {last_msg}\n**Translated ({target}):** {translated.text}")
        else:
            await interaction.response.send_message(f"No recent message found for {member.mention}", ephemeral=True)

    # ----------------------------
    # 7. /listlangs
    # ----------------------------
    @app_commands.command(name="listlangs", description="List some language codes")
    async def listlangs(self, interaction: discord.Interaction):
        codes = ["en", "es", "fr", "de", "zh-cn", "ja", "ko", "ru", "ar", "pt"]
        await interaction.response.send_message(f"Supported language codes: {', '.join(codes)}")

    # ----------------------------
    # 8. /translate_last
    # ----------------------------
    @app_commands.command(name="translate_last", description="Translate last message in channel")
    async def translate_last(self, interaction: discord.Interaction, target: str):
        async for msg in interaction.channel.history(limit=2):
            if msg.id != interaction.id:
                translated = translator.translate(msg.content, dest=target)
                await interaction.response.send_message(f"**Original:** {msg.content}\n**Translated ({target}):** {translated.text}")
                return

    # ----------------------------
    # 9. /translate_auto_user
    # ----------------------------
    @app_commands.command(name="translate_auto_user", description="Translate last message of a user to English")
    async def translate_auto_user(self, interaction: discord.Interaction, member: discord.Member):
        last_msg = None
        async for msg in interaction.channel.history(limit=100):
            if msg.author.id == member.id:
                last_msg = msg.content
                break
        if last_msg:
            translated = translator.translate(last_msg, dest="en")
            await interaction.response.send_message(f"**Original ({member.display_name}):** {last_msg}\n**Translated (en):** {translated.text}")
        else:
            await interaction.response.send_message(f"No recent message found for {member.mention}", ephemeral=True)

    # ----------------------------
    # 10. /translate_saved
    # ----------------------------
    @app_commands.command(name="translate_saved", description="Translate your saved text")
    async def translate_saved(self, interaction: discord.Interaction, text: str):
        user_id = str(interaction.user.id)
        saved_texts = self.data.setdefault(user_id, {}).setdefault("saved", [])
        saved_texts.append(text)
        save_data(self.data)
        lang = self.data.get(user_id, {}).get("lang", "en")
        translated = translator.translate(text, dest=lang)
        await interaction.response.send_message(f"✅ Saved text and translated to `{lang}`: {translated.text}")

    # ----------------------------
    # 11. /list_saved
    # ----------------------------
    @app_commands.command(name="list_saved", description="List your saved texts")
    async def list_saved(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        saved_texts = self.data.get(user_id, {}).get("saved", [])
        if saved_texts:
            await interaction.response.send_message("\n".join(saved_texts))
        else:
            await interaction.response.send_message("You have no saved texts.")

    # ----------------------------
    # 12. /clear_saved
    # ----------------------------
    @app_commands.command(name="clear_saved", description="Clear your saved texts")
    async def clear_saved(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        self.data.get(user_id, {})["saved"] = []
        save_data(self.data)
        await interaction.response.send_message("✅ Cleared all saved texts")

    # ----------------------------
    # 13. /translate_channel
    # ----------------------------
    @app_commands.command(name="translate_channel", description="Translate last 5 messages in channel")
    async def translate_channel(self, interaction: discord.Interaction, target: str):
        messages = []
        async for msg in interaction.channel.history(limit=5):
            messages.append(msg.content)
        translated_list = [translator.translate(m, dest=target).text for m in reversed(messages)]
        await interaction.response.send_message("\n".join(translated_list))

    # ----------------------------
    # 14. /detect_saved
    # ----------------------------
    @app_commands.command(name="detect_saved", description="Detect language of your saved text")
    async def detect_saved(self, interaction: discord.Interaction, index: int):
        user_id = str(interaction.user.id)
        saved_texts = self.data.get(user_id, {}).get("saved", [])
        if 0 <= index-1 < len(saved_texts):
            detected = translator.detect(saved_texts[index-1])
            await interaction.response.send_message(f"Language: {detected.lang} | Confidence: {detected.confidence}")
        else:
            await interaction.response.send_message("Invalid index", ephemeral=True)

    # ----------------------------
    # 15. /translate_index
    # ----------------------------
    @app_commands.command(name="translate_index", description="Translate a saved text by index")
    async def translate_index(self, interaction: discord.Interaction, index: int, target: str):
        user_id = str(interaction.user.id)
        saved_texts = self.data.get(user_id, {}).get("saved", [])
        if 0 <= index-1 < len(saved_texts):
            translated = translator.translate(saved_texts[index-1], dest=target)
            await interaction.response.send_message(f"Translated: {translated.text}")
        else:
            await interaction.response.send_message("Invalid index", ephemeral=True)

    # ----------------------------
    # 16. /remove_saved
    # ----------------------------
    @app_commands.command(name="remove_saved", description="Remove a saved text by index")
    async def remove_saved(self, interaction: discord.Interaction, index: int):
        user_id = str(interaction.user.id)
        saved_texts = self.data.get(user_id, {}).get("saved", [])
        if 0 <= index-1 < len(saved_texts):
            removed = saved_texts.pop(index-1)
            save_data(self.data)
            await interaction.response.send_message(f"Removed saved text: {removed}")
        else:
            await interaction.response.send_message("Invalid index", ephemeral=True)

    # ----------------------------
    # 17. /translate_dm
    # ----------------------------
    @app_commands.command(name="translate_dm", description="Translate text to DM of user")
    async def translate_dm(self, interaction: discord.Interaction, member: discord.Member, text: str, target: str):
        translated = translator.translate(text, dest=target)
        await member.send(f"Translated text from {interaction.user.display_name}: {translated.text}")
        await interaction.response.send_message(f"✅ Sent translated text to {member.mention}")

    # ----------------------------
    # 18. /translate_file
    # ----------------------------
    @app_commands.command(name="translate_file", description="Translate text from a file attachment")
    async def translate_file(self, interaction: discord.Interaction, target: str):
        if interaction.user and interaction.channel.last_message_id:
            last_msg = await interaction.channel.fetch_message(interaction.channel.last_message_id)
            if last_msg.attachments:
                file = last_msg.attachments[0]
                content = await file.read()
                text = content.decode("utf-8")
                translated = translator.translate(text, dest=target)
                await interaction.response.send_message(f"Translated:\n{translated.text}")
            else:
                await interaction.response.send_message("No attachment found", ephemeral=True)

    # ----------------------------
    # 19. /translate_multi
    # ----------------------------
    @app_commands.command(name="translate_multi", description="Translate multiple lines of text")
    async def translate_multi(self, interaction: discord.Interaction, text: str, target: str):
        lines = text.split(";")
        translated_lines = [translator.translate(line, dest=target).text for line in lines]
        await interaction.response.send_message("\n".join(translated_lines))

    # ----------------------------
    # 20. /translate_saved_all
    # ----------------------------
    @app_commands.command(name="translate_saved_all", description="Translate all your saved texts to preferred language")
    async def translate_saved_all(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        saved_texts = self.data.get(user_id, {}).get("saved", [])
        lang = self.data.get(user_id, {}).get("lang", "en")
        translated = [translator.translate(text, dest=lang).text for text in saved_texts]
        await interaction.response.send_message("\n".join(translated) if translated else "No saved texts")

async def setup(bot):
    await bot.add_cog(Translation(bot), guild=discord.Object(id=GUILD_ID))
