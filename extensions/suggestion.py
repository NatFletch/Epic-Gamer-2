import discord
from discord.ext import commands


class SuggestionHelper:
    def __init__(self, bot):
        self.bot = bot
        self.suggestion_channel_cache = {}

    async def insert_new_suggestion(self, guild, message):
        id = await self.bot.db_client.fetchrow(f"INSERT INTO suggestions_{guild} (id, discord_message) VALUES (nextval('suggestion_id_{guild}'), $1) RETURNING id", message)
        self.bot.cache.set_suggestion_message_cache(id, message)
        return id

    async def find_suggestion_channel(self, guild):
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


class Suggestions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.SuggestionHelper = SuggestionHelper(self.bot)

    @staticmethod
    def check_if_staff():
        async def predicate(ctx):
            role_id = await ctx.cog.SuggestionHelper.get_guild_staff_role(ctx.guild.id)
            author_roles = [role.id for role in ctx.author.roles]

            if role_id in author_roles or ctx.author.id == ctx.guild.owner.id or ctx.author.id in ctx.bot.owner_ids:
                return True

        return commands.check(predicate)

    @commands.hybrid_command(usage="<message>")
    @commands.cooldown(1, 120, commands.BucketType.user)
    @commands.guild_only()
    async def suggest(self, ctx, *, message: str = commands.parameter(description="The thing you want to suggest")):
        """Posts a suggestion in the server suggestions channel"""
        await self.bot.db_client.execute(f"""
                CREATE TABLE IF NOT EXISTS suggestions_{ctx.guild.id} (id int, discord_message bigint, guild_id bigint);
                CREATE SEQUENCE IF NOT EXISTS suggestion_id_{ctx.guild.id} START WITH 1 INCREMENT BY 1 OWNED BY suggestions_{ctx.guild.id}.id;""")
        
        channel_id = await self.SuggestionHelper.find_suggestion_channel(ctx.guild.id)

        if channel_id is False:
            return await ctx.send(
                "No suggestion channel configured for this server. Have your server owner run the command `/config` to set it up")

        channel = self.bot.get_channel(channel_id)
        discord_message = await channel.send("\u200b")
        suggestion_id = await self.SuggestionHelper.insert_new_suggestion(ctx.guild.id, discord_message.id)
        embed = discord.Embed(title=f"Suggestion #{suggestion_id["id"]}", description=message, color=0x000000)
        embed.set_footer(text=f"Sent by {ctx.author}", icon_url=ctx.author.avatar.with_format("png"))
        await discord_message.edit(embed=embed)
        await ctx.send(f"Suggestion #{suggestion_id["id"]} successfully posted!")
        await discord_message.add_reaction('\U0001f44d')
        await discord_message.add_reaction('\U0001f44e')

    @commands.hybrid_group(usage="")
    @commands.guild_only()
    @check_if_staff()
    async def suggestion(self, ctx):
        """The group that manages the suggestion moderation commands"""
        await ctx.send("You need to supply a sub command eg: `/suggestion accept`, `/suggestion consider` `/suggestion deny`")

    @suggestion.command(usage="<id> [reason]")
    @commands.guild_only()
    @check_if_staff()
    async def accept(self, ctx, id: int = commands.parameter(description="The suggestion id"), *, reason: str=commands.parameter(default=None, description="The description for your decision")):
        """Accepts a suggestion"""
        if not reason:
            reason = "No reason specified"

        message_id = await self.SuggestionHelper.find_message_id(ctx.guild.id, int(id))
        channel_id = await self.SuggestionHelper.find_suggestion_channel(ctx.guild.id)
        channel = self.bot.get_channel(channel_id)
        message = await channel.fetch_message(int(message_id))
        embed = message.embeds[0]
        embed.color = 0x00ff00
        try:
            embed.remove_field(0)
        except IndexError:
            pass

        embed.add_field(name=f"Suggestion Accepted By {ctx.author.name}", value=reason)
        await message.edit(content="\u00A0", embed=embed)
        await ctx.send("Suggestion successfully approved")

    @suggestion.command(usage="<id> [reason]")
    @commands.guild_only()
    @check_if_staff()
    async def deny(self, ctx, id: int = commands.parameter(description="The suggestion id"), *, reason: str=commands.parameter(default=None, description="The description for your decision")):
        """Denies a suggestion"""
        if not reason:
            reason = "No reason specified"
        message_id = await self.SuggestionHelper.find_message_id(ctx.guild.id, int(id))
        channel_id = await self.SuggestionHelper.find_suggestion_channel(ctx.guild.id)
        channel = self.bot.get_channel(channel_id)
        message = await channel.fetch_message(int(message_id))
        embed = message.embeds[0]
        embed.color = 0xff0000
        try:
            embed.remove_field(0)
        except IndexError:
            pass
        embed.add_field(name=f"Suggestion Denied By {ctx.author.name}", value=reason)
        await message.edit(content="\u00A0", embed=embed)
        await ctx.send("Suggestion successfully denied")

    @suggestion.command(usage="<id> [reason]")
    @commands.guild_only()
    @check_if_staff()
    async def consider(self, ctx, id: int = commands.parameter(description="The suggestion id"), *, reason: str=commands.parameter(default=None, description="The description for your decision")):
        """Considers a suggestion"""
        if not reason:
            reason = "No reason specified"
        message_id = await self.SuggestionHelper.find_message_id(ctx.guild.id, int(id))
        channel_id = await self.SuggestionHelper.find_suggestion_channel(ctx.guild.id)
        channel = self.bot.get_channel(channel_id)
        message = await channel.fetch_message(int(message_id))
        embed = message.embeds[0]
        embed.color = 0xfcbb42
        try:
            embed.remove_field(0)
        except IndexError:
            pass
        embed.add_field(name=f"Suggestion Considered By {ctx.author.name}", value=reason)
        await message.edit(content="\u00A0", embed=embed)
        await ctx.send("Suggestion successfully considered")


async def setup(bot):
    await bot.add_cog(Suggestions(bot))
