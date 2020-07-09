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
    elif status == 3:
        delete_session = Delete(message.chat.id, 'collections', 'card')
        delete_session.delete_card(session)

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
            call_card_menu(call)

        elif 'create' in call.data:
            call_create_card(call)

        elif 'rename' in call.data:
            call_rename_card(call)

        elif 'description' in call.data:
            call_edit_card_description(call)

        elif 'level' in call.data:
            pass

        elif 'delete' in call.data:
            if 'yes' in call.data:
                call_delete_card_yes(call)

            elif 'no' in call.data:
                call_delete_card_no(call)

            else:
                call_delete_card_menu(call)
        
        else:
            call_cards_menu(call)

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

    if collections_info:
        buttons = buttons_format('collection_show_{}', collections_info, 3, 1)
        collections_keyboard = keyboard_maker(2, **buttons)
    else:
        collections_keyboard = None

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

    text = Messages.COLLECTIONS['CREATE_COLLECTION']
    bot.answer_callback_query(call.id, text, True)
    bot.send_message(call.message.chat.id, text)
    bot.register_next_step_handler(call.message, collection_name)

def collection_name(message):
    '''Получение названия коллекции'''

    if cancel_handler(message):
        return
    
    duplicate_name = Fetch(message.chat.id, 'collections', 'collection')
    result = duplicate_name.copy_check('name', message.text)
    
    if result:
        bot.send_message(message.chat.id, Messages.ERRORS[3])
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

    text = Messages.COLLECTIONS['COLLECTION_CREATED']
    bot.send_message(message.chat.id, text.format(message.text))
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

    text = Messages.COLLECTIONS['RENAME_COLLECTION']
    bot.answer_callback_query(call.id, text, True)
    bot.send_message(call.message.chat.id, text)
    bot.register_next_step_handler(call.message, rename_collection)

def rename_collection(message):
    '''Получение нового названия коллекции'''

    if cancel_handler(message):
        return
    
    duplicate_name = Fetch(message.chat.id, 'collections', 'collection')
    result = duplicate_name.copy_check('name', message.text)
    
    if result:
        bot.send_message(message.chat.id, Messages.ERRORS[3])
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

    text = Messages.COLLECTIONS['COLLECTION_RENAMED']
    bot.send_message(message.chat.id, text.format(old_name, message.text))
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
    collection_info = Fetch(call.message.chat.id, 'collections', 'collection')
    collection_name = collection_info.collection_attribute(key, 'name')

    update_user_status = Update(call.message.chat.id)
    update_user_status.change_user_attribute('collections', -1)

    delete_collection = Delete(user_id=call.message.chat.id,
                            db_name='collections',
                            db_table='collection')
    delete_collection.delete_collection(key)

    text = Messages.DELETE_COLLECTION[
                    'DELETE_SUCCESSFUL'].format(collection_name)
    bot.answer_callback_query(call.id, text, True)
    call_collections_menu(call)

def call_delete_collection_no(call):
    '''Отмена удаления коллекции'''

    canceled_delete_text = Messages.DELETE_COLLECTION['DELETE_CANCELED']
    bot.answer_callback_query(call.id, canceled_delete_text, True)
    call_collection_menu(call)


def call_cards_menu(call):
    '''Карты определенной коллекции пользователя'''

    key = re.findall(r'\w-\d+-\d+-\w+', call.data)[0]
    collection_info = Fetch(call.message.chat.id, 'collections', 'collection')
    collection_name = collection_info.collection_attribute(key, 'name')

    fetch_cards = Fetch(call.message.chat.id, 'collections', 'card')
    cards_info = fetch_cards.user_cards(key)
    
    if cards_info:
        buttons = buttons_format('card_show_{}', cards_info, 4, 2)
        cards_keyboard = keyboard_maker(2, **buttons)
    else:
        cards_keyboard = None

    cards_buttons = keyboard_format(Messages.CARDS_BUTTONS, key)
    cards_menu = keyboard_maker(2, cards_keyboard, **cards_buttons)

    bot.answer_callback_query(call.id)
    text = Messages.CARDS['INTERFACE'].format(collection_name)
    bot.edit_message_text(text=text,
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        reply_markup=cards_menu)

