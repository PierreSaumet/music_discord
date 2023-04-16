import asyncio
import time

import discord
import yt_dlp

from discord.ext import commands

from srcs.utils import *


class Music(commands.Cog):
    def __init__(self, bot, music_historic):
        self.bot = bot
        self.is_connected = False
        self.ffmpeg_options = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 "
            "-reconnect_delay_max 5 -probesize 200M",
            "options": "-vn",
        }
        self.ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
            "quiet": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
            "restrictfilenames": True,
            "noplaylist": True,
            "nocheckcertificate": True,
            "ignoreerrors": False,
            "logtostderr": False,
            "quiet": True,
            "no_warnings": True,
            "default_search": "auto",
            "source_address": "0.0.0.0",
        }
        self.music_historic = music_historic

    @commands.command(
        name="join", help="This command makes the bot join the voice channel."
    )
    async def join(self, ctx):
        if not ctx.message.author.voice:
            await ctx.send("You are not connected to a voice channel.")
            return

        if self.is_connected:
            await ctx.send("The bot is already in a voice channel.")
            return

        channel = ctx.message.author.voice.channel

        self.is_connected = True
        await channel.connect()

        voice_client = ctx.message.guild.voice_client
        msg = await choose_hello_msg()
        try:
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(msg))
            voice_client.play(
                source, after=lambda e: print(f"Player error: {e}") if e else None
            )
        except Exception:
            await ctx.send("The bot cannot say hello.")

    @commands.command(
        name="leave", help="This command makes the bot leave the channel."
    )
    async def leave(self, ctx):
        voice_client = ctx.message.guild.voice_client

        if self.is_connected and voice_client.is_connected():
            await ctx.send("Good bye!")
            self.is_connected = False
            await voice_client.disconnect()
            return

        await ctx.send("The bot is not connected to a voice channel.")

    @commands.command(name="pause", help="This command pauses the stream.")
    async def pause(self, ctx):
        voice_client = ctx.message.guild.voice_client

        if self.is_connected and voice_client.is_playing():
            voice_client.pause()
            return

        await ctx.send("The bot is not playing anything.")

    @commands.command(name="resume", help="This command resumes the stream.")
    async def resume(self, ctx):
        voice_client = ctx.message.guild.voice_client

        if self.is_connected and voice_client.is_paused():
            voice_client.resume()
            return

        await ctx.send("The bot was not playing anything.")

    @commands.command(name="stop", help="This command stops the stream")
    async def stop(self, ctx):
        voice_client = ctx.message.guild.voice_client

        if self.is_connected and voice_client.is_playing():
            voice_client.stop()
            return

        await ctx.send("The bot is not playing anything")

    @commands.command(name="play", help="This command plays a youtube's url")
    async def play(self, ctx):
        youtube_url = "https://www.youtube.com/watch?"
        msg = ctx.message.content.split()
        voice_client = ctx.message.guild.voice_client

        if not ctx.message.author.voice:
            await ctx.send("You are not connected to a voice channel")
            return

        if not self.is_connected:
            await self.join(ctx)
            time.sleep(5)

        if len(msg) == 1:
            await ctx.send("**ERROR, please try again**")
            return

        if (
            len(msg) == 2
            and len(msg[1]) > len(youtube_url)
            and msg[1][0 : len(youtube_url)] == youtube_url
        ):

            await ctx.message.delete()
            await self.read_from_url(ctx, msg[1], True)
            return

        data = str()
        for i in range(1, len(msg)):
            data += msg[i]
            if i + 1 < len(msg):
                data += " "

        choices_lst = get_list_videos_info(data)
        if choices_lst == 1:
            await ctx.send("**ERROR, in getting videos, try again.**")
            return

        # display 5 first messages:
        msgs_to_del = list()
        for index in choices_lst:
            embed = create_embed(
                discord.Color.fuchsia(),
                "**{}**".format(index["title"]),
                "Choice: {}".format(index["choice"]),
                index["thumb"],
                "By **{0}**\n{1}".format(index["author"], index["url"]),
                "Length: {}".format(index["length"]),
            )
            tmp_msg = await ctx.send(embed=embed)
            msgs_to_del.append((tmp_msg, tmp_msg.id))

        def check(m: discord.Message):  # Checks author's choice
            if m.author != ctx.message.author:
                return False

            answers = ["0", "1", "2", "3", "4", "5"]

            for item in answers:
                if m.content == item:
                    return True
            return False

        rep = ""
        try:
            rep = await self.bot.wait_for("message", check=check, timeout=100.0)
        except asyncio.TimeoutError:
            await cleanup_msgs(msgs_to_del)
            await ctx.send("Sorry, I waited 100 secondes...")
            return

        await cleanup_msgs(msgs_to_del)
        for item in choices_lst:
            if rep.content == "0":
                await ctx.send("**For now, I can only play these songs, sorry.**")
                return
            if str(item["choice"]) == rep.content:
                embed = create_embed(
                    discord.Color.fuchsia(),
                    "**{}**".format(item["title"]),
                    "You choice: {}".format(item["choice"]),
                    item["thumb"],
                    "By **{0}**\n{1}".format(item["author"], item["url"]),
                    "Length: {}".format(item["length"]),
                )
                await ctx.send(embed=embed)
                await self.read_from_url(ctx, item["url"], False)
                return

    async def read_from_url(self, ctx, url, is_embed):
        voice_client = ctx.message.guild.voice_client

        try:
            async with ctx.typing():
                with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                    data = ydl.extract_info(url, download=False)

                    new_url = data["url"]

                    length = convert_int_to_hour(data["duration"])

                    query_hist = self.music_historic.insert_music(
                        data["uploader"], data["title"], length, url, str(ctx.author.id)
                    )
                    self.music_historic.do_query(query_hist, True)

                voice_client.play(
                    discord.FFmpegPCMAudio(new_url, **self.ffmpeg_options)
                )

            if is_embed:
                embed = create_embed(
                    discord.Color.fuchsia(),
                    "**{}**".format(data["title"]),
                    "Now playing:",
                    data["thumbnail"],
                    "{}\n From YouTube with Love <3.".format(url),
                )
                await ctx.send(embed=embed)
        except Exception:
            await ctx.send("**ERROR, please try again**")
