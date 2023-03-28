import discord
import os

from discord.ext import commands,tasks
from dotenv import load_dotenv

from srcs.music import Music
from srcs.utils import Colors

load_dotenv()

class ETCDiscordBot(commands.Bot):
    
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())
        self.is_debug = False

    async def on_ready(self):
        users_list = []

        for user in self.users:
            users_list.append([user.name, user.id])

        message = f"""
        ------------------------------------------------------
        {Colors.RED}    E.T.C is ready to rock! {Colors.END}

                - name: {Colors.RED}{self.user.name}{Colors.END},
                - id: {self.user.id},
                - status: {Colors.GREEN}{self.status}{Colors.END},
                - debug: {self.is_debug},
                - users list: {users_list}.\n
        ------------------------------------------------------
        """
        await self.add_all_cog()
        print(message)

    async def add_all_cog(self):
        await self.add_cog(Music(self))
        print("add all cog done")


if __name__ == "__main__":
    intents = discord.Intents().all()
    client = discord.Client(intents=intents)
    ETC_bot = ETCDiscordBot()
    ETC_bot.run(os.getenv("DISCORD_TOKEN"))