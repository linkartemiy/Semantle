import psycopg2
from contextlib import closing
from history_item import HistoryItem


class Database:
    dbname = 'semantle'
    user = 'postgres'
    password = 'postgres'
    host = 'localhost'
    port = 5432

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
