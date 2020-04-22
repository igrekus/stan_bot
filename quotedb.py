import dataset
import random


class QuoteDB:
    def __init__(self, path='quotes.db'):
        self.db = dataset.connect(f'sqlite:///{path}')
        self.quotes = self.db['quote']
        self.max = self.db.query('SELECT MAX(id) as max FROM quote').next()['max']

    @property
    def quote(self):
        return self.quotes.find_one(id={'>=': random.randint(1, self.max)}).values()
