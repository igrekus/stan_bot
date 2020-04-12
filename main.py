import json

from aiogram import Bot, Dispatcher, executor, types


with open('creds.json', 'rt', encoding='utf-8') as f:
    settings = json.loads(''.join(f.readlines()))

bot = Bot(token=settings['token'])
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await bot.send_message(message.chat.id, 'test message')
    # if message.text == 'start':
    #     await message.reply('start command issued')
    # elif message.text == 'help':
    #     await message.reply('help command issued')


@dp.message_handler(regexp='(^cat[s]?$|puss)')
async def cats(message: types.Message):
    with open('data/cats.jpg', 'rb') as photo:
        '''
        # Old fashioned way:
        await bot.send_photo(
            message.chat.id,
            photo,
            caption='Cats are here 😺',
            reply_to_message_id=message.message_id,
        )
        '''
        await message.reply_photo(photo, caption='катан!!1 😺')


@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(message.text)


def main():
    print('main')
    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    main()
