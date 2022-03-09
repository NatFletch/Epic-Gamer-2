import discord
import jishaku
import os
import tracemalloc

from secret import token

from discord.ext import commands

extensions = []
tracemalloc.start()

class EpicGamer(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="e?", help_command=None, case_insensitive=True, intents=discord.Intents.default())
    
        self.load_extension("jishaku")
        for e in extensions:
            self.load_extension(e)
    
    async def on_ready(self):
        print(f'{self.user.name} ({self.user.id}) is up and running at {self.latency * 1000}ms')
        print(f'-----------------------------')
    
    async def close(self):
        print(f'{self.bot.name} has shutdown!')


if __name__ == "__main__":
    EpicGamer().run(token)