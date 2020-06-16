import dataset


class BotAuth:
    def __init__(self, path='quotes.db'):
        # TODO store active permits in memory
        self.db = dataset.connect(f'sqlite:///{path}')
        self.authorized: dataset.table.Table = self.db['tg_user']
        self.permits: dataset.table.Table = self.db['tg_permits']
        self.user_permit_map: dataset.table.Table = self.db['tg_user_permits']
        self.base_permits = list(self.permits.find(title=['post links', 'post media']))

    def bot_user_exists(self, tg_user):
        return bool(list(self.authorized.find(tg_id=tg_user.id)))

    def register_tg_user(self, tg_user):
        if self.bot_user_exists(tg_user):
            return False

        # TODO make bot user class
        new_bot_user = self._upsert_bot_user(tg_user)
        self._add_base_permits(new_bot_user)
        return True

    def has_permission(self, bot_user):
        if not list(self.authorized.find(tg_id=bot_user.id)):
            return False
        return bool(list(
            self.user_permit_map.find(tg_user=bot_user.id, tg_permit=[perm['id'] for perm in self.base_permits])
        ))

    def _upsert_bot_user(self, user):
        new_bot_user = {
            'tg_id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }
        self.authorized.upsert(new_bot_user, ['tg_id'])
        return new_bot_user

    def _add_base_permits(self, new_bot_user):
        for perm in self.base_permits:
            self.user_permit_map.upsert({
                'tg_user': new_bot_user['tg_id'],
                'tg_permit': perm['id']
            }, ['tg_user', 'tg_permit'])
