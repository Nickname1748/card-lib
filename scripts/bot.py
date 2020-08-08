import telebot
from telebot import types
from datetime import datetime, timedelta

import re
import random
import locale

from texts import Messages
from config import Tokens
from database import Insert, Fetch, Update, Delete

locale.setlocale(locale.LC_ALL, "")
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
    try:
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
                call_collection_continue(call)

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

            elif 'result' in call.data:
                call_result(call)

            elif 'continue' in call.data:
                call_card_continue(call)

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
    except:
        bot.send_message(call.message.chat.id, Messages.ASSISTANCE['LOADING'])



def call_profile_menu(call):
    '''Профиль пользователя'''

    # Получение информации о пользователе
    user_info = Fetch(call.message.chat.id)
    username = user_info.user_attribute('username')
    karma = user_info.user_attribute('karma')
    collections = user_info.user_attribute('collections')
    cards = user_info.user_attribute('cards')
    
    # Создание меню профиля пользователя
    menu = keyboard_maker(1, **Messages.PROFILE_BUTTONS)
    text = Messages.PROFILE['INTERFACE'].format(username, karma,
                                                collections, cards)
    bot.answer_callback_query(call.id)
    bot.edit_message_text(text=text,
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        parse_mode='Markdown',
                        reply_markup=menu)

def call_home(call):
    '''Возвращение в Личный кабинет пользователя'''

    bot.answer_callback_query(call.id)
    private_office_menu = keyboard_maker(**Messages.PRIVATE_OFFICE_BUTTONS)
    bot.edit_message_text(text=Messages.PRIVATE_OFFICE['INTERFACE'],
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        reply_markup=private_office_menu)



def collections_menu(message):
    '''Создание меню коллекций пользователя.
    
    Parameters
    ----------
    message : Message
        Сообщение пользователя.
    
    Returns
    -------
    menu : InlineKeyboardMarkup
        Меню коллекций.
    '''

    # Получение информации о коллекции из базы данных
    collections = Fetch(message.chat.id, 'collections', 'collection')
    collections_info = collections.user_collections()

    if collections_info:
        # Создание меню из всех коллекций пользователя
        buttons = buttons_format('collection_show_{}', collections_info, 3, 1)
        collections_keyboard = keyboard_maker(2, **buttons)
    else:
        collections_keyboard = None

    # Создание навигации
    menu = keyboard_maker(row_width=2,
                        keyboard=collections_keyboard,
                        **Messages.COLLECTIONS_BUTTONS)

    return menu

def call_collections_menu(call):
    '''Изменение сообщения на меню с коллекциями'''
    
    menu = collections_menu(call.message)

    bot.answer_callback_query(call.id)
    bot.edit_message_text(text=Messages.COLLECTIONS['INTERFACE'],
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        reply_markup=menu)

def send_collections_menu(message):
    '''Отправление меню с коллекциями'''

    menu = collections_menu(message)
    menu_message = bot.send_message(chat_id=message.chat.id,
                                    text=Messages.COLLECTIONS['INTERFACE'],
                                    reply_markup=menu)

    # Обновление id сообщения Личного кабинета
    update_menu_id = Update(message.chat.id)
    update_menu_id.user_attribute('menu_id', menu_message.message_id)

def call_create_collection(call):
    '''Создание коллекции'''

    if error_handler(call.message) or cancel_handler(call.message):
        return
    
    key = f'k-{random.randint(1, 1000000000)}'\
        f'-{random.randint(1, 1000000000)}-n'
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

    # Проверка на существование коллекции со схожим ключом
    available_collection = Fetch(message.chat.id, 'collections', 'collection')
    copy_key = available_collection.general_collection(message.text, 'key')

    if copy_key:
        copy_user_collection(message)
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
    send_collections_menu(message)

