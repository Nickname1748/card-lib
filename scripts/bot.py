import telebot
from telebot import types

from config import token
from messages import Texts as texts
from database import Insert, Delete, Fetch, Update

import random
from datetime import datetime
import re

bot = telebot.TeleBot(token=token)

@bot.message_handler(commands=['start'])
def bot_start(message):
    insert_new_user = Insert(user_id=message.chat.id, db_name='users', table_name='user')
    insert_new_user.db_new_user()

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
    if error_handler(message=message):
        return

    # Creating a collection and generating a unique key.
    insert_new_collection = Insert(user_id=message.chat.id, db_name='collections', table_name='collection')
    new_key = f'k-{random.randint(100000, 1000000)}-{random.randint(1000, 10000)}-z'
    insert_new_collection.db_session_reservation(key=new_key)

    user_update = Update(user_id=message.chat.id, db_name='users', table_name='user')
    user_update.db_user_activity(active=1, session=new_key)

    bot.send_message(chat_id=message.chat.id, text=texts.msg_new_collection())
    bot.register_next_step_handler(message=message, callback=register_collection_name)

@bot.message_handler(commands=['cancel'])
def bot_cancel(message):
    user_fetch = Fetch(user_id=message.chat.id, db_name='users', table_name='user')
    session = user_fetch.db_user_activity_status()[0][2]

    if session == 1:
        delete_session = Delete(user_id=message.chat.id, db_name='collections', table_name='collection')
        delete_session.db_delete_collection(key=session)

    user_update = Update(user_id=message.chat.id, db_name='users', table_name='user')
    user_update.db_user_activity(active=0, session='')

    bot.send_message(chat_id=message.chat.id, text=texts.msg_cancel())
    bot_collections(message=message)

@bot.callback_query_handler(func=lambda call: True)
def bot_callback_query(call):
    if call.data == 'create_collection':
        bot_new_collection(message=call.message)

    elif call.data == 'back_to_list':
        keyboard = show_collections(message=call.message)

        bot.edit_message_text(text=texts.msg_collections(), 
                            chat_id=call.message.chat.id,
                            message_id=call.message.message_id, 
                            reply_markup=keyboard)

    else:
        key = re.findall(r'\w-\d{6}-\d{4}-\w+', call.data)[0]

        fetch_collection = Fetch(user_id=call.message.chat.id, db_name='collections', table_name='collection')
        result = fetch_collection.db_search_collection(key=key)

        if result:
            if call.data == key:
                collection_interface(message=call.message, collection=result)

            elif call.data == f'rename_{key}':
                if error_handler(message=call.message):
                    return

                user_update = Update(user_id=call.message.chat.id, db_name='users', table_name='user')
                user_update.db_user_activity(active=2, session=key)

                bot.send_message(chat_id=call.message.chat.id, text=texts.msg_collection_rename())
                bot.register_next_step_handler(message=call.message, callback=rename_collection)

            elif call.data == f'delete_{key}':
                delete_collection(message=call.message, collection=result)

            elif call.data == f'yes_delete_{key}':
                delete = Delete(user_id=call.message.chat.id, db_name='collections', table_name='collection')
                delete.db_delete_collection(key=key)

                bot.answer_callback_query(callback_query_id=call.id, 
                                        text=f'Вы удалили коллекцию {result[2]}')
                
                bot.delete_message(chat_id=call.message.chat.id,
                                message_id=call.message.message_id)

                bot_collections(message=call.message)
                

def show_collections(message):
    '''Displays a list of user collections.

    :param message: User message
    :return: Inline buttons with existing user collections
    '''

    fetch_collections = Fetch(user_id=message.chat.id, db_name='collections', table_name='collection')
    result = fetch_collections.db_search_collections()

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    if result:
        keyboard.add(*[types.InlineKeyboardButton(text=collection[2], callback_data=collection[1]) for collection in result])
    keyboard.add(types.InlineKeyboardButton(text='Новая коллекция', callback_data='create_collection'))

    return keyboard

