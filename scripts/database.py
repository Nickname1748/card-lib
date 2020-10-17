import random
import sqlite3


class Create:
    def users_db(self, db_name='users', db_table='user'):
        '''Creating a user database.

        Parameters
        ----------
        db_name : str
            Database name (default is 'users').
        db_table : str
            Database table name (default is 'user').
        '''

        connect = sqlite3.connect(f'{db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''CREATE TABLE {db_table}
                        (user_id integer, menu_id integer,
                        action integer, session text,
                        username text, first_name text,
                        last_name text, karma integer,
                        collections integer, cards integer)''')
        connect.commit()

    def collections_db(self, db_name='collections', db_table='collection'):
        '''Creating a collection database.
        
        Parameters
        ----------
        db_name : str
            Database name (default is 'collections').
        db_table : str
            Database table name (default is 'collection').
        '''

        connect = sqlite3.connect(f'{db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''CREATE TABLE {db_table}
                        (user_id integer, key text,
                        date text, name text,
                        cards integer)''')
        connect.commit()

    def cards_db(self, db_name='collections', db_table='card'):
        '''Creating a card database.

        Parameters
        ----------
        db_name : str
            Database name (default is 'collections').
        db_table : str
            Database table name (default is 'card').
        '''

        connect = sqlite3.connect(f'{db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''CREATE TABLE {db_table}
                        (user_id integer, key text,
                        card_key integer, date text,
                        name text, description text,
                        status text)''')
        connect.commit()

    def intents_db(self, db_name='intents', db_table='training_phrases'):
        '''Creating a intents database.

        Parameters
        ----------
        db_name : str
            Database name (default is 'intents').
        db_table : str
            Database table name (default is 'training_phrases').
        '''

        connect = sqlite3.connect(f'{db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''CREATE TABLE {db_table}
                        (name text, user_expression text)''')
        connect.commit()

    def responses_db(self, db_name='intents', db_table='responses'):
        '''Creating a responses database.

        Parameters
        ----------
        db_name : str
            Database name (default is 'intents').
        db_table : str
            Database table name (default is 'responses').
        '''

        connect = sqlite3.connect(f'{db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''CREATE TABLE {db_table}
                        (name text, text_response text)''')
        connect.commit()


class Insert:
    def __init__(self, user_id, db_name='users', db_table='user'):
        self.user_id = user_id
        self.db_name = db_name
        self.db_table = db_table

    def new_user(self, menu_id=0,
                action=0, session=None,
                username=None, first_name=None,
                last_name=None, karma=0,
                collections=0, cards=0):
        '''Writing a new user to the database.

        Parameters
        ----------
        menu_id : int
            ID of the last Personal Account of the user (default is 0).
        action : int
            User activity (default is 0).
        session : str
            Current user session: collection key
            or card key (default is None).
        username : str
            User nickname (default is None).
        first_name : str
            User first name (default is None).
        last_name : str
            User last name (default is None).
        karma : int
            User bonus points (default is 0).
        collections : int
            Number of user collections (default is 0).
        cards : int
            Number of user cards (default is 0).
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''SELECT user_id FROM {self.db_table} 
                        WHERE user_id=?''', (self.user_id,))
        fetch = cursor.fetchall()

        if not fetch:
            cursor.execute(f'''INSERT INTO {self.db_table} 
                    VALUES (?,?,?,?,?,?,?,?,?,?)''', (self.user_id, menu_id,
                                                    action, session,
                                                    username, first_name,
                                                    last_name, karma,
                                                    collections, cards))
        
        connect.commit()
    
    def create_collection(self, key, date=None, name=None, cards=0):
        '''Writing a new user collection to the database.
        
        Parameters
        ----------
        key : str
            Unique collection key.
        date : str
            Collection creation date (default is None).
        name : str
            Collection name (default is None).
        cards : int
            Number of cards in the collection (default is 0).
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''INSERT INTO {self.db_table} 
                        VALUES (?,?,?,?,?)''', (self.user_id, key,
                                                date, name,
                                                cards))
        
        connect.commit()

    def create_card(self, key, card_key, date,
                    name=None, description=None):
        '''Writing a new user card to the database.

        Parameters
        ----------
        key : str
            Unique collection key.
        card_key : str
            Unique card key.
        date : str
            Card creation date.
        name : str
            Card name (default is None).
        description : str
            Card description (default is None).
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''INSERT INTO {self.db_table} 
                        VALUES (?,?,?,?,?,?,?)''', (self.user_id, key,
                                                    card_key, date,
                                                    name, description,
                                                    date))
        
        connect.commit()

    def copy_collection(self, original_key, key, date):
        '''Copying collection cards.

        Parameters
        ----------
        original_key : str
            Original collection key.
        key : str
            New collection key.
        date : str
            Collection copy creation date.
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''SELECT * FROM {self.db_table}
                        WHERE key=?''', (original_key,))
        fetch = cursor.fetchall()
        connect.commit()

        if fetch:
            connect = sqlite3.connect(f'{self.db_name}.db')
            cursor = connect.cursor()

            for card in fetch:
                card_key = f'c-{random.randint(1, 1000000000)}-' \
                        f'{random.randint(1, 1000000000)}-d'
                cursor.execute(f'''INSERT INTO {self.db_table} 
                        VALUES (?,?,?,?,?,?,?)''', (self.user_id, key,
                                                    card_key, date,
                                                    card[4], card[5],
                                                    date))
            connect.commit()

    def new_phrase(self, name, *text):
        '''Writes a new phrase and its response to the database.

        Parameters
        ----------
        name : str
            Event key assigned to the phrase.
        *text
            Text that can serve as a call to a phrase
            or a response to a phrase.
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()

        for phrase in text:
            cursor.execute(f'''INSERT INTO {self.db_table} 
                            VALUES (?,?)''', (name, phrase))
        
        connect.commit()


class Fetch:
    def __init__(self, user_id, db_name='users', db_table='user'):
        self.user_id = user_id
        self.db_name = db_name
        self.db_table = db_table

    def user_attribute(self, attribute):
        '''Getting the value of a user variable.

        Parameters
        ----------
        attribute : str
            Variable name.
        
        Returns
        -------
        fetch : str or int or None
            Returns the value of a variable. Returns None
            if the variable is not present in the database.
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''SELECT {attribute} FROM {self.db_table} 
                        WHERE user_id=?''', (self.user_id,))
        fetch = cursor.fetchall()
        connect.commit()

        if fetch:
            return fetch[0][0]
        else:
            return None

    def collection_attribute(self, key, attribute):
        '''Retrieving the value of some variable of the user's collection.

        Parameters
        ----------
        key : str
            Unique collection key.
        attribute : str
            Variable name.

        Returns
        -------
        fetch : str or int or None
            Returns the value of a variable. Returns None
            if the variable is not present in the database.
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''SELECT {attribute} FROM {self.db_table} 
                        WHERE (user_id=?) AND (key=?)''', (self.user_id, key))
        fetch = cursor.fetchall()
        connect.commit()

        if fetch:
            return fetch[0][0]
        else:
            return None

    def card_attribute(self, card_key, attribute):
        '''Retrieving the value of some user card variable.

        Parameters
        ----------
        card_key : str
            Unique card key.
        attribute : str
            Variable name.

        Returns
        -------
        fetch : str or int or None
            Returns the value of a variable. Returns None
            if the variable is not present in the database.
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''SELECT {attribute} FROM {self.db_table} 
                        WHERE (user_id=?)
                        AND (card_key=?)''', (self.user_id, card_key))
        fetch = cursor.fetchall()
        connect.commit()

        if fetch:
            return fetch[0][0]
        else:
            return None

    def user_collections(self):
        '''Retrieving information about all user collections.

        Returns
        -------
        fetch : list
            Information about all collections.
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''SELECT * FROM {self.db_table} 
                        WHERE user_id=?''', (self.user_id,))
        fetch = cursor.fetchall()
        connect.commit()

        if fetch:
            return fetch
        else:
            return None

    def user_cards(self, key):
        '''Retrieving information about all cards in a user's collection.

        Parameters
        ----------
        key : str
            Unique collection key.
        
        Returns
        -------
        fetch : list
            Information about all cards.
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''SELECT * FROM {self.db_table}
                        WHERE (user_id=?) AND (key=?)''', (self.user_id, key))
        fetch = cursor.fetchall()
        connect.commit()

        if fetch:
            return fetch
        else:
            return None

    def copy_check(self, attribute, value=0):
        '''Checking for similar variable values.
        
        Parameters
        ----------
        attribute : str
            Variable name.
        value : int
            Variable value.

        Returns
        -------
        bool
            True if successful, False otherwise.
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''SELECT user_id FROM {self.db_table} 
                        WHERE (user_id=?)
                        AND ({attribute}=?)''', (self.user_id, value))
        fetch = cursor.fetchall()
        connect.commit()

        if fetch:
            return True
        else:
            return False

    def card_copy_check(self, key, attribute, value=0):
        '''Checking for similar values of card variables.

        Parameters
        ----------
        key : str
            Unique key of the collection in which the card is located.
        attribute : str
            Variable name.
        value : int
            Variable value.

        Returns
        -------
        bool
            True if successful, False otherwise.
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''SELECT user_id FROM {self.db_table} 
                        WHERE (user_id=?) 
                        AND ({attribute}=?) 
                        AND (key=?)''', (self.user_id, value, key))
        fetch = cursor.fetchall()
        connect.commit()

        if fetch:
            return True
        else:
            return False

    def general_collection(self, key, attribute):
        '''Checking for the existence of a collection
        and getting certain variables of that collection.

        Parameters
        ----------
        key : str
            Unique collection key.
        attribute : str
            Variable name.
        
        Returns
        -------
        fetch: str or int or None
            Returns the value of a variable. Returns None
            if the variable is not present in the database.
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''SELECT {attribute} FROM {self.db_table}
                        WHERE key=?''', (key,))
        fetch = cursor.fetchall()
        connect.commit()

        if fetch:
            return fetch[0][0]
        else:
            return None

    def intents_attribute(self):
        '''Retrieves all information about bot phrases.

        Returns
        -------
        fetch : list or None
            Returns a list of bot phrases. Returns None
            if the bot did not find phrases in the database.
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''SELECT * FROM {self.db_table}''')
        fetch = cursor.fetchall()
        connect.commit()

        if fetch:
            return fetch
        else:
            return None

    def responses_attribute(self, name):
        '''Search for bot responses to user posts.

        Parameters
        ----------
        name : str
            Event key assigned to the phrase.

        Returns
        -------
        fetch : list or None
            Returns the bot's answer list. Returns None
            if the bot did not find phrases in the database.
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''SELECT text_response FROM {self.db_table} 
                        WHERE name=?''', (name,))
        fetch = cursor.fetchall()
        connect.commit()

        if fetch:
            return fetch
        else:
            return None

    def general_card(self, name):
        '''Search for cards with a specific name in the database.

        Parameters
        ----------
        name : str
            Card name.

        Returns
        -------
        fetch : tuple or None
            Returns all information about the first matching card.
            Returns None if there are no cards with
            the given name in the collection.
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''SELECT * FROM {self.db_table}
                        WHERE name=?''', (name,))
        fetch = cursor.fetchall()
        connect.commit()

        if fetch:
            return fetch[0]
        else:
            return None


