import sqlite3


class Create:
    def users_db(self, db_name='users', db_table='user'):
        '''Создание базы данных пользователей.
        
        Parameters
        ----------
        db_name : str
            Название базы данных (default is 'users').
        db_table : str
            Название таблицы базы данных (default is 'user').
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
        '''Создание базы данных коллекций.
        
        Parameters
        ----------
        db_name : str
            Название базы данных (default is 'collections').
        db_table : str
            Название таблицы базы данных (default is 'collection').
        '''

        connect = sqlite3.connect(f'{db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''CREATE TABLE {db_table}
                        (user_id integer, key text,
                        date text, name text,
                        cards integer)''')
        connect.commit()

    def cards_db(self, db_name='collections', db_table='card'):
        '''Создание базы данных карт.

        Parameters
        ----------
        db_name : str
            Название базы данных (default is 'collections').
        db_table : str
            Название таблицы базы данных (default is 'card').
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
        '''Запись нового пользователя в базу данных.

        Parameters
        ----------
        menu_id : int
            ID последнего Личного кабинета пользователя (default is 0).
        action : int
            Активность пользователя (default is 0).
        session : str
            Текущая сессия пользователя: ключ коллекции
            или ключ карты (default is None).
        username : str
            Ник пользователя (default is None).
        first_name : str
            Имя пользователя (default is None).
        last_name : str
            Фамилия пользователя (default is None).
        karma : int
            Бонусные очки пользователя (default is 0).
        collections : int
            Количество коллекций пользователя (default is 0).
        cards : int
            Количество карт пользователя (default is 0).
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
        '''Запись новой коллекции пользователя в базу данных.
        
        Parameters
        ----------
        key : str
            Уникальный ключ коллекции.
        date : str
            Дата создания коллекции (default is None).
        name : str
            Имя коллекции (default is None).
        cards : int
            Количество карт в коллекции (default is 0).
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
        '''Запись новой карты пользователя в базу данных.
        
        Parameters
        ----------
        key : str
            Уникальный ключ коллекции.
        card_key : str
            Уникальный ключ карты.
        date : str
            Дата создания карты (default is None).
        name : str
            Имя карты (default is None).
        description : str
            Описание карты (default is None).
        status : int
            Статус карты (default is 0).
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
        '''Копирование карт коллекции.

        Parameters
        ----------
        original_key : str
            Оригинальный ключ коллекции.
        key : str
            Новый ключ коллекции.
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
        '''Получение значения какой-либо переменной пользователя.

        Parameters
        ----------
        attribute : str
            Имя переменной.
        
        Returns
        -------
        fetch : str or int or None
            Возвращает значение переменной. Возвращает None в том случае,
            если переменная отсутствует в базе данных.
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
        '''Получение значения какой-либо переменной коллекции пользователя.

        Parameters
        ----------
        key : str
            Уникальный ключ коллекции.
        attribute : str
            Имя переменной.

        Returns
        -------
        fetch : str or int or None
            Возвращает значение переменной. Возвращает None в том случае,
            если переменная отсутствует в базе данных.
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
        '''Получение значения какой-либо переменной карты пользователя.

        Parameters
        ----------
        card_key : str
            Уникальный ключ карты.
        attribute : str
            Имя переменной.

        Returns
        -------
        fetch : str or int or None
            Возвращает значение переменной. Возвращает None в том случае,
            если переменная отсутствует в базе данных.
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
        '''Получение информации о всех коллекциях пользователя.

        Returns
        -------
        fetch : list
            Информация о всех коллекциях.
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
        '''Получение информации о всех картах определенной коллекции пользователя.

        Parameters
        ----------
        key : str
            Уникальный ключ коллекции.
        
        Returns
        -------
        fetch : list
            Информация о всех картах.
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
        '''Проверка на наличие схожих значений определенных переменных.
        
        Parameters
        ----------
        attribute : str
            Имя переменной.
        value : int
            Значение переменной.

        Returns
        -------
        bool
            True, если совпадения найдены, False — если нет.
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
        '''Проверка на наличие схожих значений определенных переменных карт.

        Parameters
        ----------
        key : str
            Уникальный ключ коллекции, в которой находится карта.
        attribute : str
            Имя переменной.
        value : int
            Значение переменной.

        Returns
        -------
        bool
            True, если совпадения найдены, False — если нет.
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
        переменных этой коллекции.

        Parameters
        ----------
        key : str
            Уникальный ключ коллекции.
        attribute : str
            Имя переменной.
        
        Returns
        -------
        fetch: str or int or None
            Возвращает значение переменной. Возвращает None в том случае,
            если переменная отсутствует в базе данных.
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
        '''Обновление значения переменной пользователя.

        Parameters
        ----------
        attribute : str
            Имя переменной, которую надо изменить.
        value : int
            Новое значение переменной (default is 0).
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''UPDATE {self.db_table} SET {attribute}=?
                        WHERE user_id=?''', (value, self.user_id))
        connect.commit()

    def collection_attribute(self, key, attribute, value=0):
        '''Обновление значения переменной коллекции.

        Parameters
        ----------
        key : str
            Уникальный ключ коллекции.
        attribute : str
            Имя переменной, которую надо изменить.
        value : int
            Новое значение переменной (default is 0).
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''UPDATE {self.db_table} SET {attribute}=?
                        WHERE (user_id=?)
                        AND (key=?)''', (value, self.user_id, key))
        connect.commit()

    def card_attribute(self, card_key, attribute, value=0):
        '''Обновление значения переменной карты.

        Parameters
        ----------
        card_key : str
            Уникальный ключ карты.
        attribute : str
            Имя переменной, которую надо изменить.
        value : int
            Новое значение переменной (default is 0).
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''UPDATE {self.db_table} SET {attribute}=?
                        WHERE (user_id=?)
                        AND (card_key=?)''', (value, self.user_id, card_key))
        connect.commit()

    def change_user_attribute(self, attribute, value=0):
        '''Изменение переменной пользователя с учетом её предыдущего значения.
        
        Parameters
        ----------
        attribute : str
            Имя переменной, которую надо изменить.
        value : int
            Величина, на которую изменится значение переменной (default is 0).
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''UPDATE {self.db_table}
                        SET {attribute} = {attribute} + {value}
                        WHERE user_id=?''', (self.user_id,))
        connect.commit()

    def change_collection_attribute(self, key, attribute, value=0):
        '''Изменение переменной коллекции с учетом её предыдущего значения.
        
        Parameters
        ----------
        card_key : str
            Уникальный ключ коллекции.
        attribute : str
            Имя переменной, которую надо изменить.
        value : int
            Величина, на которую изменится значение переменной (default is 0).
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''UPDATE {self.db_table}
                        SET {attribute} = {attribute} + {value}
                        WHERE (user_id=?) AND (key=?)''', (self.user_id, key))
        connect.commit()

    def change_card_attribute(self, card_key, attribute, value=0):
        '''Изменение переменной карты с учетом её предыдущего значения.

        Parameters
        ----------
        card_key : str
            Уникальный ключ карты.
        attribute : str
            Имя переменной, которую надо изменить.
        value : int
            Величина, на которую изменится значение переменной (default is 0).
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
        '''Удаление коллекции пользователя.

        Parameters
        ----------
        key : str
            Уникальный ключ коллекции.
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''DELETE FROM {self.db_table}
                        WHERE (user_id=?) AND (key=?)''', (self.user_id, key))
        connect.commit()

    def delete_card(self, card_key):
        '''Удаление карты из коллекции пользователя.

        Parameters
        ----------
        card_key : str
            Уникальный ключ карты.
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''DELETE FROM {self.db_table}
                        WHERE (user_id=?)
                        AND (card_key=?)''', (self.user_id, card_key))
        connect.commit()
