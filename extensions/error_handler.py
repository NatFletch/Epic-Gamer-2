import discord
import traceback
import sys
from datetime import datetime
from discord.ext import commands
from discord import app_commands


class CommandErrorHandler(commands.Cog):
    def __init__(self: commands.Cog, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_command_error(self: commands.Cog, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.PrivateMessageOnly):
            await ctx.send(f"This command can only be used in DMs!")
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send(f"This command can only be used in servers!")
        elif isinstance(error, commands.CheckFailure):
            await ctx.send(f"You do not have permission to run this command!")
        elif isinstance(error, commands.DisabledCommand):
            await ctx.send(f"At the moment, `{ctx.clean_prefix}{ctx.invoked_with}` is disabled")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"This command is currently on cooldown. You can try again in {round(error.retry_after)} seconds")
        else:
            await ctx.send(f"An unknown error occured: ```{error}```")
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
        embed: discord.Embed = discord.Embed(description="For more help please join the [support server](https://discord.gg/tDYMaz7u9s)!",
                              color=0xff0000,
                              timestamp=datetime.now())
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(CommandErrorHandler(bot))
