class HistoryItem:
    def __init__(self, id, login, word, guesses, start_timestamp,
                 finish_timestamp):
        self.id = id
        self.login = login
        self.word = word
        self.guesses = guesses
        self.start_timestamp = start_timestamp
        self.finish_timestamp = finish_timestamp