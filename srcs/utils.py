import discord

from datetime import timedelta
from pytube import Search


class Colors:
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def get_list_videos(message):
    result_list = []
    url = "https://www.youtube.com/watch?v="

    s = Search(message)

    for i in range(5):
        tmp_dct = {}
        tmp_dct["choice"] = i + 1
        tmp_dct["title"] = s.results[i].title
        tmp_dct["author"] = s.results[i].author
        try:
            tmp_dct["length"] = str(
                timedelta(
                    seconds=int(s.results[i].vid_info["videoDetails"]["lengthSeconds"])
                )
            )
        except KeyError:
            print({Colors.RED} + "Error in gettings 5 videos.", {Colors.END})
            return 1
        tmp_dct["url"] = url + s.results[i].vid_info["videoDetails"]["videoId"]
        result_list.append(tmp_dct)

    return result_list


def create_embed(colour, title, author, url, description):
    embed = discord.Embed(
        colour=colour,
        title=title,
        description=description,
    )

    embed.set_author(name=author)
    embed.set_image(url=url)

    return embed