import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from datetime import datetime
from config import GUILD_ID

DATA_FILE = "tickets.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

class Tickets(commands.Cog):
    """Ticket system with JSON persistence and 20 slash commands"""

    def __init__(self, bot):
        self.bot = bot
        self.data = load_data()

    # ----------------------------
    # 1. /createticket
    # ----------------------------
    @app_commands.command(name="createticket", description="Create a support ticket")
    async def createticket(self, interaction: discord.Interaction, subject: str):
        guild_id = str(interaction.guild.id)
        ticket_id = str(int(datetime.utcnow().timestamp()))
        channel = await interaction.guild.create_text_channel(
            name=f"ticket-{ticket_id}",
            topic=f"Ticket for {interaction.user} | Subject: {subject}"
        )
        self.data.setdefault(guild_id, {}).setdefault("tickets", {})[ticket_id] = {
            "user_id": interaction.user.id,
            "channel_id": channel.id,
            "subject": subject,
            "status": "open",
            "assigned_to": None,
            "created_at": datetime.utcnow().isoformat()
        }
        save_data(self.data)
        await interaction.response.send_message(f"✅ Ticket created: {channel.mention}")

    # ----------------------------
    # 2. /closeticket
    # ----------------------------
    @app_commands.command(name="closeticket", description="Close a ticket")
    async def closeticket(self, interaction: discord.Interaction, ticket_id: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("tickets", {})
        if ticket_id not in guild_data:
            await interaction.response.send_message("❌ Ticket not found", ephemeral=True)
            return
        guild_data[ticket_id]["status"] = "closed"
        save_data(self.data)
        channel = interaction.guild.get_channel(guild_data[ticket_id]["channel_id"])
        await channel.delete()
        await interaction.response.send_message(f"✅ Ticket {ticket_id} closed and channel deleted")

    # ----------------------------
    # 3. /assignticket
    # ----------------------------
    @app_commands.command(name="assignticket", description="Assign a ticket to a staff member")
    async def assignticket(self, interaction: discord.Interaction, ticket_id: str, member: discord.Member):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("tickets", {})
        if ticket_id in guild_data:
            guild_data[ticket_id]["assigned_to"] = member.id
            save_data(self.data)
            await interaction.response.send_message(f"✅ Ticket {ticket_id} assigned to {member.mention}")
        else:
            await interaction.response.send_message("❌ Ticket not found", ephemeral=True)

    # ----------------------------
    # 4. /unassignticket
    # ----------------------------
    @app_commands.command(name="unassignticket", description="Remove the assigned staff member")
    async def unassignticket(self, interaction: discord.Interaction, ticket_id: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("tickets", {})
        if ticket_id in guild_data:
            guild_data[ticket_id]["assigned_to"] = None
            save_data(self.data)
            await interaction.response.send_message(f"✅ Ticket {ticket_id} unassigned")
        else:
            await interaction.response.send_message("❌ Ticket not found", ephemeral=True)

    # ----------------------------
    # 5. /listtickets
    # ----------------------------
    @app_commands.command(name="listtickets", description="List all tickets")
    async def listtickets(self, interaction: discord.Interaction):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("tickets", {})
        if not guild_data:
            await interaction.response.send_message("❌ No tickets found")
            return
        desc = ""
        for tid, t in guild_data.items():
            status = t["status"]
            assigned = f"<@{t['assigned_to']}>" if t["assigned_to"] else "None"
            desc += f"ID: {tid} | User: <@{t['user_id']}> | Status: {status} | Assigned: {assigned}\n"
        await interaction.response.send_message(f"📜 Tickets:\n{desc}")

    # ----------------------------
    # 6. /ticketinfo
    # ----------------------------
    @app_commands.command(name="ticketinfo", description="Get info of a ticket")
    async def ticketinfo(self, interaction: discord.Interaction, ticket_id: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("tickets", {})
        if ticket_id not in guild_data:
            await interaction.response.send_message("❌ Ticket not found", ephemeral=True)
            return
        t = guild_data[ticket_id]
        embed = discord.Embed(title=f"Ticket {ticket_id}", color=discord.Color.blue())
        embed.add_field(name="User", value=f"<@{t['user_id']}>")
        embed.add_field(name="Subject", value=t["subject"])
        embed.add_field(name="Status", value=t["status"])
        embed.add_field(name="Assigned To", value=f"<@{t['assigned_to']}>" if t["assigned_to"] else "None")
        embed.add_field(name="Channel", value=f"<#{t['channel_id']}>")
        embed.add_field(name="Created At", value=t["created_at"])
        await interaction.response.send_message(embed=embed)

    # ----------------------------
    # 7. /closemyticket
    # ----------------------------
    @app_commands.command(name="closemyticket", description="Close your own ticket")
    async def closemyticket(self, interaction: discord.Interaction):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("tickets", {})
        for tid, t in guild_data.items():
            if t["user_id"] == interaction.user.id and t["status"] == "open":
                t["status"] = "closed"
                save_data(self.data)
                channel = interaction.guild.get_channel(t["channel_id"])
                await channel.delete()
                await interaction.response.send_message(f"✅ Your ticket {tid} has been closed")
                return
        await interaction.response.send_message("❌ You have no open tickets", ephemeral=True)

    # ----------------------------
    # 8. /opentickets
    # ----------------------------
    @app_commands.command(name="opentickets", description="List open tickets")
    async def opentickets(self, interaction: discord.Interaction):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("tickets", {})
        open_tickets = [tid for tid, t in guild_data.items() if t["status"] == "open"]
        if not open_tickets:
            await interaction.response.send_message("❌ No open tickets")
            return
        await interaction.response.send_message("🟢 Open tickets: " + ", ".join(open_tickets))

    # ----------------------------
    # 9. /closedtickets
    # ----------------------------
    @app_commands.command(name="closedtickets", description="List closed tickets")
    async def closedtickets(self, interaction: discord.Interaction):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("tickets", {})
        closed_tickets = [tid for tid, t in guild_data.items() if t["status"] == "closed"]
        if not closed_tickets:
            await interaction.response.send_message("❌ No closed tickets")
            return
        await interaction.response.send_message("🔴 Closed tickets: " + ", ".join(closed_tickets))

    # ----------------------------
    # 10. /assigntome
    # ----------------------------
    @app_commands.command(name="assigntome", description="Assign an open ticket to yourself")
    async def assigntome(self, interaction: discord.Interaction, ticket_id: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("tickets", {})
        if ticket_id in guild_data:
            guild_data[ticket_id]["assigned_to"] = interaction.user.id
            save_data(self.data)
            await interaction.response.send_message(f"✅ Ticket {ticket_id} assigned to you")
        else:
            await interaction.response.send_message("❌ Ticket not found", ephemeral=True)

    # ----------------------------
    # 11. /unassignme
    # ----------------------------
    @app_commands.command(name="unassignme", description="Unassign yourself from a ticket")
    async def unassignme(self, interaction: discord.Interaction, ticket_id: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("tickets", {})
        if ticket_id in guild_data and guild_data[ticket_id]["assigned_to"] == interaction.user.id:
            guild_data[ticket_id]["assigned_to"] = None
            save_data(self.data)
            await interaction.response.send_message(f"✅ Ticket {ticket_id} unassigned from you")
        else:
            await interaction.response.send_message("❌ Ticket not found or not assigned to you", ephemeral=True)

    # ----------------------------
    # 12. /ticketcount
    # ----------------------------
    @app_commands.command(name="ticketcount", description="Show total number of tickets")
    async def ticketcount(self, interaction: discord.Interaction):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("tickets", {})
        await interaction.response.send_message(f"📊 Total tickets: {len(guild_data)}")

    # ----------------------------
    # 13. /openticketcount
    # ----------------------------
    @app_commands.command(name="openticketcount", description="Show number of open tickets")
    async def openticketcount(self, interaction: discord.Interaction):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("tickets", {})
        open_count = len([t for t in guild_data.values() if t["status"] == "open"])
        await interaction.response.send_message(f"🟢 Open tickets: {open_count}")

    # ----------------------------
    # 14. /closedticketcount
    # ----------------------------
    @app_commands.command(name="closedticketcount", description="Show number of closed tickets")
    async def closedticketcount(self, interaction: discord.Interaction):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("tickets", {})
        closed_count = len([t for t in guild_data.values() if t["status"] == "closed"])
        await interaction.response.send_message(f"🔴 Closed tickets: {closed_count}")

    # ----------------------------
    # 15. /ticketstatus
    # ----------------------------
    @app_commands.command(name="ticketstatus", description="Show status of a ticket")
    async def ticketstatus(self, interaction: discord.Interaction, ticket_id: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("tickets", {})
        if ticket_id in guild_data:
            status = guild_data[ticket_id]["status"]
            await interaction.response.send_message(f"Ticket {ticket_id} status: {status}")
        else:
            await interaction.response.send_message("❌ Ticket not found", ephemeral=True)

    # ----------------------------
    # 16. /mytickets
    # ----------------------------
    @app_commands.command(name="mytickets", description="List your tickets")
    async def mytickets(self, interaction: discord.Interaction):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("tickets", {})
        my_tickets = [tid for tid, t in guild_data.items() if t["user_id"] == interaction.user.id]
        if not my_tickets:
            await interaction.response.send_message("❌ You have no tickets")
            return
        await interaction.response.send_message("📄 Your tickets: " + ", ".join(my_tickets))

    # ----------------------------
    # 17. /assignticketcount
    # ----------------------------
    @app_commands.command(name="assignticketcount", description="Show tickets assigned to a member")
    async def assignticketcount(self, interaction: discord.Interaction, member: discord.Member):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("tickets", {})
        assigned = len([t for t in guild_data.values() if t["assigned_to"] == member.id])
        await interaction.response.send_message(f"📌 Tickets assigned to {member.mention}: {assigned}")

    # ----------------------------
    # 18. /deleteticket
    # ----------------------------
    @app_commands.command(name="deleteticket", description="Delete a ticket without closing channel")
    async def deleteticket(self, interaction: discord.Interaction, ticket_id: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("tickets", {})
        if ticket_id in guild_data:
            del guild_data[ticket_id]
            save_data(self.data)
            await interaction.response.send_message(f"🗑️ Ticket {ticket_id} deleted")
        else:
            await interaction.response.send_message("❌ Ticket not found", ephemeral=True)

    # ----------------------------
    # 19. /resettickets
    # ----------------------------
    @app_commands.command(name="resettickets", description="Delete all tickets in server")
    async def resettickets(self, interaction: discord.Interaction):
        self.data[str(interaction.guild.id)]["tickets"] = {}
        save_data(self.data)
        await interaction.response.send_message("🔄 All tickets reset")

    # ----------------------------
    # 20. /ticketassigninfo
    # ----------------------------
    @app_commands.command(name="ticketassigninfo", description="Show assignment info of a ticket")
    async def ticketassigninfo(self, interaction: discord.Interaction, ticket_id: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("tickets", {})
        if ticket_id in guild_data:
            assigned = guild_data[ticket_id]["assigned_to"]
            if assigned:
                await interaction.response.send_message(f"Ticket {ticket_id} is assigned to <@{assigned}>")
            else:
                await interaction.response.send_message(f"Ticket {ticket_id} is not assigned")
        else:
            await interaction.response.send_message("❌ Ticket not found", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Tickets(bot), guild=discord.Object(id=GUILD_ID))
