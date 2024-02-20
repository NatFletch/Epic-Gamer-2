import discord
from discord.ext import commands
from conf import embed_color


class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


async def setup(bot):
    await bot.add_cog(Config(bot))