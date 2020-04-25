import dataset
import random


class QuoteDB:
    def __init__(self, path='quotes.db'):
        self.db = dataset.connect(f'sqlite:///{path}')
        self.quotes: dataset.table.Table = self.db['quote']
        self.max = self.db.query('SELECT MAX(id) as max FROM quote').next()['max']

    def add(self, quote):
        self.quotes.insert(quote)

    @property
    def quote(self):
        self.max += 1
        return self.quotes.find_one(id={'>=': random.randint(1, self.max - 1)}).values()
