import json
import logging

from aiogram import Bot, Dispatcher, executor, types


with open('creds.json', 'rt', encoding='utf-8') as f:
    creds = json.loads(''.join(f.readlines()))

px_user = creds['user']
px_pass = creds['pass']
px_server = creds['proxy']
px_port = creds['port']
token = creds['token']
proxy = f'socks5://{px_user}:{px_pass}@{px_server}:{px_port}'

bot = Bot(token=token, proxy=proxy)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    if message.text == '/start':
        await message.reply('start command issued')
    elif message.text == '/help':
        await message.reply('help command issued')


@dp.message_handler(regexp='(^cat[s]?$|puss)')
async def cats(message: types.Message):
    with open('data/cats.jpg', 'rb') as photo:
        await message.reply_photo(photo, caption='катан!!1 😺')


@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(message.text)


def main():
    print('main')
    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    main()
