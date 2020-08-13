import telebot
import datetime

import bot
import messages
import database as db


class Format:
    @staticmethod
    def keyboard(buttons, **format_obj):
        '''Creating a keyboard with insertable elements.

        Parameters
        ----------
        buttons : list
            The buttons that the keyboard will be made of.
        **format_obj
            Inserted elements.
        
        Returns
        -------
        keyboard : dict
            Keyboard.
        '''

        keyboard = {}
        for button in buttons:
            keyboard[button] = buttons[button].format(**format_obj)

        return keyboard

    @staticmethod
    def buttons(data, format_obj, name_id=0, data_id=0):
        '''Creating buttons with insertable elements.

        Parameters
        ----------
        data : str
            Navigation bar.
        format_obj : list
            The object from which the buttons will be created.
        name_id : int
            Button name ID (default is 0).
        data_id : int
            ID of the variable to insert into the navigation bar (default is 0).
        
        Returns
        -------
        buttons : dict
            Buttons.
        '''

        buttons = {}
        for item in format_obj:
            buttons[item[name_id]] = data.format(item[data_id])

        return buttons

    @staticmethod
    def date(date):
        '''Changing the date format.

        Parameters
        ----------
        date : ste
            Date to be converted.
        
        Returns
        -------
        new_date : str
            Converted date.
        '''

        date_form = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')
        new_date = date_form.strftime('%d %B (%A), %H:%M')
        return new_date


class Handler:
    def __init__(self, bot):
        self.bot = bot

    def error(self, message):
        '''Checking for errors.

        Parameters
        ----------
        message : Message
            User message.

        Returns
        -------
        bool
            True if error, False otherwise.
        '''

        # Getting information about the user's actions and
        # the ID of his last Personal Account.
        fetch = db.Fetch(message.chat.id)
        action = fetch.user_attribute('action')
        menu_id = fetch.user_attribute('menu_id')

        if action == 1:
            self.bot.send_message(message.chat.id, messages.ERRORS[1])
            return True

        elif action == 2:
            self.bot.send_message(message.chat.id, messages.ERRORS[2])
            return True

        elif action == 3:
            self.bot.send_message(message.chat.id, messages.ERRORS[4])
            return True

        elif action == 4:
            self.bot.send_message(message.chat.id, messages.ERRORS[5])
            return True

        elif action == 5:
            self.bot.send_message(message.chat.id, messages.ERRORS[7])
            return True

        elif message.message_id != menu_id and action != 1:
            text = messages.ERRORS[0]
            self.bot.edit_message_text(text, message.chat.id, message.message_id)
            return True

        return False

    def cancel(self, message):
        '''Cancellation check.

        Parameters
        ----------
        message : Message
            User message.

        Returns
        -------
        bool
            True if successful, False otherwise.
        '''

        if not message.text or message.text == '/cancel':
            bot.cancel(message)
            return True

        return False


class Maker:
    @staticmethod
    def keyboard(row_width=3, keyboard=None, **buttons):
        '''Creating a menu keyboard.

        Notes
        -----
            Please note that when passing a ready keyboard to keyboard_maker
            its row_width will not change, since in this case
            the method will not create a new keyboard,
            but will supplement the current one with new buttons!

        Parameters
        ----------
        row_width : int
            Number of buttons per line (default is 3).
        keyboard : InlineKeyboardMarkup, optional
            Ready keyboard to add buttons to (default is None).
        **buttons
            The buttons that will make up the keyboard.
        
        Returns
        -------
        keyboard : InlineKeyboardMarkup
            Keyboard.
        '''

        if not keyboard:
            keyboard = telebot.types.InlineKeyboardMarkup(row_width)

        keyboard_buttons = [telebot.types.InlineKeyboardButton(text=text,
            callback_data=data) for text, data in buttons.items()]

        keyboard.add(*keyboard_buttons)
        return keyboard

    @staticmethod
    def navigation(key, lenght, level=0, sep=8):
        '''Creating a navigation keyboard.

        Parameters
        ----------
        key : str
            Unique collection key.
        lenght : int
            Length of the list of page elements.
        level : int
            The page the user is on (default is 0).
        sep : int
            Number of items per page (default is 8).
        
        Returns
        -------
        keyboard : InlineKeyboardMarkup
            Keyboard with navigation buttons.
        '''
        
        navigation = {0: '• {} •', 1: '{}', 'data': 'cards_{}_level_{}'}
        system_len = lenght//sep if lenght%sep == 0 else lenght//sep + 1

        buttons = []
        keyboard = telebot.types.InlineKeyboardMarkup(2)
        
        # Creating a keyboard without navigation.
        if lenght < 5*sep + 1:
            buttons = [telebot.types.InlineKeyboardButton(
                text=navigation[not (button == level)].format(button + 1),
                callback_data=navigation['data'].format(key, button))
                    for button in range(system_len)]

        # Creating a keyboard with navigation.
        else:
            for button in range(5):
                # Handling the first two buttons.
                if level == 0 or level  == 1:
                    nav = ['{}', '{}', '{}', '{} ›', '{} »']
                    nav[level] = '• {} •'

                    data = system_len if button == 4 else button + 1

                # Handling the last two buttons.
                elif level == (system_len - 1) or level == (system_len - 2):
                    nav = ['« {}', '‹ {}', '{}', '{}', '{}']
                    nav[level - system_len + 5] = '• {} •'

                    data = (button + 1 if button == 0
                            else system_len + button - 4)
                
                # Full navigation handling.
                else:
                    nav = ['« {}', '‹ {}', '• {} •', '{} ›', '{} »']

                    data = (1 if button == 0 else system_len
                            if button == 4 else button + level - 1)

                text = nav[button].format(data)
                buttons.append(telebot.types.InlineKeyboardButton(text=text,
                    callback_data=navigation['data'].format(key, data - 1)))

        keyboard.row(*buttons)
        return keyboard

