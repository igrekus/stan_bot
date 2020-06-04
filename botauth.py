import dataset


class BotAuth:
    def __init__(self, path='quotes.db'):
        self.db = dataset.connect(f'sqlite:///{path}')
        self.authorized: dataset.table.Table = self.db['auth']

    def register_user(self, user):
        print(user)
        # self.authorized.insert(user)
