import discord
import random
import psutil
import json
import inspect
from discord.ext import commands
from datetime import datetime
from discord.ext.commands.cooldowns import BucketType
from utils.naoko_paginator import NaokoPaginator
from checks.naoko_checks import *
from urllib.parse import quote
from humanize import naturaltime as ptime


class Commands:
    """Naoko Default Commands"""

    def __init__(self, bot):
        self.bot = bot
        self.thumbnail = "https://i.imgur.com/NkWHdwf.png"

    def cleanup_code(self, content):
        if content.startswith("```") and content.endswith("```"):
            return "\n".join(content.split("\n")[1:-1])
        return content.strip("` \n")

    async def category_gen(self, ctx):
        categories = {}

        for command in set(ctx.bot.walk_commands()):
            try:
                if command.category not in categories:
                    categories.update({command.category: []})
            except AttributeError:
                cog = command.cog_name or "Bot"
                if command.cog_name not in categories:
                    categories.update({cog: []})

        for command in set(ctx.bot.walk_commands()):
            if not command.hidden:
                try:
                    if command.category:
                        categories[command.category].append(command)
                except AttributeError:
                    cog = command.cog_name or "Bot"
                    categories[cog].append(command)

        return categories

    async def commandMapper(self, ctx):
        pages = []

        for category, commands in (await self.category_gen(ctx)).items():
            if not commands:
                continue
            cog = ctx.bot.get_cog(category)
            if cog:

                try:
                    thumbnail = (
                        cog.thumbnail
                        if cog.thumbnail
                        else "https://i.imgur.com/SDYOTER.png"
                    )
                except BaseException:
                    pass

                category = f"**<:cog:472833323937300480> {category}**\n*<:pointer:472836108556697611> {inspect.getdoc(cog)}*"
            commands = ", ".join([c.qualified_name for c in commands])
            embed = (
                discord.Embed(
                    color=random.randint(
                        0x000000,
                        0xFFFFFF),
                    title=f"{ctx.bot.user.display_name} Commands",
                    description=f"{category}",
                ) .set_footer(
                    text=f"Type {ctx.prefix}help <command> for more help".replace(
                        ctx.me.mention,
                        "@Naoko "),
                    icon_url=ctx.author.avatar_url,
                ) .add_field(
                    name="**Commands:**",
                    value=f"``{commands}``") .set_thumbnail(
                    url=thumbnail))
            pages.append(embed)
        await NaokoPaginator(
            extras=sorted(pages, key=lambda d: d.description)
        ).paginate(ctx)

    async def cogMapper(self, ctx, entity, cogname: str):
        try:
            await ctx.send(
                embed=discord.Embed(
                    color=random.randint(0x000000, 0xFFFFFF),
                    title=f"{ctx.bot.user.display_name} Commands",
                    description=f"**<:cog:472833323937300480> {cogname}**\n*<:pointer:472836108556697611> {inspect.getdoc(entity)}*",
                )
                .add_field(
                    name="**Commands:**",
                    value=f"``{', '.join([c.qualified_name for c in set(ctx.bot.walk_commands()) if c.cog_name == cogname])}``",
                )
                .set_footer(
                    text=f"Type {ctx.prefix}help <command> for more help".replace(
                        ctx.me.mention, "@Naoko "
                    ),
                    icon_url=ctx.author.avatar_url,
                )
                .set_thumbnail(
                    url=entity.thumbnail
                    if entity.thumbnail
                    else "https://i.imgur.com/SDYOTER.png"
                )
            )
        except BaseException:
            await ctx.send(
                f":x: | **Command or category not found. Use {ctx.prefix}help**",
                delete_after=10,
            )

    @commands.command(aliases=["commands"])
    async def help(self, ctx, *, command: str = None):
        """View Bot Help Menu"""
        if not command:
            await self.commandMapper(ctx)
        else:
            entity = self.bot.get_cog(command) or self.bot.get_command(command)
            if entity is None:
                return await ctx.send(
                    f":x: | **Command or category not found. Use {ctx.prefix}help**",
                    delete_after=10,
                )
            elif isinstance(entity, commands.Command):
                await NaokoPaginator(
                    title=f"Command: {entity.name}",
                    entries=[
                        f"**:bulb: Command Help**\n```ini\n[{entity.help}]```",
                        f"**:video_game: Command Signature**\n```ini\n{entity.signature}```",
                    ],
                    length=1,
                    colour=random.randint(0x000000, 0xFFFFFF),
                ).paginate(ctx)
            else:
                await self.cogMapper(ctx, entity, command)

    @commands.command(aliases=["hello", "hola", "bonjour", "privet"])
    async def hi(self, ctx):
        """ Say hi to Naoko """
        await ctx.send(f"<a:partyblob:460839733560344587> Hey, {ctx.author.mention}!")

    @commands.command(aliases=["prefixes"])
    @commands.guild_only()
    async def prefix(self, ctx):
        """Show custom guild prefix or default one."""
        if ctx.guild.id in self.bot.all_prefixes:
            await ctx.send(
                embed=discord.Embed(
                    color=random.randint(0x000000, 0xFFFFFF),
                    timestamp=ctx.message.created_at,
                )
                .add_field(
                    name="**✍ Prefix**",
                    value=f":zap: The prefix for this server is: `{self.bot.all_prefixes[ctx.guild.id]}`\n:exclamation: When using commands, this will be look like: `{self.bot.all_prefixes[ctx.guild.id]}help`",
                )
                .set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            )
        else:
            await ctx.send(
                embed=discord.Embed(
                    color=random.randint(0x000000, 0xFFFFFF),
                    timestamp=ctx.message.created_at,
                )
                .add_field(
                    name="**✍ Prefix**",
                    value=f":zap: The prefix for this server is: `@{self.bot.user.name}` or `n.`\n:exclamation: When using commands, this will be look like: `@{self.bot.user.name} help` or `n.help`",
                )
                .set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            )

    @commands.command()
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def upvote(self, ctx):
        """Upvote me for a big thanks!"""
        await ctx.send(
            embed=discord.Embed(
                color=random.randint(0x000000, 0xFFFFFF),
                timestamp=ctx.message.created_at,
                title="Upvote me for a big thanks!",
                url="https://discordbots.org/bot/444950506234707978/vote",
            )
            .set_image(
                url="https://discordbots.org/api/widget/444950506234707978.png?topcolor=D896FF&datacolor=823ed6&highlightcolor=D896FF&labelcolor=5d2f77&certifiedcolor=9c4cff"
            )
            .set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
        )

    @commands.command()
    @commands.cooldown(1.0, 30.0, commands.BucketType.user)
    async def about(self, ctx):
        """ Gives you bot's stats """
        delta_uptime = datetime.utcnow() - self.bot.launch_time
        (hours, remainder) = divmod(int(delta_uptime.total_seconds()), 3600)
        (minutes, seconds) = divmod(remainder, 60)
        (days, hours) = divmod(hours, 24)
        await ctx.send(
            embed=discord.Embed(
                color=random.randint(0x000000, 0xFFFFFF),
                timestamp=ctx.message.created_at,
            )
            .set_image(
                url="https://discordbots.org/api/widget/444950506234707978.png?topcolor=D896FF&datacolor=823ed6&highlightcolor=D896FF&labelcolor=5d2f77&certifiedcolor=9c4cff"
            )
            .add_field(
                name=":bar_chart: Naoko Statistics",
                value=f"**[Support Guild](https://discord.gg/y3Ph9Nj) | [Patreon](https://www.patreon.com/f4stz4p) | [Invite](https://discordapp.com/oauth2/authorize?client_id=444950506234707978&permissions=8&scope=bot) | [GitHub](https://github.com/NaokoDiscordBot/Naoko) | [Upvote](https://discordbots.org/bot/444950506234707978/vote)**\n\n<:online:452823889177870336> Alive for: **{days}D, {hours}H, {minutes}M, {seconds}S**\n:information_source: Latest update:\n```ini\n{self.bot.stat}```",
            )
            .set_footer(
                text=f"Bringing fun to Discord since {ptime(ctx.me.created_at)} | {ctx.author}",
                icon_url=ctx.author.avatar_url,
            )
        )

    @commands.command(aliases=["sandbox", "run"])
    @commands.cooldown(1.0, 10.0, commands.BucketType.user)
    async def python(self, ctx, *, code: commands.clean_content):
        """Runs a piece of code"""
        async with ctx.typing():
            async with self.bot.session.post(
                "http://coliru.stacked-crooked.com/compile",
                data=json.dumps(
                    {"cmd": "python3 main.cpp", "src": self.cleanup_code(code)}
                ),
            ) as resp:
                if resp.status != 200:
                    await ctx.send(":stopwatch: | **Timed out**", delete_after=5)

                else:
                    output = await resp.text(encoding="utf-8")

                    if len(output) < 1500:
                        await ctx.send(
                            embed=discord.Embed(
                                title="Python Sandbox",
                                description=f"```python\n{output}\n```",
                                color=random.randint(0x000000, 0xFFFFFF),
                                timestamp=ctx.message.created_at,
                            )
                            .set_thumbnail(url="http://i.imgur.com/9EftiVK.png")
                            .set_footer(
                                text="Interpreted at:", icon_url=ctx.author.avatar_url
                            )
                        )

                    else:
                        await ctx.send(
                            ":warning: | **Output too long**", delete_after=5
                        )

    @commands.command(aliases=["calc"])
    @commands.cooldown(1.0, 10.0, commands.BucketType.user)
    async def calculator(self, ctx, *, expression: str):
        """Calculate an expression"""
        async with ctx.typing():
            async with self.bot.session.get(
                f"https://www.calcatraz.com/calculator/api?c={quote(expression)}"
            ) as resp:
                if resp.status == 200:
                    resp = await resp.text(encoding="utf-8")
                    await ctx.send(
                        embed=discord.Embed(
                            color=random.randint(0x000000, 0xFFFFFF),
                            title="Calculator",
                            description=f"```fix\n{str(resp.capitalize())}```",
                            timestamp=ctx.message.created_at,
                        )
                        .set_thumbnail(url="https://i.imgur.com/HaH7nL3.png")
                        .set_footer(text="Solved at:", icon_url=ctx.author.avatar_url)
                    )
                else:
                    await ctx.send(
                        ":warning: | **An error has occured. Check your expression**",
                        delete_after=5,
                    )

    @commands.command()
    @commands.cooldown(1.0, 3.0, commands.BucketType.user)
    async def quote(self, ctx, *, messageid: int):
        """
        Quotes a person
        n.quote <your message id>
        """
        try:
            m = await ctx.channel.get_message(messageid)
        except BaseException:
            await ctx.send(
                "<:Error:501773759217401856> | **Message not found**", delete_after=5
            )
        else:
            await ctx.send(
                embed=discord.Embed(
                    color=random.randint(0x000000, 0xFFFFFF),
                    title=f"Quote - @{m.author.name} said in #{ctx.channel.name}",
                    description=m.clean_content if m.clean_content is not "" else "...",
                    url=m.jump_url,
                    timestamp=ctx.message.created_at,
                )
                .set_footer(
                    icon_url=ctx.author.avatar_url, text=f"Quoted by {ctx.author.name}"
                )
                .set_thumbnail(url=m.author.avatar_url)
            )

    @commands.command()
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def source(self, ctx):
        """
        Shows my source code
        """
        await ctx.send(
            embed=discord.Embed(
                timestamp=ctx.message.created_at,
                title="Source Code",
                url="https://github.com/NaokoDiscordBot/Naoko",
                color=random.randint(0x000000, 0xFFFFFF),
                description=f"""
I am **created** in <:python:526512892153954324> with :heart:, using:

:yellow_heart: [discord.py 1.0.0a](https://github.com/Rapptz/discord.py/tree/rewrite)
:bookmark: [asyncpg](https://github.com/MagicStack/asyncpg)
:musical_note: [aqualink](https://github.com/nanipy/aqualink)
:spider_web: [Quart](https://github.com/pgjones/quart)

:gear: And **many** other **[Python Libraries](https://pypi.org/)**...
"""
            )
            .set_thumbnail(url="https://i.imgur.com/46eHxTO.png")
            .set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        )

    @commands.command(aliases=["ss", "webscreen", "capture"])
    @nsfw()
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def snapshot(self, ctx, *, website: str):
        """
        Capture a website
        Example: n.snapshot google.com
        """
        async with ctx.typing():
            async with self.bot.session.post(
                "http://magmachain.herokuapp.com/api/v1",
                headers={"website": website}
            ) as r:
                try:
                    response = await r.json()
                    await ctx.send(
                        embed=discord.Embed(
                            color=random.randint(0x000000, 0xFFFFFF),
                            title=website,
                            url=response["website"],
                            timestamp=ctx.message.created_at
                        )

                        .set_image(
                            url=response["snapshot"]
                        )

                        .set_footer(
                            text=f"Snapshotted by {ctx.author.name} | Content above is user-generated",
                            icon_url=ctx.author.avatar_url
                        )

                    )

                except BaseException:
                    await ctx.send(
                        "<:Error:501773759217401856> | **Failed to snapshot. Check your URL or try again**",
                        delete_after=5
                    )


def setup(bot):
    bot.add_cog(Commands(bot))
