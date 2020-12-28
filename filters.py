from aiogram import types

__all__ = [
    'is_private_message',
    'is_user_admin',
    'is_command',
    'is_private_command',
    'is_private_admin_message',
    'is_bang_command',
    'is_handled_chat',
    'is_banned',
    'is_user_allowed_to_add'
]


def is_private_message(message: types.Message):
    return message['from'].id == message.chat.id


def is_user_admin(message: types.Message, admins: list):
    # TODO query db for user status
    return message['from'].id in admins


def is_command(message: types.Message, command: str):
    return message.is_command() and message.get_command().startswith(f'/{command}')


def is_private_command(message: types.Message, command: str):
    return is_private_message(message) and is_command(message, command)


def is_private_admin_message(message: types.Message, admins: list):
    return is_user_admin(message, admins) and is_private_message(message)


def is_bang_command(message: types.Message, command: str):
    return message.text.startswith(f'!{command}')


def is_handled_chat(message: types.Message, handled_chats: list):
    return message.chat.id in handled_chats


def is_banned(message: types.Message, banned_users: list):
    return message['from'].id in banned_users


def is_user_allowed_to_add(message: types.Message, allowed_to_add: list):
    return message['from'].id in allowed_to_add
