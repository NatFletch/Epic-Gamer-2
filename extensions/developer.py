import discord
import os
import conf
from discord.ext import commands


class Developer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(usage="")
    @commands.is_owner()
    async def treesync(self, ctx):
        """Syncs command tree"""
        await self.bot.tree.sync()
        await ctx.send("Successfully synced command tree")
    
    @commands.command(aliases=["reloadall", "reall"], usage="")
    @commands.is_owner()
    async def reload_extensions(self, ctx):
        """Reloads all extensions"""
        for extension in os.listdir("./extensions"):
            if extension.endswith('.py'):
                await self.bot.reload_extension("extensions." + extension[:-3])
        await self.bot.reload_extension("jishaku")
        await ctx.send("\n".join(["Reloaded -> " + extension for extension in os.listdir("./extensions") if extension.endswith(".py")]) + "\nReloaded -> Jishaku")
        
    @commands.command(usage="<channel> <title> <description> [color]")
    @commands.is_owner()
    async def embed(self, ctx, channel, title, description, color=None):
        """Posts in embed in a given channel"""
        if color is None:
            color = conf.embed_color

        channel = await commands.TextChannelConverter().convert(ctx, channel)
        
        embed = discord.Embed(title=title, description=description, color=color)
        embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar.with_format("png"))
        await channel.send(embed=embed)
        await ctx.message.delete()

    @commands.command(usage="<message_id> <message>")
    @commands.is_owner()
    async def edit_message(self, ctx, message_id, message):
        """Edits an embed message"""
        msg = await ctx.fetch_message(message_id)
        embed = msg.embeds[0]
        embed.description = message
        await msg.edit(embed=embed)

    @commands.command(usage="<string>")
    @commands.is_owner()
    async def execute_db(self, ctx, *, string):
        """Performs any action to the database"""
        db_client = await self.bot.fetch_db_client()
        message = await db_client.execute(string)
        await ctx.send(message)

    @commands.command(usage="<string>")
    @commands.is_owner()
    async def fetch_db(self, ctx, *, string):
        """Performs any action to the database"""
        db_client = await self.bot.fetch_db_client()
        message = await db_client.fetchrow(string)
        await ctx.send(message)

    @commands.command(usage="")
    @commands.is_owner()
    async def list_servers(self, ctx):
        """Lists all the servers the bot is in"""
        await ctx.send("\n".join([f"{guild.name} ({guild.id})" for guild in self.bot.guilds]))


async def setup(bot):
    await bot.add_cog(Developer(bot))
