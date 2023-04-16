import os
import sqlite3

from sqlite3 import Error
from dotenv import load_dotenv

from contextlib import closing

load_dotenv()


class UsersDatabase:
    def __init__(self):
        self.users_db = os.getenv("DB_USERS_PATH") + "users.db"
        self.connexion = None
        self.cursor = None

    def get_connexion_and_cursor(self):
        self.connexion = sqlite3.connect(self.users_db)
        self.cursor = self.connexion.cursor()

    def creates_tables_if_not_exists(self):
        self.get_connexion_and_cursor()

        self.connexion.execute(
            """CREATE TABLE IF NOT EXISTS USERS_DISCORD
            (ID         INTEGER     PRIMARY_KEY,
            DISCORD_ID         INTEGER     NOT NULL UNIQUE,
            NAME            TEXT            NOT NULL UNIQUE);"""
        )

        self.connexion.close()

    def insert_users(self, users_list):
        for item in users_list:
            act = f"INSERT OR IGNORE INTO USERS_DISCORD (DISCORD_ID,NAME) VALUES (?, ?)"

            try:
                with closing(sqlite3.connect(self.users_db)) as conn:
                    with closing(conn.cursor()) as cursor:
                        ret = cursor.execute(act, (item[1], str(item[0])))
                        conn.commit()
            except Error as e:
                raise Exception("Error with the database: ", e)

    def display_users(self):
        act = f"SELECT NAME FROM USERS_DISCORD"

        self.get_connexion_and_cursor()
        self.cursor = self.connexion.execute(act)

        rows = self.cursor.fetchall()
        for row in rows:
            print("user = ", row)

        self.connexion.close()
        return len(rows)

    def find_id_by_name(self, username):
        action = f"SELECT DISCORD_ID FROM USERS_DISCORD WHERE NAME = {username}"

        self.get_connexion_and_cursor()
        self.cursor = self.connexion.execute(action)

        discord_id = self.cursor.fetchone()

        self.connexion.close()
        if discord_id is None:
            return []

        return discord_id

    def check_table(self):
        self.get_connexion_and_cursor()

        users_table = self.connexion.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='USERS_DISCORD'"
        ).fetchall()

        self.connexion.close()

        if users_table:
            return True
        return False
