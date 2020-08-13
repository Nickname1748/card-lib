import re
import random
import datetime

import tools
import messages
import collection
import database as db


class Cards:
    def __init__(self, bot):
        self.bot = bot

    def call_menu(self, call, key=None, level=None):
        '''Change the message on the collection cards menu.
        
        Parameters
        ----------
        call : CallbackQuery
            Response to button press.
        key : str
            Unique collection key (default is None).
        level : int
            Menu page (default is None).
        '''

        if key == None:
            key = re.findall(r'\w-\d+-\d+-\w', call.data)[0]
        if level == None:
            level = int(re.findall(r'_\w+-\d+-\d+-\w+_\w+_(\d+)', call.data)[0])

        menu, text = self._create_menu(call.message, key, level)

        self.bot.answer_callback_query(call.id)
        self.bot.edit_message_text(text=text,
                                chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                reply_markup=menu)

    def send_menu(self, message, key):
        '''Sending menu cards collection.
        
        Parameters
        ----------
        call : CallbackQuery
            Response to button press.
        key : str
            Unique collection key (default is None).
        level : int
            Menu page (default is None).
        '''

        menu, text = self._create_menu(message, key)
        menu_message = self.bot.send_message(chat_id=message.chat.id,
                                            text=text,
                                            reply_markup=menu)

        # Updating the message_id of the Private Office.
        update = db.Update(message.chat.id)
        update.user_attribute('menu_id', menu_message.message_id)

    def create_card(self, call):
        '''Create a card.
        
        Parameters
        ----------
        call : CallbackQuery
            Response to button press.
        '''

        handler = tools.Handler(self.bot)
        if handler.error(call.message) or handler.cancel(call.message):
            return
        
        key = re.findall(r'\w-\d+-\d+-\w+', call.data)[0]
        card_key = f'c-{random.randint(1, 1000000000)}-' \
                f'{random.randint(1, 1000000000)}-d'

        # User status update.
        update = db.Update(call.message.chat.id)
        update.user_attribute('action', 3)
        update.user_attribute('session', card_key)

        # Allocating space for the card in the database.
        insert = db.Insert(call.message.chat.id, 'collections', 'card')
        insert.create_card(key, card_key, datetime.datetime.now())

        text = messages.CARDS['CARD_NAME']
        self.bot.answer_callback_query(call.id, text, True)
        self.bot.send_message(call.message.chat.id, text)
        self.bot.register_next_step_handler(call.message, self._card_name)

    def _card_name(self, message):
        '''Getting the name of the card.
        
        Parameters
        ----------
        message : Message
            User message.
        '''

        handler = tools.Handler(self.bot)
        if handler.cancel(message):
            return
        
        # Getting a unique card key.
        fetch = db.Fetch(message.chat.id)
        card_key = fetch.user_attribute('session')

        # Getting the unique key of the collection that the card belongs to.
        fetch = db.Fetch(message.chat.id, 'collections', 'card')
        key = fetch.card_attribute(card_key, 'key')

        # Checking for the existence of a duplicate card in the database.
        fetch = db.Fetch(message.chat.id, 'collections', 'card')
        result = fetch.card_copy_check(key, 'name', message.text)
        
        if result:
            self.bot.send_message(message.chat.id, messages.ERRORS[6])
            self.bot.register_next_step_handler(message, self._card_name)
            return
        
        # Inserting the card name to the database.
        update = db.Update(message.chat.id, 'collections', 'card')
        update.card_attribute(card_key, 'name', message.text)

        text = messages.CARDS['CARD_DESCRIPTION']
        self.bot.send_message(message.chat.id, text)
        self.bot.register_next_step_handler(message, self._card_description)
    
    def _card_description(self, message):
        '''Getting a card description.
        
        Parameters
        ----------
        message : Message
            User message.
        '''

        handler = tools.Handler(self.bot)
        if handler.cancel(message):
            return

        # Getting a unique card key.
        fetch = db.Fetch(message.chat.id)
        card_key = fetch.user_attribute('session')

        # Getting the unique key of the collection that the card belongs to.
        fetch = db.Fetch(message.chat.id, 'collections', 'card')
        key = fetch.card_attribute(card_key, 'key')

        # Getting the card name.
        fetch = db.Fetch(message.chat.id, 'collections', 'card')
        card_name = fetch.card_attribute(card_key, 'name')
        
        # Inserting a card description to the database.
        update = db.Update(message.chat.id, 'collections', 'card')
        update.card_attribute(card_key, 'description', message.text)

        # Updating user status and number of cards.
        update = db.Update(message.chat.id)
        update.user_attribute('action', 0)
        update.user_attribute('session', None)
        update.change_user_attribute('cards', 1)

        # Updating the number of cards in the user's collection.
        update = db.Update(message.chat.id, 'collections', 'collection')
        update.change_collection_attribute(key, 'cards', 1)

        text = messages.CARDS['CARD_CREATED']
        self.bot.send_message(message.chat.id, text.format(card_name))
        self.send_menu(message, key)

    def _create_menu(self, message, key, level=0):
        '''User collection cards.

        Parameters
        ----------
        call : CallbackQuery
            Response to button press.
        key : str
            Unique collection key.
        level : int
            Menu page (default is 0).
        
        Returns
        -------
        menu : InlineKeyboardMarkup
            Collection menu.
        text : str
            Collection interface text.
        '''

        # Getting the name of a collection from the database.
        fetch = db.Fetch(message.chat.id, 'collections', 'collection')
        collection_name = fetch.collection_attribute(key, 'name')

        # Getting card information from the database.
        fetch = db.Fetch(message.chat.id, 'collections', 'card')
        cards_info = fetch.user_cards(key)

        if cards_info:
            # Adding navigation buttons to menu.
            nav_obj = cards_info[8*level : 8*(level + 1)]
            navigation = tools.Maker.navigation(key, len(cards_info), level)

            # Creating a menu from all cards in a user collection.
            cards = tools.Format.buttons('card_show_{}', nav_obj, 4, 2)
            cards_menu = tools.Maker.keyboard(2, navigation, **cards)
        else:
            cards_menu = None

        # Adding exit buttons to menu.
        buttons = messages.CARDS['BUTTONS']
        keyboard = tools.Format.keyboard(buttons=buttons, collection=key)
        menu = tools.Maker.keyboard(2, cards_menu, **keyboard)
        text = messages.CARDS['INTERFACE'].format(collection_name)
        
        return menu, text


