import hashlib
import json
import logging
import random

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent, InlineQuery

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

bot = Bot(token=token, proxy=proxy)
dp = Dispatcher(bot)

quotes = {
    0: {"text": "чот нетак делоеш"},
    1: {"message_id": 129264, "text": "так все от него страдают"},
    2: {"message_id": 129323, "text": "у меня лапки"}
}


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    if message.chat.id != TEST_CHAT_ID or message.chat.id != SELF_USER:
        return
    if message.text == '/start':
        await message.reply('start command issued')
    elif message.text == '/help':
        await message.reply('help command issued')


@dp.message_handler(regexp='/send*')
async def send_welcome(message: types.Message):
    if message.chat.id != 289682796:
        return
    if '/send py' in message.text:
        s = message.text.lstrip('/send py')
        await bot.send_message(PY_CHAT_ID, s)


@dp.message_handler()
async def default_handler(message: types.Message):
    print(message)
    # if message.chat.id == TEST_CHAT_ID:
    #     await bot.send_message(message.chat.id, f'fwd message: {message.text}')
    if message.chat.id == PY_CHAT_ID:
        if message.text in ('!rules', '!правила'):
            await bot.send_message(PY_CHAT_ID, f'{message.from_user} [сюда]({rules_link}) читай', parse_mode='MarkdownV2',  disable_web_page_preview=True)
        elif message.text == '!quote':
            db_id = random.choice(list(quotes.keys()))
            try:
                msg_id = quotes[db_id]['message_id']
                await bot.forward_message(PY_CHAT_ID, PY_CHAT_ID, msg_id)
            except KeyError:
                msg_text = quotes[db_id]['text']
                await message.reply(msg_text)


def main():
    print('main')
    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    main()
