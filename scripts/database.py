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
                        last_name text, cards integer,
                        collections integer)''')
        connect.commit()
    
    def collections_db(self, db_name='collections', db_table='collection'):
        '''Создание базы данных коллекций'''

        connect = sqlite3.connect(f'{db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''CREATE TABLE {db_table}
                        (user_id integer, key text,
                        date text, name text,
                        cards integer)''')

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


class Fetch:
    def __init__(self, user_id, db_name='users', db_table='user'):
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

    def collection_attribute(self, attribute='', key=''):
        '''
        Получение какой-либо переменной коллекции пользователя
        из базы данных
        
        :param attribute:
        :param key: Уникальный ключ коллекции
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


class Update:
    def __init__(self, user_id, db_name='users', db_table='user'):
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

    def change_user_attribute(self, attribute='', value=0):
        '''Изменение переменной с учетом её предыдущего значения'''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'''UPDATE {self.db_table}
                        SET {attribute} = {attribute} + {value}
                        WHERE user_id=?''', (self.user_id,))
        connect.commit()

class Delete:
    def __init__(self, user_id, db_name='users', db_table='user'):
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


#create = Create()
#create.users_db()
#create.collections_db()
