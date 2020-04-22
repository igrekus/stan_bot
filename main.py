import hashlib
import json
import logging
import random

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from middleware import rate_limit, ThrottlingMiddleware

logging.basicConfig(level=logging.INFO)

with open('creds.json', 'rt', encoding='utf-8') as f:
    creds = json.loads(''.join(f.readlines()))

px_user = creds['user']
px_pass = creds['pass']
px_server = creds['proxy']
px_port = creds['port']
token = creds['token']
proxy = f'socks5://{px_user}:{px_pass}@{px_server}:{px_port}'
PY_CHAT_ID = creds['py_chat']
TEST_CHAT_ID = creds['test_chat']
SELF_USER = creds['self_user']

rules_link = 'https://docs.google.com/document/d/1DRhi1jzjQFqg4WRxeSY38I2W-1PQccJptQ8bmg-kEN8/edit'
engine_link = 'https://lmgtfy.com/?q='

with open('quotes.json', 'rt', encoding='utf-8') as f:
    quotes = json.loads(''.join(f.readlines()))

storage = MemoryStorage()
bot = Bot(token=token, proxy=proxy)
dp = Dispatcher(bot, storage=storage)

bot_admins = [SELF_USER]


@dp.message_handler(commands=['start', 'help'])
@rate_limit(5, 'start')
async def send_welcome(message: types.Message):
    if message.chat.id != TEST_CHAT_ID and message.chat.id != SELF_USER:
        return
    if message.text == '/start':
        await bot.send_message(message.chat.id, 'start command issued')
    elif message.text == '/help':
        await bot.send_message(message.chat.id, 'help command issued')


@dp.message_handler(lambda msg: msg.chat.id in bot_admins)
async def handle_admin(message: types.Message):
    if '/send py' in message.text:
        s = message.text.lstrip('/send py')
        await bot.send_message(PY_CHAT_ID, s)
    elif "!send" in message.text:
        _, chat, msg = message.text.split(' ', 2)
        await bot.send_message(int(chat), msg)
    elif '!import' in message.text:
        qs = 'a'
        last_id = int(list(quotes.keys())[-1])
        for q in qs.split('\n'):
            id_, text = q.split('|')
            new_quote = {
                'message_id': int(id_.lstrip('message')),
                'text': text
            }
            quotes[f'{last_id + 1}'] = new_quote
            last_id += 1
            logging.log(logging.INFO, f'Add quote "{new_quote}"')

        with open('quotes.json', 'wt', encoding='utf-8') as f:
            json.dump(quotes, f, ensure_ascii=False)
    elif '!add' in message.text:
        await pychan_quote_add(message)


@dp.message_handler(lambda msg: msg.text.startswith('!add') and msg.chat.id == PY_CHAT_ID and msg["from"].id == SELF_USER)
@rate_limit(10)
async def pychan_quote_add(message: types.Message):
    logging.log(logging.INFO, f'!add received from {message.from_user} with text "{message.text}"')
    reply = message['reply_to_message']
    if reply:
        new_quote = {'message_id': reply.message_id, 'text': reply.text}
    else:
        new_quote = {'text': message.text.lstrip('!add ')}

    last_id = int(list(quotes.keys())[-1])
    if new_quote['text']:
        quotes[f'{last_id + 1}'] = new_quote
        with open('quotes.json', 'wt', encoding='utf-8') as f:
            json.dump(quotes, f, ensure_ascii=False)
        logging.log(logging.INFO, f'Add quote "{new_quote}"')
        await message.reply(f'добавил: {new_quote["text"]}', reply=False)


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
    query = ''
    try:
        _, query = message.text.split(' ', 1)
    except ValueError:
        pass
    db = quotes
    if query:
        db = {k: v for k, v in quotes.items() if query in v}
    db_id = random.choice(list(db.keys()))
    try:
        msg_id = quotes[db_id]['message_id']
        await bot.forward_message(PY_CHAT_ID, PY_CHAT_ID, msg_id)
    except KeyError:
        msg_text = quotes[db_id]['text']
        await message.reply(msg_text, reply=False)


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
async def rules_handler(message: types.Message):
    reply = message['reply_to_message']
    if reply:
        id_ = message.reply_to_message.message_id
    else:
        id_ = message.message_id
    await bot.send_message(PY_CHAT_ID, f'[nometa.xyz](nometa.xyz)',
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
        if 'хауди' in message.text.lower() or 'дудар' in message.text.lower():
            await message.reply('у нас тут таких не любят')
    if num < 2:
        await quote_handler(message)


def main():
    print('main')
    dp.middleware.setup(ThrottlingMiddleware())
    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    main()