def copy_user_collection(message):
    '''Создание копии коллекции пользователя по ключу'''

    # Получение копии имени и количества карт коллекции
    available_collection = Fetch(message.chat.id, 'collections', 'collection')
    copy_name = available_collection.general_collection(message.text, 'name')
    copy_cards = available_collection.general_collection(message.text, 'cards')
    generous = available_collection.general_collection(message.text, 'user_id')

    # Проверка на существование дубликата коллекции в базе данных
    duplicate_name = Fetch(message.chat.id, 'collections', 'collection')
    result = duplicate_name.copy_check('name', f'{copy_name} (Копия)')
    
    if result:
        bot.send_message(message.chat.id, Messages.ERRORS[9])
        bot.register_next_step_handler(message, copy_user_collection)
        return

    # Получение уникального ключа коллекции из базы данных
    user_status = Fetch(message.chat.id)
    key = user_status.user_attribute('session')

    # Создание копии карт оригинальной коллекции
    date = datetime.now()
    copy = Insert(message.chat.id, 'collections', 'card')
    copy.copy_collection(message.text, key, date)
    
    # Запись названия коллекции и количества карт в базу данных
    insert_name = Update(message.chat.id, 'collections', 'collection')
    insert_name.collection_attribute(key, 'name', f'{copy_name} (Копия)')
    insert_name.collection_attribute(key, 'cards', copy_cards)

    # Обовление статуса пользователя
    update_user_status = Update(message.chat.id)
    update_user_status.user_attribute('action', 0)
    update_user_status.user_attribute('session', None)
    update_user_status.change_user_attribute('collections', 1)
    update_user_status.change_user_attribute('cards', copy_cards)

    # +Карма пользователю, чью коллекцию скопировали
    if generous != message.chat.id:
        generous_karma = Update(generous)
        generous_karma.change_user_attribute('karma', 1)

    text = Messages.COLLECTIONS['COLLECTION_COPIED']
    bot.send_message(message.chat.id, text.format(copy_name))
    send_collections_menu(message)

def call_collection_continue(call):
    '''Программа обучения'''

    key = re.findall(r'\w-\d+-\d+-\w', call.data)[0]

    # Поиск карты, которую пользователь повторил меньшее количество раз
    cards_info = Fetch(call.message.chat.id, 'collections', 'card')
    cards = cards_info.user_cards(key)

    if not cards:
        bot.answer_callback_query(call.id, Messages.ERRORS[8], True)
        return

    # Выбор оптимыльной карты для повторения
    rare_card = sorted(cards, key=lambda card: card[6])[0]
    card_date = datetime.strptime(rare_card[6], '%Y-%m-%d %H:%M:%S.%f')

    # Цикл повторения карт
    if (card_date - datetime.now()).days >= 0:
        text = Messages.CARDS['THE_END'].format(date_format(rare_card[6]))
        bot.answer_callback_query(call.id, text, not ('result' in call.data))

    # Создание меню изучения карты
    keyboard = keyboard_format(
                        buttons=Messages.COLLECTION_CONTINUE_BUTTONS,
                        card=rare_card[2],
                        collection=rare_card[1])
    continue_menu = keyboard_maker(1, **keyboard)
    
    bot.answer_callback_query(call.id)
    bot.edit_message_text(text=rare_card[4],
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        reply_markup=continue_menu)

def collection_menu(message, key):
    '''Создание главного меню и текста коллекции.

    Parameters
    ----------
    message : Message
        Сообщение пользователя.
    key : str
        Уникальный ключ коллекции. 
    
    Returns
    -------
    menu : InlineKeyboardMarkup
        Меню коллекции.
    text : str
        Текст интерфейса коллекции.
    '''

    # Получение информации о коллекции из базы данных
    collection_info = Fetch(message.chat.id, 'collections', 'collection')
    collection_name = collection_info.collection_attribute(key, 'name')
    collection_key = collection_info.collection_attribute(key, 'key')
    collection_cards = collection_info.collection_attribute(key, 'cards')
    collection_date = collection_info.collection_attribute(key, 'date')

    # Создание меню коллекции
    keyboard = keyboard_format(Messages.COLLECTION_BUTTONS, collection=key)
    menu = keyboard_maker(2, **keyboard)
    text = Messages.COLLECTION_MENU['INTERFACE'].format(collection_name,
                                                collection_key,
                                                collection_cards,
                                                date_format(collection_date))
    
    return menu, text

