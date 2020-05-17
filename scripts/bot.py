import telebot
from telebot import types

from config import token
from messages import Texts as texts
from database import Insert, Fetch

import random
from datetime import datetime

bot = telebot.TeleBot(token=token)

@bot.message_handler(commands=['start'])
def bot_start(message):
    insert = Insert(user_id=message.chat.id, db_name='users', table_name='user')
    insert.new_user()

    bot.send_message(chat_id=message.chat.id, text=texts.msg_start())
    bot.send_message(chat_id=message.chat.id, text=texts.msg_instruction())


@bot.message_handler(commands=['help'])
def bot_help(message):
    bot.send_message(chat_id=message.chat.id, text=texts.msg_help())


@bot.message_handler(commands=['my_collections'])
def bot_collections(message):
    keyboard = show_collections(message=message)

    bot.send_message(chat_id=message.chat.id, text=texts.msg_collections(), reply_markup=keyboard)


@bot.message_handler(commands=['new_collection'])
def bot_new_collection(message):
    bot.send_message(chat_id=message.chat.id, text=texts.msg_new_collection())

    # Creating a collection and generating a unique key.
    insert_new_collection = Insert(user_id=message.chat.id, db_name='collections', table_name='collection')
    new_key = f'k-{random.randint(100000, 1000000)}-{random.randint(1000, 10000)}-z'
    insert_new_collection.session_reservation(key=new_key)

    user_activity_change = Insert(user_id=message.chat.id, db_name='users', table_name='user')
    user_activity_change.user_activity(active=1, session=new_key)

    bot.register_next_step_handler(message=message, callback=register_collection_name)


@bot.message_handler(commands=['delete_collection'])
def bot_delete_collection(message):
    bot.send_message(chat_id=message.chat.id, text=texts.msg_delete_collection())


def show_collections(message):
    '''Displays a list of user collections.

    :param message: User message
    :return: Inline buttons with existing user collections
    '''

    fetch = Fetch(user_id=message.chat.id, db_name='collections', table_name='collection')
    result = fetch.search_collections()

    keys = []
    keyboard = types.InlineKeyboardMarkup()
    if result:
        for collection in result:
            keys.append([types.InlineKeyboardButton(text=collection[2], callback_data=collection[1]),
                        types.InlineKeyboardButton(text='🗑', callback_data=f'del_{collection[1]}'),
                        types.InlineKeyboardButton(text='✏️', callback_data=f'edit_{collection[1]}')])
    for collection in keys:
        keyboard.row(*collection)
    keyboard.add(types.InlineKeyboardButton(text='Новая коллекция.', callback_data='create_collection'))

    return keyboard


def register_collection_name(message):
    '''Collection Name.
    Creating a session to insert a collection to the database.

    :param message: User message
    '''

    fetch = Fetch(user_id=message.chat.id, db_name='users', table_name='user')
    status = fetch.user_activity_status()

    # The final insert of the collection in the database.
    insert = Insert(user_id=message.chat.id, db_name='collections', table_name='collection')
    date = f'{datetime.today().day}/{datetime.today().month}/{datetime.today().year}'
    insert.session_insert(name=message.text, key=status[0][2], creation_date=date)

    user_activity_change = Insert(user_id=message.chat.id, db_name='users', table_name='user')
    user_activity_change.user_activity(active=0, session='')

    bot.send_message(chat_id=message.chat.id, text=texts.msg_new_collection_create())
    bot_collections(message=message)

bot.polling()