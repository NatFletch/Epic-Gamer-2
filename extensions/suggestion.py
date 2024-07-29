import discord
from discord.ext import commands
from discord import app_commands


class SuggestionHelper:
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    async def insert_new_suggestion(self, guild: float, message: float):
        id: int = await self.bot.db_client.fetchrow(f"INSERT INTO suggestions_{guild} (id, discord_message) VALUES (nextval('suggestion_id_{guild}'), $1) RETURNING id", message)
        self.bot.cache.set_suggestion_message_cache(id, message)
        return id

    async def find_suggestion_channel(self, guild: float):
        # Check if channel is already cached
        if self.bot.cache.check_suggestion_channel_cache(guild) == True:
            return self.bot.cache.get_suggestion_channel_cache(guild)
        
        response = await self.bot.db_client.fetchrow("SELECT * FROM suggestion_channels WHERE guild_id = $1", guild)
        if response is not None:
            self.bot.cache.set_suggestion_channel_cache(guild, response["channel_id"])
            return response["channel_id"]
        else:
            return False

    async def find_message_id(self, guild_id, suggestion_id):
        # Check if the message is already cached
        if self.bot.cache.check_suggestion_message_cache(suggestion_id) == True:
            return self.bot.cache.get_suggestion_message_cache(suggestion_id)
        response = await self.bot.db_client.fetchrow(f"SELECT * FROM suggestions_{guild_id} WHERE id = $1", suggestion_id)
        return response["discord_message"]

    async def get_guild_staff_role(self, guild_id):
        # Check if staff role is cached
        if self.bot.cache.check_staff_cache(guild_id) == True:
            return self.bot.cache.get_staff_cache(guild_id)
        response = await self.bot.db_client.fetchrow("SELECT * FROM staff_roles WHERE guild_id = $1", guild_id)
        if response is not None:
            self.bot.cache.set_staff_cache(guild_id, response["role_id"])
            return response["role_id"]
        else:
            return False
        
    async def suggestion_check(self, interaction: discord.Interaction):
        role_id = await self.get_guild_staff_role(interaction.guild.id)
        author_roles = [role.id for role in interaction.user.roles]

        if role_id not in author_roles or interaction.user.id != 598325949808771083:
            return await interaction.response.send_message("You must be a staff member to moderate this suggestion.")


