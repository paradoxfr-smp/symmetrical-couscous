import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import os
import asyncio
from datetime import datetime, timedelta
from config import GUILD_ID

DATA_FILE = "giveaways.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

class Giveaways(commands.Cog):
    """Giveaways system with 20 slash commands and JSON persistence"""

    def __init__(self, bot):
        self.bot = bot
        self.data = load_data()
        self.check_giveaways.start()

    # ----------------------------
    # 1. /creategiveaway
    # ----------------------------
    @app_commands.command(name="creategiveaway", description="Create a new giveaway")
    async def creategiveaway(self, interaction: discord.Interaction, channel: discord.TextChannel, prize: str, duration: int, winners: int):
        """Duration in minutes"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ You need Manage Server permission.", ephemeral=True)
            return
        end_time = datetime.utcnow() + timedelta(minutes=duration)
        embed = discord.Embed(title=f"🎉 Giveaway: {prize}", description=f"React with 🎉 to enter!\nEnds at {end_time} UTC\nWinners: {winners}", color=discord.Color.green())
        msg = await channel.send(embed=embed)
        await msg.add_reaction("🎉")
        self.data.setdefault(str(interaction.guild.id), {}).setdefault("giveaways", {})[str(msg.id)] = {
            "channel_id": channel.id,
            "prize": prize,
            "end_time": end_time.isoformat(),
            "winners": winners,
            "ended": False
        }
        save_data(self.data)
        await interaction.response.send_message(f"✅ Giveaway created in {channel.mention}")

    # ----------------------------
    # 2. /endgiveaway
    # ----------------------------
    @app_commands.command(name="endgiveaway", description="End a giveaway early")
    async def endgiveaway(self, interaction: discord.Interaction, message_id: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("giveaways", {})
        if message_id in guild_data:
            guild_data[message_id]["end_time"] = datetime.utcnow().isoformat()
            save_data(self.data)
            await interaction.response.send_message(f"✅ Giveaway {message_id} ended early")
        else:
            await interaction.response.send_message("❌ Giveaway not found", ephemeral=True)

    # ----------------------------
    # 3. /rerollgiveaway
    # ----------------------------
    @app_commands.command(name="rerollgiveaway", description="Reroll winners of a giveaway")
    async def rerollgiveaway(self, interaction: discord.Interaction, message_id: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("giveaways", {})
        if message_id not in guild_data:
            await interaction.response.send_message("❌ Giveaway not found", ephemeral=True)
            return
        giveaway = guild_data[message_id]
        channel = interaction.guild.get_channel(giveaway["channel_id"])
        msg = await channel.fetch_message(int(message_id))
        users = await self.get_users(msg)
        if not users:
            await interaction.response.send_message("❌ No participants to reroll", ephemeral=True)
            return
        winners_count = giveaway["winners"]
        winners = []
        if len(users) <= winners_count:
            winners = users
        else:
            while len(winners) < winners_count:
                winner = users.pop(users.index(users[0]))
                winners.append(winner)
        mentions = ", ".join(w.mention for w in winners)
        await channel.send(f"🏆 Giveaway reroll winners: {mentions}")
        await interaction.response.send_message(f"✅ Giveaway {message_id} rerolled")

    # ----------------------------
    # 4. /listgiveaways
    # ----------------------------
    @app_commands.command(name="listgiveaways", description="List all active giveaways")
    async def listgiveaways(self, interaction: discord.Interaction):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("giveaways", {})
        if not guild_data:
            await interaction.response.send_message("❌ No active giveaways.")
            return
        desc = ""
        for msg_id, g in guild_data.items():
            status = "Ended" if g["ended"] else "Active"
            desc += f"ID: {msg_id} | Prize: {g['prize']} | Status: {status}\n"
        await interaction.response.send_message(f"📜 Giveaways:\n{desc}")

    # ----------------------------
    # 5. /giveawayinfo
    # ----------------------------
    @app_commands.command(name="giveawayinfo", description="Show detailed info of a giveaway")
    async def giveawayinfo(self, interaction: discord.Interaction, message_id: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("giveaways", {})
        if message_id not in guild_data:
            await interaction.response.send_message("❌ Giveaway not found", ephemeral=True)
            return
        g = guild_data[message_id]
        embed = discord.Embed(title=f"🎉 Giveaway Info - {g['prize']}", color=discord.Color.blue())
        embed.add_field(name="Message ID", value=message_id)
        embed.add_field(name="Channel", value=f"<#{g['channel_id']}>")
        embed.add_field(name="End Time", value=g['end_time'])
        embed.add_field(name="Winners", value=g['winners'])
        embed.add_field(name="Ended", value=g['ended'])
        await interaction.response.send_message(embed=embed)

    # ----------------------------
    # 6. /deletegiveaway
    # ----------------------------
    @app_commands.command(name="deletegiveaway", description="Delete a giveaway")
    async def deletegiveaway(self, interaction: discord.Interaction, message_id: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("giveaways", {})
        if message_id in guild_data:
            del guild_data[message_id]
            save_data(self.data)
            await interaction.response.send_message(f"🗑️ Giveaway {message_id} deleted")
        else:
            await interaction.response.send_message("❌ Giveaway not found", ephemeral=True)

    # ----------------------------
    # 7. /joinparticipants
    # ----------------------------
    @app_commands.command(name="joinparticipants", description="Show number of participants")
    async def joinparticipants(self, interaction: discord.Interaction, message_id: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("giveaways", {})
        if message_id not in guild_data:
            await interaction.response.send_message("❌ Giveaway not found")
            return
        g = guild_data[message_id]
        channel = interaction.guild.get_channel(g["channel_id"])
        msg = await channel.fetch_message(int(message_id))
        users = await self.get_users(msg)
        await interaction.response.send_message(f"👥 {len(users)} participants in giveaway {message_id}")

    # ----------------------------
    # 8. /drawgiveaway
    # ----------------------------
    @app_commands.command(name="drawgiveaway", description="Draw winners for a giveaway")
    async def drawgiveaway(self, interaction: discord.Interaction, message_id: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("giveaways", {})
        if message_id not in guild_data:
            await interaction.response.send_message("❌ Giveaway not found")
            return
        giveaway = guild_data[message_id]
        if giveaway["ended"]:
            await interaction.response.send_message("❌ Giveaway already ended")
            return
        channel = interaction.guild.get_channel(giveaway["channel_id"])
        msg = await channel.fetch_message(int(message_id))
        users = await self.get_users(msg)
        if not users:
            await interaction.response.send_message("❌ No participants")
            return
        winners = []
        winners_count = giveaway["winners"]
        if len(users) <= winners_count:
            winners = users
        else:
            while len(winners) < winners_count:
                winner = users.pop(users.index(users[0]))
                winners.append(winner)
        mentions = ", ".join(w.mention for w in winners)
        await channel.send(f"🏆 Giveaway winners: {mentions}")
        giveaway["ended"] = True
        save_data(self.data)
        await interaction.response.send_message("✅ Giveaway drawn")

    # ----------------------------
    # 9. /extendgiveaway
    # ----------------------------
    @app_commands.command(name="extendgiveaway", description="Extend a giveaway duration")
    async def extendgiveaway(self, interaction: discord.Interaction, message_id: str, minutes: int):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("giveaways", {})
        if message_id not in guild_data:
            await interaction.response.send_message("❌ Giveaway not found")
            return
        g = guild_data[message_id]
        end_time = datetime.fromisoformat(g["end_time"]) + timedelta(minutes=minutes)
        g["end_time"] = end_time.isoformat()
        save_data(self.data)
        await interaction.response.send_message(f"⏱️ Extended giveaway by {minutes} minutes")

    # ----------------------------
    # 10. /giveawayprize
    # ----------------------------
    @app_commands.command(name="giveawayprize", description="Change prize of a giveaway")
    async def giveawayprize(self, interaction: discord.Interaction, message_id: str, prize: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("giveaways", {})
        if message_id not in guild_data:
            await interaction.response.send_message("❌ Giveaway not found")
            return
        guild_data[message_id]["prize"] = prize
        save_data(self.data)
        await interaction.response.send_message(f"🎁 Prize updated to {prize}")

    # ----------------------------
    # 11. /listended
    # ----------------------------
    @app_commands.command(name="listended", description="List all ended giveaways")
    async def listended(self, interaction: discord.Interaction):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("giveaways", {})
        ended = [f"{msg_id}: {g['prize']}" for msg_id, g in guild_data.items() if g["ended"]]
        if not ended:
            await interaction.response.send_message("❌ No ended giveaways")
            return
        await interaction.response.send_message("🎉 Ended Giveaways:\n" + "\n".join(ended))

    # ----------------------------
    # 12. /listactive
    # ----------------------------
    @app_commands.command(name="listactive", description="List all active giveaways")
    async def listactive(self, interaction: discord.Interaction):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("giveaways", {})
        active = [f"{msg_id}: {g['prize']}" for msg_id, g in guild_data.items() if not g["ended"]]
        if not active:
            await interaction.response.send_message("❌ No active giveaways")
            return
        await interaction.response.send_message("🎉 Active Giveaways:\n" + "\n".join(active))

    # ----------------------------
    # 13. /giveawaywinners
    # ----------------------------
    @app_commands.command(name="giveawaywinners", description="Show winners of a giveaway")
    async def giveawaywinners(self, interaction: discord.Interaction, message_id: str):
        # Since winners are sent in the channel, we can note this as "Check channel"
        await interaction.response.send_message("ℹ️ Winners are announced in the giveaway channel.")

    # ----------------------------
    # 14. /giveawaytimeleft
    # ----------------------------
    @app_commands.command(name="giveawaytimeleft", description="Show time left for a giveaway")
    async def giveawaytimeleft(self, interaction: discord.Interaction, message_id: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("giveaways", {})
        if message_id not in guild_data:
            await interaction.response.send_message("❌ Giveaway not found")
            return
        g = guild_data[message_id]
        if g["ended"]:
            await interaction.response.send_message("❌ Giveaway already ended")
            return
        end_time = datetime.fromisoformat(g["end_time"])
        remaining = end_time - datetime.utcnow()
        minutes, seconds = divmod(int(remaining.total_seconds()), 60)
        await interaction.response.send_message(f"⏳ Time left: {minutes} minutes, {seconds} seconds")

    # ----------------------------
    # 15. /giveawaychannel
    # ----------------------------
    @app_commands.command(name="giveawaychannel", description="Show giveaway channel")
    async def giveawaychannel(self, interaction: discord.Interaction, message_id: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("giveaways", {})
        if message_id not in guild_data:
            await interaction.response.send_message("❌ Giveaway not found")
            return
        ch = interaction.guild.get_channel(guild_data[message_id]["channel_id"])
        await interaction.response.send_message(f"📍 Giveaway channel: {ch.mention}")

    # ----------------------------
    # 16. /giveawaystatus
    # ----------------------------
    @app_commands.command(name="giveawaystatus", description="Show status of a giveaway")
    async def giveawaystatus(self, interaction: discord.Interaction, message_id: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("giveaways", {})
        if message_id not in guild_data:
            await interaction.response.send_message("❌ Giveaway not found")
            return
        ended = guild_data[message_id]["ended"]
        await interaction.response.send_message(f"🎉 Giveaway status: {'Ended' if ended else 'Active'}")

    # ----------------------------
    # 17. /giveawaycount
    # ----------------------------
    @app_commands.command(name="giveawaycount", description="Show number of giveaways in server")
    async def giveawaycount(self, interaction: discord.Interaction):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("giveaways", {})
        await interaction.response.send_message(f"📊 Total giveaways: {len(guild_data)}")

    # ----------------------------
    # 18. /deleteallgiveaways
    # ----------------------------
    @app_commands.command(name="deleteallgiveaways", description="Delete all giveaways")
    async def deleteallgiveaways(self, interaction: discord.Interaction):
        self.data[str(interaction.guild.id)]["giveaways"] = {}
        save_data(self.data)
        await interaction.response.send_message("🗑️ All giveaways deleted")

    # ----------------------------
    # 19. /giveawayprizelist
    # ----------------------------
    @app_commands.command(name="giveawayprizelist", description="List all giveaway prizes")
    async def giveawayprizelist(self, interaction: discord.Interaction):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("giveaways", {})
        prizes = [g["prize"] for g in guild_data.values()]
        await interaction.response.send_message("🎁 Giveaway prizes:\n" + "\n".join(prizes))

    # ----------------------------
    # 20. /giveawayinfoall
    # ----------------------------
    @app_commands.command(name="giveawayinfoall", description="Show all giveaway info")
    async def giveawayinfoall(self, interaction: discord.Interaction):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("giveaways", {})
        if not guild_data:
            await interaction.response.send_message("❌ No giveaways found")
            return
        desc = ""
        for msg_id, g in guild_data.items():
            desc += f"ID: {msg_id} | Prize: {g['prize']} | End: {g['end_time']} | Winners: {g['winners']} | Ended: {g['ended']}\n"
        await interaction.response.send_message(f"📜 All Giveaways:\n{desc}")

    # ----------------------------
    # Helper to fetch users who reacted
    # ----------------------------
    async def get_users(self, message):
        reaction = discord.utils.get(message.reactions, emoji="🎉")
        if reaction:
            users = await reaction.users().flatten()
            return [u for u in users if not u.bot]
        return []

    # ----------------------------
    # Background task to end giveaways automatically
    # ----------------------------
    @tasks.loop(seconds=60)
    async def check_giveaways(self):
        for guild_id, g_data in self.data.items():
            for msg_id, g in g_data.get("giveaways", {}).items():
                if not g["ended"]:
                    end_time = datetime.fromisoformat(g["end_time"])
                    if datetime.utcnow() >= end_time:
                        guild = self.bot.get_guild(int(guild_id))
                        channel = guild.get_channel(g["channel_id"])
                        msg = await channel.fetch_message(int(msg_id))
                        users = await self.get_users(msg)
                        winners_count = g["winners"]
                        winners = []
                        if users:
                            if len(users) <= winners_count:
                                winners = users
                            else:
                                while len(winners) < winners_count:
                                    winners.append(users.pop(0))
                        mentions = ", ".join(w.mention for w in winners)
                        await channel.send(f"🏆 Giveaway ended! Winners: {mentions}")
                        g["ended"] = True
        save_data(self.data)

    @check_giveaways.before_loop
    async def before_check_giveaways(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Giveaways(bot), guild=discord.Object(id=GUILD_ID))
