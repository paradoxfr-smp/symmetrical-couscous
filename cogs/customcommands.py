import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from config import GUILD_ID

DATA_FILE = "customcommands.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

class CustomCommands(commands.Cog):
    """Custom commands system with JSON persistence"""

    def __init__(self, bot):
        self.bot = bot
        self.data = load_data()

    # ----------------------------
    # 1. /create_command
    # ----------------------------
    @app_commands.command(name="create_command", description="Create a custom command")
    async def create_command(self, interaction: discord.Interaction, name: str, *, response: str):
        guild_id = str(interaction.guild.id)
        self.data.setdefault(guild_id, {})[name] = response
        save_data(self.data)
        await interaction.response.send_message(f"✅ Command `{name}` created.")

    # ----------------------------
    # 2. /delete_command
    # ----------------------------
    @app_commands.command(name="delete_command", description="Delete a custom command")
    async def delete_command(self, interaction: discord.Interaction, name: str):
        guild_id = str(interaction.guild.id)
        if name in self.data.get(guild_id, {}):
            self.data[guild_id].pop(name)
            save_data(self.data)
            await interaction.response.send_message(f"✅ Command `{name}` deleted.")
        else:
            await interaction.response.send_message("❌ Command not found.", ephemeral=True)

    # ----------------------------
    # 3. /edit_command
    # ----------------------------
    @app_commands.command(name="edit_command", description="Edit a custom command")
    async def edit_command(self, interaction: discord.Interaction, name: str, *, new_response: str):
        guild_id = str(interaction.guild.id)
        if name in self.data.get(guild_id, {}):
            self.data[guild_id][name] = new_response
            save_data(self.data)
            await interaction.response.send_message(f"✅ Command `{name}` updated.")
        else:
            await interaction.response.send_message("❌ Command not found.", ephemeral=True)

    # ----------------------------
    # 4. /list_commands
    # ----------------------------
    @app_commands.command(name="list_commands", description="List all custom commands")
    async def list_commands(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        commands_list = self.data.get(guild_id, {})
        if commands_list:
            await interaction.response.send_message("\n".join(commands_list.keys()))
        else:
            await interaction.response.send_message("No custom commands created.")

    # ----------------------------
    # 5. /show_command
    # ----------------------------
    @app_commands.command(name="show_command", description="Show the response of a custom command")
    async def show_command(self, interaction: discord.Interaction, name: str):
        guild_id = str(interaction.guild.id)
        response = self.data.get(guild_id, {}).get(name)
        if response:
            await interaction.response.send_message(f"`{name}`: {response}")
        else:
            await interaction.response.send_message("❌ Command not found.", ephemeral=True)

    # ----------------------------
    # 6. /use_command
    # ----------------------------
    @app_commands.command(name="use_command", description="Use a custom command")
    async def use_command(self, interaction: discord.Interaction, name: str):
        guild_id = str(interaction.guild.id)
        response = self.data.get(guild_id, {}).get(name)
        if response:
            await interaction.response.send_message(response)
        else:
            await interaction.response.send_message("❌ Command not found.", ephemeral=True)

    # ----------------------------
    # 7. /bulk_create
    # ----------------------------
    @app_commands.command(name="bulk_create", description="Create multiple commands at once")
    async def bulk_create(self, interaction: discord.Interaction, *, input_text: str):
        """Format: command1=response1; command2=response2"""
        guild_id = str(interaction.guild.id)
        entries = input_text.split(";")
        for entry in entries:
            if "=" in entry:
                name, response = entry.split("=", 1)
                self.data.setdefault(guild_id, {})[name.strip()] = response.strip()
        save_data(self.data)
        await interaction.response.send_message("✅ Bulk commands created.")

    # ----------------------------
    # 8. /bulk_delete
    # ----------------------------
    @app_commands.command(name="bulk_delete", description="Delete multiple commands at once")
    async def bulk_delete(self, interaction: discord.Interaction, *, command_names: str):
        guild_id = str(interaction.guild.id)
        names = [n.strip() for n in command_names.split(";")]
        removed = []
        for name in names:
            if name in self.data.get(guild_id, {}):
                self.data[guild_id].pop(name)
                removed.append(name)
        save_data(self.data)
        await interaction.response.send_message(f"✅ Removed commands: {', '.join(removed)}")

    # ----------------------------
    # 9. /reset_commands
    # ----------------------------
    @app_commands.command(name="reset_commands", description="Delete all custom commands")
    async def reset_commands(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        self.data[guild_id] = {}
        save_data(self.data)
        await interaction.response.send_message("✅ All custom commands deleted.")

    # ----------------------------
    # 10. /rename_command
    # ----------------------------
    @app_commands.command(name="rename_command", description="Rename a custom command")
    async def rename_command(self, interaction: discord.Interaction, old_name: str, new_name: str):
        guild_id = str(interaction.guild.id)
        commands_dict = self.data.get(guild_id, {})
        if old_name in commands_dict:
            commands_dict[new_name] = commands_dict.pop(old_name)
            save_data(self.data)
            await interaction.response.send_message(f"✅ `{old_name}` renamed to `{new_name}`")
        else:
            await interaction.response.send_message("❌ Command not found.", ephemeral=True)

    # ----------------------------
    # 11. /search_commands
    # ----------------------------
    @app_commands.command(name="search_commands", description="Search commands containing a keyword")
    async def search_commands(self, interaction: discord.Interaction, keyword: str):
        guild_id = str(interaction.guild.id)
        commands_list = [k for k in self.data.get(guild_id, {}) if keyword.lower() in k.lower()]
        await interaction.response.send_message("\n".join(commands_list) if commands_list else "No commands found.")

    # ----------------------------
    # 12. /copy_command
    # ----------------------------
    @app_commands.command(name="copy_command", description="Copy a command to a new command name")
    async def copy_command(self, interaction: discord.Interaction, source: str, new_name: str):
        guild_id = str(interaction.guild.id)
        commands_dict = self.data.get(guild_id, {})
        if source in commands_dict:
            commands_dict[new_name] = commands_dict[source]
            save_data(self.data)
            await interaction.response.send_message(f"✅ `{source}` copied to `{new_name}`")
        else:
            await interaction.response.send_message("❌ Command not found.", ephemeral=True)

    # ----------------------------
    # 13. /command_count
    # ----------------------------
    @app_commands.command(name="command_count", description="Show number of custom commands")
    async def command_count(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        count = len(self.data.get(guild_id, {}))
        await interaction.response.send_message(f"Total custom commands: {count}")

    # ----------------------------
    # 14. /command_info
    # ----------------------------
    @app_commands.command(name="command_info", description="Show detailed info about a command")
    async def command_info(self, interaction: discord.Interaction, name: str):
        guild_id = str(interaction.guild.id)
        response = self.data.get(guild_id, {}).get(name)
        if response:
            await interaction.response.send_message(f"Command `{name}` -> Response: {response}")
        else:
            await interaction.response.send_message("❌ Command not found.", ephemeral=True)

    # ----------------------------
    # 15. /export_commands
    # ----------------------------
    @app_commands.command(name="export_commands", description="Export all commands as JSON")
    async def export_commands(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        commands_dict = self.data.get(guild_id, {})
        if commands_dict:
            await interaction.response.send_message(f"```json\n{json.dumps(commands_dict, indent=2)}\n```")
        else:
            await interaction.response.send_message("No commands to export.")

    # ----------------------------
    # 16. /import_commands
    # ----------------------------
    @app_commands.command(name="import_commands", description="Import commands from JSON")
    async def import_commands(self, interaction: discord.Interaction, *, json_text: str):
        guild_id = str(interaction.guild.id)
        try:
            commands_dict = json.loads(json_text)
            if isinstance(commands_dict, dict):
                self.data.setdefault(guild_id, {}).update(commands_dict)
                save_data(self.data)
                await interaction.response.send_message(f"✅ Imported {len(commands_dict)} commands.")
            else:
                await interaction.response.send_message("❌ Invalid JSON format.", ephemeral=True)
        except json.JSONDecodeError:
            await interaction.response.send_message("❌ Invalid JSON.", ephemeral=True)

    # ----------------------------
    # 17. /show_all_responses
    # ----------------------------
    @app_commands.command(name="show_all_responses", description="Show all command responses")
    async def show_all_responses(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        commands_dict = self.data.get(guild_id, {})
        if commands_dict:
            responses = "\n".join(f"{k}: {v}" for k, v in commands_dict.items())
            await interaction.response.send_message(f"```\n{responses}\n```")
        else:
            await interaction.response.send_message("No commands available.")

    # ----------------------------
    # 18. /duplicate_command
    # ----------------------------
    @app_commands.command(name="duplicate_command", description="Duplicate a command")
    async def duplicate_command(self, interaction: discord.Interaction, name: str):
        guild_id = str(interaction.guild.id)
        commands_dict = self.data.get(guild_id, {})
        if name in commands_dict:
            new_name = f"{name}_copy"
            commands_dict[new_name] = commands_dict[name]
            save_data(self.data)
            await interaction.response.send_message(f"✅ Command duplicated as `{new_name}`")
        else:
            await interaction.response.send_message("❌ Command not found.", ephemeral=True)

    # ----------------------------
    # 19. /replace_text
    # ----------------------------
    @app_commands.command(name="replace_text", description="Replace text in a command response")
    async def replace_text(self, interaction: discord.Interaction, name: str, old: str, new: str):
        guild_id = str(interaction.guild.id)
        commands_dict = self.data.get(guild_id, {})
        if name in commands_dict:
            commands_dict[name] = commands_dict[name].replace(old, new)
            save_data(self.data)
            await interaction.response.send_message(f"✅ Replaced `{old}` with `{new}` in `{name}`")
        else:
            await interaction.response.send_message("❌ Command not found.", ephemeral=True)

    # ----------------------------
    # 20. /clear_all
    # ----------------------------
    @app_commands.command(name="clear_all", description="Delete all commands permanently")
    async def clear_all(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        self.data[guild_id] = {}
        save_data(self.data)
        await interaction.response.send_message("✅ All custom commands cleared permanently.")

async def setup(bot):
    await bot.add_cog(CustomCommands(bot), guild=discord.Object(id=GUILD_ID))
