import telebot
from telebot import types

from texts import Messages
from config import Tokens
from database import Insert, Fetch, Update, Delete

import re
import random

from datetime import datetime

bot = telebot.TeleBot(Tokens.TOKEN)

@bot.message_handler(commands=['start'])
def bot_start(message):
    '''Начало работы с ботом'''

    # Добавление нового пользователя в базу данных
    insert_user = Insert(message.chat.id)
    insert_user.new_user(username=message.from_user.username,
                        first_name=message.from_user.first_name,
                        last_name=message.from_user.last_name)

    bot.send_message(message.chat.id, Messages.ASSISTANCE['START'])
    bot_private_office(message)

@bot.message_handler(commands=['office'])
def bot_private_office(message):
    '''Личный кабинет пользователя'''

    menu = keyboard_maker(3, **Messages.PRIVATE_OFFICE_BUTTONS)
    menu_message = bot.send_message(chat_id=message.chat.id,
                                    text=Messages.PRIVATE_OFFICE['INTERFACE'],
                                    reply_markup=menu)

    # Обновление id сообщения Личного кабинета
    update_menu_id = Update(message.chat.id)
    update_menu_id.user_attribute('menu_id', menu_message.message_id)

@bot.message_handler(commands=['cancel'])
def bot_cancel(message):
    '''Отмена текущей операции'''

    # Получение информации о статусе пользователя из базы данных
    user_status = Fetch(message.chat.id)
    action = user_status.user_attribute('action')
    session = user_status.user_attribute('session')

    if action == 1:
        # Удаление зарезервированного под коллекцию места из базы данных
        delete_session = Delete(message.chat.id, 'collections', 'collection')
        delete_session.delete_collection(session)
    elif action == 3:
        # Удаление зарезервированного под карту места из базы данных
        delete_session = Delete(message.chat.id, 'collections', 'card')
        delete_session.delete_card(session)

    # Обовление статуса пользователя
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

        elif 'info' in call.data:
            if 'on' in call.data:
                call_info_on(call)
            else:
                call_card_menu(call)

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

    # Получение информации о пользователе
    user_info = Fetch(call.message.chat.id)
    user_username = user_info.user_attribute('username')
    collections = user_info.user_attribute('collections')
    cards = user_info.user_attribute('cards')
    
    # Создание меню профиля пользователя
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

    # Получение информации о коллекции из базы данных
    collections = Fetch(call.message.chat.id, 'collections', 'collection')
    collections_info = collections.user_collections()

    if collections_info:
        # Создание меню из всех коллекций пользователя
        buttons = buttons_format('collection_show_{}', collections_info, 3, 1)
        collections_keyboard = keyboard_maker(2, **buttons)
    else:
        collections_keyboard = None

    # Создание навигации
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

    # Обовление статуса пользователя
    update_user_status = Update(call.message.chat.id)
    update_user_status.user_attribute('action', 1)
    update_user_status.user_attribute('session', key)

    # Резервирование места для коллекции в базе данных
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
    
    # Проверка на существование дубликата коллекции в базе данных
    duplicate_name = Fetch(message.chat.id, 'collections', 'collection')
    result = duplicate_name.copy_check('name', message.text)
    
    if result:
        bot.send_message(message.chat.id, Messages.ERRORS[3])
        bot.register_next_step_handler(message, collection_name)
        return

    # Получение уникального ключа коллекции из базы данных
    user_status = Fetch(message.chat.id)
    key = user_status.user_attribute('session')
    
    # Запись названия коллекции в базу данных
    insert_name = Update(message.chat.id, 'collections', 'collection')
    insert_name.collection_attribute(key, 'name', message.text)

    # Обовление статуса пользователя
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
    
    # Получение информации о коллекции из базы данных
    collection_info = Fetch(call.message.chat.id, 'collections', 'collection')
    collection_name = collection_info.collection_attribute(key, 'name')
    collection_cards = collection_info.collection_attribute(key, 'cards')
    collection_date = collection_info.collection_attribute(key, 'date')

    # Создание меню коллекции
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

    # Обовление статуса пользователя
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
    
    # Получение названия коллекции для проверки на существование дубликата
    # коллекции в базе данных
    duplicate_name = Fetch(message.chat.id, 'collections', 'collection')
    result = duplicate_name.copy_check('name', message.text)
    
    if result:
        bot.send_message(message.chat.id, Messages.ERRORS[3])
        bot.register_next_step_handler(message, collection_name)
        return

    # Получение уникального ключа и старого названия коллекции
    user_status = Fetch(message.chat.id)
    key = user_status.user_attribute('session')
    old_name = duplicate_name.collection_attribute(key, 'name')

    # Обновление названия коллекции в базе данных
    insert_name = Update(message.chat.id, 'collections', 'collection')
    insert_name.collection_attribute(key, 'name', message.text)

    # Обовление статуса пользователя
    update_user_status = Update(message.chat.id)
    update_user_status.user_attribute('action', 0)
    update_user_status.user_attribute('session', None)

    text = Messages.COLLECTIONS['COLLECTION_RENAMED']
    bot.send_message(message.chat.id, text.format(old_name, message.text))
    bot_private_office(message)

