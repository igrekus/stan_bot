import logging
import random
import requests

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from middleware import rate_limit, ThrottlingMiddleware

from config import proxy, token, rules_link, engine_link, lat_rus_map, qdb, PY_CHAT_ID, SELF_USER, bot_admins, bot_auth, chat_alias, handled_chats
from filters import *

logging.basicConfig(level=logging.INFO)

bot = Bot(token=token, proxy=proxy)
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(lambda msg: is_private_command(msg, '/start'))
@rate_limit(5, 'start')
async def on_register_request(message: types.Message):
    if message.chat.id == message.from_user.id:
        logging.info(f'Registering user {message.from_user}')
        bot_auth.register_user(message)
        await bot.send_message(message.chat.id, 'start command issued')


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
    reply = message['reply_to_message']
    if reply:
        new_quote = {'message_id': reply.message_id, 'text': reply.text}
    else:
        new_quote = {'text': message.text.lstrip('!add ')}

    if new_quote['text']:
        qdb.add(new_quote)
        logging.log(logging.INFO, f'Add quote "{new_quote}"')
        await message.reply(f'добавил: {new_quote["text"]}', reply=False)


@dp.message_handler(lambda msg: msg.text.startswith('!advice') and msg.chat.id == PY_CHAT_ID and msg["from"].id == SELF_USER)
@rate_limit(10)
async def pychan_advice(message: types.Message):
    reply = message['reply_to_message']
    if reply:
        first, second = message.text.lstrip('!advice ').split(', ')
        if first and second:
            await bot.send_message(message.chat.id, f'добавил: {first, second["text"]}', reply_to_message_id=reply.message_id)


@dp.message_handler(
    lambda msg:
    is_handled_chat(msg, handled_chats) and
    is_bang_command(msg, 'tr')
)
@rate_limit(10)
async def on_tr(message: types.Message):
    if not message.reply_to_message.text:
        return
    await message.reply(message.reply_to_message.text.translate(lat_rus_map))


@dp.message_handler(lambda msg: msg.text.startswith('!inspire') and msg.chat.id == PY_CHAT_ID and msg['from'].id == SELF_USER)
@rate_limit(10)
async def inspire_handler(message: types.Message):
    url = requests.get('https://inspirobot.me/api?generate=true').text
    if not url:
        return
    img = requests.get(url).content
    if not img:
        return
    await bot.send_photo(message.chat.id, img, reply_to_message_id=message.message_id)


@dp.message_handler(lambda msg: msg.chat.id == PY_CHAT_ID and msg.text.startswith('!lmgtfy'))
@rate_limit(5)
async def lmgtfy_handler(message: types.Message):
    reply = message['reply_to_message']
    if reply:
        query = f'{engine_link}{"+".join(message.reply_to_message.text.split(" "))}'
        id_ = message.reply_to_message.message_id
    else:
        query = f'{engine_link}{"+".join(message.text.lstrip("!lmgtfy ").split(" "))}'
        id_ = message.message_id
    await bot.send_message(message.chat.id, query, disable_web_page_preview=True, reply_to_message_id=id_)


@dp.message_handler(lambda msg: msg.chat.id == PY_CHAT_ID and msg.text.startswith('!quote'))
@rate_limit(5)
async def quote_handler(message: types.Message):
    # TODO rewrite !quote query for new db
    # query = ''
    # try:
    #     _, query = message.text.split(' ', 1)
    # except ValueError:
    #     pass
    id_, msg_id, text = qdb.quote
    logging.info(f'Send quote id={id_} text={text}')
    if msg_id:
        await bot.forward_message(message.chat.id, message.chat.id, msg_id)
    else:
        await message.reply(text, reply=False)


@dp.message_handler(lambda msg: msg.chat.id == PY_CHAT_ID and msg.text in ('!rules', '!правила'))
@rate_limit(5)
async def rules_handler(message: types.Message):
    reply = message['reply_to_message']
    if reply:
        id_ = message.reply_to_message.message_id
    else:
        id_ = message.message_id
    await bot.send_message(PY_CHAT_ID, f'[сюда]({rules_link}) читай',
                           parse_mode='MarkdownV2', disable_web_page_preview=True, reply_to_message_id=id_)


@dp.message_handler(lambda msg: msg.chat.id == PY_CHAT_ID and msg.text in ['!nometa'])
@rate_limit(5)
async def nometa_handler(message: types.Message):
    reply = message['reply_to_message']
    if reply:
        id_ = message.reply_to_message.message_id
    else:
        id_ = message.message_id
    await bot.send_message(PY_CHAT_ID, f'[nometa\\.xyz](http://nometa.xyz)',
                           parse_mode='MarkdownV2', disable_web_page_preview=True, reply_to_message_id=id_)


def get_user_link(message: types.Message):
    name = f'@{message.from_user.username}'
    if name == '@None':
        name = f'{message.from_user.first_name}'
    return name


@dp.message_handler(lambda msg: msg.chat.id == PY_CHAT_ID and msg.text.startswith('!help'))
@rate_limit(5)
async def help_handler(message: types.Message):
    await message.reply('''`\\!rules`, `\\!правила` \\- правила чятика
`\\!lutz`, `\\!лутц` \\- дать Лутцца
`\\!django`, `\\!джанго` \\- дать Джангца
`\\!help` \\- это сообщение
''', parse_mode='MarkdownV2', reply=False)


@dp.message_handler(lambda msg: msg.chat.id == PY_CHAT_ID and msg.text.lower() in ('!lutz', '!лутц'))
@rate_limit(5)
async def lutz_handler(message: types.Message):
    reply = message['reply_to_message']
    msg = message
    if reply:
        msg = message.reply_to_message
    await bot.send_message(message.chat.id, f'{get_user_link(msg)} вот, не позорься: https://t.me/python_books_archive/565')


@dp.message_handler(lambda msg: msg.chat.id == PY_CHAT_ID and msg.text.lower() in ('!django', '!джанго'))
@rate_limit(5)
async def django_handler(message: types.Message):
    await message.reply(f'держи, поискал за тебя: https://t.me/c/1338616632/133706', reply=False)


@dp.message_handler()
async def default_handler(message: types.Message):
    num = random.randint(1, 100)
    print('>', num, message)
    if message.chat.id == PY_CHAT_ID:
        lowered = message.text.lower()
        if 'хауди' in lowered or 'дудар' in lowered or 'дудь' in lowered or 'дудя' in lowered:
            await message.reply('у нас тут таких не любят')
    if num < 2:
        await quote_handler(message)


def main():
    print('main')
    dp.middleware.setup(ThrottlingMiddleware())
    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    main()
