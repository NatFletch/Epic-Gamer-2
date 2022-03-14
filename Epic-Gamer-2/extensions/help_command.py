import discord
from discord.ext import commands

color = 0xff2e2e

class EpicHelpSelect(discord.ui.Select):
    def __init__(self):
        super().__init__(placeholder="Select a Command Category",options=options)
    async def callback(self, interaction: discord.Interaction):
        print(interaction.data)
        await send_cog_help()

class EpicHelpView(discord.ui.View):
    def __init__(self, *, timeout=60):
        super().__init__(timeout=timeout)
        self.add_item(EpicHelpSelect())


class EpicHelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__(command_attrs=dict(hidden=True))

    def get_command_signature(self, command):
        return f'{self.clean_prefix}{command.qualified_name} {command.signature}'

    def get_ending_note(self):
        return f'Use {self.clean_prefix} {self.invoked_with} [help] for more info on a command'

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title=f'{self.context.bot.name} Help Menu', description="**Categories**", color=color)
        description = self.bot.description

        if description:
            embed.description = description
        
        for cog, commands in mapping.items():
            filtered = await self.filter_commands(commands, sort=False)
            commands = [f'`{self.clean_prefix}{c.name}`' for c in filtered]
            description = " ".join(commands)
            options = []
            if filtered:
                options.append(discord.SelectOption(label=cog.qualified_name, description=cog.description))
            

            embed.set_footer(text=self.get_ending_note())
            await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog):
        embed = discord.Embed(title=f"{cog.qualified_name} Commands", color=color)
        filtered = await self.filter_commands(cog.get_commands(), sort=False)
        commands = [f'`{self.clean_prefix}{c.name}`' for c in filtered]
        description = " ".join(commands)
        embed.description = description
        embed.set_footer(text=self.get_ending_note())
        await self.get_destination().send(embed=embed)
    
    async def send_group_help(self, group):
        text = "No Aliases"
        if len(group.aliases) > 0:
            text = " | ".join(group.aliases)
        embed = discord.Embed(title=f"{self.clean_prefix}{group.qualified_name}", colour=0xff0000)
        if group.help:
            embed.description = f"**Description:** {group.help}\n**Aliases:** {text}\n{group.brief}\n**Usage:**\n```{self.clean_prefix}{group.name} {group.signature}```"

        if isinstance(group, commands.Group):
            filtered = await self.filter_commands(group.commands, sort=True)
            for command in filtered:
                text = "No Aliases"
                if len(group.aliases) > 0:
                    text = " | ".join(command.aliases)
                embed.add_field(name=f"{self.clean_prefix}{command.qualified_name}", value=f"**Description:** {command.help}\n**Aliases:** {text}\n{command.brief}\n**Usage:**\n```{self.clean_prefix}{command.qualified_name} {command.signature}```" or '...', inline=False)

        await self.get_destination().send(embed=embed)

    send_command_help = send_group_help

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.old_help_command = bot.help_command
        bot.help_command = EmbedHelpCommand()
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self.old_help_command


def setup(bot):
    bot.add_cog(Help(bot))