def call_delete_collection_menu(call):
    '''Меню удаления коллекции'''

    # Создание меню удаления коллекции
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

    # Получение имени коллекции из базы данных
    collection_info = Fetch(call.message.chat.id, 'collections', 'collection')
    collection_name = collection_info.collection_attribute(key, 'name')

    # Изменение количества коллекций в профиле пользователя
    update_user_status = Update(call.message.chat.id)
    update_user_status.change_user_attribute('collections', -1)

    # Удаление коллекции из базы данных
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

    key = re.findall(r'\w-\d+-\d+-\w', call.data)[0]
    level = int(re.findall(r'_\w+-\d+-\d+-\w+_\w+_(\d+)', call.data)[0])

    # Получение названия коллекции из базы данных
    collection_info = Fetch(call.message.chat.id, 'collections', 'collection')
    collection_name = collection_info.collection_attribute(key, 'name')

    # Получение информации о карте из базы данных
    fetch_cards = Fetch(call.message.chat.id, 'collections', 'card')
    cards_info = fetch_cards.user_cards(key)
    
    if cards_info:
        # Добавление в меню кнопок навигации
        nav_obj = cards_info[8*level:8*(level+1)]
        navigation = keyboard_navigation(key, cards_info, level)

        # Создание меню из всех карт определенной коллекции пользователя
        buttons = buttons_format('card_show_{}', nav_obj, 4, 2)
        cards_keyboard = keyboard_maker(2, navigation, **buttons)
    else:
        cards_keyboard = None

    # Добавление в меню кнопок выхода
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

    # Обовление статуса пользователя
    update_user_status = Update(call.message.chat.id)
    update_user_status.user_attribute('action', 3)
    update_user_status.user_attribute('session', card_key)

    # Резервирование места для карты в базе данных
    insert_card = Insert(call.message.chat.id, 'collections', 'card')
    insert_card.create_card(key, card_key, date)

    text = Messages.CARDS['CARD_NAME']
    bot.answer_callback_query(call.id, text, True)
    bot.send_message(call.message.chat.id, text)
    bot.register_next_step_handler(call.message, card_name)

def card_name(message):
    '''Получение названия карты'''

    if cancel_handler(message):
        return
    
    # Получение уникального ключа карты
    user_status = Fetch(message.chat.id)
    card_key = user_status.user_attribute('session')

    # Получение уникального ключа коллекции, которой принадлежит карта
    card_collection_info = Fetch(message.chat.id, 'collections', 'card')
    key = card_collection_info.card_attribute(card_key, 'key')

    # Проверка на существование дубликата карты в базе данных
    duplicate_name = Fetch(message.chat.id, 'collections', 'card')
    result = duplicate_name.card_copy_check(key, 'name', message.text)
    
    if result:
        bot.send_message(message.chat.id, Messages.ERRORS[6])
        bot.register_next_step_handler(message, card_name)
        return
    
    # Запись имени карты в базу данных
    insert_name = Update(message.chat.id, 'collections', 'card')
    insert_name.card_attribute(card_key, 'name', message.text)

    text = Messages.CARDS['CARD_DESCRIPTION']
    bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(message, card_description)

def card_description(message):
    '''Получение описания карты'''

    if cancel_handler(message):
        return

    # Получение уникального ключа карты
    user_status = Fetch(message.chat.id)
    card_key = user_status.user_attribute('session')

    # Получение уникального ключа коллекции, которой принадлежит карта
    card_collection_info = Fetch(message.chat.id, 'collections', 'card')
    key = card_collection_info.card_attribute(card_key, 'key')

    # Получение имени карты
    card_info = Fetch(message.chat.id, 'collections', 'card')
    card_name = card_info.card_attribute(card_key, 'name')
    
    # Запись описания карты в базу данных
    insert_name = Update(message.chat.id, 'collections', 'card')
    insert_name.card_attribute(card_key, 'description', message.text)

    # Обовление статуса пользователя и количества карт
    update_user_status = Update(message.chat.id)
    update_user_status.user_attribute('action', 0)
    update_user_status.user_attribute('session', None)
    update_user_status.change_user_attribute('cards', 1)

    # Обновление количества карт в коллекции пользователя
    collection_cards = Update(message.chat.id, 'collections', 'collection')
    collection_cards.change_collection_attribute(key, 'cards', 1)

    text = Messages.CARDS['CARD_CREATED']
    bot.send_message(message.chat.id, text.format(card_name))
    bot_private_office(message)


