from aiogram import types

__all__ = [
    'is_private_message',
    'is_user_admin',
    'is_command',
    'is_private_command',
    'is_private_admin_message',
]


def is_private_message(message: types.Message):
    return message['from'].id == message.chat.id


def is_user_admin(message: types.Message, admins: list):
    return message.chat.id in admins


def is_command(message: types.Message, command):
    return message.is_command() and message.get_command().startswith(f'{command}')


def is_private_command(message: types.Message, command: str):
    return is_private_message(message) and is_command(message, command)


def is_private_admin_message(message: types.Message, admins):
    return is_user_admin(message, admins) and is_private_message(message)
