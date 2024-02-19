import discord
from conf import embed_color
from discord.ext import commands


class SuggestionHelper:
    def __init__(self, bot):
        self.bot = bot

    async def insert_new_suggestion(self, message, guild):
        db_client = await self.bot.fetch_db_client()
        connection = db_client.get_connection()
        await connection.execute("INSERT INTO suggestions (guild_id, message_id) VALUES ($1, $2)", message, guild)

    async def find_suggestion_channel(self, guild):
        db_client = await self.bot.fetch_db_client()
        connection = db_client.get_connection()
        response = await connection.fetchrow("SELECT * FROM suggestion_channels WHERE guild_id = $1", guild)
        return response["channel_id"]

    async def find_suggestion_id(self, message_id):
        db_client = await self.bot.fetch_db_client()
        connection = db_client.get_connection()
        response = await connection.fetchrow("SELECT * FROM suggestions WHERE discord_message = $1", message_id)
        return response["id"]


class Suggestions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(aliases=["suggestion"])
    async def suggest(self, ctx, *, message):
        """Posts a suggestion in the server suggestions channel"""
        channel = await SuggestionHelper(self.bot).find_suggestion_channel(ctx.guild.id)
        suggestion_id = await SuggestionHelper(self.bot).find_suggestion_id(ctx.message.id)
        embed = discord.Embed(title=f"Suggestion #{suggestion_id}", description=message, color=embed_color)
        embed.set_footer(text=f"Send by {ctx.author}", icon_url=ctx.author.avatar.with_format("png"))
        await channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Suggestions(bot))