def call_card_menu(call):
    '''Главное меню карты'''

    card_key = re.findall(r'\w-\d+-\d+-\w+', call.data)[0]

    # Получение информации о карте из базы данных
    card_info = Fetch(call.message.chat.id, 'collections', 'card')
    card_name = card_info.card_attribute(card_key, 'name')
    card_collection = card_info.card_attribute(card_key, 'key')
    card_description = card_info.card_attribute(card_key, 'description')

    # Создание меню карты
    m_buttons = keyboard_format(Messages.CARD_MENU_BUTTONS, card_key)
    card_buttons = keyboard_maker(2, **m_buttons)
    b_buttons = keyboard_format(Messages.CARD_BOTTOM_BUTTONS, card_collection)
    card_menu = keyboard_maker(2, card_buttons, **b_buttons)

    main_text = Messages.CARD_MENU['INTERFACE'].format(card_name,
                                                    card_description)
    bot.answer_callback_query(call.id)
    bot.edit_message_text(text=main_text,
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        reply_markup=card_menu,
                        parse_mode='Markdown')

def call_rename_card(call):
    '''Переименование карты'''

    if error_handler(call.message) or cancel_handler(call.message):
        return
    
    card_key = re.findall(r'\w-\d+-\d+-\w+', call.data)[0]

    # Обовление статуса пользователя
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

    # Получение уникального ключа карты
    user_status = Fetch(message.chat.id)
    card_key = user_status.user_attribute('session')

    # Получение уникального ключа коллекции, которой принадлежит карта
    card_collection_info = Fetch(message.chat.id, 'collections', 'card')
    key = card_collection_info.card_attribute(card_key, 'key')
    
    # Получение старого имени карты и проверка на существование дубликата
    # карты в базе данных
    duplicate_name = Fetch(message.chat.id, 'collections', 'card')
    result = duplicate_name.card_copy_check(key, 'name', message.text)
    old_name = duplicate_name.card_attribute(card_key, 'name')
    
    if result:
        bot.send_message(message.chat.id, Messages.ERRORS[6])
        bot.register_next_step_handler(message, rename_card)
        return

    # Обновление имени карты в базе данных
    insert_name = Update(message.chat.id, 'collections', 'card')
    insert_name.card_attribute(card_key, 'name', message.text)

    # Обовление статуса пользователя
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

    # Обовление статуса пользователя
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

    # Получение уникального ключа карты из базы данных
    user_status = Fetch(message.chat.id)
    card_key = user_status.user_attribute('session')

    # Обновление описания карты
    insert_description = Update(message.chat.id, 'collections', 'card')
    insert_description.card_attribute(card_key, 'description', message.text)

    # Обовление статуса пользователя
    update_user_status = Update(message.chat.id)
    update_user_status.user_attribute('action', 0)
    update_user_status.user_attribute('session', None)

    bot.send_message(message.chat.id, Messages.CARDS['CARD_EDITED'])
    bot_private_office(message)

def call_delete_card_menu(call):
    '''Меню удаления карты'''

    card_key = re.findall(r'\w-\d+-\d+-\w+', call.data)[0]

    # Создание меню удаления карты
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

    # Получение информации о карте из базы данных
    card_info = Fetch(call.message.chat.id, 'collections', 'card')
    card_name = card_info.card_attribute(card_key, 'name')
    key = card_info.card_attribute(card_key, 'key')

    # Обновление количества карт пользователя
    update_user_status = Update(call.message.chat.id)
    update_user_status.change_user_attribute('cards', -1)

    # Обновление количества карт в коллекции пользователя
    collection_cards = Update(call.message.chat.id, 'collections', 'collection')
    collection_cards.change_collection_attribute(key, 'cards', -1)

    # Удаление карты из базы данных
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

