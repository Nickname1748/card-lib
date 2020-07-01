import telebot
from telebot import types

import re
import random

from datetime import datetime

from texts import Messages
from config import Tokens
from database import Insert, Fetch, Update, Delete

bot = telebot.TeleBot(Tokens.TOKEN)

@bot.message_handler(commands=['start'])
def bot_start(message):
    '''Начало работы с ботом'''

    insert_user = Insert(message.chat.id)
    insert_user.new_user(username=message.from_user.username,
                        first_name=message.from_user.first_name,
                        last_name=message.from_user.last_name)

    bot.send_message(message.chat.id, Messages.ASSISTANCE['START'])
    bot_private_office(message)

@bot.message_handler(commands=['office'])
def bot_private_office(message):
    '''Личный кабинет пользователя'''

    private_office_menu = keyboard_maker(3, **Messages.PRIVATE_OFFICE_BUTTONS)
    menu_message = bot.send_message(chat_id=message.chat.id,
                            text=Messages.PRIVATE_OFFICE['INTERFACE'],
                            reply_markup=private_office_menu)

    update_menu_id = Update(message.chat.id)
    update_menu_id.user_attribute('menu_id', menu_message.message_id)

@bot.message_handler(commands=['cancel'])
def bot_cancel(message):
    '''Отмена текущей операции'''

    user_status = Fetch(message.chat.id)
    status = user_status.user_attribute('action')
    session = user_status.user_attribute('session')

    if status == 1:
        delete_session = Delete(message.chat.id, 'collections', 'collection')
        delete_session.delete_collection(session)

    update_user_status = Update(message.chat.id)
    update_user_status.user_attribute('action', 0)
    update_user_status.user_attribute('session', None)

    bot.send_message(message.chat.id, Messages.ASSISTANCE['CANCEL'])
    bot_private_office(message)

@bot.callback_query_handler(func=lambda call: True)
def bot_callback_query(call):
    if error_handler(call.message):
        return

    elif call.data == 'profile':
        call_profile_menu(call)

    elif 'collection' in call.data:
        if 'create' in call.data:
            call_create_collection(call)
        else:
            call_collections_menu(call)

    elif 'show' in call.data:
        call_collection_menu(call)

    elif call.data == 'home':
        call_home(call)


def call_profile_menu(call):
    '''Профиль пользователя'''

    user_info = Fetch(call.message.chat.id)
    user_username = user_info.user_attribute('username')
    collections = user_info.user_attribute('collections')
    cards = user_info.user_attribute('cards')
    
    profile_menu = keyboard_maker(1, **Messages.PROFILE_BUTTONS)
    main_text = Messages.PROFILE['INTERFACE'].format(user_username,
                                                    collections,
                                                    cards)
    bot.answer_callback_query(call.id)
    bot.edit_message_text(text=main_text,
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        reply_markup=profile_menu)


def call_collections_menu(call):
    '''Коллекции пользователя'''

    fetch_collections = Fetch(user_id=call.message.chat.id,
                            db_name='collections',
                            db_table='collection')
    collections_info = fetch_collections.user_collections()

    buttons = {}
    collections_keyboard = None
    if collections_info:
        for collection in collections_info:
            buttons[collection[3]] = f'show_{collection[1]}'
        collections_keyboard = keyboard_maker(2, **buttons)

    collections_menu = keyboard_maker(row_width=2,
                                    keyboard=collections_keyboard,
                                    **Messages.COLLECTIONS_BUTTONS)

    bot.answer_callback_query(call.id)
    bot.edit_message_text(text=Messages.COLLECTIONS['INTERFACE'],
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        reply_markup=collections_menu)

