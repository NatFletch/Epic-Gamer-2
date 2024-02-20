import discord
from conf import embed_color
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
        return response["channel_id"]

    async def find_suggestion_id(self, message_id, guild_id):
        db_client = await self.bot.fetch_db_client()
        response = await db_client.fetchrow("SELECT * FROM suggestions WHERE discord_message = $1 AND guild_id = $2", message_id, guild_id)
        return response["id"]

    async def find_message_id(self, guild_id, suggestion_id):
        db_client = await self.bot.fetch_db_client()
        response = await db_client.fetchrow("SELECT * FROM suggestions WHERE id = $1 AND guild_id = $2", suggestion_id, guild_id)
        return response["discord_message"]
    
    async def get_guild_staff_role(self, guild_id):
        db_client = await self.bot.fetch_db_client()
        response = await db_client.fetchrow("SELECT * FROM suggestion_allowed_roles WHERE guild_id = $1", guild_id)
        return response["role_id"]


class Suggestions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.shelper = SuggestionHelper(self.bot)

    @staticmethod
    def check_if_staff():
        async def predicate(ctx):
            role_id = await ctx.cog.shelper.get_guild_staff_role(ctx.guild.id)
            author_roles = [role.id for role in ctx.author.roles]
            return role_id in author_roles or ctx.guild.owner.id == ctx.author.id

        return commands.check(predicate)

    @commands.hybrid_group(aliases=["suggestion"])
    async def suggest(self, ctx, *, message):
        """Posts a suggestion in the server suggestions channel"""
        channel = self.bot.get_channel(await self.shelper.find_suggestion_channel(ctx.guild.id))
        discord_message = await channel.send("\u200b")
        await self.shelper.insert_new_suggestion(ctx.guild.id, discord_message.id)

        suggestion_id = await self.shelper.find_suggestion_id(discord_message.id, ctx.guild.id)

        embed = discord.Embed(title=f"Suggestion #{suggestion_id}", description=message, color=0x000000)
        embed.set_footer(text=f"Sent by {ctx.author}", icon_url=ctx.author.avatar.with_format("png"))
        await discord_message.edit(embed=embed)
        await discord_message.add_reaction('\U0001f44d')
        await discord_message.add_reaction('\U0001f44e')
        await ctx.send(f"Suggestion #{suggestion_id} successfully posted!")

    @suggest.command()
    @check_if_staff()
    async def accept(self, ctx, id, *, reason):
        """Accepts a suggestion"""
        message_id = await self.shelper.find_message_id(ctx.guild.id, int(id))
        channel_id = await self.shelper.find_suggestion_channel(ctx.guild.id)
        channel = self.bot.get_channel(channel_id)
        message = await channel.fetch_message(int(message_id))
        embed = message.embeds[0]
        embed.color = 0x00ff00
        embed.title = "(Accepted) " + embed.title
        try:
            embed.remove_field(0)
        except IndexError:
            pass

        embed.add_field(name=f"Suggestion Accepted By {ctx.author.name}", value=reason)
        await message.edit(content="\u00A0", embed=embed)
        await ctx.send("Suggestion successfully approved")

    @suggest.command()
    @check_if_staff()
    async def deny(self, ctx, id, *, reason):
        """Denies a suggestion"""
        message_id = await self.shelper.find_message_id(ctx.guild.id, int(id))
        channel_id = await self.shelper.find_suggestion_channel(ctx.guild.id)
        channel = self.bot.get_channel(channel_id)
        message = await channel.fetch_message(int(message_id))
        embed = message.embeds[0]
        embed.color = 0xff0000
        embed.title = "(Denied) " + embed.title
        try:
            embed.remove_field(0)
        except IndexError:
            pass
        embed.add_field(name=f"Suggestion Denied By {ctx.author.name}", value=reason)
        await message.edit(content="\u00A0", embed=embed)
        await ctx.send("Suggestion successfully denied")

    @suggest.command()
    @check_if_staff()
    async def consider(self, ctx, id, *, reason):
        """Considers a suggestion"""
        message_id = await self.shelper.find_message_id(ctx.guild.id, int(id))
        channel_id = await self.shelper.find_suggestion_channel(ctx.guild.id)
        channel = self.bot.get_channel(channel_id)
        message = await channel.fetch_message(int(message_id))
        embed = message.embeds[0]
        embed.color = 0xfcbb42
        embed.title = "(Considered) " + embed.title
        title = embed.title.split()
        bad_titles = ["(Accepted)", "(Considered)", "(Denied)"]
        try:
            embed.remove_field(0)
        except IndexError:
            pass
        embed.add_field(name=f"Suggestion Considered By {ctx.author.name}", value=reason)
        await message.edit(content="\u00A0", embed=embed)
        await ctx.send("Suggestion successfully considered")


async def setup(bot):
    await bot.add_cog(Suggestions(bot))
