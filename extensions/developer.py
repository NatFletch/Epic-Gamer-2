import discord
import os
from discord.ext import commands


class Developer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    @commands.is_owner()
    async def treesync(self, ctx):
        """Syncs command tree"""
        await self.bot.tree.sync()
        await ctx.send("Successfully synced command tree")
    
    @commands.hybrid_command(aliases=["reloadall", "reall"])
    @commands.is_owner()
    async def reload_extensions(self, ctx):
        """Reloads all extensions"""
        for extension in os.listdir("./"):
            if(extension.endswith('.py')):
                await self.bot.load_extension("extensions." + extension[:-3])
        await self.bot.load_extension("jishaku")
        await ctx.send(["Reloaded" + extension for extension in os.listdir("./extensions")].split("\n"))


async def setup(bot):
    await bot.add_cog(Developer(bot))