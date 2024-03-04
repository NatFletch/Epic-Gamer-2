import discord
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
            discord.Status.online: "<:Online:1208304786982572062> Online",
            discord.Status.dnd: "<:dnd:1208304483994697758> Do Not Disturb",
            discord.Status.idle: "<:Idle:1208304788455038986> Idle",
            discord.Status.offline: "<:offline:1208304481033256990> Offline",
        }
        embed = discord.Embed(
            title=f"{member.name}",
            description=f"""
                **Username:** {member.name}
                **Nickname:** {member.nick}
                **Account Creation Date:** {format_dt(member.created_at, style="F")}
                **Server Join Date:** {format_dt(member.joined_at, style="F")}
                **Join Position:** {sorted(ctx.guild.members, key=lambda member: member.joined_at).index(member) + 1}
                **Status:** {status_dict[ctx.guild.get_member(member.id).status]}
                **Top Role:** {member.top_role.mention}
                **Roles:** {" ".join([role.mention for role in member.roles if role != ctx.guild.default_role])}
            """,
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
            description=f"""
                **Server Name:** {guild.name}
                **Server Member Count:** {guild.member_count}
                **Server Creation Date:** {format_dt(guild.created_at, style="F")}
                **Owner:** {guild.owner.mention}
                **Text Channel Count:** {len(guild.text_channels)},
                **Voice Channel Count:** {len(guild.voice_channels)}
                **Role Count:** {len(guild.roles)}
                **Verification Level:** {vlevel_dict.get(guild.verification_level)}
                **Nitro Boost Level:** {boost_dict.get(guild.premium_tier)}
            """,
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
            description=f"""
                **Bot Name:** {self.bot.user.name}
                **Server Count:** {len(self.bot.guilds)}
                **Account Creation Date:** {format_dt(self.bot.user.created_at, style="F")}
                **Owner:** NatFletch
                **Latency:** {round(self.bot.latency * 1000)}ms,
                **CPU Usage:** {round(load15 / os.cpu_count() * 100)}%,
                **Memory:** {round(psutil.virtual_memory()[3] / 1000000000, 2)} gb / {round(psutil.virtual_memory()[0] / 1000000000, 2)} gb
            """,
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
