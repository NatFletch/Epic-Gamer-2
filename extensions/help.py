import discord
from discord.ext import commands
from conf import embed_color


class EpicHelpCommand(commands.MinimalHelpCommand):
    def __init__(self):
        super().__init__(command_attrs=dict(hidden=True, usage=""))

    def get_command_signature(self, command):
        return f"{self.context.clean_prefix}{command.qualified_name} {command.usage}"

    def get_ending_note(self):
        return f"Use {self.context.clean_prefix}{self.invoked_with} [command] for more info on a command"

    async def send_bot_help(self, mapping):
        destination = self.get_destination()
        embed = discord.Embed(
            title=f"{self.context.bot.user.name} Help Command",
            description="**Categories**",
            color=embed_color)
        embed.set_footer(text=self.get_ending_note())

        for cog, _commands in mapping.items():
            filtered_list = await self.filter_commands(_commands, sort=True)
            command_list = [f"`{self.context.clean_prefix}{command.qualified_name}`" for command in filtered_list]
            if filtered_list:
                embed.add_field(name=cog.qualified_name, value=" ".join(command_list), inline=False)

        await destination.send(embed=embed)

    async def send_cog_help(self, cog):
        destination = self.get_destination()
        embed = discord.Embed(title=f"{cog.qualified_name} Help", color=embed_color)
        filtered_list = await self.filter_commands(cog.get_commands(), sort=True)
        command_list = "\n".join([f"`{self.get_command_signature(command)}`" for command in filtered_list])
        embed.description = f"Use `{self.context.clean_prefix}help [command]` for more info on a command.\nYou can also use `{self.context.clean_prefix}help [category]` for more info on a category.\n\n**{cog.qualified_name} Commands**\n{command_list}"
        embed.set_footer(text="Key: `<option>` means the option is required while `[option]` means its optional.")
        await destination.send(embed=embed)

    async def send_group_help(self, command):
        """Group help and command help logic in one function"""
        destination = self.get_destination()
        embed = discord.Embed(title=f"{self.context.clean_prefix}{command.qualified_name}", color=embed_color)
        alias_help = "No Aliases"

        if len(command.aliases) > 0:
            alias_help = " | ".join(command.aliases)

        cooldown = command.cooldown
        if cooldown is not None:
            cooldown = f"{cooldown.rate} command(s) for every {cooldown.per} second(s)"

        if command.help:
            embed.description = f"**Description:** {command.help}\n**Aliases**: {alias_help}\n**Cooldown**: {cooldown}\n**Usage:**```{self.get_command_signature(command)}```"

        if isinstance(command, commands.Group):
            filtered_list = await self.filter_commands(command.commands, sort=True)
            for group_command in filtered_list:
                alias_help = "No Aliases"

                if len(command.aliases) > 0:
                    alias_help = " | ".join(group_command.aliases)

                cooldown = group_command.cooldown
                if cooldown is not None:
                    cooldown = f"{cooldown.rate} command(s) for every {cooldown.per} second(s)"

                embed.add_field(name=f"{self.context.clean_prefix}{command.qualified_name}",
                                value=f"**Description:** {group_command.help}\n**Aliases:** {alias_help}\n**Cooldown**: {cooldown}\n**Usage:**\n```{self.get_command_signature(group_command)}```",
                                inline=False)

        await destination.send(embed=embed)

    send_command_help = send_group_help


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = EpicHelpCommand()
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self._original_help_command


async def setup(bot):
    await bot.add_cog(Help(bot))
