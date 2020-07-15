import sqlite3


class Create:
    def users_db(self, db_name='users', db_table='user'):
        '''Создание базы данных пользователей'''

        connect = sqlite3.connect(f'{db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''CREATE TABLE {db_table}
                        (user_id integer, menu_id integer,
                        action integer, session text,
                        username text, first_name text,
                        last_name text, collections integer,
                        cards integer)''')
        connect.commit()
    
    def collections_db(self, db_name='collections', db_table='collection'):
        '''Создание базы данных коллекций'''

        connect = sqlite3.connect(f'{db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''CREATE TABLE {db_table}
                        (user_id integer, key text,
                        date text, name text,
                        cards integer)''')
        connect.commit()

    def cards_db(self, db_name='collections', db_table='card'):
        '''Создание базы данных карт'''

        connect = sqlite3.connect(f'{db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''CREATE TABLE {db_table}
                        (user_id integer, key text,
                        card_key integer, date text,
                        name text, description text,
                        score integer)''')
        connect.commit()


class Insert:
    def __init__(self, user_id=None, db_name='users', db_table='user'):
        self.user_id = user_id
        self.db_name = db_name
        self.db_table = db_table

    def new_user(self, menu_id=0, action=0,
                session=None, username=None, first_name=None,
                last_name=None, cards=0, collections=0):
        '''Запись нового пользователя в базу данных'''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''SELECT user_id FROM {self.db_table} 
                        WHERE user_id=?''', (self.user_id,))
        fetch = cursor.fetchall()

        if not fetch:
            cursor.execute(f'''INSERT INTO {self.db_table} 
                        VALUES (?,?,?,?,?,?,?,?,?)''', (self.user_id, menu_id,
                                                    action, session,
                                                    username, first_name,
                                                    last_name, cards,
                                                    collections))
        
        connect.commit()
    
    def create_collection(self, key='', date=None,
                        name=None, cards=0):
        '''Запись новой коллекции пользователя в базу данных'''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''INSERT INTO {self.db_table} 
                        VALUES (?,?,?,?,?)''', (self.user_id, key,
                                                date, name,
                                                cards))
        
        connect.commit()

    def create_card(self, key='', card_key='', date=None,
                    name=None, description=None, status=0):
        '''Запись новой карты пользователя в базу данных'''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''INSERT INTO {self.db_table} 
                        VALUES (?,?,?,?,?,?,?)''', (self.user_id, key,
                                                card_key, date,
                                                name, description,
                                                status))
        
        connect.commit()


class Fetch:
    def __init__(self, user_id=None, db_name='users', db_table='user'):
        self.user_id = user_id
        self.db_name = db_name
        self.db_table = db_table

    def user_attribute(self, attribute=''):
        '''
        Получение какой-либо переменной пользователя из базы данных
        
        :param attribute:
        :return: Значение переменной
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

    def collection_attribute(self, key='', attribute=''):
        '''
        Получение какой-либо переменной коллекции пользователя
        из базы данных
        
        :param key: Уникальный ключ коллекции
        :param attribute:
        :return: Значение переменной
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

    def card_attribute(self, card_key='', attribute=''):
        '''
        Получение какой-либо переменной карты пользователя
        из базы данных
        
        :param card_key: Уникальный ключ карты
        :param attribute:
        :return: Значение переменной
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''SELECT {attribute} FROM {self.db_table} 
            WHERE (user_id=?) AND (card_key=?)''', (self.user_id, card_key))
        fetch = cursor.fetchall()
        connect.commit()

        if fetch:
            return fetch[0][0]
        else:
            return None

    def user_collections(self):
        '''
        Получение всех коллекций пользователя

        :return:
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

    def user_cards(self, key=''):
        '''
        Получение всех карт из определенной коллекции пользователя

        :return:
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

    def copy_check(self, attribute='', value=0):
        '''
        Проверка на наличие схожих значений определенных переменных
        в базе данных
        
        :return: True/False
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

    def card_copy_check(self, key='', attribute='', value=0):
        '''
        Проверка на наличие схожих значений определенных переменных
        карт в базе данных
        
        :return: True/False
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


class Update:
    def __init__(self, user_id=None, db_name='users', db_table='user'):
        self.user_id = user_id
        self.db_name = db_name
        self.db_table = db_table

    def user_attribute(self, attribute='', value=0):
        '''
        Обновление значения какой-либо переменной пользователя
        в базе данных
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''UPDATE {self.db_table} SET {attribute}=?
                        WHERE user_id=?''', (value, self.user_id))
        connect.commit()

    def collection_attribute(self, key='',
                            attribute='', value=0):
        '''
        Обновление значения какой-либо переменной коллекции
        в базе данных
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''UPDATE {self.db_table} SET {attribute}=?
                        WHERE (user_id=?) AND (key=?)''', (value, 
                                                        self.user_id,
                                                        key))
        connect.commit()

    def card_attribute(self, card_key='',
                    attribute='', value=0):
        '''
        Обновление значения какой-либо переменной карты
        в базе данных
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''UPDATE {self.db_table} SET {attribute}=?
                        WHERE (user_id=?) AND (card_key=?)''', (value,
                                                        self.user_id,
                                                        card_key))
        connect.commit()

    def change_user_attribute(self, attribute='', value=0):
        '''Изменение переменной с учетом её предыдущего значения'''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''UPDATE {self.db_table}
                        SET {attribute} = {attribute} + {value}
                        WHERE user_id=?''', (self.user_id,))
        connect.commit()

    def change_collection_attribute(self, key='', attribute='', value=0):
        '''Изменение переменной коллекции с учетом её предыдущего значения'''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''UPDATE {self.db_table}
                        SET {attribute} = {attribute} + {value}
                        WHERE (user_id=?) AND (key=?)''', (self.user_id, key))
        connect.commit()

    def change_card_attribute(self, card_key='', attribute='', value=0):
        '''Изменение переменной карты с учетом её предыдущего значения'''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''UPDATE {self.db_table}
                        SET {attribute} = {attribute} + {value}
                        WHERE (user_id=?)
                        AND (card_key=?)''', (self.user_id, card_key))
        connect.commit()


class Delete:
    def __init__(self, user_id=None, db_name='users', db_table='user'):
        self.user_id = user_id
        self.db_name = db_name
        self.db_table = db_table

    def delete_collection(self, key=''):
        '''
        Удаление коллекции пользователя
        
        :param key: Уникальный ключ коллекции
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''DELETE FROM {self.db_table}
                        WHERE (user_id=?) AND (key=?)''', (self.user_id, key))
        connect.commit()

    def delete_card(self, card_key=''):
        '''
        Удаление коллекции пользователя
        
        :param card_key: Уникальный ключ карты
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''DELETE FROM {self.db_table}
            WHERE (user_id=?) AND (card_key=?)''', (self.user_id, card_key))
        connect.commit()

#create = Create()
#create.users_db()
#create.collections_db()
#create.cards_db()
