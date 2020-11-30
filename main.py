import logging
import random
import requests

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ContentType

from middleware import rate_limit, ThrottlingMiddleware

from config import proxy, token, rules_link, engine_link, google_link, lat_rus_map, qdb, bot_admins, bot_auth, chat_alias, handled_chats, banned_users
from filters import *
from helpers import *

logging.basicConfig(level=logging.INFO)

bot = Bot(token=token, proxy=proxy)
dp = Dispatcher(bot, storage=MemoryStorage())


# TODO move logging to a middleware class: https://surik00.gitbooks.io/aiogram-lessons/content/chapter3.html

@dp.message_handler(lambda msg: is_private_command(msg, 'ban'))
async def on_private_ban(message: types.Message):
    await bot.delete_message(-1001338616632, 201690)
    # await bot.restrict_chat_member(-1001338616632, 1319784856, can_send_messages=False)


@dp.message_handler(lambda msg: is_private_command(msg, 'register'))
@rate_limit(5, 'register')
async def on_private_register(message: types.Message):
    logging.info(f'Registering user {message.from_user}')
    result = bot_auth.register_tg_user(message.from_user)
    if result:
        await bot.send_message(message.chat.id, 'записал')
    else:
        await bot.send_message(message.chat.id, 'что-то пошло не так')


@dp.message_handler(lambda msg: is_private_admin_message(msg, admins=bot_admins))
async def on_admin_private_message(message: types.Message):
    logging.info(f'private admin query: {message["from"]} - {message.text}')
    if is_command(message, 'send'):
        chat, text = message.get_args().split(sep=' ', maxsplit=1)
        chat = chat_alias.get(chat, chat)
        await bot.send_message(int(chat), text)
    elif is_bang_command(message, 'inspire'):
        url = requests.get('https://inspirobot.me/api?generate=true').text
        if not url:
            return
        img = requests.get(url).content
        if not img:
            return
        await bot.send_photo(message.chat.id, img, reply_to_message_id=message.message_id)
    elif is_bang_command(message, 'add'):
        await on_bang_add(message)


@dp.message_handler(
    lambda msg:
    is_handled_chat(msg, handled_chats) and
    is_bang_command(msg, 'add') and
    is_user_admin(msg, bot_admins)
)
@rate_limit(10)
async def on_bang_add(message: types.Message):
    logging.log(logging.INFO, f'!add from: {message["from"]} - "{message.text}"')

    is_reply, id_, args = parse_bang_command(message, 'add')
    if not args:
        return

    new_quote = {'message_id': id_, 'text': args} if is_reply else {'text': args}
    qdb.add(new_quote)
    logging.log(logging.INFO, f'Add quote "{new_quote}"')
    await message.reply(f'добавил: {new_quote["text"]}', reply=False)


@dp.message_handler(
    lambda msg:
    is_handled_chat(msg, handled_chats) and
    is_bang_command(msg, 'del') and
    is_user_admin(msg, bot_admins)
)
async def on_bang_del(message: types.Message):
    logging.log(logging.INFO, f'!del from: {message["from"]} - "{message}"')

    is_reply, id_, args = parse_bang_command(message, 'add')
    if not is_reply:
        return

    await bot.delete_message(message.chat.id, id_)
    await message.delete()


@dp.message_handler(
    lambda msg:
    is_handled_chat(msg, handled_chats) and
    not is_banned(msg, banned_users) and
    is_bang_command(msg, 'tr')
)
@rate_limit(10)
async def on_bang_tr(message: types.Message):
    if not message.reply_to_message.text:
        return
    await message.reply(message.reply_to_message.text.translate(lat_rus_map))


@dp.message_handler(
    lambda msg:
    is_handled_chat(msg, handled_chats) and
    is_bang_command(msg, 'inspire') and
    is_user_admin(msg, bot_admins)
)
@rate_limit(10)
async def on_bang_inspire(message: types.Message):
    url = requests.get('https://inspirobot.me/api?generate=true').text
    if not url:
        return
    img = requests.get(url).content
    if not img:
        return
    await message.reply_photo(img, reply=False)


