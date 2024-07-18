import discord
import traceback
import sys
import math
from datetime import datetime
from discord.ext import commands


class CommandErrorHandler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        ignored = (commands.CommandNotFound)

        error = getattr(error, 'original', error)

        # Anything in ignored will return and prevent anything happening.
        if isinstance(error, ignored):
            return

        if isinstance(error, commands.DisabledCommand):
            await ctx.send(f'{ctx.command} has been disabled.')

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
            except discord.HTTPException:
                pass

        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"This command is on cooldown. Please wait {math.floor(error.retry_after)} seconds")

        else:
            # All other Errors not returned come here. And we can just print the default TraceBack.
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
            embed = discord.Embed(
                title="An Unknown Error Has Occured!",
                description=f"```{error}```",
                color=self.bot.color)
            
            await ctx.send(embed=embed)
        embed = discord.Embed(description="For more help please join the [support server](https://discord.gg/tDYMaz7u9s)!",
                              color=0xff0000,
                              timestamp=datetime.now())
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(CommandErrorHandler(bot))
