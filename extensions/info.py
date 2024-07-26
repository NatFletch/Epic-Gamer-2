import discord
import typing
import sys
import psutil
import os
from discord import app_commands
from discord.ext import commands
from discord.utils import format_dt


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    @app_commands.describe(member = "The user you want info on")
    @discord.app_commands.allowed_installs(users=False, guilds=True)
    @discord.app_commands.allowed_contexts(guilds=True, dms=False, private_channels=False)
    async def userinfo(self, interaction: discord.Interaction, member: typing.Union[discord.Member, discord.User]= None):
        """Fetches info for a given user or on yourself"""
        if not member:
            member = interaction.user

        status_dict = {
            discord.Status.online: "<:status_online:1216551760089579550> Online",
            discord.Status.dnd: "<:status_dnd:1216551750740344832> Do Not Disturb",
            discord.Status.idle: "<:status_idle:1216551753537818644> Idle",
            discord.Status.offline: "<:status_offline:1216551756784472094> Offline",
        }
        
        public_flag_dict = {
            "active_developer": "<:active_developer:1216549585804202025>",
            "bug_hunter": "<:bug_hunter:1216549584252309514>",
            "bug_hunter_level_2": "<:golden_bug_hunter:1216549591382495293>",
            "discord_certified_moderator": "<:discord_certified_moderator:1219416662906900561>",
            "early_supporter": "<:early_supporter:1216549589885128795>",
            "verified_bot_developer": "<:verified_bot_developer:1216550341395615785>",
            "hypesquad": "<:hypesquad:1216550334399250522>",
            "hypesquad_balance": "<:balance:1216549580032708698>",
            "hypesquad_bravery": "<:bravery:1216549581408571483>",
            "hypesquad_brilliance": "<:brilliance:1216549582671057056>",
            "partner": "<:discord_partner:1216549587360419990>",
            "staff": "<:discord_staff:1216549588693946488>",
        }
        
        flags_list = []
        for name, value in member.public_flags:
            if value:
                flags_list.append(public_flag_dict[name])
        
        fetched_member = await self.bot.fetch_user(member.id)
        
        embed = discord.Embed(
            title=f"{member.name}",
            color=fetched_member.accent_color
        )
        embed.set_author(name=member.name, icon_url=member.avatar.with_format("png"))
        embed.set_footer(text=interaction.user.name, icon_url=interaction.user.avatar.with_format("png"))
        embed.set_thumbnail(url=member.avatar.with_format("png"))
        
        embed.add_field(name="Username", value=member.name)
        embed.add_field(name="Nickname", value=member.display_name)
        embed.add_field(name="Account Creation Date", value=format_dt(member.created_at, style='F'))
        embed.add_field(name="Badges", value="".join(flags_list))
        if type(member) is discord.Member:
            embed.add_field(name="Server Join Date", value=format_dt(member.joined_at, style='F'))
            embed.add_field(name="Join Position", value=sorted(interaction.guild.members, key=lambda member: member.joined_at).index(member) + 1)
            embed.add_field(name="Top Role", value=member.top_role.mention)
            embed.add_field(name="Status", value=status_dict[interaction.guild.get_member(member.id).status])
            embed.add_field(name="Roles", value=' '.join([role.mention for role in member.roles if role != interaction.guild.default_role]))
        await interaction.response.send_message(embed=embed)

    @app_commands.command()
    @commands.guild_only()
    @discord.app_commands.allowed_installs(users=True, guilds=True)
    @discord.app_commands.allowed_contexts(guilds=True, dms=False, private_channels=False)
    async def serverinfo(self, interaction: discord.Interaction):
        """Fetches info on the current server"""
        guild = interaction.guild

        vlevel_dict = {
            discord.VerificationLevel.none: "None",
            discord.VerificationLevel.low: "Low",
            discord.VerificationLevel.medium: "Medium",
            discord.VerificationLevel.high: "High",
            discord.VerificationLevel.highest: "Highest"
        }

        boost_dict = {
            0: "No Level",
            1: "Level One",
            2: "Level Two",
            3: "Level Three"
        }

        embed = discord.Embed(
            title=f"{guild.name}",
            color=self.bot.color
        )

        if not (icon := guild.icon): icon = self.bot.user.avatar
        embed.set_author(name=guild.name, icon_url=icon.with_format("png"))
        embed.set_footer(text=interaction.user.name, icon_url=interaction.user.avatar.with_format("png"))
        
        embed.add_field(name="Server Name", value=guild.name)
        embed.add_field(name="Member Count", value=guild.member_count)
        embed.add_field(name="Created At", value=format_dt(guild.created_at, style='F'))
        embed.add_field(name="Owner", value=guild.owner.mention)
        embed.add_field(name="Text Channel Count", value=len(guild.text_channels))
        embed.add_field(name="Voice Channel Count", value=len(guild.voice_channels))
        embed.add_field(name="Role Count", value=len(guild.roles))
        embed.add_field(name="Verification Level", value=vlevel_dict.get(guild.verification_level))
        embed.add_field(name="Nitro Boost Level", value=boost_dict.get(guild.premium_tier))
        await interaction.response.send_message(embed=embed)

    @app_commands.command()
    @discord.app_commands.allowed_installs(users=True, guilds=True)
    @discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def statistics(self, interaction: discord.Interaction):
        """Provides some stats on the bot"""
        load1, load5, load15 = psutil.getloadavg()
        embed = discord.Embed(
            title=f"{self.bot.user.name}",
            color=self.bot.color
        )
        embed.set_footer(text=interaction.user.name, icon_url=interaction.user.avatar.with_format("png"))
        
        embed.add_field(name="Bot Name", value=self.bot.user.name)
        embed.add_field(name="Server Count", value=len(self.bot.guilds))
        embed.add_field(name="Member Count", value=len(self.bot.users))
        embed.add_field(name="Account Creation Date", value=format_dt(self.bot.user.created_at, style="F"))
        embed.add_field(name="Owner", value="NatFletch")
        embed.add_field(name="Latency", value=f"{round(self.bot.latency * 1000)}ms")
        embed.add_field(name="CPU Usage", value=f"{round(load15 / os.cpu_count() * 100)}%")
        embed.add_field(name="Memory", value=f"{round(psutil.virtual_memory()[3] / 1000000000, 2)} GB / {round(psutil.virtual_memory()[0] / 1000000000, 2)} GB")
        embed.add_field(name="Python Version", value=f"{sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}")
        embed.add_field(name="Discord.py Version", value=discord.__version__)
        await interaction.response.send_message(embed=embed)

    @app_commands.command()
    @discord.app_commands.allowed_installs(users=True, guilds=True)
    @discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def ping(self, interaction: discord.Interaction):
        """Shows the bot's current latency"""
        await interaction.response.send_message(f"Pong! {round(self.bot.latency * 1000)}ms")


async def setup(bot):
    await bot.add_cog(Info(bot))
