import discord
from discord.ext import commands


class SuggestionHelper:
    def __init__(self, bot):
        self.bot = bot

    async def insert_new_suggestion(self, guild, message):
        db_client = await self.bot.fetch_db_client()
        await db_client.execute("INSERT INTO suggestions (guild_id, discord_message) VALUES ($1, $2)", guild, message)

    async def find_suggestion_channel(self, guild):
        db_client = await self.bot.fetch_db_client()
        response = await db_client.fetchrow("SELECT * FROM suggestion_channels WHERE guild_id = $1", guild)
        if response is not None:
            return response["channel_id"]
        else:
            return False

    async def find_suggestion_id(self, message_id, guild_id):
        db_client = await self.bot.fetch_db_client()
        response = await db_client.fetchrow("SELECT * FROM suggestions WHERE discord_message = $1 AND guild_id = $2",
                                            message_id, guild_id)
        return response["id"]

    async def find_message_id(self, guild_id, suggestion_id):
        db_client = await self.bot.fetch_db_client()
        response = await db_client.fetchrow("SELECT * FROM suggestions WHERE id = $1 AND guild_id = $2", suggestion_id,
                                            guild_id)
        return response["discord_message"]

    async def get_guild_staff_role(self, guild_id):
        db_client = await self.bot.fetch_db_client()
        response = await db_client.fetchrow("SELECT * FROM staff_roles WHERE guild_id = $1", guild_id)
        if response is not None:
            return response["role_id"]
        else:
            return False


class Suggestions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.shelper = SuggestionHelper(self.bot)

    @staticmethod
    def check_if_staff():
        async def predicate(ctx):
            role_id = await ctx.cog.shelper.get_guild_staff_role(ctx.guild.id)
            author_roles = [role.id for role in ctx.author.roles]

            if role_id in author_roles or ctx.author.id == ctx.guild.owner.id or ctx.author.id in ctx.bot.owner_ids:
                return True

        return commands.check(predicate)

    @commands.hybrid_command(usage="<message>")
    @commands.cooldown(1, 120)
    @commands.guild_only()
    async def suggest(self, ctx, *, message: str = commands.parameter(default=None, description="The thing you want to suggest")):
        """Posts a suggestion in the server suggestions channel"""
        channel_id = await self.shelper.find_suggestion_channel(ctx.guild.id)
        if channel_id is False:
            return await ctx.send(
                "This server does not have a configured suggestions channel. Have your owner run the command `/config settings.suggestions.suggestion_channel <channel>` to set it up")
        if message is None: return await ctx.send("Please provide a suggestion message in the command")
        channel = self.bot.get_channel(channel_id)
        discord_message = await channel.send("\u200b")
        await self.shelper.insert_new_suggestion(ctx.guild.id, discord_message.id)

        suggestion_id = await self.shelper.find_suggestion_id(discord_message.id, ctx.guild.id)

        embed = discord.Embed(title=f"Suggestion #{suggestion_id}", description=message, color=0x000000)
        embed.set_footer(text=f"Sent by {ctx.author}", icon_url=ctx.author.avatar.with_format("png"))
        await discord_message.edit(embed=embed)
        await discord_message.add_reaction('\U0001f44d')
        await discord_message.add_reaction('\U0001f44e')
        await ctx.send(f"Suggestion #{suggestion_id} successfully posted!")

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

        message_id = await self.shelper.find_message_id(ctx.guild.id, int(id))
        channel_id = await self.shelper.find_suggestion_channel(ctx.guild.id)
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
        message_id = await self.shelper.find_message_id(ctx.guild.id, int(id))
        channel_id = await self.shelper.find_suggestion_channel(ctx.guild.id)
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
        message_id = await self.shelper.find_message_id(ctx.guild.id, int(id))
        channel_id = await self.shelper.find_suggestion_channel(ctx.guild.id)
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
