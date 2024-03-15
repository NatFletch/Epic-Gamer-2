import discord
from datetime import datetime
from discord.ext import commands
from conf import embed_color


class ConfigHelper:
    def __init__(self, bot):
        self.bot = bot

    async def set_suggestion_channel(self, guild_id, channel_id):
        db_client = await self.bot.fetch_db_client()
        if await db_client.fetchrow("SELECT * FROM suggestion_channels WHERE guild_id = $1", guild_id) is not None:
            return await db_client.execute("UPDATE suggestion_channels SET channel_id = $1 WHERE guild_id = $2", channel_id, guild_id)
        await db_client.execute("INSERT INTO suggestion_channels (guild_id, channel_id) VALUES ($1, $2)", guild_id, channel_id)

    async def set_staff_role(self, guild_id, role_id):
        db_client = await self.bot.fetch_db_client()
        if await db_client.fetchrow("SELECT * FROM staff_roles WHERE guild_id = $1", guild_id) is not None:
            return await db_client.execute("UPDATE staff_roles SET role_id = $1 WHERE guild_id = $2", role_id, guild_id)
        await db_client.execute("INSERT INTO staff_roles (guild_id, role_id) VALUES ($1, $2)", guild_id, role_id)


def check_if_owner():
    async def predicate(ctx):
        if ctx.author.id == ctx.guild.owner.id:
            return True
        if commands.is_owner:
            return True
        await ctx.send("You do not have permission to run this command!")
        return False
    return commands.check(predicate)

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
            await interaction.response.send_message("Please enter your staff role", view=discord.ui.View().add_item(role_select))
        elif self.values[0] == "Suggestion Channel":
            channel_select = SuggestionChannelSelect()
            await interaction.response.send_message("Please enter your suggestion channel", view=discord.ui.View().add_item(channel_select))

class StaffRoleSelect(discord.ui.RoleSelect):
    def __init__(self):
        super().__init__(placeholder="Choose your staff role", min_values=1, max_values=1)
        
    async def callback(self, interaction):
        role = self.values[0]
        chelper = ConfigHelper(interaction.client)
        await chelper.set_staff_role(interaction.guild_id, role.id)
        await interaction.response.send_message(f"You have successfully set the staff role to: {role.mention}!", allowed_mentions=discord.AllowedMentions().none())
        
class SuggestionChannelSelect(discord.ui.ChannelSelect):
    def __init__(self):
        super().__init__(placeholder="Choose your suggestio channel", min_values=1, max_values=1)
    
    async def callback(self, interaction):
        channel = self.values[0]
        chelper = ConfigHelper(interaction.client)
        await chelper.set_suggestion_channel(interaction.guild_id, channel.id)
        await interaction.response.send_message(f"You have successfully set the suggestion channel to: {channel.mention}")
        
class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.chelper = ConfigHelper(self.bot)

    @commands.hybrid_command(aliases=["conf", "configure", "settings"], usage="[setting] <option>")
    @commands.guild_only()
    @check_if_owner()
    async def config(self, ctx):
        """Command to change server settings"""
        embed = discord.Embed(
            title="Configuration Menu",
            description="Welcome to the Epic Gamer configuration menu. Here you can change any specific settings related to your server",
            color=embed_color,
            timestamp=datetime.now()
        )
        await ctx.send(embed=embed, view=discord.ui.View().add_item(ConfigSelect()))



async def setup(bot):
    await bot.add_cog(Config(bot))
