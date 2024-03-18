import discord
import sys
import psutil
import os
from discord.ext import commands
from discord.utils import format_dt
from conf import embed_color


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(aliases=["uinfo", "ui", "user-info"], usage="[member]")
    async def userinfo(self, ctx, member: discord.Member = commands.parameter(default=None, description="The user you would like to find info on")):
        """Fetches info for a given user or on yourself"""
        if not member:
            member = ctx.author

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
        
        embed = discord.Embed(
            title=f"{member.name}",
            description=f"**Username:** {member.name}\n**Nickname:** {member.nick}\n**Account Creation Date:** {format_dt(member.created_at, style='F')}\n**Server Join Date:** {format_dt(member.joined_at, style='F')}\n**Join Position:** {sorted(ctx.guild.members, key=lambda member: member.joined_at).index(member) + 1}\n**Status:** {status_dict[ctx.guild.get_member(member.id).status]}\n**Badges:** {''.join(flags_list)}\n**Top Role:** {member.top_role.mention}\n**Roles:** {' '.join([role.mention for role in member.roles if role != ctx.guild.default_role])}",
            color=member.accent_color
        )
        embed.set_author(name=member.name, icon_url=member.avatar.with_format("png"))
        embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar.with_format("png"))
        embed.set_thumbnail(url=member.avatar.with_format("png"))
        await ctx.send(embed=embed)

    @commands.hybrid_command(aliases=["sinfo"], usage="")
    async def serverinfo(self, ctx: commands.Context):
        """Fetches info on the current server"""
        guild = ctx.guild

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
            description=f'**Server Name:** {guild.name}\n**Server Member Count:** {guild.member_count}\n**Server Creation Date:** {format_dt(guild.created_at, style="F")}\n**Owner:** {guild.owner.mention}\n**Text Channel Count:** {len(guild.text_channels)}\n**Voice Channel Count:** {len(guild.voice_channels)}\n**Role Count:** {len(guild.roles)}\n**Verification Level:** {vlevel_dict.get(guild.verification_level)}\n**Nitro Boost Level:** {boost_dict.get(guild.premium_tier)}',
            color=embed_color
        )

        if not (icon := guild.icon): icon = self.bot.user.avatar
        embed.set_author(name=guild.name, icon_url=icon.with_format("png"))
        embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar.with_format("png"))
        await ctx.send(embed=embed)

    @commands.hybrid_command(aliases=["stats"], usage="")
    async def statistics(self, ctx):
        """Provides some stats on the bot"""
        load1, load5, load15 = psutil.getloadavg()
        embed = discord.Embed(
            title=f"{self.bot.user.name}",
            description=f'**Bot Name:** {self.bot.user.name}\n**Server Count:** {len(self.bot.guilds)}\n**Member Count:** {len(self.bot.users)}\n\n**Account Creation Date:** {format_dt(self.bot.user.created_at, style="F")}\n**Owner:** NatFletch\n\n**Latency:** {round(self.bot.latency * 1000)}ms\n**CPU Usage:** {round(load15 / os.cpu_count() * 100)}%\n**Memory:** {round(psutil.virtual_memory()[3] / 1000000000, 2)} gb / {round(psutil.virtual_memory()[0] / 1000000000, 2)} gb\n\n**Python Version:** {sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}\n**Discord.py Version:** {discord.__version__}',
            color=embed_color
        )
        embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar.with_format("png"))
        await ctx.send(embed=embed)

    @commands.hybrid_command(aliases=["latency"], usage="")
    async def ping(self, ctx):
        """Shows the bot's current latency"""
        await ctx.send(f"Pong! {round(self.bot.latency * 1000)}ms")


async def setup(bot):
    await bot.add_cog(Info(bot))