def call_info_on(call):
    '''Показать дополнительную информацию о карте'''

    card_key = re.findall(r'\w-\d+-\d+-\w+', call.data)[0]

    # Получение информации о карте из базы даных
    card_info = Fetch(call.message.chat.id, 'collections', 'card')
    card_name = card_info.card_attribute(card_key, 'name')
    card_collection = card_info.card_attribute(card_key, 'key')
    card_description = card_info.card_attribute(card_key, 'description')
    card_date = card_info.card_attribute(card_key, 'date')

    # Создание меню карты
    m_buttons = keyboard_format(Messages.CARD_INFO_MENU_BUTTONS, card_key)
    card_buttons = keyboard_maker(2, **m_buttons)
    b_buttons = keyboard_format(Messages.CARD_BOTTOM_BUTTONS, card_collection)
    card_menu = keyboard_maker(2, card_buttons, **b_buttons)

    main_text = Messages.CARD_MENU['INFO_INTERFACE'].format(card_name,
                                                    card_description,
                                                    card_date[:16])
    bot.answer_callback_query(call.id)
    bot.edit_message_text(text=main_text,
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        reply_markup=card_menu,
                        parse_mode='Markdown')


def call_home(call):
    '''Возвращение в личный кабинет пользователя'''

    bot.answer_callback_query(call.id)
    private_office_menu = keyboard_maker(**Messages.PRIVATE_OFFICE_BUTTONS)
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

def keyboard_format(buttons, format_object):
    '''
    Создание клавиатур с вставляемыми элементами
    
    :return: Клавиатура
    '''

    keyboard = {}
    for button in buttons:
        keyboard[button] = buttons[button].format(format_object)

    return keyboard

def buttons_format(call, object_info, call_id=None, name_id=None):
    '''Создание кнопок с вставляемыми элементами
    
    :return: Кнопки
    '''

    buttons = {}
    for item in object_info:
        buttons[item[call_id]] = call.format(item[name_id])
            
    return buttons

def keyboard_navigation(key, nav_obj, level):
    '''Создание навигационной клавиатуры'''
    
    navigation = {
        'main': '• {} •', 
        'other': '{}', 
        'data': 'cards_{}_level_{}'
    }
    lenght = len(nav_obj)
    system_len = lenght // 8 if lenght % 8 == 0 else lenght // 8 + 1

    keyboard = types.InlineKeyboardMarkup(2)
    buttons = []
    if lenght < 41:
        buttons = [types.InlineKeyboardButton(
            text=navigation['main'].format(button + 1)
            if button == level
            else navigation['other'].format(button + 1),
            callback_data=navigation['data'].format(key, button))
            for button in range(system_len)]
    else:
        for button in range(5):
            if level == 0 or level  == 1:
                nav = {0: '{}', 1: '{}', 2: '{}', 3: '{} ›', 4: '{} »'}
                nav[level] = '• {} •'

                button_format = system_len if button == 4 else button + 1
                text = nav[button].format(button_format)
            elif level == (system_len - 1) or level == (system_len - 2):
                nav = {0: '« {}', 1: '‹ {}', 2: '{}', 3: '{}', 4: '{}'}
                nav[5 + level - system_len] = '• {} •'

                button_format = button+1 if button==0 else system_len+button-4
                text = nav[button].format(button_format)
            else:
                nav = {0: '« {}', 1: '‹ {}', 2: '• {} •', 3: '{} ›', 4: '{} »'}

                if button == 0:
                    button_format = button + 1
                elif button == 1 or button == 2 or button == 3:
                    button_format = level + button - 1
                else:
                    button_format = system_len

                text = nav[button].format(button_format)

            buttons.append(types.InlineKeyboardButton(text=text,
                callback_data=navigation['data'].format(key, button_format-1)))

    keyboard.row(*buttons)
    return keyboard

def error_handler(message):
    '''
    Проверка на наличие ошибок
    
    :return:
    '''

    # Получение информации о действиях пользователя
    # и id его последнего Личного кабинета
    user_status = Fetch(message.chat.id)
    action = user_status.user_attribute('action')
    menu_id = user_status.user_attribute('menu_id')

    if action == 1:
        bot.send_message(message.chat.id, Messages.ERRORS[1])
        return True

    elif action == 2:
        bot.send_message(message.chat.id, Messages.ERRORS[2])
        return True

    elif action == 3:
        bot.send_message(message.chat.id, Messages.ERRORS[4])
        return True

    elif action == 4:
        bot.send_message(message.chat.id, Messages.ERRORS[5])
        return True
    
    elif action == 5:
        bot.send_message(message.chat.id, Messages.ERRORS[7])
        return True

    elif message.message_id != menu_id and action != 1:
        bot.edit_message_text(text=Messages.ERRORS[0],
                            chat_id=message.chat.id,
                            message_id=message.message_id)
        return True

    return False

def cancel_handler(message):
    '''Проверка на отмену операции'''

    if (not message.text
            or message.text == '/cancel'
            or message.text.lower() == 'отмена'):
        bot_cancel(message)
        return True

    return False


if __name__ == '__main__':
    bot.polling()