def call_create_card(call):
    '''Создание карты'''

    if error_handler(call.message) or cancel_handler(call.message):
        return
    
    key = re.findall(r'\w-\d+-\d+-\w+', call.data)[0]
    card_key = f'c-{random.randint(1, 1000000)}-{random.randint(1, 1000)}-d'
    date = datetime.now()

    update_user_status = Update(call.message.chat.id)
    update_user_status.user_attribute('action', 3)
    update_user_status.user_attribute('session', card_key)

    insert_collection = Insert(user_id=call.message.chat.id,
                            db_name='collections',
                            db_table='card')
    insert_collection.create_card(key, card_key, date)

    text = Messages.CARDS['CARD_NAME']
    bot.answer_callback_query(call.id, text, True)
    bot.send_message(call.message.chat.id, text)
    bot.register_next_step_handler(call.message, card_name)

def card_name(message):
    '''Получение названия карты'''

    if cancel_handler(message):
        return
    
    user_status = Fetch(message.chat.id)
    card_key = user_status.user_attribute('session')
    card_collection_info = Fetch(message.chat.id, 'collections', 'card')
    key = card_collection_info.card_attribute(card_key, 'key')

    duplicate_name = Fetch(message.chat.id, 'collections', 'card')
    result = duplicate_name.card_copy_check(key, 'name', message.text)
    
    if result:
        bot.send_message(message.chat.id, Messages.ERRORS[6])
        bot.register_next_step_handler(message, card_name)
        return
    
    insert_name = Update(message.chat.id, 'collections', 'card')
    insert_name.card_attribute(card_key, 'name', message.text)

    text = Messages.CARDS['CARD_DESCRIPTION']
    bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(message, card_description)

def card_description(message):
    '''Получение описания карты'''

    if cancel_handler(message):
        return

    user_status = Fetch(message.chat.id)
    card_key = user_status.user_attribute('session')

    card_collection_info = Fetch(message.chat.id, 'collections', 'card')
    key = card_collection_info.card_attribute(card_key, 'key')

    card_info = Fetch(message.chat.id, 'collections', 'card')
    card_name = card_info.card_attribute(card_key, 'name')
    
    insert_name = Update(message.chat.id, 'collections', 'card')
    insert_name.card_attribute(card_key, 'description', message.text)

    update_user_status = Update(message.chat.id)
    update_user_status.user_attribute('action', 0)
    update_user_status.user_attribute('session', None)
    update_user_status.change_user_attribute('cards', 1)

    collection_cards = Update(message.chat.id, 'collections', 'collection')
    collection_cards.change_collection_attribute(key, 'cards', 1)

    text = Messages.CARDS['CARD_CREATED']
    bot.send_message(message.chat.id, text.format(card_name))
    bot_private_office(message)


def call_card_menu(call):
    '''Главное меню карты'''

    card_key = re.findall(r'\w-\d+-\d+-\w+', call.data)[0]

    card_info = Fetch(call.message.chat.id, 'collections', 'card')
    card_name = card_info.card_attribute(card_key, 'name')
    card_collection = card_info.card_attribute(card_key, 'key')
    card_description = card_info.card_attribute(card_key, 'description')
    card_date = card_info.card_attribute(card_key, 'date')

    m_buttons = keyboard_format(Messages.CARD_MENU_BUTTONS, card_key)
    card_buttons = keyboard_maker(2, **m_buttons)
    b_buttons = keyboard_format(Messages.CARD_BOTTOM_BUTTONS, card_collection)
    card_menu = keyboard_maker(2, card_buttons, **b_buttons)

    main_text = Messages.CARD_MENU['INTERFACE'].format(card_name,
                                                    card_description,
                                                    card_date[:16])
    bot.answer_callback_query(call.id)
    bot.edit_message_text(text=main_text,
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        reply_markup=card_menu)

def call_rename_card(call):
    '''Переименование карты'''

    if error_handler(call.message) or cancel_handler(call.message):
        return
    
    card_key = re.findall(r'\w-\d+-\d+-\w+', call.data)[0]
    update_user_status = Update(call.message.chat.id)
    update_user_status.user_attribute('action', 4)
    update_user_status.user_attribute('session', card_key)

    text = Messages.CARDS['RENAME_CARD']
    bot.answer_callback_query(call.id, text, True)
    bot.send_message(call.message.chat.id, text)
    bot.register_next_step_handler(call.message, rename_card)

