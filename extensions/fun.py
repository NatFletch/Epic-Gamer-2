import discord
import random

from discord.ext import commands


class Fun(commands.Bot):
    """Fun commands for you to enjoy"""
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def roll(self, ctx, number: int=None):
        """Rolls a dice. Can have multiple sides if specified"""
        if not number:
            number = 6

        await ctx.send(random.randint(0, number))


async def setup(bot):
    await bot.add_cog(Fun(bot))
