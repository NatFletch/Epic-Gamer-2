import discord

from secret import token

from discord.ext import commands

extensions = []

class EpicGamer(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="e?", help_command=None, case_insensitive=True, intents=discord.Intents.default())

if __name__ == "__main__":
    bot = EpicGamer()
    bot.run(token)
    
    for e in extensions:
        bot.load_extension(e)