def register_collection_name(message):
    '''Creating a session to insert a collection to the database.

    :param message: User message
    '''

    if message.text == '/cancel':
        bot_cancel(message)
        return

    user_fetch = Fetch(user_id=message.chat.id, db_name='users', table_name='user')
    status = user_fetch.db_user_activity_status()[0][2]

    # The final insert of the collection in the database.
    final_insert = Insert(user_id=message.chat.id, db_name='collections', table_name='collection')
    date = f'{datetime.today().day}/{datetime.today().month}/{datetime.today().year}'
    final_insert.db_session_insert(name=message.text, key=status, creation_date=date)

    user_update = Update(user_id=message.chat.id, db_name='users', table_name='user')
    user_update.db_user_activity(active=0, session='')

    bot.send_message(chat_id=message.chat.id, text=texts.msg_new_collection_create())
    bot_collections(message=message)

def error_handler(message):
    '''Handling errors that may occur during an unexpected user action scenario.

    :param message: User message
    :return: True/False the presence of an error
    '''

    user_fetch = Fetch(user_id=message.chat.id, db_name='users', table_name='user')
    status = user_fetch.db_user_activity_status()

    if message.text == '/cancel':
        bot_cancel(message)
        return True

    elif status[0][1] == 1:
        # Called when a user attempts to create a new collection when a collection is already being created.
        error_message = texts.msg_err_collection_create() + texts.msg_err_solution_collection_create()
        bot.send_message(chat_id=message.chat.id, text=error_message)
        return True
    
    elif status[0][1] == 2:
        # Called when a user attempts to perform an action while renaming a collection.
        error_message = texts.msg_err_collection_rename() + texts.msg_err_solution_collection_rename()
        bot.send_message(chat_id=message.chat.id, text=error_message)
        return True
    
    return False

def collection_interface(message, collection=None):
    '''User collection information interface.

    :param collection: Collection information
    '''

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*[types.InlineKeyboardButton(text='Продолжить изучение', callback_data=f'cards_{collection[1]}'),
                types.InlineKeyboardButton(text='Добавить карточку', callback_data=f'new_card_{collection[1]}'),
                types.InlineKeyboardButton(text='Изменить название', callback_data=f'rename_{collection[1]}'),
                types.InlineKeyboardButton(text='Удалить коллекцию', callback_data=f'delete_{collection[1]}'),
                types.InlineKeyboardButton(text='< Вернуться к списку коллекций', callback_data='back_to_list')])

    text = texts.msg_collection_interface().format(collection[2], collection[3], collection[4])
    bot.edit_message_text(text=text, chat_id=message.chat.id, 
                        message_id=message.message_id, reply_markup=keyboard)

def delete_collection(message, collection=None):
    '''Delete user collection.

    :param collection: Collection information
    '''

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*[types.InlineKeyboardButton(text='Да, удалить!', callback_data=f'yes_delete_{collection[1]}'),
                types.InlineKeyboardButton(text='Нет, это ошибка!', callback_data='back_to_list')])

    bot.edit_message_text(text=texts.msg_delete_collection(), chat_id=message.chat.id,
                        message_id=message.message_id, reply_markup=keyboard)

def rename_collection(message):
    '''Rename user collection.
    '''

    if message.text == '/cancel':
        bot_cancel(message)
        return

    user_fetch = Fetch(user_id=message.chat.id, db_name='users', table_name='user')
    status = user_fetch.db_user_activity_status()[0][2]

    user_rename_collection = Update(user_id=message.chat.id, db_name='collections', table_name='collection')
    user_rename_collection.db_rename_collection(name=message.text, key=status)
    
    user_update = Update(user_id=message.chat.id, db_name='users', table_name='user')
    user_update.db_user_activity(active=0, session='')

    bot.send_message(chat_id=message.chat.id, text=texts.msg_collection_renamed())
    bot_collections(message=message)

if __name__ == '__main__':
    bot.polling()
