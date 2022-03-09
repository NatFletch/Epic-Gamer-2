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
        print('sending cog help')
        return
