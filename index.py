import discord
import os
import tracemalloc

from secret import token

from discord.ext import commands

extensions = ["extensions.help_command", "extensions.fun"]

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
tracemalloc.start()


class EpicGamer(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="e?", case_insensitive=True, intents=discord.Intents.all(), help_command=None)
    
    async def on_ready(self):
        print(f'{self.user.name} ({self.user.id}) is up and running at {round(self.latency * 1000)}ms')
        print(f'-----------------------------')
    
    async def close(self):
        print(f'{self.user.name} has shutdown!')

    async def setup_hook(self):
        for e in extensions:
            await self.load_extension(e)


if __name__ == "__main__":
    EpicGamer().run(token)
