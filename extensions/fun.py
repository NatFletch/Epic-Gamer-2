import discord
import random
import aiohttp
from discord.ext import commands
from conf import embed_color


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.hybrid_command(name="8ball", usage="<message>")
    async def advice(self, ctx, *, message: str = commands.parameter(default=None, description="The message you wish to give to the 8 ball")):
        """Take a shot at the magic 8 ball for advice!"""
        if message is None: return await ctx.send("You need to provide a message for the 8 ball to answer")
        responses = ["Definitely.", "It is certain.", "Most likely." , "Outlook good.", "Yes.", "You may rely on it.", "Ask again later.",
                     "Better not tell you now.", "My reply is no.", "Signs point to yes.", "Very doubtful.", "Without a doubt.", "Cannot predict now."
                     "Concentrate and ask again.", "It is decidely so.", "My sources say no."]
        await ctx.send(f"{ctx.author.mention} asks {message}: {random.choice(responses)}")
        
    @commands.hybrid_command(usage="")
    @commands.cooldown(1, 5)
    async def meme(self, ctx):
        """Finds a random meme from some subreddits"""
        subreddits = ["funny", "memes", "dankmemes", "shitposting", "ContagiousLaughter", "whenthe"]
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://meme-api.com/gimme/{random.choice(subreddits)}") as response:
                    json = await response.json(content_type=None)

                    embed = discord.Embed(title=json.get("title"), color=embed_color)
                    embed.set_image(url=json["url"])
                    embed.set_author(name=f"u/"+json["author"])
                    embed.set_footer(text="r/" + json["subreddit"])
                    await ctx.send(embed=embed)

    @commands.hybrid_command(usage="<option1> <option2>")
    async def choose(self, ctx, option1: str = commands.parameter(description="The first option"), option2: str = commands.parameter(description="The second option")):
        """Chooses between two different options"""
        responses = ["I think you should choose", "I'm leaning towards", "I really like", "Go for", "Try", "I suggest"]
        await ctx.send(f"{random.choice(responses)} {random.choice([option1, option2])}")

    @commands.hybrid_command(usage="[sides]")
    async def roll(self, ctx, number: int = commands.parameter(default=6, description="The number of sides for the dice")):
        """Rolls a dice between 1 and specified number"""
        number = int(number)
        if number > 1000000:
            number = 6
        await ctx.send(f"Rolling {number} sided dice... rolled: {random.randint(1,number)}")


async def setup(bot):
    await bot.add_cog(Fun(bot))