def call_collection_menu(call):
    '''Изменение сообщения на меню коллекции'''

    key = re.findall(r'\w-\d+-\d+-\w', call.data)[0]
    menu, text = collection_menu(call.message, key)

    bot.answer_callback_query(call.id)
    bot.edit_message_text(text=text,
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        parse_mode='Markdown',
                        reply_markup=menu)

def send_collection_menu(message, key):
    '''Отправление меню коллекции'''

    menu, text = collection_menu(message, key)
    menu_message = bot.send_message(chat_id=message.chat.id,
                                    text=text,
                                    parse_mode='Markdown',
                                    reply_markup=menu)

    # Обновление id сообщения Личного кабинета
    update_menu_id = Update(message.chat.id)
    update_menu_id.user_attribute('menu_id', menu_message.message_id)

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
    
    # Получение названия коллекции для проверки на существование
    # дубликата коллекции в базе данных
    duplicate_name = Fetch(message.chat.id, 'collections', 'collection')
    result = duplicate_name.copy_check('name', message.text)
    
    if result:
        bot.send_message(message.chat.id, Messages.ERRORS[3])
        bot.register_next_step_handler(message, rename_collection)
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
    send_collection_menu(message, key)

def call_delete_collection_menu(call):
    '''Меню удаления коллекции'''

    # Создание меню удаления коллекции
    key = re.findall(r'\w-\d+-\d+-\w+', call.data)[0]
    buttons = keyboard_format(buttons=Messages.DELETE_COLLECTION_BUTTONS,
                            collection=key)
    delete_collection = keyboard_maker(1, **buttons)

    bot.answer_callback_query(call.id)
    bot.edit_message_text(text=Messages.DELETE_COLLECTION['DELETE'],
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        reply_markup=delete_collection,
                        parse_mode='Markdown')

def call_delete_collection_yes(call):
    '''Согласие на удаление коллекции'''

    key = re.findall(r'\w-\d+-\d+-\w+', call.data)[0]

    # Получение имени коллекции из базы данных
    collection_info = Fetch(call.message.chat.id, 'collections', 'collection')
    collection_name = collection_info.collection_attribute(key, 'name')
    collection_cards = collection_info.collection_attribute(key, 'cards')

    # Изменение количества коллекций и карт в профиле пользователя
    update_user_status = Update(call.message.chat.id)
    update_user_status.change_user_attribute('collections', -1)
    update_user_status.change_user_attribute('cards', -int(collection_cards))

    # Удаление коллекции из базы данных
    delete_collection = Delete(user_id=call.message.chat.id,
                            db_name='collections',
                            db_table='collection')
    delete_collection.delete_collection(key)

    # Удаление всех карт коллекции
    delete_cards = Delete(user_id=call.message.chat.id,
                        db_name='collections',
                        db_table='card')
    delete_cards.delete_collection_cards(key)

    text = Messages.DELETE_COLLECTION[
                    'DELETE_SUCCESSFUL'].format(collection_name)
    bot.answer_callback_query(call.id, text, True)
    call_collections_menu(call)

def call_delete_collection_no(call):
    '''Отмена удаления коллекции'''

    canceled_delete_text = Messages.DELETE_COLLECTION['DELETE_CANCELED']
    bot.answer_callback_query(call.id, canceled_delete_text, True)
    call_collection_menu(call)



def cards_menu(message, key, level=0):
    '''Карты определенной коллекции пользователя.

    Parameters
    ----------
    key : str
        Уникальный ключ коллекции.
    level : int
        Страница, на которой находится пользователь (default is 0).
    
    Returns
    -------
    menu : InlineKeyboardMarkup
        Меню коллекции.
    text : str
        Текст интерфейса коллекции.
    '''

    # Получение названия коллекции из базы данных
    collection_info = Fetch(message.chat.id, 'collections', 'collection')
    collection_name = collection_info.collection_attribute(key, 'name')

    # Получение информации о карте из базы данных
    fetch_cards = Fetch(message.chat.id, 'collections', 'card')
    cards_info = fetch_cards.user_cards(key)
    
    if cards_info:
        # Добавление кнопок навигации в меню
        nav_obj = cards_info[8*level : 8*(level + 1)]
        navigation = keyboard_navigation(key, len(cards_info), level, 8)

        # Создание меню из всех карт определенной коллекции пользователя
        buttons = buttons_format('card_show_{}', nav_obj, 4, 2)
        cards_keyboard = keyboard_maker(2, navigation, **buttons)
    else:
        cards_keyboard = None

    # Добавление кнопок выхода в меню
    keyboard = keyboard_format(Messages.CARDS_BUTTONS, collection=key)
    menu = keyboard_maker(2, cards_keyboard, **keyboard)
    text = Messages.CARDS['INTERFACE'].format(collection_name)
    
    return menu, text

