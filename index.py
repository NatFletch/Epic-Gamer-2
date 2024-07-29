import discord
import asyncpg
import os
import tracemalloc
import traceback
import datetime
import sys
from conf import token, database_url, embed_color, economy
from util.cache import EpicCache
from discord.ext import commands
from util.DatabaseClient import EpicDatabaseClient

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
tracemalloc.start()
intents = discord.Intents.default()
intents.presences = True
intents.members = True

class EpicGamer(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or("e/"),
            case_insensitive=True,
            intents=intents,
            activity=discord.Activity(type=discord.ActivityType.listening, name=f"an epic group of users")
        )
        self.cache: EpicCache = EpicCache(self)
        self.color: int = embed_color
        self.economy = economy

    async def on_ready(self: commands.Bot):
        # Cool message for startup
        print("Epic Gamer is up and running")
        print(f"Latency: {round(self.latency * 1000)}ms")
        print(f"Server Count: {len(self.guilds)}")

    @staticmethod
    async def fetch_db_client() -> EpicDatabaseClient:
        connection = await asyncpg.connect(database_url)
        return EpicDatabaseClient(connection)

    async def setup_hook(self):
        # Setup the database, if it isn't already setup
        self.db_client: EpicDatabaseClient = await self.fetch_db_client()
        await self.db_client.setup_tables()

        # Automatically find all extensions and load them
        for extension in os.listdir("./extensions"):
            if extension.endswith('.py'):
                await self.load_extension("extensions." + extension[:-3])
        await self.load_extension("jishaku")

    async def close(self):
        # Ensures the database gets closed when the code is done running
        await self.db_client.close()
        print("DB Closed")
        await super().close()


bot = EpicGamer()

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    if isinstance(error, discord.app_commands.NoPrivateMessage):
        await interaction.response.send_message(f"This command can only be used in servers!")
    elif isinstance(error, discord.app_commands.CommandOnCooldown):
        await interaction.response.send_message(f"This command is currently on cooldown. You can try again in {round(error.retry_after)} seconds")
    else:
        await interaction.response.send_message(f"An unknown error occured: ```{error}```")
        print('Ignoring exception in command {}:'.format(interaction.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
    embed: discord.Embed = discord.Embed(description="For more help please join the [support server](https://discord.gg/tDYMaz7u9s)!",
                            color=0xff0000,
                            timestamp=datetime.datetime.now())
    await interaction.response.send_message(embed=embed)


if __name__ == "__main__":
    bot.run(token)
