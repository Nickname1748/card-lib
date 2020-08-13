import re
import random
import datetime

import tools
import messages
import database as db


class Collections:
    def __init__(self, bot):
        self.bot = bot

    def call_menu(self, call):
        '''Changing the message on the collections menu.
        
        Parameters
        ----------
        call : CallbackQuery
            Response to button press.
        '''
        
        menu = self._create_menu(call.message)
        self.bot.answer_callback_query(call.id)
        self.bot.edit_message_text(text=messages.COLLECTIONS['INTERFACE'],
                                chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                reply_markup=menu)

    def send_menu(self, message):
        '''Sending a collections menu.
        
        Parameters
        ----------
        message : Message
            User message.
        '''

        menu = self._create_menu(message)
        menu_message = self.bot.send_message(chat_id=message.chat.id,
                                    text=messages.COLLECTIONS['INTERFACE'],
                                    reply_markup=menu)

        # Updating the message_id of the Private Office.
        update = db.Update(message.chat.id)
        update.user_attribute('menu_id', menu_message.message_id)

    def create_collection(self, call):
        '''Collection creation.
        
        Parameters
        ----------
        call : CallbackQuery
            Response to button press.
        '''

        handler = tools.Handler(self.bot)
        if handler.error(call.message) or handler.cancel(call.message):
            return
        
        date = datetime.datetime.now()
        key = f'k-{random.randint(1, 1000000000)}' \
            f'-{random.randint(1, 1000000000)}-n'

        # User status update.
        update = db.Update(call.message.chat.id)
        update.user_attribute('action', 1)
        update.user_attribute('session', key)

        # Allocating space for a collection in the database.
        insert = db.Insert(call.message.chat.id, 'collections', 'collection')
        insert.create_collection(key, date)

        text = messages.COLLECTIONS['CREATE_COLLECTION']
        self.bot.answer_callback_query(call.id, text, True)
        self.bot.send_message(call.message.chat.id, text)
        self.bot.register_next_step_handler(call.message, self._save_collection)

    def copy_collection(self, message):
        '''Creating a copy of a user collection.
        
        Parameters
        ----------
        message : Message
            User message.
        '''

        # Getting a copy of the name and number of cards in the collection.
        fetch = db.Fetch(message.chat.id, 'collections', 'collection')
        name = fetch.general_collection(message.text, 'name')
        cards = fetch.general_collection(message.text, 'cards')
        karma = fetch.general_collection(message.text, 'user_id')

        # Checking for a duplicate collection in the database.
        fetch = db.Fetch(message.chat.id, 'collections', 'collection')
        result = fetch.copy_check('name', f'{name} (Копия)')
        
        if result:
            self.bot.send_message(message.chat.id, messages.ERRORS[9])
            self.bot.register_next_step_handler(message, self.copy_collection)
            return

        # Getting a unique collection key from the database.
        fetch = db.Fetch(message.chat.id)
        key = fetch.user_attribute('session')

        # Making copies of cards from the original collection.
        date = datetime.datetime.now()
        insert = db.Insert(message.chat.id, 'collections', 'card')
        insert.copy_collection(message.text, key, date)
        
        # Inserting the name of the collection 
        # and the number of cards in the database.
        update = db.Update(message.chat.id, 'collections', 'collection')
        update.collection_attribute(key, 'name', f'{name} (Копия)')
        update.collection_attribute(key, 'cards', cards)

        # User status update.
        update = db.Update(message.chat.id)
        update.user_attribute('action', 0)
        update.user_attribute('session', None)
        update.change_user_attribute('collections', 1)
        update.change_user_attribute('cards', cards)

        # Adding karma to the user whose collection was copied.
        if karma != message.chat.id:
            update = db.Update(karma)
            update.change_user_attribute('karma', 1)

        text = messages.COLLECTIONS['COLLECTION_COPIED']
        self.bot.send_message(message.chat.id, text.format(name))
        self.send_menu(message)

    def _save_collection(self, message):
        '''Get the name of the collection and save it to the database.
        
        Parameters
        ----------
        message : Message
            User message.
        '''

        handler = tools.Handler(self.bot)
        if handler.cancel(message):
            return

        # Checking for the existence of a collection with a similar key.
        fetch = db.Fetch(message.chat.id, 'collections', 'collection')
        copy_key = fetch.general_collection(message.text, 'key')

        if copy_key:
            self.copy_collection(message)
            return

        # Checking for a duplicate collection in the database.
        fetch = db.Fetch(message.chat.id, 'collections', 'collection')
        result = fetch.copy_check('name', message.text)
        
        if result:
            self.bot.send_message(message.chat.id, messages.ERRORS[3])
            self.bot.register_next_step_handler(message, self._save_collection)
            return

        # Getting a unique collection key from the database.
        fetch = db.Fetch(message.chat.id)
        key = fetch.user_attribute('session')
        
        # Inserting the collection name to the database.
        update = db.Update(message.chat.id, 'collections', 'collection')
        update.collection_attribute(key, 'name', message.text)

        # User status update.
        update = db.Update(message.chat.id)
        update.user_attribute('action', 0)
        update.user_attribute('session', None)
        update.change_user_attribute('collections', 1)

        text = messages.COLLECTIONS['COLLECTION_CREATED']
        self.bot.send_message(message.chat.id, text.format(message.text))
        self.send_menu(message)

    def _create_menu(self, message):
        '''Create user collections menu.
        
        Parameters
        ----------
        message : Message
            User message.
        
        Returns
        -------
        menu : InlineKeyboardMarkup
            Collections menu.
        '''

        # Getting information about collections from the database.
        fetch = db.Fetch(message.chat.id, 'collections', 'collection')
        info = fetch.user_collections()

        # Create a menu from all user collections.
        if info:
            buttons = tools.Format.buttons('collection_show_{}', info, 3, 1)
            keyboard = tools.Maker.keyboard(2, **buttons)
        else:
            keyboard = None

        # Create menu.
        menu_buttons = messages.COLLECTIONS['BUTTONS']
        menu = tools.Maker.keyboard(2, keyboard, **menu_buttons)

        return menu