@dp.message_handler(
    lambda msg:
    is_handled_chat(msg, handled_chats) and
    not is_banned(msg, banned_users) and
    is_bang_command(msg, 'lmgtfy')
)
@rate_limit(5)
async def on_bang_lmgtfy(message: types.Message):
    _, id_, args = parse_bang_command(message, 'lmgtfy')
    await bot.send_message(
        message.chat.id,
        f'{engine_link}{"+".join(args.split(" "))}',
        disable_web_page_preview=True,
        reply_to_message_id=id_
    )


@dp.message_handler(
    lambda msg:
    is_handled_chat(msg, handled_chats) and
    not is_banned(msg, banned_users) and
    is_bang_command(msg, 'g')
)
@rate_limit(5)
async def on_bang_lmgtfy(message: types.Message):
    _, id_, args = parse_bang_command(message, 'g')
    await bot.send_message(
        message.chat.id,
        f'{google_link}{"+".join(args.split(" "))}',
        disable_web_page_preview=True,
        reply_to_message_id=id_
    )


@dp.message_handler(
    lambda msg:
    is_handled_chat(msg, handled_chats) and
    not is_banned(msg, banned_users) and
    is_bang_command(msg, 'quote')
)
@rate_limit(5)
async def on_bang_quote(message: types.Message):
    # TODO send only quotes belonging to the source channel
    id_, msg_id, text = qdb.quote
    logging.info(f'Send quote id={id_} text={text}')
    if msg_id:
        await bot.forward_message(message.chat.id, message.chat.id, msg_id)
    else:
        await message.reply(text, reply=False)


@dp.message_handler(
    lambda msg:
    is_handled_chat(msg, handled_chats) and
    not is_banned(msg, banned_users) and
    (is_bang_command(msg, 'rules') or is_bang_command(msg, 'правила'))
)
@rate_limit(5)
async def on_bang_rules(message: types.Message):
    _, id_, _ = parse_bang_command(message, message.text[1:])   # TODO HACK meh
    await bot.send_message(
        message.chat.id,
        f'[сюда]({rules_link}) читай',
        parse_mode='MarkdownV2',
        disable_web_page_preview=True,
        reply_to_message_id=id_
    )


@dp.message_handler(
    lambda msg:
    is_handled_chat(msg, handled_chats) and
    not is_banned(msg, banned_users) and
    is_bang_command(msg, 'nometa')
)
@rate_limit(5)
async def on_bang_nometa(message: types.Message):
    _, id_, _ = parse_bang_command(message, 'nometa')
    await bot.send_message(
        message.chat.id,
        f'[nometa\\.xyz](http://nometa.xyz)\n[neprivet](https://neprivet.ru/)',
        parse_mode='MarkdownV2',
        disable_web_page_preview=True,
        reply_to_message_id=id_
    )


@dp.message_handler(
    lambda msg:
    is_handled_chat(msg, handled_chats) and
    not is_banned(msg, banned_users) and
    is_bang_command(msg, 'bdmtss')
)
@rate_limit(5)
async def on_bang_rimshot(message: types.Message):
    _, id_, _ = parse_bang_command(message, 'bdmtss')
    await bot.forward_message(message.chat.id, message.chat.id, 211281)


@dp.message_handler(
    lambda msg:
    is_handled_chat(msg, handled_chats) and
    not is_banned(msg, banned_users) and
    (is_bang_command(msg, 'help') or is_bang_command(msg, 'помощь') or is_bang_command(msg, 'хелп'))
)
@rate_limit(5)
async def on_bang_help(message: types.Message):
    await message.reply('''`\\!rules`, `\\!правила` \\- правила чятика
`\\!lutz`, `\\!лутц` \\- дать Лутцца
`\\!django`, `\\!джанго` \\- дать Джангца
`\\!help` \\- это сообщение
''', parse_mode='MarkdownV2', reply=False)