class Card:
    def __init__(self, bot):
        self.bot = bot

    def call_menu(self, call):
        '''Changing the message to the main menu of the card.
        
        Parameters
        ----------
        call : CallbackQuery
            Response to button press.
        '''

        card_key = re.findall(r'\w-\d+-\d+-\w+', call.data)[0]
        menu, text = self._create_menu(call.message, card_key)

        self.bot.answer_callback_query(call.id)
        self.bot.edit_message_text(text=text,
                                chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                reply_markup=menu,
                                parse_mode='Markdown')

    def send_menu(self, message, card_key):
        '''Sending the main menu of the card.
        
        Parameters
        ----------
        message : Message
            User message.
        card_key : str
            Unique card key.
        '''

        menu, text = self._create_menu(message, card_key)
        menu_message = self.bot.send_message(chat_id=message.chat.id,
                                            text=text,
                                            reply_markup=menu,
                                            parse_mode='Markdown')

        # Updating the message_id of the Private Office.
        update = db.Update(message.chat.id)
        update.user_attribute('menu_id', menu_message.message_id)

    def start_learning(self, call):
        '''Start learning the card.
        
        Parameters
        ----------
        call : CallbackQuery
            Response to button press.
        '''

        card_key = re.findall(r'\w-\d+-\d+-\w', call.data)[0]

        # Getting card information from the database.
        fetch = db.Fetch(call.message.chat.id, 'collections', 'card')
        description = fetch.card_attribute(card_key, 'description')
        key = fetch.card_attribute(card_key, 'key')

        # Creating a card result menu.
        buttons = messages.CARD['RESULT_BUTTONS']
        keyboard = tools.Format.keyboard(buttons=buttons,
                                        card=card_key,
                                        collection=key)
        menu = tools.Maker.keyboard(1, **keyboard)
        
        self.bot.answer_callback_query(call.id)
        self.bot.edit_message_text(text=description,
                                chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                parse_mode='Markdown',
                                reply_markup=menu)

    def result(self, call):
        '''Getting learning outcomes and moving to the next card.
        
        Parameters
        ----------
        call : CallbackQuery
            Response to button press.
        '''

        minutes = int(call.data[-4:])
        status = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
        card_key = re.findall(r'_\w-\d+-\d+-\w_(\w-\d+-\d+-\w)', call.data)[0]

        # Inserting a new result to the database.
        update = db.Update(call.message.chat.id, 'collections', 'card')
        update.card_attribute(card_key, 'status', status)

        training = collection.Collection(self.bot)
        training.continue_learning(call)

    def rename(self, call):
        '''Renaming a card.
        
        Parameters
        ----------
        call : CallbackQuery
            Response to button press.
        '''

        handler = tools.Handler(self.bot)
        if handler.error(call.message) or handler.cancel(call.message):
            return
        
        card_key = re.findall(r'\w-\d+-\d+-\w+', call.data)[0]

        # User status update.
        update = db.Update(call.message.chat.id)
        update.user_attribute('action', 4)
        update.user_attribute('session', card_key)

        text = messages.CARDS['RENAME_CARD']
        self.bot.answer_callback_query(call.id, text, True)
        self.bot.send_message(call.message.chat.id, text)
        self.bot.register_next_step_handler(call.message, self._save_new_name)

    def edit_description(self, call):
        '''Change card description.
        
        Parameters
        ----------
        call : CallbackQuery
            Response to button press.
        '''

        handler = tools.Handler(self.bot)
        if handler.error(call.message) or handler.cancel(call.message):
            return
        
        card_key = re.findall(r'\w-\d+-\d+-\w+', call.data)[0]

        # User status update.
        update = db.Update(call.message.chat.id)
        update.user_attribute('action', 5)
        update.user_attribute('session', card_key)

        next_step = self._save_new_description
        text = messages.CARDS['EDIT_DESCRIPTION_CARD']
        self.bot.answer_callback_query(call.id, text, True)
        self.bot.send_message(call.message.chat.id, text)
        self.bot.register_next_step_handler(call.message, next_step)

    def delete_menu(self, call):
        '''Delete card menu.
        
        Parameters
        ----------
        call : CallbackQuery
            Response to button press.
        '''

        card_key = re.findall(r'\w-\d+-\d+-\w+', call.data)[0]

        # Creating a menu for deleting a card.
        buttons = messages.CARD['DELETE_BUTTONS']
        keyboard = tools.Format.keyboard(buttons=buttons, card=card_key)
        menu = tools.Maker.keyboard(1, **keyboard)

        text = messages.CARD['DELETE']['WARNING']
        self.bot.answer_callback_query(call.id)
        self.bot.edit_message_text(text=text,
                                chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                reply_markup=menu)

    def delete_yes(self, call):
        '''Consent to remove the card.
        
        Parameters
        ----------
        call : CallbackQuery
            Response to button press.
        '''

        card_key = re.findall(r'\w-\d+-\d+-\w+', call.data)[0]

        # Getting card information from the database.
        fetch = db.Fetch(call.message.chat.id, 'collections', 'card')
        name = fetch.card_attribute(card_key, 'name')
        key = fetch.card_attribute(card_key, 'key')

        # Updating the number of user cards.
        update = db.Update(call.message.chat.id)
        update.change_user_attribute('cards', -1)

        # Updating the number of cards in the user's collection.
        update = db.Update(call.message.chat.id, 'collections', 'collection')
        update.change_collection_attribute(key, 'cards', -1)

        # Removing a card from the database.
        delete = db.Delete(call.message.chat.id, 'collections', 'card')
        delete.delete_card(card_key)

        text = messages.CARD['DELETE']['SUCCESSFUL'].format(name)
        self.bot.answer_callback_query(call.id, text, True)

        cards = Cards(self.bot)
        cards.call_menu(call, key, 0)

    def delete_no(self, call):
        '''Cancel card deletion.
        
        Parameters
        ----------
        call : CallbackQuery
            Response to button press.
        '''

        text = messages.CARD['DELETE']['CANCELED']
        self.bot.answer_callback_query(call.id, text, True)
        self.call_menu(call)

    def info(self, call):
        '''Additional information about the card.
        
        Parameters
        ----------
        call : CallbackQuery
            Response to button press.
        '''

        card_key = re.findall(r'\w-\d+-\d+-\w+', call.data)[0]

        # Getting card information from the database.
        fetch = db.Fetch(call.message.chat.id, 'collections', 'card')
        key = fetch.card_attribute(card_key, 'key')
        name = fetch.card_attribute(card_key, 'name')
        description = fetch.card_attribute(card_key, 'description')
        date = tools.Format.date(fetch.card_attribute(card_key, 'date'))
        status = tools.Format.date(fetch.card_attribute(card_key, 'status'))

        # Creating a card menu.
        buttons = messages.CARD['INFO_BUTTONS']
        keyboard = tools.Format.keyboard(buttons=buttons,
                                        card=card_key,
                                        collection=key)
        menu = tools.Maker.keyboard(2, **keyboard)

        text = messages.CARD['INFO'].format(name, description, date, status)
        self.bot.answer_callback_query(call.id)
        self.bot.edit_message_text(text=text,
                                chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                reply_markup=menu,
                                parse_mode='Markdown')

    def _create_menu(self, message, card_key):
        '''Creating the main card menu.

        Parameters
        ----------
        message : Message
            User message.
        card_key : str
            Unique card key.

        Returns
        -------
        menu : InlineKeyboardMarkup
            Card menu.
        text : str
            Card interface text.
        '''

        # Getting card information from the database.
        fetch = db.Fetch(message.chat.id, 'collections', 'card')
        key = fetch.card_attribute(card_key, 'key')
        name = fetch.card_attribute(card_key, 'name')
        description = fetch.card_attribute(card_key, 'description')

        # Creating a card menu.
        buttons = messages.CARD['BUTTONS']
        keyboard = tools.Format.keyboard(buttons=buttons,
                                        card=card_key,
                                        collection=key)
        menu = tools.Maker.keyboard(2, **keyboard)
        text = messages.CARD['INTERFACE'].format(name, description)

        return menu, text

    def _save_new_name(self, message):
        '''Getting a new card name.
        
        Parameters
        ----------
        message : Message
            User message.
        '''

        handler = tools.Handler(self.bot)
        if handler.cancel(message):
            return

        # Getting a unique card key.
        fetch = db.Fetch(message.chat.id)
        card_key = fetch.user_attribute('session')

        # Getting the unique key of the collection that the card belongs to.
        fetch = db.Fetch(message.chat.id, 'collections', 'card')
        key = fetch.card_attribute(card_key, 'key')

        # Getting the old card name and 
        # checking for a duplicate card in the database.
        fetch = db.Fetch(message.chat.id, 'collections', 'card')
        old_name = fetch.card_attribute(card_key, 'name')
        result = fetch.card_copy_check(key, 'name', message.text)

        if result:
            self.bot.send_message(message.chat.id, messages.ERRORS[6])
            self.bot.register_next_step_handler(message, self._save_new_name)
            return

        # Updating the card name in the database.
        update = db.Update(message.chat.id, 'collections', 'card')
        update.card_attribute(card_key, 'name', message.text)

        # User status update.
        update = db.Update(message.chat.id)
        update.user_attribute('action', 0)
        update.user_attribute('session', None)

        text = messages.CARDS['CARD_RENAMED'].format(old_name, message.text)
        self.bot.send_message(message.chat.id, text)
        self.send_menu(message, card_key)

    def _save_new_description(self, message):
        '''Getting a new card description.
        
        Parameters
        ----------
        message : Message
            User message.
        '''
        
        handler = tools.Handler(self.bot)
        if handler.cancel(message):
            return

        # Getting a unique card key from the database.
        fetch = db.Fetch(message.chat.id)
        card_key = fetch.user_attribute('session')

        # Card description update.
        update = db.Update(message.chat.id, 'collections', 'card')
        update.card_attribute(card_key, 'description', message.text)

        # User status update.
        update = db.Update(message.chat.id)
        update.user_attribute('action', 0)
        update.user_attribute('session', None)

        self.bot.send_message(message.chat.id, messages.CARDS['CARD_EDITED'])
        self.send_menu(message, card_key)

