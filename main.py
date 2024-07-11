import logging
import os

from aiogram import F, Dispatcher, Bot
from aiogram.filters import CommandStart
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, Message
from dotenv import load_dotenv

from smartavia_parser import *

load_dotenv()
button1 = KeyboardButton(text='Сочи СПБ')
button2 = KeyboardButton(text='СПБ Сочи')
button3 = KeyboardButton(text='Выбрать направление')
btn_1 = KeyboardButton(text='Кнопка 1')
btn_2 = KeyboardButton(text='Кнопка 2')
btn_3 = KeyboardButton(text='Кнопка 3')

keyboard_date = ReplyKeyboardMarkup(
    keyboard=[[button1, button2], [button3]],
    resize_keyboard=True,
    input_field_placeholder='ддмм',
    one_time_keyboard=True)
keyboard_direction = ReplyKeyboardMarkup(
    keyboard=[[button1, button2], [button3]],
    resize_keyboard=True,
    input_field_placeholder='Спб Сочи',
    one_time_keyboard=True)

bot = Bot(token=os.getenv('TELEGRAM_TOKEN_TRAINING_BOT'))
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)
passengers_dict = {}


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(text='Welcome to smartavia bot\n Пользуйтесь '
                              'кнопками и подсказками на экране',
                         reply_markup=keyboard_date)


@dp.message(F.text == 'Выбрать направление')
async def request_direction(message: Message):
    await message.answer('Введите пункт отправления и пункт назначения, '
                         'через пробел', reply_markup=keyboard_direction)


@dp.message(F.text.regexp(r'[А-Яа-яЁё-]+ [А-Яа-яЁё-]+'))
@dp.message(F.text == 'Сочи СПБ')
@dp.message(F.text == 'СПБ Сочи')
async def get_flight_data(message: Message):
    passengers_dict[message.from_user.id] = message.text
    await message.answer('введите желаемую дату вылета: 🛫️\nчисло и месяц',
                         reply_markup=keyboard_date)


@dp.message(F.text.regexp(r'\d\d\W\d\d'))
@dp.message(F.text.regexp(r'\d\d\d\d'))
async def send_flights(message: Message):
    date = message.text
    if len(date) == 5:
        date = date[:2] + date[3:]
    dep_air = passengers_dict.get(message.from_user.id).split()[0].title()
    arrive_air = passengers_dict.get(message.from_user.id).split()[1].title()
    print(f'dep_air: {dep_air}')
    print(f'arrive_air: {arrive_air}')
    if arrive_air == 'Сочи':
        direction = f'✈️    🌆️{dep_air}-{arrive_air}🏝️\n'
    elif dep_air == 'Сочи':
        direction = f'✈️    🏝️{dep_air}-{arrive_air}🌆️\n'
    else:
        direction = f'✈️    {dep_air}-{arrive_air}\n'

    # direction = (f'✈️    🌆️{dep_air}-{arrive_air}🏝️\n' if arrive_air == 'Сочи'
    #              else f'✈️    🏝️{dep_air}-{arrive_air}🌆️\n')
    await message.answer(
        text=get_5_days_flights(get_driver(date, dep_air, arrive_air),
                                get_soup(
                                    get_driver(date, dep_air, arrive_air)),
                                direction
                                ),
        reply_markup=keyboard_date)


@dp.message()
async def send_flights(message: Message):
    await message.answer(text='Нужно ввести дату в формате 2506, где 25 - '
                              'это день, 06 - это месяц❗️',
                         reply_markup=keyboard_date)


if __name__ == '__main__':
    dp.run_polling(bot)
