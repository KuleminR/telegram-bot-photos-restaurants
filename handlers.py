import json
import random
import time

from main import bot, dp
from states import States

from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, \
    CallbackQuery, InputMedia, \
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext
from config import BOT_TOKEN, admin_id
from parsers import get_new_shiba_base, get_mcdonalds_events

# index 0 - mcdonald's
# index 1 - BK
# index 3 - KFC
db_events = {'McDonald\'s': {'events': [], 'get_function': get_mcdonalds_events, 'update_time': 0},
             'Burger King': {'events': [], 'get_function': None, 'update_time': 0},
             'KFC': {'events': [], 'get_function': None, 'update_time': 0}
            }

async def send_to_admin(dp):
    #get_new_shiba_base(10)
    await bot.send_message(chat_id=admin_id, text="Бот запущен")

@dp.message_handler(commands=['start'], state='*')
async def start(message: Message):
    greet_message = 'Доступные команды:\n' \
                    '/<тематическое название фото> - получить случайную фотографию чего-либо(определяется выбранным в "parsers.py" параметром search_term)\n' \
                    '/food_events - получить информацию об акциях в ресторане быстрого питания на выбор'

    await bot.send_message(message.from_user.id, greet_message)


@dp.message_handler(commands=['<тематическое название фото>'], state='*')
async def get_photo(message: Message):
    with open('db.txt', 'r') as f:
        db_dict = json.load(f)
    if not db_dict['resource_available']:
        await bot.send_message(message.from_user.id, 'Извините, сервис временно недоступен')
    else:
        with open('photo_links.txt', 'r') as f:
            photo_links = f.readlines()
        if len(photo_links) == 0:
            get_new_photo_base(5)

        photo_link = photo_links.pop(random.randint(0, len(photo_links) - 1))

        with open('photo_links.txt', 'w') as f:
            f.writelines(photo_links)

        await bot.send_photo(message.from_user.id, photo_link)


@dp.message_handler(commands=['food_events'], state='*')
async def choose_restaurant(message:Message):
    keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton('McDonald\'s')],
                                             # [KeyboardButton('Burger King')],
                                             # [KeyboardButton('KFC')]
                                             ],
                                   one_time_keyboard=True
                                   )
    state = dp.current_state()
    await bot.send_message(message.from_user.id, text='Выберите ресторан:', reply_markup=keyboard)
    await state.set_state(States.loading_restaurant_events)


@dp.message_handler(state=States.loading_restaurant_events)
async def get_events(message: Message, state: FSMContext):
    chat_id = message.from_user.id
    choice = message.text
    await bot.send_chat_action(chat_id, 'typing')

    # index 0 - link, index 1 - img (may be missing)
    last_upd_day = time.localtime(db_events[choice]['update_time']).tm_yday
    time_from_update = time.localtime(time.time()).tm_yday - last_upd_day
    print(time_from_update)
    if abs(time_from_update) >= 1:
        db_events[choice]['events'] = db_events[choice]['get_function']()
        db_events[choice]['update_time'] = time.time()
        print(db_events[choice]['update_time'])

    events = db_events[choice]['events']
    index = 0
    event = events[index]
    next_index = index + 1
    prev_index = index - 1
    if prev_index < 0:
        prev_index = len(events) - 1
    if next_index >= len(events):
        next_index = 0
    rb_data = choice + '.' + str(next_index)
    lb_data = choice + '.' + str(prev_index)
    keyboard = [[InlineKeyboardButton('Предыдущая акция', callback_data=rb_data),
                 InlineKeyboardButton('Следующая акция', callback_data=lb_data)]]
    keyboard_markup = InlineKeyboardMarkup(2, inline_keyboard=keyboard)
    await bot.send_message(chat_id, text='Акции этого ресторана:', reply_markup=ReplyKeyboardRemove())
    await bot.send_photo(chat_id, event[1], caption=event[0], reply_markup=keyboard_markup)
    await state.finish()


@dp.callback_query_handler(lambda callback_query: True, state='*')
async def get_next_event(callback_query: CallbackQuery):
    chat_id = callback_query.from_user.id
    message_id = callback_query.message.message_id
    data = callback_query.data.split('.')
    choice = data[0]
    event_index = int(data[1])
    event = db_events[choice]['events'][event_index]

    next_index = event_index + 1
    prev_index = event_index - 1
    if prev_index < 0:
        prev_index = len(db_events[choice]['events']) - 1

    if next_index >= len(db_events[choice]['events']):
        next_index = 0
    rb_data = choice + '.' + str(next_index)
    lb_data = choice + '.' + str(prev_index)

    keyboard = [[InlineKeyboardButton('Предыдущая акция', callback_data=rb_data),
                 InlineKeyboardButton('Следующая акция', callback_data=lb_data)]]
    keyboard_markup = InlineKeyboardMarkup(2, inline_keyboard=keyboard)

    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_media(InputMedia(media=event[1]), chat_id=chat_id, message_id=message_id)
    await bot.edit_message_caption(chat_id=chat_id, message_id=message_id, caption=event[0])
    await bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=keyboard_markup)