class Update:
    def __init__(self, user_id, db_name='users', db_table='user'):
        self.user_id = user_id
        self.db_name = db_name
        self.db_table = db_table

    def user_attribute(self, attribute, value=0):
        '''Updating the value of a user variable.

        Parameters
        ----------
        attribute : str
            The name of the variable to be changed.
        value : int
            New variable value (default is 0).
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''UPDATE {self.db_table} SET {attribute}=?
                        WHERE user_id=?''', (value, self.user_id))
        connect.commit()

    def collection_attribute(self, key, attribute, value=0):
        '''Updating the value of a collection variable.

        Parameters
        ----------
        key : str
            Unique collection key.
        attribute : str
            The name of the variable to be changed.
        value : int
            New variable value (default is 0).
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''UPDATE {self.db_table} SET {attribute}=?
                        WHERE (user_id=?)
                        AND (key=?)''', (value, self.user_id, key))
        connect.commit()

    def card_attribute(self, card_key, attribute, value=0):
        '''Updating the value of a card variable.

        Parameters
        ----------
        card_key : str
            Unique card key.
        attribute : str
            The name of the variable to be changed.
        value : int
            New variable value (default is 0).
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''UPDATE {self.db_table} SET {attribute}=?
                        WHERE (user_id=?)
                        AND (card_key=?)''', (value, self.user_id, card_key))
        connect.commit()

    def change_user_attribute(self, attribute, value=0):
        '''Changing a user variable based on its previous value.
        
        Parameters
        ----------
        attribute : str
            The name of the variable to be changed.
        value : int
            The amount by which the value of the variable will change (default is 0).
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''UPDATE {self.db_table}
                        SET {attribute} = {attribute} + {value}
                        WHERE user_id=?''', (self.user_id,))
        connect.commit()

    def change_collection_attribute(self, key, attribute, value=0):
        '''Changing a collection variable based on its previous value.
        
        Parameters
        ----------
        card_key : str
            Unique collection key.
        attribute : str
            The name of the variable to be changed.
        value : int
            The amount by which the value of the variable will change (default is 0).
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''UPDATE {self.db_table}
                        SET {attribute} = {attribute} + {value}
                        WHERE (user_id=?) AND (key=?)''', (self.user_id, key))
        connect.commit()

    def change_card_attribute(self, card_key, attribute, value=0):
        '''Changing a card variable based on its previous value.

        Parameters
        ----------
        card_key : str
            Unique card key.
        attribute : str
            The name of the variable to be changed.
        value : int
            The amount by which the value of the variable will change (default is 0).
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''UPDATE {self.db_table}
                        SET {attribute} = {attribute} + {value}
                        WHERE (user_id=?)
                        AND (card_key=?)''', (self.user_id, card_key))
        connect.commit()


