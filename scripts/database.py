import sqlite3


class Create:
    def users_db(self, db_name='users', db_table='user'):
        '''Создание базы данных пользователей
        
        :param db_name: Название базы данных
        :type db_name: str
        :param db_table: Название таблицы в базе данных
        :type db_table: str
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
        '''Создание базы данных коллекций
        
        :param db_name: Название базы данных
        :type db_name: str
        :param db_table: Название таблицы в базе данных
        :type db_table: str
        '''

        connect = sqlite3.connect(f'{db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''CREATE TABLE {db_table}
                        (user_id integer, key text,
                        date text, name text,
                        cards integer)''')
        connect.commit()

    def cards_db(self, db_name='collections', db_table='card'):
        '''Создание базы данных карт
        
        :param db_name: Название базы данных
        :type db_name: str
        :param db_table: Название таблицы в базе данных
        :type db_table: str
        '''

        connect = sqlite3.connect(f'{db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''CREATE TABLE {db_table}
                        (user_id integer, key text,
                        card_key integer, date text,
                        name text, description text,
                        score integer)''')
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
        '''Запись нового пользователя в базу данных

        :param menu_id: ID последнего Личного кабинета
            (default is 0)
        :type menu_id: int
        :param action: Активность пользователя
            (default is 0)
        :type action: int
        :param session: Текущая сессия пользователя (ключ коллекции/карты)
            (default is None)
        :type session: str
        :param username: Ник пользователя
            (default is None)
        :type username: str
        :param first_name: Имя пользователя
            (default is None)
        :type first_name: str
        :param last_name: Фамилия пользователя
            (default is None)
        :type last_name: str
        :param karma: Бонусные очки пользователя
            (default is 0)
        :type karma: int
        :param collections: Количество коллекций пользователя
            (default is 0)
        :type collections: int
        :param cards: Количество карт пользователя
            (default is 0)
        :type cards: int
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
        '''Запись новой коллекции пользователя в базу данных
        
        :param key: Уникальный ключ коллекции
        :type key: str
        :param date: Дата создания коллекции
            (default is None)
        :type date: str
        :param name: Имя коллекции
            (default is None)
        :type name: str
        :param cards: Количество карт в коллекции
            (default is 0)
        :type cards: int
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''INSERT INTO {self.db_table} 
                        VALUES (?,?,?,?,?)''', (self.user_id, key,
                                                date, name,
                                                cards))
        
        connect.commit()

    def create_card(self, key, card_key, date=None,
                    name=None, description=None, status=0):
        '''Запись новой карты пользователя в базу данных
        
        :param key: Уникальный ключ коллекции
        :type key: str
        :param card_key: Уникальный ключ карты
        :type card_key: str
        :param date: Дата создания карты
            (default is None)
        :type date: str
        :param name: Имя карты
            (default is None)
        :type name: str
        :param description: Описание карты
            (default is None)
        :type description: str
        :param status: Статус карты
            (default is 0)
        :type status: int
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''INSERT INTO {self.db_table} 
                        VALUES (?,?,?,?,?,?,?)''', (self.user_id, key,
                                                    card_key, date,
                                                    name, description,
                                                    status))
        
        connect.commit()

    def copy_collection(self, original_key, key):
        '''Копирование карт коллекции
        
        :param original_key: Оригинальный ключ коллекции
        :type original_key: str
        :param key: Новый ключ коллекции
        :type key: str
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
                cursor.execute(f'''INSERT INTO {self.db_table} 
                                VALUES (?,?,?,?,?,?,?)''', (self.user_id, key,
                                                            card[2], card[3],
                                                            card[4], card[5],
                                                            0))
            connect.commit()


class Fetch:
    def __init__(self, user_id, db_name='users', db_table='user'):
        self.user_id = user_id
        self.db_name = db_name
        self.db_table = db_table

    def user_attribute(self, attribute):
        '''Получение значения какой-либо переменной пользователя
        
        :param attribute: Имя переменной
        :type attribute: str
        :returns: Значение переменной
        :rtype: str/int
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
        '''Получение значения какой-либо переменной коллекции пользователя
        
        :param key: Уникальный ключ коллекции
        :type key: str
        :param attribute: Имя переменной
        :type attribute: str
        :returns: Значение переменной
        :rtype: str/int
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
        '''Получение значения какой-либо переменной карты пользователя
        
        :param card_key: Уникальный ключ карты
        :type card_key: str
        :param attribute: Имя переменной
        :type attribute: str
        :returns: Значение переменной
        :rtype: str/int
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
        '''Получение информации о всех коллекциях пользователя

        :returns: Информация о всех коллекциях
        :rtype: list
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
        '''Получение информации о всех картах определенной коллекции пользователя

        :param key: Уникальный ключ коллекции
        :type key: str
        :returns: Информация о всех картах
        :rtype: list
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
        '''Проверка на наличие схожих значений определенных переменных
        
        :param attribute: Имя переменной
        :type attribute: str
        :param value: Значение переменной
        :type value: int
        :returns: True/False
        :rtype: bool
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
        '''Проверка на наличие схожих значений определенных переменных карт
        
        :param key: Уникальный ключ коллекции, в которой находится карта
        :type key: str
        :param attribute: Имя переменной
        :type attribute: str
        :param value: Значение переменной
        :type value: int
        :returns: True/False
        :rtype: bool
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
        '''Проверка на существование коллекции и получение определенных
        переменных этой коллекции

        :param key: Уникальный ключ коллекции
        :type key: str
        :param attribute: Имя переменной
        :type attribute: str
        :returns: Значение переменной
        :rtype: str/int
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


class Update:
    def __init__(self, user_id, db_name='users', db_table='user'):
        self.user_id = user_id
        self.db_name = db_name
        self.db_table = db_table

    def user_attribute(self, attribute, value=0):
        '''Обновление значения переменной пользователя

        :param attribute: Имя переменной, которую надо изменить
        :type attribute: str
        :param value: Новое значение переменной
            (default is 0)
        :type value: int
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''UPDATE {self.db_table} SET {attribute}=?
                        WHERE user_id=?''', (value, self.user_id))
        connect.commit()

    def collection_attribute(self, key, attribute, value=0):
        '''Обновление значения переменной коллекции

        :param key: Уникальный ключ коллекции
        :type key: str
        :param attribute: Имя переменной, которую надо изменить
        :type attribute: str
        :param value: Новое значение переменной
            (default is 0)
        :type value: int
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''UPDATE {self.db_table} SET {attribute}=?
                        WHERE (user_id=?)
                        AND (key=?)''', (value, self.user_id, key))
        connect.commit()

    def card_attribute(self, card_key, attribute, value=0):
        '''Обновление значения переменной карты

        :param card_key: Уникальный ключ карты
        :type card_key: str
        :param attribute: Имя переменной, которую надо изменить
        :type attribute: str
        :param value: Новое значение переменной
            (default is 0)
        :type value: int
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''UPDATE {self.db_table} SET {attribute}=?
                        WHERE (user_id=?)
                        AND (card_key=?)''', (value, self.user_id, card_key))
        connect.commit()

    def change_user_attribute(self, attribute, value=0):
        '''Изменение переменной пользователя с учетом её предыдущего значения
        
        :param attribute: Имя переменной, которую надо изменить
        :type attribute: str
        :param value: Величина, на которую изменится значение переменной
            (default is 0)
        :type value: int
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''UPDATE {self.db_table}
                        SET {attribute} = {attribute} + {value}
                        WHERE user_id=?''', (self.user_id,))
        connect.commit()

    def change_collection_attribute(self, key, attribute, value=0):
        '''Изменение переменной коллекции с учетом её предыдущего значения
        
        :param card_key: Уникальный ключ коллекции
        :type card_key: str
        :param attribute: Имя переменной, которую надо изменить
        :type attribute: str
        :param value: Величина, на которую изменится значение переменной
            (default is 0)
        :type value: int
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''UPDATE {self.db_table}
                        SET {attribute} = {attribute} + {value}
                        WHERE (user_id=?) AND (key=?)''', (self.user_id, key))
        connect.commit()

    def change_card_attribute(self, card_key, attribute, value=0):
        '''Изменение переменной карты с учетом её предыдущего значения
        
        :param card_key: Уникальный ключ карты
        :type card_key: str
        :param attribute: Имя переменной, которую надо изменить
        :type attribute: str
        :param value: Величина, на которую изменится значение переменной
            (default is 0)
        :type value: int
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
        '''Удаление коллекции пользователя
        
        :param key: Уникальный ключ коллекции
        :type key: str
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''DELETE FROM {self.db_table}
                        WHERE (user_id=?) AND (key=?)''', (self.user_id, key))
        connect.commit()

    def delete_card(self, card_key):
        '''Удаление карты из коллекции пользователя
        
        :param card_key: Уникальный ключ карты
        :type card_key: str
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''DELETE FROM {self.db_table}
                        WHERE (user_id=?)
                        AND (card_key=?)''', (self.user_id, card_key))
        connect.commit()
