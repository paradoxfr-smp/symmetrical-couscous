import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from datetime import datetime, timedelta
from config import GUILD_ID

DATA_FILE = "polls.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

class Polls(commands.Cog):
    """Server Polls management with 20 slash commands"""

    def __init__(self, bot):
        self.bot = bot
        self.data = load_data()

    # ----------------------------
    # 1. /createpoll
    # ----------------------------
    @app_commands.command(name="createpoll", description="Create a new poll")
    async def createpoll(self, interaction: discord.Interaction, question: str, option1: str, option2: str, option3: str = None, option4: str = None):
        poll_id = str(int(datetime.utcnow().timestamp()))
        options = [option1, option2]
        if option3:
            options.append(option3)
        if option4:
            options.append(option4)
        self.data.setdefault(str(interaction.guild.id), {}).setdefault("polls", {})[poll_id] = {
            "question": question,
            "options": options,
            "votes": {opt: [] for opt in options},
            "created_by": interaction.user.id,
            "created_at": datetime.utcnow().isoformat(),
            "status": "open"
        }
        save_data(self.data)
        options_list = "\n".join(f"{i+1}. {opt}" for i, opt in enumerate(options))
        await interaction.response.send_message(f"📊 Poll `{poll_id}` created:\n**{question}**\n{options_list}")

    # ----------------------------
    # 2. /closepoll
    # ----------------------------
    @app_commands.command(name="closepoll", description="Close a poll")
    async def closepoll(self, interaction: discord.Interaction, poll_id: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("polls", {})
        if poll_id not in guild_data:
            await interaction.response.send_message("❌ Poll not found", ephemeral=True)
            return
        guild_data[poll_id]["status"] = "closed"
        save_data(self.data)
        await interaction.response.send_message(f"✅ Poll `{poll_id}` closed")

    # ----------------------------
    # 3. /vote
    # ----------------------------
    @app_commands.command(name="vote", description="Vote in a poll")
    async def vote(self, interaction: discord.Interaction, poll_id: str, option: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("polls", {})
        if poll_id not in guild_data:
            await interaction.response.send_message("❌ Poll not found", ephemeral=True)
            return
        poll = guild_data[poll_id]
        if poll["status"] != "open":
            await interaction.response.send_message("⚠️ Poll is closed", ephemeral=True)
            return
        # Remove previous votes
        for opts in poll["votes"].values():
            if interaction.user.id in opts:
                opts.remove(interaction.user.id)
        if option not in poll["votes"]:
            await interaction.response.send_message("❌ Invalid option", ephemeral=True)
            return
        poll["votes"][option].append(interaction.user.id)
        save_data(self.data)
        await interaction.response.send_message(f"✅ You voted for `{option}`")

    # ----------------------------
    # 4. /pollresults
    # ----------------------------
    @app_commands.command(name="pollresults", description="Show results of a poll")
    async def pollresults(self, interaction: discord.Interaction, poll_id: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("polls", {})
        if poll_id not in guild_data:
            await interaction.response.send_message("❌ Poll not found", ephemeral=True)
            return
        poll = guild_data[poll_id]
        embed = discord.Embed(title=f"📊 Poll Results: {poll['question']}", color=discord.Color.green())
        for opt, voters in poll["votes"].items():
            embed.add_field(name=opt, value=f"{len(voters)} votes", inline=False)
        await interaction.response.send_message(embed=embed)

    # ----------------------------
    # 5. /deletepoll
    # ----------------------------
    @app_commands.command(name="deletepoll", description="Delete a poll")
    async def deletepoll(self, interaction: discord.Interaction, poll_id: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("polls", {})
        if poll_id in guild_data:
            del guild_data[poll_id]
            save_data(self.data)
            await interaction.response.send_message(f"🗑️ Poll `{poll_id}` deleted")
        else:
            await interaction.response.send_message("❌ Poll not found", ephemeral=True)

    # ----------------------------
    # 6. /listpolls
    # ----------------------------
    @app_commands.command(name="listpolls", description="List all polls")
    async def listpolls(self, interaction: discord.Interaction):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("polls", {})
        if not guild_data:
            await interaction.response.send_message("❌ No polls found")
            return
        desc = ""
        for pid, p in guild_data.items():
            desc += f"ID: {pid} | {p['question']} | Status: {p['status']}\n"
        await interaction.response.send_message(f"📄 Polls:\n{desc}")

    # ----------------------------
    # 7. /pollinfo
    # ----------------------------
    @app_commands.command(name="pollinfo", description="Detailed info of a poll")
    async def pollinfo(self, interaction: discord.Interaction, poll_id: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("polls", {})
        if poll_id not in guild_data:
            await interaction.response.send_message("❌ Poll not found", ephemeral=True)
            return
        poll = guild_data[poll_id]
        embed = discord.Embed(title=f"📊 {poll['question']}", color=discord.Color.blue())
        embed.add_field(name="Status", value=poll["status"])
        embed.add_field(name="Options", value="\n".join(poll["options"]))
        await interaction.response.send_message(embed=embed)

    # ----------------------------
    # 8. /pollstatus
    # ----------------------------
    @app_commands.command(name="pollstatus", description="Check status of a poll")
    async def pollstatus(self, interaction: discord.Interaction, poll_id: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("polls", {})
        if poll_id in guild_data:
            status = guild_data[poll_id]["status"]
            await interaction.response.send_message(f"Poll `{poll_id}` status: {status}")
        else:
            await interaction.response.send_message("❌ Poll not found", ephemeral=True)

    # ----------------------------
    # 9. /addoption
    # ----------------------------
    @app_commands.command(name="addoption", description="Add an option to a poll")
    async def addoption(self, interaction: discord.Interaction, poll_id: str, option: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("polls", {})
        if poll_id in guild_data:
            poll = guild_data[poll_id]
            if option in poll["options"]:
                await interaction.response.send_message("⚠️ Option already exists", ephemeral=True)
                return
            poll["options"].append(option)
            poll["votes"][option] = []
            save_data(self.data)
            await interaction.response.send_message(f"✅ Option `{option}` added to poll `{poll_id}`")
        else:
            await interaction.response.send_message("❌ Poll not found", ephemeral=True)

    # ----------------------------
    # 10. /removeoption
    # ----------------------------
    @app_commands.command(name="removeoption", description="Remove an option from a poll")
    async def removeoption(self, interaction: discord.Interaction, poll_id: str, option: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("polls", {})
        if poll_id in guild_data:
            poll = guild_data[poll_id]
            if option in poll["options"]:
                poll["options"].remove(option)
                poll["votes"].pop(option, None)
                save_data(self.data)
                await interaction.response.send_message(f"🗑️ Option `{option}` removed from poll `{poll_id}`")
            else:
                await interaction.response.send_message("⚠️ Option not found", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Poll not found", ephemeral=True)

    # ----------------------------
    # 11. /votecount
    # ----------------------------
    @app_commands.command(name="votecount", description="Show number of votes for an option")
    async def votecount(self, interaction: discord.Interaction, poll_id: str, option: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("polls", {})
        if poll_id in guild_data:
            votes = len(guild_data[poll_id]["votes"].get(option, []))
            await interaction.response.send_message(f"Option `{option}` has {votes} votes")
        else:
            await interaction.response.send_message("❌ Poll not found", ephemeral=True)

    # ----------------------------
    # 12. /myvote
    # ----------------------------
    @app_commands.command(name="myvote", description="Check what you voted in a poll")
    async def myvote(self, interaction: discord.Interaction, poll_id: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("polls", {})
        if poll_id in guild_data:
            poll = guild_data[poll_id]
            for opt, voters in poll["votes"].items():
                if interaction.user.id in voters:
                    await interaction.response.send_message(f"✅ You voted for `{opt}`")
                    return
            await interaction.response.send_message("⚠️ You haven't voted in this poll", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Poll not found", ephemeral=True)

    # ----------------------------
    # 13. /pollcreator
    # ----------------------------
    @app_commands.command(name="pollcreator", description="Show who created a poll")
    async def pollcreator(self, interaction: discord.Interaction, poll_id: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("polls", {})
        if poll_id in guild_data:
            creator_id = guild_data[poll_id]["created_by"]
            await interaction.response.send_message(f"Poll `{poll_id}` created by <@{creator_id}>")
        else:
            await interaction.response.send_message("❌ Poll not found", ephemeral=True)

    # ----------------------------
    # 14. /resetpoll
    # ----------------------------
    @app_commands.command(name="resetpoll", description="Reset all votes in a poll")
    async def resetpoll(self, interaction: discord.Interaction, poll_id: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("polls", {})
        if poll_id in guild_data:
            for key in guild_data[poll_id]["votes"]:
                guild_data[poll_id]["votes"][key] = []
            save_data(self.data)
            await interaction.response.send_message(f"🔄 All votes reset for poll `{poll_id}`")
        else:
            await interaction.response.send_message("❌ Poll not found", ephemeral=True)

    # ----------------------------
    # 15. /pollvoters
    # ----------------------------
    @app_commands.command(name="pollvoters", description="List voters of an option")
    async def pollvoters(self, interaction: discord.Interaction, poll_id: str, option: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("polls", {})
        if poll_id in guild_data:
            voters = guild_data[poll_id]["votes"].get(option, [])
            if voters:
                mentions = ", ".join(f"<@{uid}>" for uid in voters)
                await interaction.response.send_message(f"Voters for `{option}`: {mentions}")
            else:
                await interaction.response.send_message("No votes yet for this option")
        else:
            await interaction.response.send_message("❌ Poll not found", ephemeral=True)

    # ----------------------------
    # 16. /polloptions
    # ----------------------------
    @app_commands.command(name="polloptions", description="List all options of a poll")
    async def polloptions(self, interaction: discord.Interaction, poll_id: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("polls", {})
        if poll_id in guild_data:
            options = guild_data[poll_id]["options"]
            await interaction.response.send_message(f"Options for poll `{poll_id}`: {', '.join(options)}")
        else:
            await interaction.response.send_message("❌ Poll not found", ephemeral=True)

    # ----------------------------
    # 17. /pollvotecounts
    # ----------------------------
    @app_commands.command(name="pollvotecounts", description="Show vote counts for all options")
    async def pollvotecounts(self, interaction: discord.Interaction, poll_id: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("polls", {})
        if poll_id in guild_data:
            poll = guild_data[poll_id]
            counts = "\n".join(f"{opt}: {len(voters)}" for opt, voters in poll["votes"].items())
            await interaction.response.send_message(f"Vote counts for poll `{poll_id}`:\n{counts}")
        else:
            await interaction.response.send_message("❌ Poll not found", ephemeral=True)

    # ----------------------------
    # 18. /pollcount
    # ----------------------------
    @app_commands.command(name="pollcount", description="Show total polls in server")
    async def pollcount(self, interaction: discord.Interaction):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("polls", {})
        await interaction.response.send_message(f"📊 Total polls: {len(guild_data)}")

    # ----------------------------
    # 19. /pollresetall
    # ----------------------------
    @app_commands.command(name="pollresetall", description="Delete all polls")
    async def pollresetall(self, interaction: discord.Interaction):
        self.data[str(interaction.guild.id)]["polls"] = {}
        save_data(self.data)
        await interaction.response.send_message("🔄 All polls deleted")

    # ----------------------------
    # 20. /pollsummary
    # ----------------------------
    @app_commands.command(name="pollsummary", description="Summary of a poll")
    async def pollsummary(self, interaction: discord.Interaction, poll_id: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("polls", {})
        if poll_id in guild_data:
            poll = guild_data[poll_id]
            summary = f"Poll `{poll_id}` - {poll['question']}\nStatus: {poll['status']}\n"
            for opt, voters in poll["votes"].items():
                summary += f"{opt}: {len(voters)} votes\n"
            await interaction.response.send_message(summary)
        else:
            await interaction.response.send_message("❌ Poll not found", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Polls(bot), guild=discord.Object(id=GUILD_ID))