class Delete:
    def __init__(self, user_id, db_name='users', db_table='user'):
        self.user_id = user_id
        self.db_name = db_name
        self.db_table = db_table

    def delete_collection(self, key):
        '''Deleting a user collection.

        Parameters
        ----------
        key : str
            Unique collection key.
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''DELETE FROM {self.db_table}
                        WHERE (user_id=?) AND (key=?)''', (self.user_id, key))
        connect.commit()

    def delete_collection_cards(self, key):
        '''Removing all cards in a user's collection.

        Parameters
        ----------
        key : str
            Unique collection key.
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''SELECT * FROM {self.db_table}
                        WHERE key=?''', (key,))
        fetch = cursor.fetchall()
        connect.commit()

        if fetch:
            connect = sqlite3.connect(f'{self.db_name}.db')
            cursor = connect.cursor()

            for card in fetch:
                cursor.execute(f'''DELETE FROM {self.db_table}
                                WHERE (user_id=?)
                                AND (key=?)''', (self.user_id, card[1]))
            connect.commit()

    def delete_card(self, card_key):
        '''Removing a card from a user's collection.

        Parameters
        ----------
        card_key : str
            Unique card key.
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''DELETE FROM {self.db_table}
                        WHERE (user_id=?)
                        AND (card_key=?)''', (self.user_id, card_key))
        connect.commit()

