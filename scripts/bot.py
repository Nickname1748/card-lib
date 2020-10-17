import telebot
import locale
import pyttsx3

import tools
import config
import messages
import conversation
import database as db
import card as card_py
import collection as collection_py

locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
bot = telebot.TeleBot(config.Tokens.TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    '''Getting started with a bot.
        
    Parameters
    ----------
    message : Message
        User message.
    '''

    # Adding a new user to the database.
    insert = db.Insert(message.chat.id)
    insert.new_user(username=message.from_user.username,
                    first_name=message.from_user.first_name,
                    last_name=message.from_user.last_name)

    bot.send_message(message.chat.id, messages.ASSISTANCE['START'])

@bot.message_handler(commands=['office'])
def private_office(message):
    '''User's personal account.
        
    Parameters
    ----------
    message : Message
        User message.
    '''

    menu = tools.Maker.keyboard(3, **messages.OFFICE['BUTTONS'])
    menu_message = bot.send_message(chat_id=message.chat.id,
                                    text=messages.OFFICE['INTERFACE'],
                                    reply_markup=menu)

    # Updating the message_id of the Personal Account.
    update = db.Update(message.chat.id)
    update.user_attribute('menu_id', menu_message.message_id)

@bot.message_handler(commands=['cancel'])
def cancel(message):
    '''Canceling the current operation.
        
    Parameters
    ----------
    message : Message
        User message.
    '''

    # Getting information about user status from the database.
    fetch = db.Fetch(message.chat.id)
    action = fetch.user_attribute('action')
    session = fetch.user_attribute('session')

    if action == 1:
        # Removing a collection-reserved space from the database.
        delete = db.Delete(message.chat.id, 'collections', 'collection')
        delete.delete_collection(session)
    elif action == 3:
        # Removing a card-reserved space from the database.
        delete = db.Delete(message.chat.id, 'collections', 'card')
        delete.delete_card(session)

    # User status update.
    update = db.Update(message.chat.id)
    update.user_attribute('action', 0)
    update.user_attribute('session', None)

    bot.send_message(message.chat.id, messages.ASSISTANCE['CANCEL'])
    private_office(message)

@bot.message_handler(content_types=['text'])
def dialog(message):
    '''Answers the user to a question.
        
    Parameters
    ----------
    message : Message
        User message.
    '''

    conv = conversation.Intents(message)
    phrase = conv.phrase_handler()
    bot.send_message(message.chat.id, phrase)

    engine = pyttsx3.init()
    engine.setProperty('voice', engine.getProperty('voices')[3].id)
    engine.save_to_file(phrase, 'dboqp_bot.mp3')
    engine.runAndWait()
    bot.send_voice(message.chat.id, open('dboqp_bot.mp3', 'rb'))

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    try:
        handler = tools.Handler(bot)
        if handler.error(call.message):
            return

        elif call.data == 'profile':
            profile_menu(call)

        elif 'collection' in call.data:
            collections = collection_py.Collections(bot)
            collection = collection_py.Collection(bot)

            if 'show' in call.data:
                collection.call_menu(call)

            elif 'create' in call.data:
                collections.create_collection(call)

            elif 'continue' in call.data:
                collection.continue_learning(call)

            elif 'rename' in call.data:
                collection.rename(call)

            elif 'delete' in call.data:
                if 'yes' in call.data:
                    collection.delete_yes(call)

                elif 'no' in call.data:
                    collection.delete_no(call)

                else:
                    collection.delete_menu(call)

            else:
                collections.call_menu(call)

        elif 'card' in call.data:
            cards = card_py.Cards(bot)
            card = card_py.Card(bot)

            if 'show' in call.data:
                card.call_menu(call)

            elif 'create' in call.data:
                cards.create_card(call)

            elif 'result' in call.data:
                card.result(call)

            elif 'continue' in call.data:
                card.start_learning(call)

            elif 'rename' in call.data:
                card.rename(call)

            elif 'description' in call.data:
                card.edit_description(call)

            elif 'info' in call.data:
                if 'on' in call.data:
                    card.info(call)
                else:
                    card.call_menu(call)

            elif 'delete' in call.data:
                if 'yes' in call.data:
                    card.delete_yes(call)

                elif 'no' in call.data:
                    card.delete_no(call)

                else:
                    card.delete_menu(call)
            
            else:
                cards.call_menu(call)

        elif call.data == 'home':
            home(call)
    except:
        bot.send_message(call.message.chat.id, messages.ASSISTANCE['LOADING'])

def home(call):
    '''Return to the user's Personal Account.
        
    Parameters
    ----------
    call : CallbackQuery
        Response to button press.
    '''

    bot.answer_callback_query(call.id)
    menu = tools.Maker.keyboard(**messages.OFFICE['BUTTONS'])
    bot.edit_message_text(text=messages.OFFICE['INTERFACE'],
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        reply_markup=menu)

def profile_menu(call):
    '''User profile.
        
    Parameters
    ----------
    call : CallbackQuery
        Response to button press.
    '''

    # Getting information about a user.
    fetch = db.Fetch(call.message.chat.id)
    karma = fetch.user_attribute('karma')
    cards = fetch.user_attribute('cards')
    username = fetch.user_attribute('username')
    collections = fetch.user_attribute('collections')

    # Creating a user profile menu.
    menu = tools.Maker.keyboard(1, **messages.PROFILE['BUTTONS'])
    text = messages.PROFILE['INTERFACE'].format(username, karma,
                                                collections, cards)
    bot.answer_callback_query(call.id)
    bot.edit_message_text(text=text,
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        parse_mode='Markdown',
                        reply_markup=menu)

if __name__ == '__main__':
    bot.polling()

