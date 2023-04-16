import time

import discord

from dotenv import load_dotenv
from discord.ext import commands

from srcs.utils import *

load_dotenv()


class HistoricCmds(commands.Cog):
    def __init__(self, bot, music_historic):
        self.bot = bot
        self.music_historic = music_historic

    @commands.command(
        name="hist", help="This command displays some historicsmusic query"
    )
    async def hist(self, ctx):
        """
        usage:
            1) !hist ==> display last 5 songs from the author
            2) !hist num=3 'or' user='username'
                display last 3 songs of the author or last 5 songs of the username
            3) !hist num=10 user='username'
                display last 10 songs of the given username
        """
        msg = ctx.message.content.split()
        results = []

        if len(msg) == 1:
            results = self.music_historic.get_last_five_songs(ctx.author.name)
        elif len(msg) == 2:
            num, user = parse_query_historic(msg[1])

            users_info = [
                {"id": x.id, "name": x.name, "nickname": x.nick}
                for x in ctx.guild.members
            ]

            if user:
                for item in users_info:
                    if user == item["name"] or user == item["nickname"]:
                        results = self.music_historic.get_last_five_songs(item["name"])
                        break
            if num:
                results = self.music_historic.get_songs(ctx.author.name, num)
        elif len(msg) == 3:
            num, user = parse_messages_historics(msg[1], msg[2])
            users_info = [
                {"id": x.id, "name": x.name, "nickname": x.nick}
                for x in ctx.guild.members
            ]

            if user:
                for item in users_info:
                    if user == item["name"] or user == item["nickname"]:
                        results = self.music_historic.get_songs(item["name"], num)
                        break

        else:
            await ctx.send("**ERROR, no last music for your query.**")
            return

        if len(results) == 0:
            await ctx.send("**ERROR, no last music for your query.**")
            return

        for item in results:
            embed = create_embed(
                discord.Color.fuchsia(),
                "{} listened: **{}**".format(ctx.author.name, item[2]),
                "Day: {} at {}".format(item[6], item[7]),
                None,
                "By **{0}**\n url: {1}".format(item[1], item[4]),
                "Length: {}".format(item[3]),
            )
            await ctx.send(embed=embed)
            time.sleep(2)

        return
