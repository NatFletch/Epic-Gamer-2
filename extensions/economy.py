import discord
import random
import conf
from discord.ext import commands
from discord import app_commands

class EpicEconomyHelper:
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        
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
    
    # Thanks ChatGPT for these next three functions
    def _determine_outcome(self):
        """Rolls dice and determines the outcome"""
        user_roll = random.randint(1, 10)
        bot_roll = random.randint(1, 10)

        if user_roll > bot_roll:
            return "Win", user_roll, bot_roll
        elif user_roll < bot_roll:
            return "Lose", user_roll, bot_roll
        else:
            return "Tied", user_roll, bot_roll

    def _update_balance(self, prev_balance, bet_amount, outcome):
        """Updates the user's balance based on the outcome"""
        if outcome == "Win":
            return prev_balance + bet_amount
        elif outcome == "Lose":
            return prev_balance - bet_amount
        return prev_balance

    def _get_outcome_color(self, outcome):
        """Returns the color based on the outcome"""
        colors = {
            "Win": 0x00ff00,  # Green for win
            "Lose": 0xff0000, # Red for lose
            "Tied": 0xffff00  # Yellow for tie
        }
        return colors.get(outcome, 0xffffff) # Default to white if outcome is unknown
    
    def search_outcome(self, outcome: int, money: int, prev_balance: int):
        if outcome == 0:
            return "LOSS!", "lost", prev_balance - money, random.choice(["donating to a homeless person", "by dropping them in a sewer", "getting robbed", "natural causes",
                                           "a black hole opening up in your wallet", "getting mugged", "dropping them in a bush", "dropping them in a dumpster"])
        if outcome == 1:
            return "FIND!", "found", prev_balance + money, random.choice(["finding them in a vending machine coin return", "robbing a bank", "finding them on the ground", "begging for donations",
                                           "finding them in a laundromat", "finding them in a bush", "finding them in a trash can",
                                           "finding them in a dumpster", "finding them in a vending machine"])


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.helper = EpicEconomyHelper(bot)
        
    @app_commands.command()
    @discord.app_commands.allowed_installs(users=True, guilds=True)
    @discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def register(self, interaction: discord.Interaction):
        """Registers an account in the Epic economy"""
        if await self.helper.check_for_account(interaction.user.id):
            return await interaction.response.send_message("You already have an account registered")
        await self.helper.register_account(interaction.user.id)
        await interaction.response.send_message(f"Your account has been registered with 100 {self.bot.economy}")
        
        
    @app_commands.command()
    @discord.app_commands.allowed_installs(users=True, guilds=True)
    @discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def balance(self, interaction: discord.Interaction):
        """Views your account balance"""
        await interaction.response.send_message(f"{await self.helper.get_money(interaction.user.id)} {self.bot.economy}")
    
    @app_commands.command()
    @app_commands.describe(money=f"The amount of {conf.economy} you wish to gamble")
    @discord.app_commands.allowed_installs(users=True, guilds=True)
    @discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def gamble(self, interaction: discord.Interaction, money: int):
        """Gamble away your life savings"""
        if not await self.helper.check_for_account(interaction.user.id):
            return await interaction.response.send_message("You do not have an account. Type `/register` to get an account")
        
        # Validate the bet amount
        if money <= 0:
            return await interaction.response.send_message(
                f"You need to bet a positive amount of {self.bot.economy}"
            )
        
        prev_balance = await self.helper.get_money(interaction.user.id)

        if money > prev_balance:
            return await interaction.response.send_message(
                "You cannot bet more than your current balance. Please bet a lower amount."
            )

        # Determine the outcome
        outcome, user_roll, bot_roll = self.helper._determine_outcome()

        # Update the user's balance based on the outcome
        new_balance = self.helper._update_balance(prev_balance, money, outcome)
        await self.helper.set_money(interaction.user.id, new_balance)

        # Prepare and send the result message
        embed = discord.Embed(
            title=f"You {outcome}",
            color=self.helper._get_outcome_color(outcome),
            description=f"New balance: {new_balance}"
        )
        embed.add_field(name=f"{interaction.user.name} rolls", value=user_roll, inline=False)
        embed.add_field(name=f"{self.bot.user.name} rolls", value=bot_roll, inline=False)
        await interaction.response.send_message(embed=embed)
        
    @app_commands.command()
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.checks.cooldown(1, 120)
    async def search(self, interaction: discord.Interaction):
        """Searches for more money"""
        prev_balance = await self.helper.get_money(interaction.user.id)
        outcome = random.randint(0,1)
        winnings = random.randint(5,100)
        
        if prev_balance == 1:
            return interaction.response.send_message(f"You need more than 1 {self.bot.economy[:-1]} to search. You could lose that {self.bot.economy[-1]} you know.")
        if winnings > prev_balance:
            winnings = random.randint(1, prev_balance-1)
        
        exclaim_status, status, new_balance, action = self.helper.search_outcome(outcome, winnings, prev_balance)
        await self.helper.set_money(interaction.user.id, new_balance)
        await interaction.response.send_message(f"{exclaim_status} You {status} {winnings} {self.bot.economy} by {action}. Your new balance is {new_balance} {self.bot.economy}")
            
async def setup(bot):
    await bot.add_cog(Economy(bot))