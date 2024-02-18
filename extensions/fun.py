import discord
import random
import aiohttp
from discord.ext import commands
from conf import embed_color


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.hybrid_command(name="8ball")
    async def advice(self, ctx, *, message):
        """Take a shot at the magic 8 ball for advice!"""
        responses = ["Definitely.", "It is certain.", "Most likely." , "Outlook good.", "Yes.", "You may rely on it.", "Ask again later.",
                     "Better not tell you now.", "My reply is no.", "Signs point to yes.", "Very doubtful.", "Without a doubt.", "Cannot predict now."
                     "Concentrate and ask again.", "It is decidely so.", "My sources say no."]
        await ctx.send(f"{ctx.author.mention}: {random.choice(responses)}")
        
    @commands.hybrid_command()
    async def meme(self, ctx):
        """Finds a random meme from some subreddits"""
        subreddits = ["funny", "memes", "dankmemes", "shitposting", "ContagiousLaughter", "whenthe"]
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://meme-api.com/gimme/{random.choice(subreddits)}") as response:
                json = await response.json(content_type=None)
                    
                embed = discord.Embed(title=json.get("title"), color=embed_color)
                embed.set_image(url=json["url"])
                embed.set_author(name=f"u/"+json["author"])
                embed.set_footer(text="r/" + json["subreddit"])
                await ctx.send(embed=embed)
                
        
async def setup(bot):
    await bot.add_cog(Fun(bot))