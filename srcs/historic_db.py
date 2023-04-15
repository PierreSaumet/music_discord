import os
import sqlite3

from sqlite3 import Error
from datetime import date, datetime
from dotenv import load_dotenv

from contextlib import closing

load_dotenv()


class MusicHistoric:
    def __init__(self):
        self.music_db = os.getenv("DB_MUSIC_PATH") + "music_historic.db"
        self.connexion = None
        self.cursor = None

    def get_connexion_and_cursor(self):
        self.connexion = sqlite3.connect(self.music_db)
        self.cursor = self.connexion.cursor()

    def creates_tables_if_not_exists(self):
        self.get_connexion_and_cursor()

        self.connexion.execute("PRAGMA foreign_keys = 1")

        self.connexion.execute(
            """CREATE TABLE IF NOT EXISTS MUSIC_HISTORY
            (ID INTEGER PRIMARY KEY,
            AUTHOR           TEXT    NOT NULL,
            TITLE           TEXT    NOT NULL,
            LENGTH           TEXT    NOT NULL,
            URL           TEXT    NOT NULL,
            DISCORD_ID       INTEGER    NOT NULL,
            DATE           TEXT    NOT NULL,
            TIME           TEXT    NOT NULL,
            FOREIGN KEY (DISCORD_ID)
                REFERENCES USERS_DB (DISCORD_ID));"""
        )

        self.connexion.close()

    def insert_music(self, author, title, length, url, discord_id) -> str:
        now = datetime.now()

        action = f"INSERT INTO MUSIC_HISTORY (AUTHOR,TITLE,LENGTH,URL,DISCORD_ID,DATE,TIME) \
            VALUES ('{author}', '{title}', '{length}', '{url}', '{discord_id}', '{date.today()}', '{now.strftime('%H:%M:%S')}')"

        return action

    def get_all_music_history(self, order, number):
        action = f"SELECT * FROM MUSIC_HISTORY"

        return action

    def do_query(self, action: str, act: bool):
        if not action:
            return False

        try:
            with closing(sqlite3.connect(self.music_db)) as conn:
                with closing(conn.cursor()) as cursor:
                    ret = cursor.execute(action)
                    if act:
                        conn.commit()
                    else:
                        return self.display(ret)
        except Error as e:
            raise Exception("Error with the database: ", e)

        return True

    def display(self, to_display):
        ret = []
        for item in to_display:
            print("item = ", item)
            ret.append(item)
        return ret