@dp.message_handler(
    lambda msg:
    is_handled_chat(msg, handled_chats) and
    not is_banned(msg, banned_users) and
    (is_bang_command(msg, 'lutz') or is_bang_command(msg, 'лутц'))
)
@rate_limit(5)
async def ob_bang_lutz(message: types.Message):
    await message.reply(
        f'{user_link(message if not message.reply_to_message else message.reply_to_message)} '
        f'вот, не позорься:\n'
        f'https://t.me/python_books_archive/565\n'
        f'https://t.me/pythonlib/162\n'
        f'https://t.me/python_books_archive/95',
        reply=False
    )


@dp.message_handler(
    lambda msg:
    is_handled_chat(msg, handled_chats) and
    not is_banned(msg, banned_users) and
    (is_bang_command(msg, 'django') or is_bang_command(msg, 'джанго'))
)
@rate_limit(5)
async def on_bang_django(message: types.Message):
    await message.reply(
        f'{user_link(message)} '
        f'держи, поискал за тебя: https://t.me/c/1338616632/133706',
        reply=False
    )


@dp.message_handler(
    lambda msg:
    is_handled_chat(msg, handled_chats) and
    not is_banned(msg, banned_users) and
    _is_yt_in(msg)
)
async def on_yt_mention(message: types.Message):
    await message.reply('у нас тут таких не любят')


@dp.message_handler(
    lambda msg:
    is_handled_chat(msg, handled_chats) and
    is_bang_command(msg, 'voice') and
    is_user_admin(msg, bot_admins)
)
async def on_bang_voice(message: types.Message):
    if not message.reply_to_message:
        return
    res = bot_auth.voice(message.reply_to_message.from_user)
    if res:
        await message.reply('ок', reply=False)


@dp.message_handler(
    lambda msg:
    is_handled_chat(msg, handled_chats) and
    is_bang_command(msg, 'devoice') and
    is_user_admin(msg, bot_admins)
)
async def on_bang_devoice(message: types.Message):
    if not message.reply_to_message:
        return
    res = bot_auth.devoice(message.reply_to_message.from_user)
    if res:
        await message.reply('покарано', reply=False)


def _is_yt_in(message):
    # TODO generalize for arbitrary text tokens
    lowered = message.text.lower()
    return 'хауди' in lowered or 'дудар' in lowered or 'дудь' in lowered or 'дудя' in lowered or 'хоуди' in lowered


@dp.message_handler(content_types=[ContentType.AUDIO, ContentType.DOCUMENT, ContentType.VIDEO, ContentType.VIDEO_NOTE, ContentType.VOICE, ContentType.POLL, ContentType.PHOTO])
async def on_media_post(message: types.Message):
    logging.info(f'media post: {message}')
    # await bot.send_message(289682796, f"potential spam from {message.from_user}")


@dp.message_handler(content_types=[ContentType.PINNED_MESSAGE])
async def on_pinned_message(message: types.Message):
    logging.info(f'pin message: {message}')


@dp.message_handler(content_types=[ContentType.NEW_CHAT_MEMBERS, ContentType.LEFT_CHAT_MEMBER])
async def on_join_left_menber(message: types.Message):
    logging.info(f'join/left: {message}')


# TODO refactor
@dp.message_handler(
    lambda msg: bool(msg.entities)
)
async def on_entity_in_message(message: types.Message):
    logging.info(f'entity: {message}')
    if message.from_user.id in banned_users:
        print('del message', message)
        await message.delete()
    if 'hypebomber' in message.text:
        await message.delete()
    elif 'приватные прокси' in message.text:
        await message.delete()
    elif 'socks5' in message.text:
        await message.delete()
    # await bot.send_message(810095709, f'spam? "{message.text}" from {message.from_user}')


@dp.message_handler()
async def default_handler(message: types.Message):
    if message.from_user.id in banned_users:
        print('del message', message)
        await message.delete()

    num = random.randint(1, 100)
    print('>', num, message)

    if is_handled_chat(message, handled_chats):
        if num < 3:
            await on_bang_quote(message)


def main():
    dp.middleware.setup(ThrottlingMiddleware())
    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    main()