def call_cards_menu(call, key=None, level=None):
    '''Изменение сообщения на меню карт определенной коллекции'''
    
    if key == None:
        key = re.findall(r'\w-\d+-\d+-\w', call.data)[0]
    if level == None:
        level = int(re.findall(r'_\w+-\d+-\d+-\w+_\w+_(\d+)', call.data)[0])
    menu, text = cards_menu(call.message, key, level)

    bot.answer_callback_query(call.id)
    bot.edit_message_text(text=text,
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        reply_markup=menu)

def send_cards_menu(message, key):
    '''Отправление меню карт определенной коллекции'''

    menu, text = cards_menu(message, key, 0)
    menu_message = bot.send_message(message.chat.id, text, reply_markup=menu)

    # Обновление id сообщения Личного кабинета
    update_menu_id = Update(message.chat.id)
    update_menu_id.user_attribute('menu_id', menu_message.message_id)

def call_create_card(call):
    '''Создание карты'''

    if error_handler(call.message) or cancel_handler(call.message):
        return
    
    key = re.findall(r'\w-\d+-\d+-\w+', call.data)[0]
    card_key = f'c-{random.randint(1, 1000000000)}-' \
            f'{random.randint(1, 1000000000)}-d'
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

    send_cards_menu(message, key)

def card_menu(message, card_key):
    '''Создание главного меню карты.

    Parameters
    ----------
    message : Message
        Сообщение пользователя.
    card_key : str
        Уникальный ключ карты.

    Returns
    -------
    menu : InlineKeyboardMarkup
        Меню карты.
    text : str
        Текст интерфейса карты.
    '''

    # Получение информации о карте из базы данных
    card_info = Fetch(message.chat.id, 'collections', 'card')
    card_name = card_info.card_attribute(card_key, 'name')
    key = card_info.card_attribute(card_key, 'key')
    card_description = card_info.card_attribute(card_key, 'description')

    # Создание меню карты
    keyboard = keyboard_format(buttons=Messages.CARD_ORIGINAL_MENU_BUTTONS,
                            card=card_key,
                            collection=key)

    menu = keyboard_maker(2, **keyboard)
    text = Messages.CARD_MENU['INTERFACE'].format(card_name, card_description)
    return menu, text

def call_card_menu(call):
    '''Изменение сообщения на главное меню карты'''

    card_key = re.findall(r'\w-\d+-\d+-\w+', call.data)[0]
    menu, text = card_menu(call.message, card_key)

    bot.answer_callback_query(call.id)
    bot.edit_message_text(text=text,
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        reply_markup=menu,
                        parse_mode='Markdown')

def send_card_menu(message, card_key):
    '''Отправление главного меню карты'''

    menu, text = card_menu(message, card_key)
    menu_message = bot.send_message(chat_id=message.chat.id,
                                    text=text,
                                    reply_markup=menu,
                                    parse_mode='Markdown')

    # Обновление id сообщения Личного кабинета
    update_menu_id = Update(message.chat.id)
    update_menu_id.user_attribute('menu_id', menu_message.message_id)

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
    send_card_menu(message, card_key)

def call_card_continue(call):
    '''Начало изучения карты'''

    card_key = re.findall(r'\w-\d+-\d+-\w', call.data)[0]

    # Получение информации о карте из базы данных
    card_info = Fetch(call.message.chat.id, 'collections', 'card')
    description = card_info.card_attribute(card_key, 'description')
    key = card_info.card_attribute(card_key, 'key')

    # Создание меню результата карты
    keyboard = keyboard_format(buttons=Messages.CARD_RESULT_BUTTONS,
                            card=card_key,
                            collection=key)
    result_menu = keyboard_maker(1, **keyboard)
    
    bot.answer_callback_query(call.id)
    bot.edit_message_text(text=description,
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        parse_mode='Markdown',
                        reply_markup=result_menu)

