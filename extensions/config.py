import discord
from datetime import datetime
from discord import app_commands
from discord.ext import commands


class ConfigHelper:
    def __init__(self, bot):
        self.bot = bot

    async def set_suggestion_channel(self, guild_id: float, channel_id: float):
        if await self.bot.db_client.fetchrow("SELECT * FROM suggestion_channels WHERE guild_id = $1", guild_id) is not None:
            self.bot.cache.set_suggestion_channel_cache(guild_id, channel_id)
            return await self.bot.db_client.execute("UPDATE suggestion_channels SET channel_id = $1 WHERE guild_id = $2", channel_id, guild_id)
        self.bot.cache.set_suggestion_channel_cache(guild_id, channel_id)
        await self.bot.db_client.execute("INSERT INTO suggestion_channels (guild_id, channel_id) VALUES ($1, $2)", guild_id, channel_id)

    async def set_staff_role(self, guild_id, role_id):
        if await self.bot.db_client.fetchrow("SELECT * FROM staff_roles WHERE guild_id = $1", guild_id) is not None:
            self.bot.cache.set_staff_cache(guild_id, role_id)
            return await self.bot.db_client.execute("UPDATE staff_roles SET role_id = $1 WHERE guild_id = $2", role_id, guild_id)
        self.bot.cache.set_staff_cache(guild_id, role_id)
        await self.bot.db_client.execute("INSERT INTO staff_roles (guild_id, role_id) VALUES ($1, $2)", guild_id, role_id)


def check_if_owner():
    async def predicate(interaction: discord.Interaction):
        if interaction.user.id == interaction.guild.owner_id:
            return True
        if commands.is_owner:
            return True
        await interaction.response.send_message("You do not have permission to run this command!")
        return False
    return app_commands.check(predicate)

class ConfigSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Staff Role", description="Set the staff role for your server to give permissions to others"),
            discord.SelectOption(label="Suggestion Channel", description="Set the channel your suggestions will be sent to")
        ]
        super().__init__(placeholder="Choose a configuration option", min_values=1, max_values=1, options=options)
        
    async def callback(self, interaction):
        if self.values[0] == "Staff Role":
            role_select = StaffRoleSelect()
            await interaction.response.send_message("Please enter your staff role", view=discord.ui.View().add_item(role_select), ephemeral=True)
        elif self.values[0] == "Suggestion Channel":
            channel_select = SuggestionChannelSelect()
            await interaction.response.send_message("Please enter your suggestion channel", view=discord.ui.View().add_item(channel_select), ephemeral=True)

class StaffRoleSelect(discord.ui.RoleSelect):
    def __init__(self):
        super().__init__(placeholder="Choose your staff role", min_values=1, max_values=1)
        
    async def callback(self, interaction):
        role = self.values[0]
        chelper = ConfigHelper(interaction.client)
        await chelper.set_staff_role(interaction.guild_id, role.id)
        await interaction.response.send_message(f"You have successfully set the staff role to: {role.mention}!", allowed_mentions=discord.AllowedMentions().none(), ephemeral=True)
        
class SuggestionChannelSelect(discord.ui.ChannelSelect):
    def __init__(self):
        super().__init__(placeholder="Choose your suggestion channel", min_values=1, max_values=1)
    
    async def callback(self, interaction):
        channel = self.values[0]
        chelper = ConfigHelper(interaction.client)
        await chelper.set_suggestion_channel(interaction.guild_id, channel.id)
        await interaction.response.send_message(f"You have successfully set the suggestion channel to: {channel.mention}", ephemeral=True)
         
class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.chelper = ConfigHelper(self.bot)

    @app_commands.command()
    @commands.guild_only()
    @check_if_owner()
    async def config(self, interaction: discord.Interaction):
        """Command to change server settings"""
        embed = discord.Embed(
            title="Configuration Menu",
            description="Welcome to the Epic Gamer configuration menu. Here you can change any specific settings related to your server",
            color=self.bot.color,
            timestamp=datetime.now()
        )
        await interaction.response.send_message(embed=embed, view=discord.ui.View().add_item(ConfigSelect()), ephemeral=True)



async def setup(bot):
    await bot.add_cog(Config(bot))