class Suggestions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.SuggestionHelper = SuggestionHelper(self.bot)
        

    @app_commands.command()
    @app_commands.describe(message = "The suggestion you want to post")
    @commands.cooldown(1, 120, commands.BucketType.user)
    async def suggest(self, interaction: discord.Interaction, *, message: str):
        """Posts a suggestion in the server suggestions channel"""
        await self.bot.db_client.execute(f"""
                CREATE TABLE IF NOT EXISTS suggestions_{interaction.guild.id} (id int, discord_message bigint, guild_id bigint);
                CREATE SEQUENCE IF NOT EXISTS suggestion_id_{interaction.guild.id} START WITH 1 INCREMENT BY 1 OWNED BY suggestions_{interaction.guild.id}.id;""")
        
        channel_id = await self.SuggestionHelper.find_suggestion_channel(interaction.guild.id)

        if channel_id is False:
            return await interaction.response.send_message(
                "No suggestion channel configured for this server. Have your server owner run the command `/config` to set it up")

        channel = self.bot.get_channel(channel_id)
        discord_message = await channel.send("\u200b")
        suggestion_id = await self.SuggestionHelper.insert_new_suggestion(interaction.guild.id, discord_message.id)
        embed = discord.Embed(title=f"Suggestion #{suggestion_id["id"]}", description=message, color=0x000000)
        embed.set_footer(text=f"Sent by {interaction.user.name}", icon_url=interaction.user.avatar.with_format("png"))
        await discord_message.edit(embed=embed)
        await interaction.response.send_message(f"Suggestion #{suggestion_id["id"]} successfully posted!")
        await discord_message.add_reaction('\U0001f44d')
        await discord_message.add_reaction('\U0001f44e')

    @app_commands.command()
    @app_commands.describe(id="The suggestion ID", reason="The reason behind your decision")
    async def suggestion_accept(self, interaction: discord.Interaction, id: int, *, reason: str=None):
        """Accepts a suggestion"""
        await self.SuggestionHelper.suggestion_check(interaction)
        channel_id = await self.SuggestionHelper.find_suggestion_channel(interaction.guild.id)
        if channel_id is False:
            return await interaction.response.send_message(
                "No suggestion channel configured for this server. Have your server owner run the command `/config` to set it up")
            
        if not reason:
            reason = "No reason specified"

        message_id = await self.SuggestionHelper.find_message_id(interaction.guild.id, int(id))
        channel_id = await self.SuggestionHelper.find_suggestion_channel(interaction.guild.id)
        channel = self.bot.get_channel(channel_id)
        message = await channel.fetch_message(int(message_id))
        embed = message.embeds[0]
        embed.color = 0x00ff00
        try:
            embed.remove_field(0)
        except IndexError:
            pass

        embed.add_field(name=f"Suggestion Accepted By {interaction.user.name}", value=reason)
        await message.edit(content="\u00A0", embed=embed)
        await interaction.response.send_message("Suggestion successfully approved")

    @app_commands.command()
    @app_commands.describe(id="The suggestion ID", reason="The reason behind your decision")
    async def suggestion_deny(self, interaction: discord.Interaction, id: int, *, reason: str=None):
        """Denies a suggestion"""
        await self.SuggestionHelper.suggestion_check(interaction)
        channel_id = await self.SuggestionHelper.find_suggestion_channel(interaction.guild.id)
        if channel_id is False:
            return await interaction.response.send_message(
                "No suggestion channel configured for this server. Have your server owner run the command `/config` to set it up")
        if not reason:
            reason = "No reason specified"
        message_id = await self.SuggestionHelper.find_message_id(interaction.guild.id, int(id))
        channel_id = await self.SuggestionHelper.find_suggestion_channel(interaction.guild.id)
        channel = self.bot.get_channel(channel_id)
        message = await channel.fetch_message(int(message_id))
        embed = message.embeds[0]
        embed.color = 0xff0000
        try:
            embed.remove_field(0)
        except IndexError:
            pass
        embed.add_field(name=f"Suggestion Denied By {interaction.user.name}", value=reason)
        await message.edit(content="\u00A0", embed=embed)
        await interaction.response.send_message("Suggestion successfully denied")

    @app_commands.command()
    @app_commands.describe(id="The suggestion ID", reason="The reason behind your decision")
    async def suggestion_consider(self, interaction: discord.Interaction, id: int, *, reason: str=None):
        """Considers a suggestion"""
        await self.SuggestionHelper.suggestion_check(interaction)
        channel_id = await self.SuggestionHelper.find_suggestion_channel(interaction.guild.id)
        if channel_id is False:
            return await interaction.response.send_message(
                "No suggestion channel configured for this server. Have your server owner run the command `/config` to set it up")
        if not reason:
            reason = "No reason specified"
        message_id = await self.SuggestionHelper.find_message_id(interaction.guild.id, int(id))
        channel_id = await self.SuggestionHelper.find_suggestion_channel(interaction.guild.id)
        channel = self.bot.get_channel(channel_id)
        message = await channel.fetch_message(int(message_id))
        embed = message.embeds[0]
        embed.color = 0xfcbb42
        try:
            embed.remove_field(0)
        except IndexError:
            pass
        embed.add_field(name=f"Suggestion Considered By {interaction.user.name}", value=reason)
        await message.edit(content="\u00A0", embed=embed)
        await interaction.response.send_message("Suggestion successfully considered")


async def setup(bot):
    await bot.add_cog(Suggestions(bot))
