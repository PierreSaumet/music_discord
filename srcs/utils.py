import discord

from datetime import timedelta
from random import randrange

from pytube import Search


class Colors:
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    WARNING = "\033[93m"
    END = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def get_list_videos_info(message):
    result_list = []
    url = "https://www.youtube.com/watch?v="

    s = Search(message)

    NUM_RESULTS = 10

    i = 0
    while len(result_list) < 5 and i < NUM_RESULTS:
        if (
            "videoDetails" in s.results[i].vid_info
            and "reelShelfRenderer" not in s.results[i].vid_info["videoDetails"]
        ):
            tmp_dct = {}
            tmp_dct["choice"] = len(result_list) + 1
            tmp_dct["title"] = s.results[i].title
            tmp_dct["author"] = s.results[i].author
            tmp_dct["thumb"] = s.results[i].thumbnail_url
            tmp_dct["url"] = url + s.results[i].vid_info["videoDetails"]["videoId"]

            try:
                tmp_dct["length"] = str(
                    timedelta(
                        seconds=int(
                            s.results[i].vid_info["videoDetails"]["lengthSeconds"]
                        )
                    )
                )
            except KeyError:
                tmp_dct["length"] = "error_length"

            result_list.append(tmp_dct)

    return result_list


def create_embed(colour, title, author, url, description, length=None):
    embed = discord.Embed(
        colour=colour,
        title=title,
        description=description,
    )

    embed.set_author(name=author)
    if url:
        embed.set_image(url=url)
    if length:
        embed.set_footer(text=length)

    return embed


async def cleanup_msgs(msgs_to_del):
    for item in msgs_to_del:
        await item[0].delete()
    return


async def choose_hello_msg():
    hello_files = {
        0: "srcs/mp3/hello_en.mp3",
        1: "srcs/mp3/hello_es.mp3",
        2: "srcs/mp3/hello_fr.mp3",
        3: "srcs/mp3/hello_pt.mp3",
        4: "srcs/mp3/hello_zh-CN.mp3",
    }
    nbr = randrange(0, 5)
    return hello_files[nbr]


def convert_int_to_hour(integer):
    hours = integer // 60
    minutes = integer % 60
    return "{:02d}:{:02d}".format(hours, minutes)


def parse_query_historic(msg):
    if msg.startswith("num="):
        num_str = msg[4:]
        if num_str.isnumeric():
            return num_str, None
    elif msg.startswith("user="):
        user_str = msg[5:]
        if user_str.isalpha():
            return None, user_str
    return None, None


def parse_messages_historics(msg_one, msg_two):
    num_one, user_one = parse_query_historic(msg_one)
    num_two, user_two = parse_query_historic(msg_two)

    if num_one is None and user_one is None:
        return None, None
    elif num_two is None and user_two is None:
        return None, None
    elif num_one and num_two:
        return None, None
    elif user_one and user_two:
        return None, None
    elif num_one and user_two:
        return num_one, user_two
    elif num_two and user_one:
        return num_two, user_one
    else:
        return None, None
