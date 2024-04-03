import asyncio

import os

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile, ContentType

import json

from googletrans import Translator

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

translator = Translator()

ADMIN_ID = os.getenv("ADMIN")

bot = Bot(token=os.getenv("TOKEN"), parse_mode=ParseMode.HTML)
dp = Dispatcher()


async def start_bot(bot: Bot):
    await bot.send_message(ADMIN_ID, text='<b>Бот запущен</b>')


async def stop_bot(bot: Bot):
    await bot.send_message(ADMIN_ID, text='<b>Бот остановлен</b>')


async def get_start(message: types.Message):
    await message.answer(text=message.text)

@dp.message(F.content_type == ContentType.TEXT)
async def trans_json(message: types.Message):
    file_id = message.document.file_id
    file_info = await bot.get_file(file_id)
    doc = await bot.download_file(file_info.file_path)
    file_name = file_info.file_path.split("/")[-1]
    if file_name[-5:] == '.json':
        await message.answer('Перевожу...')
        json_data = json.loads(doc.read())
        file = json_data
        ru_words = {}
        k = 0
        for key in file.keys():
            k += 1
            ru_words[key] = translator.translate(file[key], 'ru').text
            if k % 50 == 0:
                await message.answer(f'{k}')

        with open('ru_ru.json', 'w', encoding='utf-8') as ru_words_js:
            json.dump(ru_words, ru_words_js, indent=4, ensure_ascii=False)

        document = FSInputFile(path=r'C:\Users\smile\Desktop\Python_study\pythonProject\trans-bot\ru_ru.json')
        await bot.send_document(message.from_user.id, document=document)
    else:
        await message.answer('Я не умею обрабатывать документы с таким форматом')


async def start():
    dp.message.register(get_start, Command(commands=['start']))
    dp.message.register(trans_json)
    dp.shutdown.register(stop_bot)
    dp.startup.register(start_bot)
    await bot.delete_webhook(drop_pending_updates=True)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(start())
