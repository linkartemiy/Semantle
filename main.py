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

logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class Game(StatesGroup):
    word = State()
    guess = State()
    words = State()


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
    answer_data = query.data

    await state.update_data(word='q')

    await Game.words.set()

    await bot.send_message(
        query.from_user.id,
        'Давай играть, отгадай мое слово! Чтобы закончить, просто напиши "стоп"'
    )


@dp.message_handler(state='*', commands='стоп')
@dp.message_handler(Text(equals='стоп', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    word = ''
    if 'word' in data:
        word = data['word']

    await state.finish()
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
    words = []
    if 'words' in data:
        words = data['words']
    words.append(message.text)
    await state.update_data(words=words)

    word = ''
    if 'word' in data:
        word = data['word']

    if message.text == word:
        keyboard_markup = types.InlineKeyboardMarkup(row_width=3)

        text_and_data = (
            ('Играть', 'play'),
            ('История', 'history'),
        )
        row_btns = (types.InlineKeyboardButton(text, callback_data=data)
                    for text, data in text_and_data)

        keyboard_markup.row(*row_btns)

        await state.finish()

        await message.reply("Правильно!", reply_markup=keyboard_markup)
    else:
        await message.reply("Неправильно")


@dp.callback_query_handler(text='history')
async def inline_kb_answer_callback_handler(query: types.CallbackQuery):
    await query.answer('История игр:')

    text = ''

    await bot.send_message(query.from_user.id, text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)