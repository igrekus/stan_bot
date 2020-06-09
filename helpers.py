from aiogram import types

__all__ = [
    'has_reply',
    'parse_bang_command'
]


def has_reply(message: types.Message):
    return bool(message['reply_to_message'])


def parse_bang_command(message: types.Message):
    reply = message['reply_to_message']
    args = message.text.lstrip("!lmgtfy")

    if reply:
        if not args:
            args = message.reply_to_message.text
        id_ = message.reply_to_message.message_id
    else:
        id_ = message.message_id

    return id_, args.strip()
