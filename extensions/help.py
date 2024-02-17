import discord
from conf import embed_color
from discord.ext import commands

class EpicHelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__(command_attrs=dict(hidden=True));

    def get_ending_note(self) -> str:
        return f"Use {self.clean_prefix}{self.invoked_with} [help] for more info on a command."
    
    def get_command_signature(self, command) -> str:
        return f"{self.clean_prefix}{command.qualified_name} {command.signature}"

    async def send_bot_help(self, mapping) -> None:
        embed: discord.Embed = discord.Embed(title="Embed Gamer Help Menu", description="**Categories**", color=embed_color)

        for cog, commands in mapping.items():
            filtered: list = await self.filter_commands(commands, sort=False)
            command_list: list = [f"`{self.clean_prefix}{c.name}`" for c in filtered]
            pretty_list: str = " ".join(commands)

            if filtered:
                embed.add_field(name=cog.qualified_name, value=pretty_list, inline=False)

        embed.set_footer(text=self.get_ending_note())
        await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog) -> None:
        embed: discord.Embed = discord.Embed(title=f"{cog.qualified_name} Commands", color=embed_color)
        filtered: list = await self.filter_commands(cog.get_commands(), sort=False)
        command_list: list = [f"`{self.clean_prefix}{c.name}`" for c in filtered]
        pretty_list: str = " ".join(command_list)
        embed.description = pretty_list
        embed.set_footer(text=self.get_ending_note)
        await self.get_destination().send(embed=embed)

    async def send_group_help(self, group):
        text: str = "No Aliases"
        if len(group.aliases) > 0:
            text = " | ".join(group.aliases)
        
        embed: discord.Embed = discord.Embed(title=f"{self.clean_prefix}{group.qualified_name}", color=embed_color)

        if group.help:
            embed.description = f"**Description:** {group.help}\n**Aliases:** {text}\n{group.brief}\n**Usage:**\n```{self.clean_prefix}{group.name} {group.signature}```"
        
        if isinstance(group, commands.Group):
            filtered: list = await self.filter_commands(group.commands, sort=True)

            for command in filtered:
                text: str = "No Aliases"
                if len(group.aliases) > 0:
                    text: str = " | ".join(command.aliases)
                embed.add_field(name=f"{self.clean_prefix}{command.qualified_name}", value=f"**Description:** {command.help}\n**Aliases:** {text}\n{command.brief}\n**Usage:**\n```{self.clean_prefix}{command.qualified_name} {command.signature}```" or '...', inline=False)
        
        await self.get_destination().send(embed=embed)
    
    send_command_help = send_group_help


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.help_command = EpicHelpCommand()
        bot.help_command.cog = self


async def setup(bot):
    await bot.add_cog(Help(bot))