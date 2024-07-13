import discord
import asyncpg
import os
import tracemalloc

from conf import token, database_url
from util.cache import EpicCache
from discord.ext import commands
from util.DatabaseClient import DatabaseClient

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
tracemalloc.start()


class EpicGamer(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or("e/"),
            case_insensitive=True,
            intents=discord.Intents.all(),
            activity=discord.Activity(type=discord.ActivityType.listening, name="e/help")
        )
        self.cache = EpicCache(self)

    async def on_ready(self):
        # Cool message for startup
        print("Epic Gamer is up and running")
        print(f"Latency: {round(self.latency * 1000)}ms")
        print(f"Server Count: {len(self.guilds)}")

    @staticmethod
    async def fetch_db_client():
        connection = await asyncpg.connect(database_url)
        return DatabaseClient(connection)

    async def setup_hook(self):
        # Setup the database, if it isn't already setup
        self.db_client = await self.fetch_db_client()
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


if __name__ == "__main__":
    EpicGamer().run(token)
