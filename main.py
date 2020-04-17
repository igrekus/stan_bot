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

with open('quotes.json', 'rt', encoding='utf-8') as f:
    quotes = json.loads(''.join(f.readlines()))

storage = MemoryStorage()
bot = Bot(token=token, proxy=proxy)
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=['start', 'help'])
@rate_limit(5, 'start')
async def send_welcome(message: types.Message):
    if message.chat.id != TEST_CHAT_ID and message.chat.id != SELF_USER:
        return
    if message.text == '/start':
        await bot.send_message(message.chat.id, 'start command issued')
    elif message.text == '/help':
        await bot.send_message(message.chat.id, 'help command issued')


@dp.message_handler(regexp='/send*')
async def send_welcome(message: types.Message):
    if message.chat.id != SELF_USER:
        return
    if '/send py' in message.text:
        s = message.text.lstrip('/send py')
        await bot.send_message(PY_CHAT_ID, s)


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


@dp.message_handler()
@rate_limit(5)
async def default_handler(message: types.Message):
    print(message)
    if message.chat.id == PY_CHAT_ID:
        if message.text in ('!rules', '!правила'):
            name = f'@{message.from_user.username}'
            if name == '@None':
                name = f'{message.from_user.first_name}'
            await bot.send_message(PY_CHAT_ID, f'{name} [сюда]({rules_link}) читай', parse_mode='MarkdownV2',  disable_web_page_preview=True)
        elif message.text == '!quote':
            db_id = random.choice(list(quotes.keys()))
            try:
                msg_id = quotes[db_id]['message_id']
                await bot.forward_message(PY_CHAT_ID, PY_CHAT_ID, msg_id)
            except KeyError:
                msg_text = quotes[db_id]['text']
                await message.reply(msg_text, reply=False)
        elif 'хауди' in message.text.lower() or 'дудар' in message.text.lower():
            await message.reply('у нас тут таких не любят')
        elif message.text == '!help':
            await message.reply('''`\\!rules`, `\\!правила` \\- правила чятика
`\\!quote` \\- цитатка
`\\!lutz`, `\\!лутц` \\- дать Лутцца
`\\!help` \\- это сообщение
''', parse_mode='MarkdownV2', reply=False)
        elif message.text.lower() in ('!lutz', '!лутц'):
            await message.reply('пссст, парень, нехочеш немножечко Лутцца?')


def main():
    print('main')
    dp.middleware.setup(ThrottlingMiddleware())
    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    main()
