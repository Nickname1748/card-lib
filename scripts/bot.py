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
    insert_new_user = Insert(user_id=message.chat.id, db_name='users', table_name='user')
    insert_new_user.new_user()

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

@bot.message_handler(commands=['cancel'])
def bot_cancel(message):
    bot.send_message(chat_id=message.chat.id, text=texts.msg_cancel())

    user_activity_status = Fetch(user_id=message.chat.id, db_name='users', table_name='user')
    session = user_activity_status.user_activity_status()[0][2]

    delete_session = Insert(user_id=message.chat.id, db_name='collections', table_name='collection')
    delete_session.delete_collection(key=session)

    user_activity_change = Insert(user_id=message.chat.id, db_name='users', table_name='user')
    user_activity_change.user_activity(active=0, session='')

@bot.callback_query_handler(func=lambda call: True)
def bot_callback_query(call):
    if call.data == "create_collection":
        bot_new_collection(call.message)

def show_collections(message):
    '''Displays a list of user collections.

    :param message: User message
    :return: Inline buttons with existing user collections
    '''

    fetch_collections = Fetch(user_id=message.chat.id, db_name='collections', table_name='collection')
    result = fetch_collections.search_collections()

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    if result:
        keyboard.add(*[types.InlineKeyboardButton(text=collection[2], callback_data=collection[1]) for collection in result])
    keyboard.add(types.InlineKeyboardButton(text='Новая коллекция', callback_data='create_collection'))

    return keyboard

def register_collection_name(message):
    '''Collection Name.
    Creating a session to insert a collection to the database.

    :param message: User message
    '''

    if message.text == '/cancel':
        bot_cancel(message)
        return

    user_activity_status_check = Fetch(user_id=message.chat.id, db_name='users', table_name='user')
    status = user_activity_status_check.user_activity_status()

    # The final insert of the collection in the database.
    final_insert = Insert(user_id=message.chat.id, db_name='collections', table_name='collection')
    date = f'{datetime.today().day}/{datetime.today().month}/{datetime.today().year}'
    final_insert.session_insert(name=message.text, key=status[0][2], creation_date=date)

    user_activity_change = Insert(user_id=message.chat.id, db_name='users', table_name='user')
    user_activity_change.user_activity(active=0, session='')

    bot.send_message(chat_id=message.chat.id, text=texts.msg_new_collection_create())
    bot_collections(message=message)

def error_handler(message):
    '''Handling errors that may occur during an unexpected user action scenario.

    :param message: User message
    :return: True/False the presence of an error
    '''

    user_activity_status = Fetch(user_id=message.chat.id, db_name='users', table_name='user')
    status = user_activity_status.user_activity_status()

    if status[0][1] == 1:
        # Called when a user attempts to create a new collection when a collection is already being created.
        error_message = texts.msg_err_collection_create() + texts.msg_err_solution_collection_create()
        bot.send_message(chat_id=message.chat.id, text=error_message)
        return True
    
    return False

bot.polling()