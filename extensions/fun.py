import discord
import random
import aiohttp
from discord.ext import commands
from discord import app_commands


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name="8ball")
    @app_commands.describe(message = "The message you wish to give to the magic 8ball")
    @app_commands.allowed_installs(users=True, guilds=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def advice(self, interaction: discord.Interaction, *, message: str):
        """Take a shot at the magic 8 ball for advice!"""
        responses = ["Definitely.", "It is certain.", "Most likely." , "Outlook good.", "Yes.", "You may rely on it.", "Ask again later.",
                     "Better not tell you now.", "My reply is no.", "Signs point to yes.", "Very doubtful.", "Without a doubt.", "Cannot predict now."
                     "Concentrate and ask again.", "It is decidely so.", "My sources say no."]
        await interaction.response.send_message(f"{interaction.user.mention} asks {message}: {random.choice(responses)}")
        
    @app_commands.command()
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def meme(self, interaction: discord.Interaction):
        """Finds a random meme from some subreddits"""
        subreddits = ["funny", "memes", "dankmemes", "shitposting", "whenthe"]
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://meme-api.com/gimme/{random.choice(subreddits)}") as response:
                json = await response.json(content_type=None)

                embed = discord.Embed(title=json.get("title"), color=self.bot.color)
                embed.set_image(url=json["url"])
                embed.set_author(name=f"u/"+json["author"])
                embed.set_footer(text="r/" + json["subreddit"])
                await interaction.response.send_message(embed=embed)

    @app_commands.command()
    @app_commands.describe(option1 = "The first option", option2 = "The second option")
    @app_commands.allowed_installs(users=True, guilds=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def choose(self, interaction: discord.Interaction, option1: str, option2: str):
        """Chooses between two different options"""
        responses = ["I think you should choose", "I'm leaning towards", "I really like", "Go for", "Try", "I suggest"]
        await interaction.response.send_message(f"{random.choice(responses)} {random.choice([option1, option2])}")

    @app_commands.command()
    @app_commands.describe(number = "The number of sides for the dice")
    @app_commands.allowed_installs(users=True, guilds=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def roll(self, interaction: discord.Interaction, number: int = 6):
        """Rolls a dice between 1 and specified number"""
        number = int(number)
        if number > 1000000 or number <= 0:
            number = 6
        await interaction.response.send_message(f"Rolling {number} sided dice... rolled: {random.randint(1,number)}")
        
    @app_commands.command()
    @discord.app_commands.allowed_installs(users=True, guilds=True)
    @discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def coinflip(self, interaction: discord.Interaction):
        """Flips a coin"""
        await interaction.response.send_message(random.choice(["Heads", "Tails"]))


async def setup(bot):
    await bot.add_cog(Fun(bot))
