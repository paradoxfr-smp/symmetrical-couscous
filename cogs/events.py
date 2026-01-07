import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from datetime import datetime, timedelta
from config import GUILD_ID

DATA_FILE = "events.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

class Events(commands.Cog):
    """Server Events management with 20 slash commands"""

    def __init__(self, bot):
        self.bot = bot
        self.data = load_data()

    # ----------------------------
    # 1. /createevent
    # ----------------------------
    @app_commands.command(name="createevent", description="Create a new event")
    async def createevent(self, interaction: discord.Interaction, title: str, description: str, date: str, time: str):
        """Date format YYYY-MM-DD, time format HH:MM"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ You need Manage Server permission.", ephemeral=True)
            return
        dt = f"{date} {time}"
        event_id = str(int(datetime.utcnow().timestamp()))
        self.data.setdefault(str(interaction.guild.id), {}).setdefault("events", {})[event_id] = {
            "title": title,
            "description": description,
            "datetime": dt,
            "attendees": []
        }
        save_data(self.data)
        await interaction.response.send_message(f"✅ Event `{title}` created with ID `{event_id}`")

    # ----------------------------
    # 2. /deleteevent
    # ----------------------------
    @app_commands.command(name="deleteevent", description="Delete an event")
    async def deleteevent(self, interaction: discord.Interaction, event_id: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("events", {})
        if event_id in guild_data:
            del guild_data[event_id]
            save_data(self.data)
            await interaction.response.send_message(f"🗑️ Event `{event_id}` deleted")
        else:
            await interaction.response.send_message("❌ Event not found", ephemeral=True)

    # ----------------------------
    # 3. /listevents
    # ----------------------------
    @app_commands.command(name="listevents", description="List all upcoming events")
    async def listevents(self, interaction: discord.Interaction):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("events", {})
        if not guild_data:
            await interaction.response.send_message("❌ No events found")
            return
        desc = ""
        for eid, e in guild_data.items():
            desc += f"ID: {eid} | {e['title']} | {e['datetime']} | Attendees: {len(e['attendees'])}\n"
        await interaction.response.send_message(f"📅 Upcoming Events:\n{desc}")

    # ----------------------------
    # 4. /eventinfo
    # ----------------------------
    @app_commands.command(name="eventinfo", description="Show detailed info about an event")
    async def eventinfo(self, interaction: discord.Interaction, event_id: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("events", {})
        if event_id not in guild_data:
            await interaction.response.send_message("❌ Event not found", ephemeral=True)
            return
        e = guild_data[event_id]
        embed = discord.Embed(title=f"📌 {e['title']}", description=e['description'], color=discord.Color.blue())
        embed.add_field(name="Date & Time", value=e['datetime'])
        embed.add_field(name="Attendees", value=str(len(e['attendees'])))
        await interaction.response.send_message(embed=embed)

    # ----------------------------
    # 5. /attendevent
    # ----------------------------
    @app_commands.command(name="attendevent", description="Join an event")
    async def attendevent(self, interaction: discord.Interaction, event_id: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("events", {})
        if event_id not in guild_data:
            await interaction.response.send_message("❌ Event not found", ephemeral=True)
            return
        if interaction.user.id not in guild_data[event_id]["attendees"]:
            guild_data[event_id]["attendees"].append(interaction.user.id)
            save_data(self.data)
            await interaction.response.send_message(f"✅ You joined the event `{guild_data[event_id]['title']}`")
        else:
            await interaction.response.send_message("⚠️ You are already attending this event", ephemeral=True)

    # ----------------------------
    # 6. /leaveevent
    # ----------------------------
    @app_commands.command(name="leaveevent", description="Leave an event")
    async def leaveevent(self, interaction: discord.Interaction, event_id: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("events", {})
        if event_id not in guild_data:
            await interaction.response.send_message("❌ Event not found", ephemeral=True)
            return
        if interaction.user.id in guild_data[event_id]["attendees"]:
            guild_data[event_id]["attendees"].remove(interaction.user.id)
            save_data(self.data)
            await interaction.response.send_message(f"✅ You left the event `{guild_data[event_id]['title']}`")
        else:
            await interaction.response.send_message("⚠️ You are not attending this event", ephemeral=True)

    # ----------------------------
    # 7. /eventattendees
    # ----------------------------
    @app_commands.command(name="eventattendees", description="List attendees of an event")
    async def eventattendees(self, interaction: discord.Interaction, event_id: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("events", {})
        if event_id not in guild_data:
            await interaction.response.send_message("❌ Event not found")
            return
        attendees = guild_data[event_id]["attendees"]
        if not attendees:
            await interaction.response.send_message("⚠️ No attendees yet")
            return
        mentions = ", ".join(f"<@{uid}>" for uid in attendees)
        await interaction.response.send_message(f"👥 Attendees:\n{mentions}")

    # ----------------------------
    # 8. /editeventtitle
    # ----------------------------
    @app_commands.command(name="editeventtitle", description="Edit the title of an event")
    async def editeventtitle(self, interaction: discord.Interaction, event_id: str, new_title: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("events", {})
        if event_id in guild_data:
            guild_data[event_id]["title"] = new_title
            save_data(self.data)
            await interaction.response.send_message(f"✅ Event title updated to `{new_title}`")
        else:
            await interaction.response.send_message("❌ Event not found", ephemeral=True)

    # ----------------------------
    # 9. /editeventdescription
    # ----------------------------
    @app_commands.command(name="editeventdescription", description="Edit the description of an event")
    async def editeventdescription(self, interaction: discord.Interaction, event_id: str, new_description: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("events", {})
        if event_id in guild_data:
            guild_data[event_id]["description"] = new_description
            save_data(self.data)
            await interaction.response.send_message(f"✅ Event description updated")
        else:
            await interaction.response.send_message("❌ Event not found", ephemeral=True)

    # ----------------------------
    # 10. /editeventdatetime
    # ----------------------------
    @app_commands.command(name="editeventdatetime", description="Edit the date/time of an event")
    async def editeventdatetime(self, interaction: discord.Interaction, event_id: str, date: str, time: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("events", {})
        if event_id in guild_data:
            guild_data[event_id]["datetime"] = f"{date} {time}"
            save_data(self.data)
            await interaction.response.send_message(f"✅ Event date/time updated")
        else:
            await interaction.response.send_message("❌ Event not found", ephemeral=True)

    # ----------------------------
    # 11. /addeventattendee
    # ----------------------------
    @app_commands.command(name="addeventattendee", description="Manually add an attendee to an event")
    async def addeventattendee(self, interaction: discord.Interaction, event_id: str, member: discord.Member):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("events", {})
        if event_id in guild_data:
            if member.id not in guild_data[event_id]["attendees"]:
                guild_data[event_id]["attendees"].append(member.id)
                save_data(self.data)
                await interaction.response.send_message(f"✅ {member.mention} added to the event")
            else:
                await interaction.response.send_message("⚠️ Member already attending", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Event not found", ephemeral=True)

    # ----------------------------
    # 12. /removeeventattendee
    # ----------------------------
    @app_commands.command(name="removeeventattendee", description="Remove an attendee from an event")
    async def removeeventattendee(self, interaction: discord.Interaction, event_id: str, member: discord.Member):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("events", {})
        if event_id in guild_data:
            if member.id in guild_data[event_id]["attendees"]:
                guild_data[event_id]["attendees"].remove(member.id)
                save_data(self.data)
                await interaction.response.send_message(f"✅ {member.mention} removed from the event")
            else:
                await interaction.response.send_message("⚠️ Member is not attending", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Event not found", ephemeral=True)

    # ----------------------------
    # 13. /eventcount
    # ----------------------------
    @app_commands.command(name="eventcount", description="Show total number of events")
    async def eventcount(self, interaction: discord.Interaction):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("events", {})
        await interaction.response.send_message(f"📊 Total events: {len(guild_data)}")

    # ----------------------------
    # 14. /eventupcoming
    # ----------------------------
    @app_commands.command(name="eventupcoming", description="Show upcoming events sorted by date")
    async def eventupcoming(self, interaction: discord.Interaction):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("events", {})
        upcoming = sorted(guild_data.items(), key=lambda x: x[1]["datetime"])
        desc = ""
        for eid, e in upcoming:
            desc += f"{e['datetime']} - {e['title']} (ID: {eid})\n"
        if not desc:
            desc = "❌ No upcoming events"
        await interaction.response.send_message(desc)

    # ----------------------------
    # 15. /eventattendeecount
    # ----------------------------
    @app_commands.command(name="eventattendeecount", description="Show number of attendees for an event")
    async def eventattendeecount(self, interaction: discord.Interaction, event_id: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("events", {})
        if event_id in guild_data:
            count = len(guild_data[event_id]["attendees"])
            await interaction.response.send_message(f"👥 {count} attendees for event `{guild_data[event_id]['title']}`")
        else:
            await interaction.response.send_message("❌ Event not found", ephemeral=True)

    # ----------------------------
    # 16. /eventattendeelist
    # ----------------------------
    @app_commands.command(name="eventattendeelist", description="List attendees of an event")
    async def eventattendeelist(self, interaction: discord.Interaction, event_id: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("events", {})
        if event_id in guild_data:
            attendees = guild_data[event_id]["attendees"]
            if attendees:
                mentions = ", ".join(f"<@{uid}>" for uid in attendees)
                await interaction.response.send_message(mentions)
            else:
                await interaction.response.send_message("⚠️ No attendees yet")
        else:
            await interaction.response.send_message("❌ Event not found", ephemeral=True)

    # ----------------------------
    # 17. /eventeditattendee
    # ----------------------------
    @app_commands.command(name="eventeditattendee", description="Replace an attendee with another")
    async def eventeditattendee(self, interaction: discord.Interaction, event_id: str, old_member: discord.Member, new_member: discord.Member):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("events", {})
        if event_id in guild_data:
            attendees = guild_data[event_id]["attendees"]
            if old_member.id in attendees:
                attendees.remove(old_member.id)
                attendees.append(new_member.id)
                save_data(self.data)
                await interaction.response.send_message(f"✅ Replaced {old_member.mention} with {new_member.mention}")
            else:
                await interaction.response.send_message(f"⚠️ {old_member.mention} is not attending", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Event not found", ephemeral=True)

    # ----------------------------
    # 18. /eventclearattendees
    # ----------------------------
    @app_commands.command(name="eventclearattendees", description="Remove all attendees from an event")
    async def eventclearattendees(self, interaction: discord.Interaction, event_id: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("events", {})
        if event_id in guild_data:
            guild_data[event_id]["attendees"] = []
            save_data(self.data)
            await interaction.response.send_message(f"🗑️ All attendees removed from event `{guild_data[event_id]['title']}`")
        else:
            await interaction.response.send_message("❌ Event not found", ephemeral=True)

    # ----------------------------
    # 19. /eventedit
    # ----------------------------
    @app_commands.command(name="eventedit", description="Edit any part of an event")
    async def eventedit(self, interaction: discord.Interaction, event_id: str, field: str, value: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("events", {})
        if event_id in guild_data:
            if field.lower() in ["title", "description", "datetime"]:
                guild_data[event_id][field.lower()] = value
                save_data(self.data)
                await interaction.response.send_message(f"✅ Event {field} updated")
            else:
                await interaction.response.send_message("⚠️ Field must be title, description, or datetime", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Event not found", ephemeral=True)

    # ----------------------------
    # 20. /eventreset
    # ----------------------------
    @app_commands.command(name="eventreset", description="Delete all events in server")
    async def eventreset(self, interaction: discord.Interaction):
        self.data[str(interaction.guild.id)]["events"] = {}
        save_data(self.data)
        await interaction.response.send_message("🔄 All events reset")

async def setup(bot):
    await bot.add_cog(Events(bot), guild=discord.Object(id=GUILD_ID))
