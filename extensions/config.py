import discord
from discord.ext import commands
from conf import embed_color


class ConfigHelper:
    def __init__(self, bot):
        self.bot = bot

    async def set_suggestion_channel(self, guild_id, channel_id):
        db_client = await self.bot.fetch_db_client()
        if await db_client.fetchrow("SELECT * FROM suggestion_channels WHERE guild_id = $1", guild_id) is not None:
            return await db_client.execute("UPDATE suggestion_channels SET channel_id = $1 WHERE guild_id = $2", channel_id, guild_id)
        await db_client.execute("INSERT INTO suggestion_channels (guild_id, channel_id) VALUES ($1, $2)", guild_id, channel_id)

    async def set_staff_role(self, guild_id, role_id):
        db_client = await self.bot.fetch_db_client()
        if await db_client.fetchrow("SELECT * FROM staff_roles WHERE guild_id = $1", guild_id) is not None:
            return await db_client.execute("UPDATE staff_roles SET role_id = $1 WHERE guild_id = $2", role_id, guild_id)
        await db_client.execute("INSERT INTO staff_roles (guild_id, role_id) VALUES ($1, $2)", guild_id, role_id)


def check_if_owner():
    async def predicate(ctx):
        if ctx.author.id == ctx.guild.owner.id:
            return True
        if ctx.author.id in ctx.bot.owner_ids:
            return True
        return False
    return commands.check(predicate)


class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.chelper = ConfigHelper(self.bot)

    @commands.hybrid_command(aliases=["conf", "configure", "settings"], usage="[setting] <option>")
    @commands.guild_only()
    @check_if_owner()
    async def config(self, ctx, setting: str = commands.parameter(default=None, description="The setting you would like to change"), option: str = commands.parameter(default=None, description="The option for the specific setting")):
        """Command to change server settings"""
        if setting == "settings.suggestions.suggestion_channel":
            converted = await commands.TextChannelConverter().convert(ctx, option)
            option = converted.id
            await self.chelper.set_suggestion_channel(ctx.guild.id, option)
            await ctx.send(f"You have successfully set the suggestions channel to {converted.mention}!")
        elif setting == "settings.meta.staff_role":
            converted = await commands.RoleConverter().convert(ctx, option)
            option = converted.id
            await self.chelper.set_staff_role(ctx.guild.id, option)
            await ctx.send(f"You have successfully set the staff role to {converted.mention}!", allowed_mentions=discord.AllowedMentions.none())
        else:
            await ctx.send(
                f"""Unfortunately, I do not recognize {setting}. The allowed settings there are would be:
                -> settings.meta.staff_role <role>
                -> settings.meta.admin_role <role>
                -> settings.suggestions.suggestion_channel <channel>
                """)


async def setup(bot):
    await bot.add_cog(Config(bot))
