import dataset


class BotAuth:
    def __init__(self, path='quotes.db'):
        self.db = dataset.connect(f'sqlite:///{path}')
        self.authorized: dataset.table.Table = self.db['tg_user']
        self.permits: dataset.table.Table = self.db['tg_permits']
        self.user_permit_map: dataset.table.Table = self.db['tg_user_permits']
        self.base_permits = list(self.permits.find(title=['post links', 'post media']))

    def register_user(self, user):
        if list(self.authorized.find(tg_id=user.id)):
            return False

        new_user = {
            'tg_id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }

        self.authorized.upsert(new_user, ['tg_id'])
        for perm in self.base_permits:
            self.user_permit_map.upsert({
                'tg_user': new_user['tg_id'],
                'tg_permit': perm['id']
            }, ['tg_user', 'tg_permit'])

        return True

    def has_permission(self, user):
        exists = list(self.authorized.find(tg_id=user.id))
        if not exists:
            return False
        has_permits = list(self.user_permit_map.find(tg_user=user.id, tg_permit=[perm['id'] for perm in self.base_permits]))
        if not has_permits:
            return False
        return True
