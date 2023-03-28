import discord
import time
import yt_dlp

from discord.ext import commands
from random import randrange

from srcs.utils import create_embed


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_connected = False
        self.ffmpeg_options = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -probesize 200M",
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
            "source_address": "0.0.0.0",  # bind to ipv4 since ipv6 addresses cause issues sometimes
        }

    @commands.command(
        name="join", help="This commands make the bot join the voice channel."
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

        nbr = randrange(0, 5)
        if nbr == 0:
            hello_mp3 = "srcs/mp3/hello_en.mp3"
        elif nbr == 1:
            hello_mp3 = "srcs/mp3/hello_es.mp3"
        elif nbr == 2:
            hello_mp3 = "srcs/mp3/hello_fr.mp3"
        elif nbr == 3:
            hello_mp3 = "srcs/mp3/hello_pt.mp3"
        else:
            hello_mp3 = "srcs/mp3/hello_zh-CN.mp3"

        voice_client = ctx.message.guild.voice_client
        try:
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(hello_mp3))
            voice_client.play(
                source, after=lambda e: print(f"Player error: {e}") if e else None
            )
        except:
            await ctx.send("The bot cannot say hello.")

    @commands.command(
        name="leave", help="This command makes the bot leave the voie channel."
    )
    async def leave(self, ctx):
        voice_client = ctx.message.guild.voice_client

        if self.is_connected and voice_client.is_connected():
            await ctx.send("Good bye!")
            self.is_connected = False
            await voice_client.disconnect()
            return

        await ctx.send("The bot is not connected to a voice channel.")

    @commands.command(name="pause", help="This command pauses the current stream.")
    async def pause(self, ctx):
        voice_client = ctx.message.guild.voice_client

        if self.is_connected and voice_client.is_playing():
            voice_client.pause()
            return

        await ctx.send("The bot is not playing anything.")

    @commands.command(name="resume", help="This command resumes the current stream.")
    async def resume(self, ctx):
        voice_client = ctx.message.guild.voice_client

        if self.is_connected and voice_client.is_paused():
            voice_client.resume()
            return

        await ctx.send("The bot was not playing anything.")

    @commands.command(name="stop", help="This command stops the current stream")
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

        # Case of Youtube Url with/without nbr of repeatition
        if (
            len(msg) == 2
            and len(msg[1]) > len(youtube_url)
            and msg[1][0 : len(youtube_url)] == youtube_url
        ):

            await ctx.message.delete()
            await self.read_from_url(ctx, msg[1])
            return

        # choose between 5 musics
        try:
            async with ctx.typing():
                with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                    data = ydl.extract_info(msg[1], download=False)
                    url = data["url"]
                voice_client.play(discord.FFmpegPCMAudio(url, **self.ffmpeg_options))

            await ctx.send("**Now playing:** {}".format("test"))
        except:
            await ctx.send("**ERROR, please try again**")

    async def read_from_url(self, ctx, url):
        voice_client = ctx.message.guild.voice_client

        try:
            async with ctx.typing():
                with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                    data = ydl.extract_info(url, download=False)
                    new_url = data["url"]
                voice_client.play(
                    discord.FFmpegPCMAudio(new_url, **self.ffmpeg_options)
                )

            embed = create_embed(
                discord.Color.fuchsia(),
                "**{}**".format(data["title"]),
                "Now playing:",
                data["thumbnail"],
                "{}\n From YouTube with Love <3.".format(url),
            )
            await ctx.send(embed=embed)
        except:
            await ctx.send("**ERROR, please try again**")