def call_result(call):
    '''Переход к следующей карте'''

    status = datetime.now() + timedelta(minutes=int(call.data[-4:]))
    card_key = re.findall(r'_\w-\d+-\d+-\w_(\w-\d+-\d+-\w)', call.data)[0]

    # Запись нового результата в базу данных
    card_status = Update(call.message.chat.id, 'collections', 'card')
    card_status.card_attribute(card_key, 'status', status)

    call_collection_continue(call)

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
    send_card_menu(message, card_key)

def call_delete_card_menu(call):
    '''Меню удаления карты'''

    card_key = re.findall(r'\w-\d+-\d+-\w+', call.data)[0]

    # Создание меню удаления карты
    keyboard = keyboard_format(Messages.DELETE_CARD_BUTTONS, card=card_key)
    delete_menu = keyboard_maker(1, **keyboard)

    bot.answer_callback_query(call.id)
    bot.edit_message_text(text=Messages.DELETE_CARD['DELETE'],
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        reply_markup=delete_menu)

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
    call_cards_menu(call, key, 0)

def call_delete_card_no(call):
    '''Отмена удаления карты'''

    canceled_delete_text = Messages.DELETE_CARD['DELETE_CANCELED']
    bot.answer_callback_query(call.id, canceled_delete_text, True)
    call_card_menu(call)

def call_info_on(call):
    '''Дополнительная информация о карте'''

    card_key = re.findall(r'\w-\d+-\d+-\w+', call.data)[0]

    # Получение информации о карте из базы даных
    card_info = Fetch(call.message.chat.id, 'collections', 'card')
    card_name = card_info.card_attribute(card_key, 'name')
    key = card_info.card_attribute(card_key, 'key')
    card_description = card_info.card_attribute(card_key, 'description')
    card_date = card_info.card_attribute(card_key, 'date')
    card_status = card_info.card_attribute(card_key, 'status')

    # Создание меню карты
    keyboard = keyboard_format(buttons=Messages.CARD_INFO_MENU_BUTTONS,
                            card=card_key,
                            collection=key)
    menu = keyboard_maker(2, **keyboard)

    main_text = Messages.CARD_MENU['INFO_INTERFACE'].format(card_name,
                                                    card_description,
                                                    date_format(card_date),
                                                    date_format(card_status))
    bot.answer_callback_query(call.id)
    bot.edit_message_text(text=main_text,
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        reply_markup=menu,
                        parse_mode='Markdown')



def keyboard_maker(row_width=3, keyboard=None, **buttons):
    '''Создание клавиатуры меню.

    Notes
    -----
        Учтите, что передавая в keyboard_maker готовую клавиатуру
        её row_width не изменится, так как в таком случае метод
        не создаст новую клавиатуру, а дополнит текущую новыми кнопками!

    Parameters
    ----------
    row_width : int
        Количество кнопок в строке (default is 3).
    keyboard : InlineKeyboardMarkup, optional
        Готовая клавиатура, в которую необходимо 
        добавить кнопки (default is None).
    **buttons
        Кнопки, из которых будет состоять клавиатура.
    
    Returns
    -------
    keyboard : InlineKeyboardMarkup
        Готовая клавиатура.
    '''

    if not keyboard:
        keyboard = types.InlineKeyboardMarkup(row_width)

    keyboard_buttons = [types.InlineKeyboardButton(text=text,
        callback_data=data) for text, data in buttons.items()]

    keyboard.add(*keyboard_buttons)
    return keyboard

def keyboard_format(buttons, **format_obj):
    '''Создание клавиатуры с вставляемыми элементами.

    Parameters
    ----------    
    buttons : list
        Кнопки, из которых будет сделана клавиатура.
    **format_obj
        Вставляемые элементы.
    
    Returns
    -------
    keyboard : dict
        Готовая клавиатура.
    '''

    keyboard = {}
    for button in buttons:
        keyboard[button] = buttons[button].format(**format_obj)

    return keyboard

