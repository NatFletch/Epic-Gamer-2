import discord
import random
from discord.ext import commands


class EpicEconomyHelper:
    def __init__(self, bot):
        self.bot = bot
        
    async def check_for_account(self, user_id):
        data = await self.bot.db_client.fetchrow("SELECT * FROM money WHERE user_id = $1", user_id)
        if not data:
            return False
        return True
    
    async def register_account(self, user_id):
        self.bot.cache.set_money_cache(user_id, 100)
        await self.bot.db_client.execute("INSERT INTO money (user_id, money) VALUES ($1, $2)", user_id, 100)
        
    async def get_money(self, user_id):
        if self.bot.cache.get_money_cache(user_id):
            return self.bot.cache.get_money_cache(user_id)
        money = await self.bot.db_client.fetchrow("SELECT * FROM money WHERE user_id = $1", user_id)    
        self.bot.cache.set_money_cache(user_id, money["money"])
        return money["money"]
        
    async def set_money(self, user_id, money):
        self.bot.cache.set_money_cache(user_id, money)
        await self.bot.db_client.execute("UPDATE money SET money = $1 WHERE user_id = $2", money, user_id)


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.helper = EpicEconomyHelper(bot)
        
    @commands.command()
    async def register(self, ctx):
        """Registers an account in the Epic economy"""
        if await self.helper.check_for_account(ctx.author.id):
            return await ctx.send("You already have an account registered")
        await self.helper.register_account(ctx.author.id)
        await ctx.send("Your account has been registered with 100 coins")
        
        
    @commands.command()
    async def balance(self, ctx):
        """Views your accoutn balance"""
        await ctx.send(f"{await self.helper.get_money(ctx.author.id)} coins")
    
    @commands.command()
    async def gamble(self, ctx, money: int):
        """Gamble away your life savings"""
        if await self.helper.check_for_account(ctx.author.id):
            if not money:
                return await ctx.send("You need to at least bet something")
            if money < 1:
                return await ctx.send("You cannot make a bet that is zero or negative")
            
            prev_balance = await self.helper.get_money(ctx.author.id)
            
            if money == prev_balance:
                return await ctx.send("You cannot make a bet that will make you go bankrupt, unfortunately.")
            
            if money > prev_balance:
                return await ctx.send("Please bet something lower than your current balance. I can't make you go in debt")
        
            outcome = "Tie"
            outcome_dict = {
                "Win": 0x00ff00,
                "Lose": 0xff0000,
                "Tied": 0xffff00
            }
            
            user_roll = random.randint(1,10)
            bot_roll = random.randint(1,10)
            
            if user_roll > bot_roll:
                outcome = "Win"
            elif user_roll < bot_roll:
                outcome = "Lose"
            else:
                outcome = "Tied"
            
            if outcome == "Win":
                await self.helper.set_money(ctx.author.id, prev_balance + money)
            elif outcome == "Lose":
                await self.helper.set_money(ctx.author.id, prev_balance - money)
                
            e = discord.Embed(title=f"You {outcome}",
                            color=outcome_dict[outcome])
            e.add_field(name=f"{ctx.author.name} rolls", value=user_roll, inline=False)
            e.add_field(name=f"{self.bot.user.name} rolls", value=bot_roll, inline=False)
            await ctx.send(embed=e)
        else:
            await ctx.send("You do not have an account. Type `/register` to get an account")
        
            
async def setup(bot):
    await bot.add_cog(Economy(bot))