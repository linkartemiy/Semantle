import psycopg2
from contextlib import closing
from history_item import HistoryItem
import os
from dotenv import load_dotenv

load_dotenv()


class Database:
    dbname = os.getenv('POSTGRES_DB')
    user = os.getenv('POSTGRES_USER')
    password = os.getenv('POSTGRES_PASSWORD')
    host = os.getenv('POSTGRES_SERVER')
    port = os.getenv('POSTGRES_PORT')

    def __init__(self):
        self.create_history()

    def connect(self):
        return psycopg2.connect(dbname=self.dbname,
                                user=self.user,
                                password=self.password,
                                host=self.host,
                                port=self.port)

    def add_history(self, history_item: HistoryItem):
        with closing(self.connect()) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    'INSERT INTO history (login, word, guesses, start_timestamp, finish_timestamp) VALUES (\''
                    + history_item.login + '\', \'' + history_item.word +
                    '\', \'' + ','.join(history_item.guesses) + '\', \'' +
                    str(history_item.start_timestamp) + '\', \'' +
                    str(history_item.finish_timestamp) + '\')')
            connection.commit()

    def get_history(self, login: str):
        history = []
        with closing(self.connect()) as connection:
            with connection.cursor() as cursor:
                cursor.execute('SELECT * FROM history WHERE login = \'' +
                               login + '\'')
                for row in cursor:
                    history.append(
                        HistoryItem(row[0], row[1], row[2], row[3], row[4],
                                    row[5]))
        return history

    def create_history(self):
        with closing(self.connect()) as connection:
            with connection.cursor() as cursor:
                cursor.execute('CREATE TABLE history IF NOT EXISTS (id bigserial, login varchar(255), word varchar(255), guesses text, start_timestamp timestamp, finish_timestamp timestamp)')
            connection.commit()
