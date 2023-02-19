import os
from dotenv import load_dotenv

load_dotenv()

import asyncio
import logging

import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor

from datetime import datetime, timezone

from model import Model

from database import Database

from history_item import HistoryItem

logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class Game(StatesGroup):
    word = State()
    guess = State()
    words = State()
    hints = State()
    hint = State()
    start_timestamp = State()


model = Model()
database = Database()


@dp.message_handler(commands='start')
async def start_cmd_handler(message: types.Message):
    keyboard_markup = types.InlineKeyboardMarkup(row_width=3)

    text_and_data = (
        ('Играть', 'play'),
        ('История', 'history'),
    )
    row_btns = (types.InlineKeyboardButton(text, callback_data=data)
                for text, data in text_and_data)

    keyboard_markup.row(*row_btns)

    await message.reply(
        "Привет! Со мной вы можете сыграть в Sementle (угадай слово). На каждое слово я буду отвечать процентом схожести.",
        reply_markup=keyboard_markup)


@dp.callback_query_handler(text='play')
async def inline_kb_answer_callback_handler(query: types.CallbackQuery,
                                            state: FSMContext):
    word = model.getRandomWord()[0] + "_PROPN"
    while not word.endswith('PROPN') or not word in model.model:
        word = model.getRandomWord()[0] + "_PROPN"

    await state.update_data(word=word)
    await state.update_data(start_timestamp=datetime.now(timezone.utc))

    await Game.words.set()

    await bot.send_message(
        query.from_user.id,
        'Давай играть, отгадай мое слово! Чтобы закончить, просто напиши "стоп". Чтобы я подсказал, напиши "подскажи".'
    )


@dp.message_handler(state='*', commands='стоп')
@dp.message_handler(Text(equals='стоп', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    word = ''
    if 'word' in data:
        word = data['word']

    words = []
    if 'words' in data:
        words = data['words']

    if 'start_timestamp' in data:
        start_timestamp = data['start_timestamp']

    await state.finish()

    database.add_history(
        HistoryItem(0, message.chat.username,
                    word.split('_')[0], words, start_timestamp,
                    datetime.now(timezone.utc)))

    keyboard_markup = types.InlineKeyboardMarkup(row_width=3)

    text_and_data = (
        ('Играть', 'play'),
        ('История', 'history'),
    )
    row_btns = (types.InlineKeyboardButton(text, callback_data=data)
                for text, data in text_and_data)

    keyboard_markup.row(*row_btns)
    await message.reply('А я загадал "' + word + '"!',
                        reply_markup=keyboard_markup)


@dp.message_handler(lambda message: message.text, state=Game.words)
async def process_word(message: types.Message, state: FSMContext):
    data = await state.get_data()
    word = ''
    if 'word' in data:
        word = data['word']

    hints = []
    if 'hints' in data:
        hints = data['hints']
    else:
        count = 0
        for i in model.model.most_similar(positive=[word], topn=100000):
            if (i[0].endswith("PROPN")
                    and model.model.similarity(word, i[0]) >= 0.5):
                hints.append(i[0].split("_")[0])
                count += 1
            if count >= 100:
                break
        await state.update_data(hints=hints)

    hint = len(hints) - 1
    if 'hint' in data:
        hint = data['hint']
    else:
        await state.update_data(hint=hint)
    if message.text.lower().strip() == "подскажи":
        hint_word = ''
        if hint >= 0:
            hint_word = hints[hint]
            hint -= 1
            await state.update_data(hint=hint)
            p = int(model.model.similarity(word, hint_word + "_PROPN") * 100)
            await message.reply("Вот тебе подсказка: " + hint_word +
                                ". Процент схожести: " + str(p) + "%")
        else:
            await message.reply('Подсказки исчерпаны.')
    else:
        words = []
        if 'words' in data:
            words = data['words']
        words.append(message.text)
        await state.update_data(words=words)

        guess = message.text.lower() + "_PROPN"

        if guess == word:
            keyboard_markup = types.InlineKeyboardMarkup(row_width=3)

            text_and_data = (
                ('Играть', 'play'),
                ('История', 'history'),
            )
            row_btns = (types.InlineKeyboardButton(text, callback_data=data)
                        for text, data in text_and_data)

            keyboard_markup.row(*row_btns)

            await state.finish()

            if 'start_timestamp' in data:
                start_timestamp = data['start_timestamp']

            database.add_history(
                HistoryItem(0, message.chat.username,
                            word.split('_')[0], words, start_timestamp,
                            datetime.now(timezone.utc)))

            await message.reply("Правильно!", reply_markup=keyboard_markup)
        else:
            if not guess in model.model:
                await message.reply("Я не знаю такого слова.")
            else:
                p = int(model.model.similarity(word, guess) * 100)
                await message.reply("Не угадал. Процент схожести слов: " +
                                    str(p) + "%")


@dp.callback_query_handler(text='history')
async def inline_kb_answer_callback_handler(query: types.CallbackQuery):
    await query.answer('История игр:')

    text = ''

    await bot.send_message(query.from_user.id, text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)