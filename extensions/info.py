import discord
import time
from discord.ext import commands
from discord_timestamps import format_timestamp as format_time
from discord_timestamps import TimestampType
from conf import embed_color

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(aliases=["uinfo", "ui", "user-info"])
    async def userinfo(self, ctx: commands.Context, member = None) -> None:
        """Fetches info for a given user or on yourself"""
        if not member: member = ctx.author
        
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
                **Account Creation Date:** {format_time(time.mktime(member.created_at.timetuple()), TimestampType.LONG_DATE)}
                **Server Join Date:** {format_time(time.mktime(member.joined_at.timetuple()), TimestampType.LONG_DATE)}
                **Join Position:** {sorted(ctx.guild.members, key=lambda member: member.joined_at).index(member) + 1}
                **Status:** {status_dict[member.status]}
                **Top Role:** {member.top_role.mention}
                **Roles:** {" ".join([role.mention for role in member.roles if role != ctx.guild.default_role])}
            """,
            color=member.accent_color
        )
        embed.set_author(name=member.name, icon_url=member.avatar.with_format("png"))
        embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar.with_format("png"))
        embed.set_thumbnail(url=member.avatar.with_format("png"))
        await ctx.send(embed=embed)

    @commands.hybrid_command(aliases=["sinfo"])
    async def serverinfo(self, ctx: commands.Context, server=None):
        if not server: server = ctx.server



async def setup(bot):
    await bot.add_cog(Info(bot))    

