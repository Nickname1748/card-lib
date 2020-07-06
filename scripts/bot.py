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
        if 'show' in call.data:
            call_collection_menu(call)

        elif 'create' in call.data:
            call_create_collection(call)

        elif 'continue' in call.data:
            pass

        elif 'rename' in call.data:
            call_rename_collection(call)

        elif 'delete' in call.data:
            if 'yes' in call.data:
                call_delete_collection_yes(call)

            elif 'no' in call.data:
                call_delete_collection_no(call)

            else:
                call_delete_collection_menu(call)

        else:
            call_collections_menu(call)

    elif 'card' in call.data:
        if 'show' in call.data:
            pass

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
            buttons[collection[3]] = f'collection_show_{collection[1]}'
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
    
    duplicate_name = Fetch(message.chat.id, 'collections', 'collection')
    result = duplicate_name.copy_check('name', message.text)
    
    if result:
        bot.send_message(message.chat.id, Messages.ERRORS[4])
        bot.register_next_step_handler(message, collection_name)
        return

    user_status = Fetch(message.chat.id)
    key = user_status.user_attribute('session')
    
    insert_name = Update(message.chat.id, 'collections', 'collection')
    insert_name.collection_attribute(key, 'name', message.text)

    update_user_status = Update(message.chat.id)
    update_user_status.user_attribute('action', 0)
    update_user_status.user_attribute('session', None)
    update_user_status.change_user_attribute('collections', 1)

    answer_text = Messages.COLLECTIONS['COLLECTION_CREATED']
    bot.send_message(message.chat.id, answer_text.format(message.text))
    bot_private_office(message)


def call_collection_menu(call):
    '''Главное меню коллекции'''

    key = re.findall(r'\w-\d+-\d+-\w+', call.data)[0]
    
    collection_info = Fetch(call.message.chat.id, 'collections', 'collection')
    collection_name = collection_info.collection_attribute(key, 'name')
    collection_cards = collection_info.collection_attribute(key, 'cards')
    collection_date = collection_info.collection_attribute(key, 'date')

    buttons = keyboard_format(Messages.COLLECTION_BUTTONS, key)
    collection_menu = keyboard_maker(2, **buttons)
    main_text = Messages.COLLECTION_MENU['INTERFACE'].format(collection_name,
                                                        collection_cards,
                                                        collection_date[:16])
    bot.answer_callback_query(call.id)
    bot.edit_message_text(text=main_text,
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        reply_markup=collection_menu)

def call_rename_collection(call):
    '''Переименование коллекции'''

    if error_handler(call.message) or cancel_handler(call.message):
        return
    
    key = re.findall(r'\w-\d+-\d+-\w+', call.data)[0]
    update_user_status = Update(call.message.chat.id)
    update_user_status.user_attribute('action', 2)
    update_user_status.user_attribute('session', key)

    answer_text = Messages.COLLECTIONS['RENAME_COLLECTION']
    bot.answer_callback_query(call.id, answer_text, True)
    bot.send_message(call.message.chat.id, answer_text)
    bot.register_next_step_handler(call.message, rename_collection)

def rename_collection(message):
    '''Получение нового названия коллекции'''

    if cancel_handler(message):
        return
    
    duplicate_name = Fetch(message.chat.id, 'collections', 'collection')
    result = duplicate_name.copy_check('name', message.text)
    
    if result:
        bot.send_message(message.chat.id, Messages.ERRORS[4])
        bot.register_next_step_handler(message, collection_name)
        return

    user_status = Fetch(message.chat.id)
    key = user_status.user_attribute('session')
    old_name = duplicate_name.collection_attribute(key, 'name')

    insert_name = Update(message.chat.id, 'collections', 'collection')
    insert_name.collection_attribute(key, 'name', message.text)

    update_user_status = Update(message.chat.id)
    update_user_status.user_attribute('action', 0)
    update_user_status.user_attribute('session', None)

    answer = Messages.COLLECTIONS['COLLECTION_RENAMED']
    bot.send_message(message.chat.id, answer.format(old_name, message.text))
    bot_private_office(message)

def call_delete_collection_menu(call):
    '''Меню удаления коллекции'''

    key = re.findall(r'\w-\d+-\d+-\w+', call.data)[0]
    buttons = keyboard_format(Messages.DELETE_COLLECTION_BUTTONS, key)
    delete_collection = keyboard_maker(1, **buttons)

    bot.answer_callback_query(call.id)
    bot.edit_message_text(text=Messages.DELETE_COLLECTION['DELETE'],
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        reply_markup=delete_collection)

def call_delete_collection_yes(call):
    '''Согласие на удаление коллекции'''

    key = re.findall(r'\w-\d+-\d+-\w+', call.data)[0]
    fetch_collection_name = Fetch(user_id=call.message.chat.id,
                                db_name='collections',
                                db_table='collection')
    collection_name = fetch_collection_name.collection_attribute(key, 'name')

    update_user_status = Update(call.message.chat.id)
    update_user_status.change_user_attribute('collections', -1)

    delete_collection = Delete(user_id=call.message.chat.id,
                            db_name='collections',
                            db_table='collection')
    delete_collection.delete_collection(key)

    successful_delete_text = Messages.DELETE_COLLECTION[
                                'DELETE_SUCCESSFUL'].format(collection_name)
    bot.answer_callback_query(call.id, successful_delete_text, True)
    call_collections_menu(call)

def call_delete_collection_no(call):
    '''Отмена удаления коллекции'''

    canceled_delete_text = Messages.DELETE_COLLECTION['DELETE_CANCELED']
    bot.answer_callback_query(call.id, canceled_delete_text, True)
    call_collection_menu(call)


def call_home(call):
    '''Возвращение в личный кабинет пользователя'''

    private_office_menu = keyboard_maker(3, **Messages.PRIVATE_OFFICE_BUTTONS)
    bot.answer_callback_query(call.id)
    bot.edit_message_text(text=Messages.PRIVATE_OFFICE['INTERFACE'],
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        reply_markup=private_office_menu)


def keyboard_maker(row_width=3, keyboard=None, **buttons):
    '''
    Создание клавиатур меню
    
    :return: Клавиатура
    '''

    if not keyboard:
        keyboard = types.InlineKeyboardMarkup(row_width)

    keyboard_buttons = [types.InlineKeyboardButton(text=text,
        callback_data=data) for text, data in buttons.items()]

    keyboard.add(*keyboard_buttons)
    return keyboard

def keyboard_format(buttons=None, format_object=None):
    '''
    Создание клавиатур с вставляемыми элементами
    
    :return: Клавиатура
    '''

    keyboard = {}
    for button in buttons:
        keyboard[button] = buttons[button].format(format_object)

    return keyboard

def error_handler(message):
    '''Проверка на наличие ошибок'''

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
        bot.edit_message_text(text=Messages.ERRORS[3],
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
