import math

import discord
import conf
import os
import jishaku
import asyncpg
import tracemalloc
import traceback
import sys
from util.DatabaseClient import DatabaseClient
from discord.ext import commands

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
tracemalloc.start()


class EpicGamer(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix=commands.when_mentioned_or("e/"),
            case_insensitive=True,
            intents=discord.Intents.all(),
            activity=discord.Activity(type=discord.ActivityType.listening, name="e/help")
        )

    async def on_ready(self) -> None:
        print("Epic Gamer is up and running")
        print(f"Latency: {round(self.latency * 1000)}")
        print(f"Server Count: {len(self.guilds)}")

    @staticmethod
    async def fetch_db_client():
        connection = await asyncpg.connect("postgres://postgres@localhost/epic-gamer-2")
        return DatabaseClient(connection)

    async def setup_hook(self) -> None:
        # Check if database tables exist
        db_client = await self.fetch_db_client()
        suggestions_table = await db_client.find_suggestion_table()
        suggestions_channel_table = await db_client.find_suggestion_channel_table()
        if not suggestions_table.get("to_regclass"):
            await db_client.create_suggestion_table()

        if not suggestions_channel_table.get("to_regclass"):
            await db_client.create_suggestion_channel_table()

        # Automatically find all extensions and load them
        for extension in os.listdir("./extensions"):
            if extension.endswith('.py'):
                await self.load_extension("extensions." + extension[:-3])
        await self.load_extension("jishaku")

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(f"That command was not found. Use `e/help` for a list of commands")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(f"You are missing permissions. You require `{error.missing_perms}` to use this")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(
                f"Your arguments are not correct. Please view help on this command using `e/help {ctx.invoked_with}` to see how to use it")
            print(error)
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"You missed a required argument. Make sure to add `{error.param}` when using this command")
        elif isinstance(error, commands.NotOwner):
            await ctx.send("Only developers can use this command :)")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(
                f"I am missing permissions to perform this operation. I am missing {error.missing_perms} permissions")
        elif isinstance(error, commands.NSFWChannelRequired):
            await ctx.send(
                f"Woah, I'm not getting banned anytime soon! You need to be in an NSFW channel to execute this command!")
        elif isinstance(error, commands.ExtensionAlreadyLoaded):
            await ctx.send("I already loaded that cog. No need to load it again")
        elif isinstance(error, commands.ExtensionNotFound):
            await ctx.send(f"Hmmm I can't seem to find {error.name}")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"You are using this command too fast! You have {math.floor(error.retry_after)} seconds until you can use this command again")
        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
            text = "".join(traceback.format_exception_only(type(error), error))
            embed = discord.Embed(title="An Unknown Error Occurred!",
                                  description=f'```py\nIgnoring exception in command {ctx.command}:\n{text}\n```',
                                  color=0xff0000)
            await ctx.send(embed=embed)

        embed = discord.Embed(title="Further steps",
                              description="For more help please join our support server: https://discord.gg/tDYMaz7u9s",
                              color=conf.embed_color)
        await ctx.send(embed=embed)

    async def close(self):
        db_client = self.fetch_db_client()
        db_client.close()
        print("DB Closed")
        await super().close()


if __name__ == "__main__":
    EpicGamer().run(conf.token)
