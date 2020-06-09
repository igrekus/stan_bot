from aiogram import types

__all__ = [
    'has_reply',
    'parse_bang_command',
    'user_link'
]


def has_reply(message: types.Message):
    return bool(message['reply_to_message'])


def parse_bang_command(message: types.Message, command: str):
    args = message.text.lstrip(f'!{command}')

    if has_reply(message):
        if not args:
            args = message.reply_to_message.text
        id_ = message.reply_to_message.message_id
    else:
        id_ = message.message_id

    return has_reply(message), id_, args.strip()


def user_link(message: types.Message):
    name = f'@{message.from_user.username}'
    if name == '@None':
        name = f'{message.from_user.first_name}'
    return name