def call_create_collection(call):
    '''Создание коллекции'''

    if error_handler(call.message) or cancel_handler(call.message):
        return
    
    key = f'k-{random.randint(1, 1000000)}-{random.randint(1, 1000)}-n'
    date = datetime.now()

    update_user_status = Update(call.message.chat.id)
    update_user_status.user_attribute('action', 1)
    update_user_status.user_attribute('session', key)

    insert_collection = Insert(user_id=call.message.chat.id,
                            db_name='collections',
                            db_table='collection')
    insert_collection.create_collection(key, date)

    answer_text = Messages.COLLECTIONS['CREATE_COLLECTION']
    bot.answer_callback_query(call.id, answer_text, True)
    bot.send_message(call.message.chat.id, answer_text)
    bot.register_next_step_handler(call.message, collection_name)

def collection_name(message):
    '''Получение названия коллекции'''

    if cancel_handler(message):
        return

    user_status = Fetch(message.chat.id)
    key = user_status.user_attribute('session')
    
    insert_name = Update(message.chat.id, 'collections', 'collection')
    insert_name.collection_attribute(key, 'name', message.text)

    update_user_status = Update(message.chat.id)
    update_user_status.user_attribute('action', 0)
    update_user_status.user_attribute('session', None)
    update_user_status.change_user_attribute('collections', 1)

    # TO DO: Проверка на отличающиеся названия
    answer_text = Messages.COLLECTIONS['COLLECTION_CREATED']
    bot.send_message(message.chat.id, answer_text.format(message.text))
    bot_private_office(message)


def call_collection_menu(call):
    '''Главное меню коллекции'''

    key = re.findall(r'\w-\d+-\d+-\w+', call.data)[0]
    
    collection_info = Fetch(call.message.chat.id, 'collections', 'collection')
    collection_name = collection_info.collection_attribute('name', key)
    collection_cards = collection_info.collection_attribute('cards', key)
    collection_date = collection_info.collection_attribute('date', key)

    buttons = {}
    for collection in Messages.COLLECTION_BUTTONS:
        buttons[collection] = Messages.COLLECTION_BUTTONS[collection].format(key)

    collection_menu = keyboard_maker(2, **buttons)
    main_text = Messages.COLLECTION_MENU['INTERFACE'].format(collection_name,
                                                        collection_cards,
                                                        collection_date[:16])
    bot.answer_callback_query(call.id)
    bot.edit_message_text(text=main_text,
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        reply_markup=collection_menu)


def call_home(call):
    '''Возвращение в личный кабинет пользователя'''

    private_office_menu = keyboard_maker(3, **Messages.PRIVATE_OFFICE_BUTTONS)
    bot.answer_callback_query(call.id)
    bot.edit_message_text(text=Messages.PRIVATE_OFFICE['INTERFACE'],
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        reply_markup=private_office_menu)


def keyboard_maker(row_width=3, keyboard=None, **buttons):
    '''Создание клавиатур меню'''

    if not keyboard:
        keyboard = types.InlineKeyboardMarkup(row_width)

    keyboard_buttons = [types.InlineKeyboardButton(text=text,
        callback_data=data) for text, data in buttons.items()]

    keyboard.add(*keyboard_buttons)
    return keyboard

def error_handler(message):
    '''Проверка на наличие ошибки'''

    user_status = Fetch(message.chat.id)
    status = user_status.user_attribute('action')
    menu_id = user_status.user_attribute('menu_id')

    if status == 1:
        bot.send_message(message.chat.id, Messages.ERRORS[1])
        return True

    elif status == 2:
        bot.send_message(message.chat.id, Messages.ERRORS[2])
        return True

    elif message.message_id != menu_id and status != 1:
        bot.edit_message_text(text=Messages.ASSISTANCE['OLD_SESSION'],
                            chat_id=message.chat.id,
                            message_id=message.message_id)
        return True

    return False

def cancel_handler(message):
    '''Проверка на отмену операции'''

    if message.text == '/cancel' or message.text.lower() == 'отмена':
        bot_cancel(message)
        return True

    return False

if __name__ == '__main__':
    bot.polling()
