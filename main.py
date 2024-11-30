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
button_aeroflot = KeyboardButton(text='Аэрофлот')
button_smartavia = KeyboardButton(text='Смартавиа')

keyboard_date = ReplyKeyboardMarkup(
    keyboard=[[button1, button2],
              [button3],
              [button_smartavia, button_aeroflot]],
    resize_keyboard=True,
    input_field_placeholder='ддмм',
    one_time_keyboard=True)
keyboard_direction = ReplyKeyboardMarkup(
    keyboard=[[button1, button2],
              [button3],
              [button_smartavia, button_aeroflot]],
    resize_keyboard=True,
    input_field_placeholder='москва минск',
    one_time_keyboard=True)

bot = Bot(token=os.getenv('TELEGRAM_TOKEN_TRAINING_BOT'))
dp = Dispatcher()

passengers_dict = {}


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(text='Welcome to smartavia bot\n Пользуйтесь '
                              'кнопками и подсказками на экране',
                         reply_markup=keyboard_date
                         )


@dp.message(F.text == 'Выбрать направление')
async def request_direction(message: Message):
    await message.answer('Введите пункт отправления и пункт назначения '
                         'через пробел или выберите в меню.',
                         reply_markup=keyboard_direction)


@dp.message(F.text == 'Аэрофлот')
@dp.message(F.text == 'Смартавиа')
async def get_air_company(message: Message):
    passengers_dict[message.from_user.username] = message.text
    await message.answer('Введите пункт отправления и пункт назначения '
                         'через пробел или выберите в меню.',
                         reply_markup=keyboard_direction)


@dp.message(F.text.regexp(r'[А-Яа-яЁё-]+ [А-Яа-яЁё-]+'))
@dp.message(F.text == 'Сочи СПБ')
@dp.message(F.text == 'СПБ Сочи')
async def get_flight_data(message: Message):
    if not all(city.title() in AIRPORT_CODES for city in message.text.split()):
        for city in message.text.split():
            if city.title() not in AIRPORT_CODES:
                logger.warning(f'В городе {city} нет аэропорта, '
                               f'попробуйте ещё раз.')
                await message.answer(f'В городе {city} нет аэропорта, '
                                     f'попробуйте ещё раз.',
                                     reply_markup=keyboard_direction)
    else:
        passengers_dict[message.from_user.id] = message.text
        await message.answer('введите желаемую дату вылета: 🛫️\nчисло и месяц',
                             reply_markup=keyboard_date)


@dp.message(F.text.regexp(r'(0[1-9]|[12][0-9]|3[01])(0[1-9]|1[012])'))
@dp.message(F.text.regexp(r'(0[1-9]|[12][0-9]|3[01])\W(0[1-9]|1[012])'))
async def send_flights(message: Message):
    date = message.text
    if len(date) == 5:
        date = date[:2] + date[3:]
    if passengers_dict.get(message.from_user.id) is None:
        logger.warning('не выбрано направление. return')
        return await message.answer('Вы не выбрали направление')
    dep_air = passengers_dict.get(message.from_user.id).split()[0].title()
    arrive_air = passengers_dict.get(message.from_user.id).split()[1].title()
    if arrive_air == 'Сочи':
        direction = f'✈️    🌆️{dep_air}-{arrive_air}🏝️\n'
    elif dep_air == 'Сочи':
        direction = f'✈️    🏝️{dep_air}-{arrive_air}🌆️\n'
    else:
        direction = f'✈️    {dep_air}-{arrive_air}\n'
    if passengers_dict.get(message.from_user.username) == 'Аэрофлот':
        url = AEROFLOT_URL
        current_date = str(datetime.date.today().year) + date[2:] + date[:2]
        await message.answer(
            # text=seven_days_aeroflot(url, current_date, dep_air, arrive_air)
            text=one_day_aeroflot(url, current_date, dep_air, arrive_air)
        )
    else:
        url = SMARTAVIA_URL
        await message.answer(
            text=five_days_smartavia(url, date, dep_air, arrive_air,direction),
            reply_markup=keyboard_date
        )


@dp.message(F.text.regexp(r'\d'))
@dp.message(F.text.regexp(r'\W\d'))
async def send_flights(message: Message):
    logger.warning(f'введена no correct дата: {message.text}')
    await message.answer(text='Нужно ввести дату в формате 2506, где 25 - '
                              'это день, 06 - это месяц❗️',
                         reply_markup=keyboard_date)


@dp.message(F.text.regexp(r'[a-zA-Z]'))
async def send_flights(message: Message):
    logger.warning(f'введён текст: {message.text}')
    await message.answer(text='Можно вводить только кириллические символы❗️',
                         reply_markup=keyboard_direction)


if __name__ == '__main__':
    dp.run_polling(bot)
