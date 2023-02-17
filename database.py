import psycopg2
from history_item import HistoryItem


class Database:
    dbname = 'semantle'
    user = 'postgres'
    password = 'postgres'
    host = 'localhost'

    def connect(self):
        return psycopg2.connect(dbname=self.dbname,
                                user=self.user,
                                password=self.password,
                                host=self.host)

    def add_history(self, history_item: HistoryItem):
        connection = self.connect()
        cursor = connection.cursor()
        cursor.execute(
            'INSERT INTO history (login, word, guesses, start_timestamp, finish_timestamp) VALUES (\'%s\', \'%s\', \'%s\', %s, %s)',
            (
                history_item.login,
                history_item.word,
                history_item.guesses,
                history_item.start_timestamp,
                history_item.finish_timestamp,
            ))
