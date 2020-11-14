import re
import random
import difflib

import messages
import database as db


class Intents:
    def __init__(self, message):
        self.message = message

    def phrase_handler(self):
        '''Defines the type of user questione.

        Returns
        -------
        fetch : str
            Returns the bot's response
            or message about unrecognized text.
        '''

        actions = {}
        text = re.sub(r'(\,|\.|\?|\!|\:)', '', self.message.text.lower())

        fetch = db.Fetch(self.message.chat.id, 'intents', 'training_phrases')
        intents = fetch.intents_attribute()

        for intent in intents:
            if intent[1] in text:
                actions[intent[0]] = intent[1]

        phrases = ''
        fetch = db.Fetch(self.message.chat.id, 'intents', 'responses')

        for key in actions:
            var_text = random.choice(fetch.responses_attribute(key))[0]

            if key == 'find':
                phrases += f'{var_text} '.format(self._action(actions[key]))
            else:
                phrases += f'{var_text} '

        if phrases == '':
            var_text = random.choice(fetch.responses_attribute('error'))[0]
            phrases = var_text

        return phrases

    def _action(self, ans):
        '''Performs the action requested by the user.

        Returns
        -------
        fetch : str
            Returns the bot's response
            or message about unrecognized text.
        '''

        if re.findall(':', self.message.text):
            try:
                response = re.findall(r'\: (.*)[\,\.\?\!]', self.message.text)[0]
            except:
                try:
                    response = re.findall(r'\: (.*)\b', self.message.text)[0]
                except:
                    response = 'error'

            try:
                fetch = db.Fetch(self.message.chat.id, 'collections', 'card')
                all_cards = [i[4] for i in fetch.all_user_cards()]
                card = difflib.get_close_matches(response, all_cards)
            except:
                return messages.ERRORS[10]

            if card:
                fetch = db.Fetch(self.message.chat.id, 'collections', 'card')
                card = fetch.general_card(card[0])
                return card[5]

        elif ans in self.message.text.lower():
            try:
                try:
                    fr_text = fr'{ans} (.*)[\,\.\?\!]'
                    response = re.findall(fr_text, self.message.text)[0]
                except:
                    fr_text = fr'{ans.capitalize()} (.*)[\,\.\?\!]'
                    response = re.findall(fr_text, self.message.text)[0]
            except:
                try:
                    try:
                        fr_text = fr'{ans} (.*)\b'
                        response = re.findall(fr_text, self.message.text)[0]
                    except:
                        fr_text = fr'{ans.capitalize()} (.*)\b'
                    response = re.findall(fr_text, self.message.text)[0]
                except:
                    response = 'error'

            try:
                fetch = db.Fetch(self.message.chat.id, 'collections', 'card')
                all_cards = [i[4] for i in fetch.all_user_cards()]
                card = difflib.get_close_matches(response, all_cards)
            except:
                return messages.ERRORS[10]

            if card:
                fetch = db.Fetch(self.message.chat.id, 'collections', 'card')
                card = fetch.general_card(card[0])
                return card[5]

        return messages.ERRORS[10]