def rename_card(message):
    '''Получение нового названия карты'''

    if cancel_handler(message):
        return

    user_status = Fetch(message.chat.id)
    card_key = user_status.user_attribute('session')
    card_collection_info = Fetch(message.chat.id, 'collections', 'card')
    key = card_collection_info.card_attribute(card_key, 'key')
    
    duplicate_name = Fetch(message.chat.id, 'collections', 'card')
    result = duplicate_name.card_copy_check(key, 'name', message.text)
    old_name = duplicate_name.card_attribute(card_key, 'name')
    
    if result:
        bot.send_message(message.chat.id, Messages.ERRORS[6])
        bot.register_next_step_handler(message, rename_card)
        return

    insert_name = Update(message.chat.id, 'collections', 'card')
    insert_name.card_attribute(card_key, 'name', message.text)

    update_user_status = Update(message.chat.id)
    update_user_status.user_attribute('action', 0)
    update_user_status.user_attribute('session', None)

    text = Messages.CARDS['CARD_RENAMED']
    bot.send_message(message.chat.id, text.format(old_name, message.text))
    bot_private_office(message)

def call_edit_card_description(call):
    '''Изменение описания карты'''

    if error_handler(call.message) or cancel_handler(call.message):
        return
    
    card_key = re.findall(r'\w-\d+-\d+-\w+', call.data)[0]
    update_user_status = Update(call.message.chat.id)
    update_user_status.user_attribute('action', 5)
    update_user_status.user_attribute('session', card_key)

    text = Messages.CARDS['EDIT_DESCRIPTION_CARD']
    bot.answer_callback_query(call.id, text, True)
    bot.send_message(call.message.chat.id, text)
    bot.register_next_step_handler(call.message, edit_card_description)

def edit_card_description(message):
    '''Получение нового описания карты'''

    if cancel_handler(message):
        return

    user_status = Fetch(message.chat.id)
    card_key = user_status.user_attribute('session')
    
    card_info = Fetch(message.chat.id, 'collections', 'card')
    old_description = card_info.card_attribute(card_key, 'description')

    insert_description = Update(message.chat.id, 'collections', 'card')
    insert_description.card_attribute(card_key, 'description', message.text)

    update_user_status = Update(message.chat.id)
    update_user_status.user_attribute('action', 0)
    update_user_status.user_attribute('session', None)

    text = Messages.CARDS['CARD_EDITED']
    bot.send_message(message.chat.id, text.format(old_description,
                                                message.text))
    bot_private_office(message)

def call_delete_card_menu(call):
    '''Меню удаления карты'''

    card_key = re.findall(r'\w-\d+-\d+-\w+', call.data)[0]
    buttons = keyboard_format(Messages.DELETE_CARD_BUTTONS, card_key)
    delete_card = keyboard_maker(1, **buttons)

    bot.answer_callback_query(call.id)
    bot.edit_message_text(text=Messages.DELETE_CARD['DELETE'],
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        reply_markup=delete_card)

def call_delete_card_yes(call):
    '''Согласие на удаление карты'''

    card_key = re.findall(r'\w-\d+-\d+-\w+', call.data)[0]
    card_info = Fetch(call.message.chat.id, 'collections', 'card')
    card_name = card_info.card_attribute(card_key, 'name')
    key = card_info.card_attribute(card_key, 'key')

    update_user_status = Update(call.message.chat.id)
    update_user_status.change_user_attribute('cards', -1)

    collection_cards = Update(call.message.chat.id, 'collections', 'collection')
    collection_cards.change_collection_attribute(key, 'cards', -1)

    delete_card = Delete(call.message.chat.id, 'collections', 'card')
    delete_card.delete_card(card_key)

    text = Messages.DELETE_CARD['DELETE_SUCCESSFUL'].format(card_name)
    bot.answer_callback_query(call.id, text, True)
    call_collections_menu(call)

def call_delete_card_no(call):
    '''Отмена удаления карты'''

    canceled_delete_text = Messages.DELETE_CARD['DELETE_CANCELED']
    bot.answer_callback_query(call.id, canceled_delete_text, True)
    call_card_menu(call)


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

def buttons_format(call='', object_info=None,
                call_id=None, name_id=None):
    '''Создание кнопок с вставляемыми элементами
    
    :return: Кнопки'''

    buttons = {}
    for item in object_info:
        buttons[item[call_id]] = call.format(item[name_id])
            
    return buttons

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

    elif status == 3:
        bot.send_message(message.chat.id, Messages.ERRORS[4])
        return True

    elif status == 4:
        bot.send_message(message.chat.id, Messages.ERRORS[5])
        return True
    
    elif status == 5:
        bot.send_message(message.chat.id, Messages.ERRORS[7])
        return True

    elif message.message_id != menu_id and status != 1:
        bot.edit_message_text(text=Messages.ERRORS[0],
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
