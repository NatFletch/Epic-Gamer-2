import discord
import conf
import os
import jishaku
import tracemalloc
from discord.ext import commands

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
tracemalloc.start()

class EpicGamer(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix = commands.when_mentioned_or("e/"),
            case_insensitive = True,
            intents = discord.Intents.all(),
            activity = discord.Activity(type=discord.ActivityType.listening, name="e/help")
        )

    async def on_ready(self) -> None:
        print("Epic Gamer is up and running")
        print(f"Latency: {round(self.latency * 100)}")
        print(f"Server Count: {len(self.guilds)}")

    async def setup_hook(self) -> None:
        # Automatically find all extensions and load them

        for extension in os.listdir("./extensions"):
            if(extension.endswith('.py')):
                await self.load_extension("extensions." + extension[:-3])
        await self.load_extension("jishaku")


if __name__ == "__main__":
    EpicGamer().run(conf.token)