import logging
import os

from aiogram import F, Dispatcher, Bot
from aiogram.filters import CommandStart
from aiogram.types import (KeyboardButton, ReplyKeyboardMarkup,
                           Message, InlineKeyboardButton,
                           InlineKeyboardMarkup)
from dotenv import load_dotenv

from smartavia_parser import *

load_dotenv()
button1 = KeyboardButton(text='5 рейсов')
button2 = KeyboardButton(text='найти билеты')
btn_1 = KeyboardButton(text='Кнопка 1')
btn_2 = KeyboardButton(text='Кнопка 2')
inline_button1 = InlineKeyboardButton(text='stepik', callback_data='enter '
                                                                   'data')
inline_button2 = InlineKeyboardButton(text='smartavia',
                                      callback_data='button2 pressed')
keyboard = ReplyKeyboardMarkup(
    keyboard=[[button1, button2]],
    resize_keyboard=True,
    input_field_placeholder='ддмм',
    one_time_keyboard=True)
inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[[inline_button1],
                                                        [inline_button2]])

bot = Bot(token=os.getenv('TELEGRAM_TOKEN_TRAINING_BOT'))
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(text='Welcome to smartavia bot',
                         reply_markup=keyboard)


@dp.message(F.text == 'найти билеты')
async def get_flight_data(message: Message):
    await message.answer('введите дату:\nчисло и месяц ',
                         reply_markup=keyboard)


@dp.message(F.text == '5 рейсов')
async def get_five_flights(message: Message):
    await message.answer(text=get_5_days_flights(driver, soup),
                         reply_markup=keyboard)


@dp.message(lambda message: message.text.isdigit(), F.text.len() == 4)
async def send_flights(message: Message):
    date = message.text
    print(f'date: {date}')
    await message.answer(text=get_5_days_flights(get_driver(date), get_soup(
        get_driver(date))),
                         reply_markup=keyboard)


@dp.message(lambda message: message.text.isdigit(), F.text.len() != 4)
async def send_flights(message: Message):
    await message.answer(text='Нужно ввести дату в формате 2506, где 25 - '
                              'это день, 06 - это месяц',
                         reply_markup=keyboard)


@dp.message()
async def send_flights(message: Message):
    await message.answer(text='Нужно ввести дату в формате 2506, где 25 - '
                              'это день, 06 - это месяц!',
                         reply_markup=keyboard)


if __name__ == '__main__':
    dp.run_polling(bot)