def buttons_format(data, format_obj, name_id=0, data_id=0):
    '''Создание кнопок с вставляемыми элементами.

    Parameters
    ----------
    data : str
        Строка навигации.
    format_obj : list
        Объект, из которого будут созданы кнопки.
    name_id : int
        ID имени кнопки (default is 0).
    data_id : int
        ID переменной, вставляемой в строку навигации (default is 0).
    
    Returns
    -------
    buttons : dict
        Готовые кнопки.
    '''

    buttons = {}
    for item in format_obj:
        buttons[item[name_id]] = data.format(item[data_id])

    return buttons

def keyboard_navigation(key, lenght, level=0, sep=8):
    '''Создание навигационной клавиатуры.

    Parameters
    ----------
    key : str
        Уникальный ключ коллекции.
    lenght : int
        Длина списка элементов страницы.
    level : int
        Страница, на которой находится пользователь (default is 0).
    sep : int
        Количество элементов на странице (default is 8).
    
    Returns
    -------
    keyboard : InlineKeyboardMarkup
        Клавиатура с кнопками навигации.
    '''
    
    navigation = {0: '• {} •', 1: '{}', 'data': 'cards_{}_level_{}'}
    system_len = lenght//sep if lenght%sep == 0 else lenght//sep + 1

    buttons = []
    keyboard = types.InlineKeyboardMarkup(2)
    
    # Создание клавиатуры без навигации
    if lenght < 5*sep + 1:
        buttons = [types.InlineKeyboardButton(
            text=navigation[not (button==level)].format(button + 1),
            callback_data=navigation['data'].format(key, button))
                for button in range(system_len)]

    # Создание клавиатуры с навигацией
    else:
        for button in range(5):
            # Обработка первых двух кнопок
            if level == 0 or level  == 1:
                nav = {0: '{}', 1: '{}', 2: '{}', 3: '{} ›', 4: '{} »'}
                nav[level] = '• {} •'

                data = system_len if button == 4 else button + 1

            # Обработка последних двух кнопок
            elif level == (system_len - 1) or level == (system_len - 2):
                nav = {0: '« {}', 1: '‹ {}', 2: '{}', 3: '{}', 4: '{}'}
                nav[level - system_len + 5] = '• {} •'

                data = button + 1 if button == 0 else system_len + button - 4
            
            # Обработка полной навигации
            else:
                nav = {0: '« {}', 1: '‹ {}', 2: '• {} •', 3: '{} ›', 4: '{} »'}

                data = (1 if button == 0 else system_len
                        if button == 4 else button + level - 1)

            text = nav[button].format(data)
            buttons.append(types.InlineKeyboardButton(text=text,
                    callback_data=navigation['data'].format(key, data - 1)))

    keyboard.row(*buttons)
    return keyboard

def error_handler(message):
    '''Проверка на наличие ошибок.

    Parameters
    ----------
    message : Message
        Сообщение пользователя.

    Returns
    -------
    bool
        True, если есть ошибка, False — если ошибок нет.
    '''

    # Получение информации о действиях пользователя
    # и ID его последнего Личного кабинета
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
        text = Messages.ERRORS[0]
        bot.edit_message_text(text, message.chat.id, message.message_id)
        return True

    return False

def cancel_handler(message):
    '''Проверка на отмену операции.

    Parameters
    ----------
    message : Message
        Сообщение пользователя.
    
    Returns
    -------
    bool
        True, если пользователь отменил операцию, False — если нет.
    '''

    if (not message.text
            or message.text == '/cancel'
            or message.text.lower() == 'отмена'):
        bot_cancel(message)
        return True

    return False

def date_format(date):
    '''Изменение формата даты.

    Parameters
    ----------
    date : ste
        Дата, которую нужно преобразовать.
    
    Returns
    -------
    new_date : str
        Преобразованная дата.
    '''

    date_form = datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')
    new_date = date_form.strftime('%B %d (%A), %H:%M')
    return new_date

if __name__ == '__main__':
    bot.polling()