class Collection:
    def __init__(self, bot):
        self.bot = bot

    def call_menu(self, call):
        '''Changing the message on the collection menu.
        
        Parameters
        ----------
        call : CallbackQuery
            Response to button press.
        '''

        key = re.findall(r'\w-\d+-\d+-\w', call.data)[0]
        menu, text = self._create_menu(call.message, key)

        self.bot.answer_callback_query(call.id)
        self.bot.edit_message_text(text=text,
                                chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                parse_mode='Markdown',
                                reply_markup=menu)

    def send_menu(self, message, key):
        '''Sending a collection menu.
        
        Parameters
        ----------
        message : Message
            User message.
        key : str
            Unique collection key.
        '''

        menu, text = self._create_menu(message, key)
        menu_message = self.bot.send_message(chat_id=message.chat.id,
                                            text=text,
                                            parse_mode='Markdown',
                                            reply_markup=menu)

        # Updating the message_id of the Private Office.
        update = db.Update(message.chat.id)
        update.user_attribute('menu_id', menu_message.message_id)

    def continue_learning(self, call):
        '''Training program.

        Parameters
        ----------
        call : CallbackQuery
            Response to button press.
        '''

        key = re.findall(r'\w-\d+-\d+-\w', call.data)[0]

        # Find a card that the user has repeated fewer times.
        fetch = db.Fetch(call.message.chat.id, 'collections', 'card')
        cards = fetch.user_cards(key)

        if not cards:
            self.bot.answer_callback_query(call.id, messages.ERRORS[8], True)
            return

        # Choosing the optimal card for repetition.
        rare_card = sorted(cards, key=lambda card: card[6])[0]
        date_format = '%Y-%m-%d %H:%M:%S.%f'
        card_date = datetime.datetime.strptime(rare_card[6], date_format)

        # Card repetition cycle.
        if (card_date - datetime.datetime.now()).days >= 0:
            text_date = tools.Format.date(rare_card[6])
            text = messages.CARDS['THE_END'].format(text_date)
            display = not ('result' in call.data)
            self.bot.answer_callback_query(call.id, text, display)

        # Create a card study menu.
        buttons = messages.COLLECTION['CONTINUE_BUTTONS']
        keyboard = tools.Format.keyboard(buttons=buttons,
                                        card=rare_card[2],
                                        collection=rare_card[1])
        menu = tools.Maker.keyboard(1, **keyboard)

        self.bot.answer_callback_query(call.id)
        self.bot.edit_message_text(text=rare_card[4],
                                chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                reply_markup=menu)

    def rename(self, call):
        '''Renaming a collection.

        Parameters
        ----------
        call : CallbackQuery
            Response to button press.
        '''

        handler = tools.Handler(self.bot)
        if handler.error(call.message) or handler.cancel(call.message):
            return

        key = re.findall(r'\w-\d+-\d+-\w+', call.data)[0]

        # User status update.
        update = db.Update(call.message.chat.id)
        update.user_attribute('action', 2)
        update.user_attribute('session', key)

        text = messages.COLLECTIONS['RENAME_COLLECTION']
        self.bot.answer_callback_query(call.id, text, True)
        self.bot.send_message(call.message.chat.id, text)
        self.bot.register_next_step_handler(call.message, self._save_new_name)

    def delete_menu(self, call):
        '''Delete collection menu.

        Parameters
        ----------
        call : CallbackQuery
            Response to button press.
        '''

        # Create a collection deletion menu.
        key = re.findall(r'\w-\d+-\d+-\w+', call.data)[0]
        buttons = messages.COLLECTION['DELETE_BUTTONS']
        keyboard = tools.Format.keyboard(buttons=buttons,
                                        collection=key)
        menu = tools.Maker.keyboard(1, **keyboard)

        text = messages.COLLECTION['DELETE']['WARNING']
        self.bot.answer_callback_query(call.id)
        self.bot.edit_message_text(text=text,
                                chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                reply_markup=menu,
                                parse_mode='Markdown')

    def delete_yes(self, call):
        '''Consent to delete collection.

        Parameters
        ----------
        call : CallbackQuery
            Response to button press.
        '''

        key = re.findall(r'\w-\d+-\d+-\w+', call.data)[0]

        # Getting collection name from database.
        fetch = db.Fetch(call.message.chat.id, 'collections', 'collection')
        name = fetch.collection_attribute(key, 'name')
        cards = fetch.collection_attribute(key, 'cards')

        # Change the number of collections and cards in the user profile.
        update_user_status = db.Update(call.message.chat.id)
        update_user_status.change_user_attribute('collections', -1)
        update_user_status.change_user_attribute('cards', -int(cards))

        # Removing a collection from a database.
        delete = db.Delete(call.message.chat.id, 'collections', 'collection')
        delete.delete_collection(key)

        # Removing all cards in a collection from the database.
        delete = db.Delete(call.message.chat.id, 'collections', 'card')
        delete.delete_collection_cards(key)

        text = messages.COLLECTION['DELETE']['SUCCESSFUL'].format(name)
        self.bot.answer_callback_query(call.id, text, True)

        collections = Collections(self.bot)
        collections.call_menu(call)

    def delete_no(self, call):
        '''Cancel deleting a collection.

        Parameters
        ----------
        call : CallbackQuery
            Response to button press.
        '''

        text = messages.COLLECTION['DELETE']['CANCELED']
        self.bot.answer_callback_query(call.id, text, True)
        self.call_menu(call)

    def _save_new_name(self, message):
        '''Getting a new collection name.
        
        Parameters
        ----------
        message : Message
            User message.
        '''

        handler = tools.Handler(self.bot)
        if handler.cancel(message):
            return

        # Getting the name of a collection to check for a duplicate
        # collection in the database.
        fetch = db.Fetch(message.chat.id, 'collections', 'collection')
        result = fetch.copy_check('name', message.text)

        if result:
            self.bot.send_message(message.chat.id, messages.ERRORS[3])
            self.bot.register_next_step_handler(message, self._save_new_name)
            return

        # Getting a unique key and old collection name.
        fetch_status = db.Fetch(message.chat.id)
        key = fetch_status.user_attribute('session')
        old_name = fetch.collection_attribute(key, 'name')

        # Updating the collection name in the database.
        update = db.Update(message.chat.id, 'collections', 'collection')
        update.collection_attribute(key, 'name', message.text)

        # User status update.
        update = db.Update(message.chat.id)
        update.user_attribute('action', 0)
        update.user_attribute('session', None)

        text = messages.COLLECTIONS['COLLECTION_RENAMED']
        formatted_text = text.format(old_name, message.text)
        self.bot.send_message(message.chat.id, formatted_text)
        self.send_menu(message, key)

    def _create_menu(self, message, key):
        '''Creating the main menu and collection text.

        Parameters
        ----------
        message : Message
            User message.
        key : str
            Unique collection key.
        
        Returns
        -------
        menu : InlineKeyboardMarkup
            Collection menu.
        text : str
            Collection interface text.
        '''

        # Getting information about a collection from a database.
        fetch = db.Fetch(message.chat.id, 'collections', 'collection')
        name = fetch.collection_attribute(key, 'name')
        cards = fetch.collection_attribute(key, 'cards')
        date = tools.Format.date(fetch.collection_attribute(key, 'date'))

        # Creating a collection menu.
        buttons = messages.COLLECTION['BUTTONS']
        keyboard = tools.Format.keyboard(buttons=buttons, collection=key)
        menu = tools.Maker.keyboard(2, **keyboard)
        text = messages.COLLECTION['INTERFACE'].format(name, key, cards, date)
        
        return menu, text

