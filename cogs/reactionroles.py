import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from config import GUILD_ID

DATA_FILE = "reactionroles.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

class ReactionRoles(commands.Cog):
    """Reaction Roles system with 20 slash commands and JSON persistence"""

    def __init__(self, bot):
        self.bot = bot
        self.data = load_data()

    # ----------------------------
    # 1. /createrolemessage
    # ----------------------------
    @app_commands.command(name="createrolemessage", description="Create a reaction role message")
    async def createrolemessage(self, interaction: discord.Interaction, channel: discord.TextChannel, content: str):
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message("❌ You need Manage Roles permission.", ephemeral=True)
            return
        message = await channel.send(content)
        self.data.setdefault(str(interaction.guild.id), {}).setdefault("messages", {})[str(message.id)] = {}
        save_data(self.data)
        await interaction.response.send_message(f"✅ Reaction role message created in {channel.mention}")

    # ----------------------------
    # 2. /addreactionrole
    # ----------------------------
    @app_commands.command(name="addreactionrole", description="Add a reaction role to a message")
    async def addreactionrole(self, interaction: discord.Interaction, message_id: str, emoji: str, role: discord.Role):
        guild_data = self.data.setdefault(str(interaction.guild.id), {}).setdefault("messages", {})
        if message_id not in guild_data:
            await interaction.response.send_message("❌ Message ID not found.", ephemeral=True)
            return
        guild_data[message_id][emoji] = role.id
        save_data(self.data)
        message = await interaction.channel.fetch_message(int(message_id))
        await message.add_reaction(emoji)
        await interaction.response.send_message(f"✅ Added reaction {emoji} for role {role.name}")

    # ----------------------------
    # 3. /removereactionrole
    # ----------------------------
    @app_commands.command(name="removereactionrole", description="Remove a reaction role from a message")
    async def removereactionrole(self, interaction: discord.Interaction, message_id: str, emoji: str):
        guild_data = self.data.setdefault(str(interaction.guild.id), {}).setdefault("messages", {})
        if message_id in guild_data and emoji in guild_data[message_id]:
            del guild_data[message_id][emoji]
            save_data(self.data)
            message = await interaction.channel.fetch_message(int(message_id))
            await message.clear_reaction(emoji)
            await interaction.response.send_message(f"✅ Removed reaction {emoji}")
        else:
            await interaction.response.send_message("❌ Reaction role not found.", ephemeral=True)

    # ----------------------------
    # 4. /listreactionroles
    # ----------------------------
    @app_commands.command(name="listreactionroles", description="List all reaction roles in a server")
    async def listreactionroles(self, interaction: discord.Interaction):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("messages", {})
        if not guild_data:
            await interaction.response.send_message("❌ No reaction roles found.")
            return
        desc = ""
        for msg_id, roles in guild_data.items():
            desc += f"Message ID: {msg_id}\n"
            for emoji, role_id in roles.items():
                role = interaction.guild.get_role(role_id)
                if role:
                    desc += f"  {emoji} → {role.name}\n"
        await interaction.response.send_message(f"📜 Reaction Roles:\n{desc}")

    # ----------------------------
    # 5. /deleterolemessage
    # ----------------------------
    @app_commands.command(name="deleterolemessage", description="Delete a reaction role message")
    async def deleterolemessage(self, interaction: discord.Interaction, message_id: str):
        guild_data = self.data.setdefault(str(interaction.guild.id), {}).setdefault("messages", {})
        if message_id in guild_data:
            del guild_data[message_id]
            save_data(self.data)
            await interaction.response.send_message(f"🗑️ Reaction role message {message_id} deleted")
        else:
            await interaction.response.send_message("❌ Message ID not found.", ephemeral=True)

    # ----------------------------
    # 6. /reactionroleshelp
    # ----------------------------
    @app_commands.command(name="reactionroleshelp", description="Shows reaction roles help")
    async def reactionroleshelp(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Reaction Roles Help", color=discord.Color.green())
        embed.add_field(name="/createrolemessage", value="Create a reaction role message", inline=False)
        embed.add_field(name="/addreactionrole", value="Add a reaction-role pair", inline=False)
        embed.add_field(name="/removereactionrole", value="Remove a reaction-role pair", inline=False)
        embed.add_field(name="/listreactionroles", value="List all reaction roles", inline=False)
        await interaction.response.send_message(embed=embed)

    # ----------------------------
    # 7. /massaddrole
    # ----------------------------
    @app_commands.command(name="massaddrole", description="Add a role to everyone with a reaction")
    async def massaddrole(self, interaction: discord.Interaction, message_id: str, emoji: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("messages", {})
        if message_id not in guild_data or emoji not in guild_data[message_id]:
            await interaction.response.send_message("❌ Reaction role not found.", ephemeral=True)
            return
        role_id = guild_data[message_id][emoji]
        role = interaction.guild.get_role(role_id)
        if not role:
            await interaction.response.send_message("❌ Role not found.", ephemeral=True)
            return
        message = await interaction.channel.fetch_message(int(message_id))
        users = await message.reactions[0].users().flatten()
        for user in users:
            if user.bot:
                continue
            member = interaction.guild.get_member(user.id)
            if member:
                await member.add_roles(role)
        await interaction.response.send_message(f"✅ Added role {role.name} to users who reacted with {emoji}")

    # ----------------------------
    # 8. /massremoverole
    # ----------------------------
    @app_commands.command(name="massremoverole", description="Remove a role from everyone with a reaction")
    async def massremoverole(self, interaction: discord.Interaction, message_id: str, emoji: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("messages", {})
        if message_id not in guild_data or emoji not in guild_data[message_id]:
            await interaction.response.send_message("❌ Reaction role not found.", ephemeral=True)
            return
        role_id = guild_data[message_id][emoji]
        role = interaction.guild.get_role(role_id)
        if not role:
            await interaction.response.send_message("❌ Role not found.", ephemeral=True)
            return
        message = await interaction.channel.fetch_message(int(message_id))
        users = await message.reactions[0].users().flatten()
        for user in users:
            if user.bot:
                continue
            member = interaction.guild.get_member(user.id)
            if member:
                await member.remove_roles(role)
        await interaction.response.send_message(f"✅ Removed role {role.name} from users who reacted with {emoji}")

    # ----------------------------
    # 9. /addreactionemoji
    # ----------------------------
    @app_commands.command(name="addreactionemoji", description="Add emoji to a reaction role message")
    async def addreactionemoji(self, interaction: discord.Interaction, message_id: str, emoji: str):
        message = await interaction.channel.fetch_message(int(message_id))
        await message.add_reaction(emoji)
        await interaction.response.send_message(f"✅ Added emoji {emoji} to message {message_id}")

    # ----------------------------
    # 10. /removereactionemoji
    # ----------------------------
    @app_commands.command(name="removereactionemoji", description="Remove emoji from a message")
    async def removereactionemoji(self, interaction: discord.Interaction, message_id: str, emoji: str):
        message = await interaction.channel.fetch_message(int(message_id))
        await message.clear_reaction(emoji)
        await interaction.response.send_message(f"✅ Removed emoji {emoji} from message {message_id}")

    # ----------------------------
    # 11. /reactionrolesinfo
    # ----------------------------
    @app_commands.command(name="reactionrolesinfo", description="Show reaction role info for a message")
    async def reactionrolesinfo(self, interaction: discord.Interaction, message_id: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("messages", {})
        if message_id not in guild_data:
            await interaction.response.send_message("❌ Message ID not found.", ephemeral=True)
            return
        desc = ""
        for emoji, role_id in guild_data[message_id].items():
            role = interaction.guild.get_role(role_id)
            if role:
                desc += f"{emoji} → {role.name}\n"
        await interaction.response.send_message(f"📜 Reaction Roles for message {message_id}:\n{desc}")

    # ----------------------------
    # 12. /clearallreactionroles
    # ----------------------------
    @app_commands.command(name="clearallreactionroles", description="Clear all reaction roles in a server")
    async def clearallreactionroles(self, interaction: discord.Interaction):
        self.data[str(interaction.guild.id)]["messages"] = {}
        save_data(self.data)
        await interaction.response.send_message("🗑️ Cleared all reaction roles in the server.")

    # ----------------------------
    # 13. /reactionrolecount
    # ----------------------------
    @app_commands.command(name="reactionrolecount", description="Count reaction roles on a message")
    async def reactionrolecount(self, interaction: discord.Interaction, message_id: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("messages", {})
        if message_id not in guild_data:
            await interaction.response.send_message("❌ Message not found.")
            return
        count = len(guild_data[message_id])
        await interaction.response.send_message(f"📊 {count} reaction roles on message {message_id}")

    # ----------------------------
    # 14. /reactionrolesmessages
    # ----------------------------
    @app_commands.command(name="reactionrolesmessages", description="List all messages with reaction roles")
    async def reactionrolesmessages(self, interaction: discord.Interaction):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("messages", {})
        if not guild_data:
            await interaction.response.send_message("❌ No messages with reaction roles found.")
            return
        messages = "\n".join(guild_data.keys())
        await interaction.response.send_message(f"📝 Messages with reaction roles:\n{messages}")

    # ----------------------------
    # 15. /reactionroleemojis
    # ----------------------------
    @app_commands.command(name="reactionroleemojis", description="List all emojis for a reaction role message")
    async def reactionroleemojis(self, interaction: discord.Interaction, message_id: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("messages", {})
        if message_id not in guild_data:
            await interaction.response.send_message("❌ Message not found.")
            return
        emojis = ", ".join(guild_data[message_id].keys())
        await interaction.response.send_message(f"🎭 Emojis for message {message_id}: {emojis}")

    # ----------------------------
    # 16. /reactionroleinfofull
    # ----------------------------
    @app_commands.command(name="reactionroleinfofull", description="Show all reaction role info for server")
    async def reactionroleinfofull(self, interaction: discord.Interaction):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("messages", {})
        if not guild_data:
            await interaction.response.send_message("❌ No reaction roles found.")
            return
        desc = ""
        for msg_id, roles in guild_data.items():
            desc += f"Message ID: {msg_id}\n"
            for emoji, role_id in roles.items():
                role = interaction.guild.get_role(role_id)
                if role:
                    desc += f"  {emoji} → {role.name}\n"
        await interaction.response.send_message(f"📜 Full Reaction Roles Info:\n{desc}")

    # ----------------------------
    # 17. /reactionroleadduser
    # ----------------------------
    @app_commands.command(name="reactionroleadduser", description="Add a reaction role manually to a user")
    async def reactionroleadduser(self, interaction: discord.Interaction, member: discord.Member, message_id: str, emoji: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("messages", {})
        if message_id not in guild_data or emoji not in guild_data[message_id]:
            await interaction.response.send_message("❌ Reaction role not found.", ephemeral=True)
            return
        role = interaction.guild.get_role(guild_data[message_id][emoji])
        if role:
            await member.add_roles(role)
            await interaction.response.send_message(f"✅ Added role {role.name} to {member.mention}")

    # ----------------------------
    # 18. /reactionroleremoveuser
    # ----------------------------
    @app_commands.command(name="reactionroleremoveuser", description="Remove a reaction role manually from a user")
    async def reactionroleremoveuser(self, interaction: discord.Interaction, member: discord.Member, message_id: str, emoji: str):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("messages", {})
        if message_id not in guild_data or emoji not in guild_data[message_id]:
            await interaction.response.send_message("❌ Reaction role not found.", ephemeral=True)
            return
        role = interaction.guild.get_role(guild_data[message_id][emoji])
        if role:
            await member.remove_roles(role)
            await interaction.response.send_message(f"✅ Removed role {role.name} from {member.mention}")

    # ----------------------------
    # 19. /reactionroleclearuser
    # ----------------------------
    @app_commands.command(name="reactionroleclearuser", description="Remove all reaction roles from a user")
    async def reactionroleclearuser(self, interaction: discord.Interaction, member: discord.Member):
        guild_data = self.data.get(str(interaction.guild.id), {}).get("messages", {})
        for msg_id, roles in guild_data.items():
            for emoji, role_id in roles.items():
                role = interaction.guild.get_role(role_id)
                if role and role in member.roles:
                    await member.remove_roles(role)
        await interaction.response.send_message(f"🗑️ Removed all reaction roles from {member.mention}")

    # ----------------------------
    # 20. /reactionrolesreset
    # ----------------------------
    @app_commands.command(name="reactionrolesreset", description="Reset all reaction roles in the server")
    async def reactionrolesreset(self, interaction: discord.Interaction):
        self.data[str(interaction.guild.id)]["messages"] = {}
        save_data(self.data)
        await interaction.response.send_message("🔄 All reaction roles reset.")

    # ----------------------------
    # Event listener for reactions
    # ----------------------------
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id:
            return
        guild_data = self.data.get(str(payload.guild_id), {}).get("messages", {})
        message_roles = guild_data.get(str(payload.message_id), {})
        if str(payload.emoji) in message_roles:
            guild = self.bot.get_guild(payload.guild_id)
            role = guild.get_role(message_roles[str(payload.emoji)])
            member = guild.get_member(payload.user_id)
            if role and member:
                await member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        guild_data = self.data.get(str(payload.guild_id), {}).get("messages", {})
        message_roles = guild_data.get(str(payload.message_id), {})
        if str(payload.emoji) in message_roles:
            guild = self.bot.get_guild(payload.guild_id)
            role = guild.get_role(message_roles[str(payload.emoji)])
            member = guild.get_member(payload.user_id)
            if role and member:
                await member.remove_roles(role)

async def setup(bot):
    await bot.add_cog(ReactionRoles(bot), guild=discord.Object(id=GUILD_ID))
