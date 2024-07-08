import logging
import os

from aiogram import F, Dispatcher, Bot
from aiogram.filters import CommandStart
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, Message
from dotenv import load_dotenv

from smartavia_parser import *
from passengers import Passenger

load_dotenv()
button1 = KeyboardButton(text='Сочи-СПБ')
button2 = KeyboardButton(text='СПБ-Сочи')
button3 = KeyboardButton(text='найти билеты')
btn_1 = KeyboardButton(text='Кнопка 1')
btn_2 = KeyboardButton(text='Кнопка 2')
btn_3 = KeyboardButton(text='Кнопка 3')

keyboard = ReplyKeyboardMarkup(
    keyboard=[[button1, button2], ],
    resize_keyboard=True,
    input_field_placeholder='ддмм',
    one_time_keyboard=True)

bot = Bot(token=os.getenv('TELEGRAM_TOKEN_TRAINING_BOT'))
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)
passengers_dict = {}


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(text='Welcome to smartavia bot',
                         reply_markup=keyboard)


@dp.message(F.text == 'Сочи-СПБ')
@dp.message(F.text == 'СПБ-Сочи')
async def get_flight_data(message: Message):
    passengers_dict[message.from_user.id] = message.text

    print(passengers_dict)
    Passenger(message.from_user.first_name, message.from_user.id)
    await message.answer('введите желаемую дату вылета:\nчисло и месяц без '
                         'пробелов',
                         reply_markup=keyboard)


@dp.message(lambda message: message.text.isdigit(), F.text.len() == 4)
async def send_flights(message: Message):
    date = message.text
    direction = f'{passengers_dict.get(message.from_user.id)}\n'
    print(direction)
    dep_air = passengers_dict.get(message.from_user.id).split('-')[0]
    arrive_air = passengers_dict.get(message.from_user.id).split('-')[1]
    await message.answer(
        text=get_5_days_flights(get_driver(date, dep_air, arrive_air),
                                get_soup(
                                    get_driver(date, dep_air, arrive_air)),
                                direction
                                ),
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
