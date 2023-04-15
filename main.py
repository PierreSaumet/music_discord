import discord
import os

from discord.ext import commands
from dotenv import load_dotenv

from srcs.music import Music
from srcs.utils import Colors
from srcs.users_db import UsersDatabase
from srcs.historic_db import MusicHistoric

load_dotenv()


class ETCDiscordBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())
        self.is_debug = False
        self.users_db = UsersDatabase()
        self.historic_db = MusicHistoric()

        self.test = "test"

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

        # Init all Databases
        self.users_db.creates_tables_if_not_exists()
        self.users_db.insert_users(users_list)
        self.historic_db.creates_tables_if_not_exists()

    async def add_all_cog(self):
        await self.add_cog(Music(self, self.historic_db))


if __name__ == "__main__":
    intents = discord.Intents().all()
    client = discord.Client(intents=intents)
    ETC_bot = ETCDiscordBot()
    ETC_bot.run(os.getenv("DISCORD_TOKEN"))
