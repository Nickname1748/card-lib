import sqlite3


class Create():
    
    def create_users_db(self, db_name='users_n', table_name='table_m'):
        connect = sqlite3.connect(f'{db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'CREATE TABLE {table_name}' \
                        ' (user_id integer, active integer,' \
                        ' session text)')
        connect.commit()


    def create_collections_db(self, db_name='collections_n', table_name='table_m'):
        connect = sqlite3.connect(f'{db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'CREATE TABLE {table_name}' \
                        ' (user_id integer, key integer,' \
                        ' name text, cards_number integer,' \
                        ' creation_date text)')
        connect.commit()


class Insert():

    def __init__(self, user_id='123456789',
                db_name='name_n', table_name='table_m'):

        self.user_id = user_id
        self.db_name = db_name
        self.table_name = table_name


    def new_user(self):
        '''Insert a new user to the database.
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'SELECT user_id FROM {self.table_name}' \
                        ' WHERE user_id=?', (self.user_id,))
        fetch = cursor.fetchall()

        if not fetch:
            cursor.execute(f'INSERT INTO {self.table_name}' \
                            ' VALUES (?,?,?)', (self.user_id, 0, ''))
        connect.commit()


    def session_reservation(self, key='k-123456-0987-z'):
        '''Create a new collection.

        :param key: Unique collection identifier
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'INSERT INTO {self.table_name}' \
                        ' VALUES (?,?,?,?,?)',
                        (self.user_id, key, '', 0, ''))
        connect.commit()


    def session_insert(self, name='collection_a',
                        key='k-123456-0987-z', creation_date='DD/MM/YY'):
        '''Insert collection to the database.

        :param name: Collection Name
        :param key: Unique collection identifier
        :param creation_date: Collection creation date
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'UPDATE {self.table_name} SET name=?' \
                        ' WHERE (user_id=?) AND (key=?)',
                        (name, self.user_id, key))
        cursor.execute(f'UPDATE {self.table_name} SET creation_date=?' \
                        ' WHERE (user_id=?) AND (key=?)',
                        (creation_date, self.user_id, key))
        connect.commit()
    

    def user_activity(self, active=0, session='k-123456-0987-z'):
        '''Tracking user activity in the bot.

        :param active: User activity (0/1 - Inactive/Active)
        :param session: Active session
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'UPDATE {self.table_name} SET active=?' \
                        ' WHERE user_id=?', (active, self.user_id))
        cursor.execute(f'UPDATE {self.table_name} SET session=?' \
                        ' WHERE user_id=?', (session, self.user_id))
        connect.commit()


class Fetch():

    def __init__(self, user_id='123456789',
                db_name='name_n', table_name='table_m'):

        self.user_id = user_id
        self.db_name = db_name
        self.table_name = table_name


    def search_collections(self):
        '''Search collections in the database.

        :return: All collection information
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'SELECT * FROM {self.table_name}' \
                        ' WHERE user_id=?', (self.user_id,))
        fetch = cursor.fetchall()

        if fetch:
            connect.commit()
            return fetch
        else:
            connect.commit()
            return None


    def user_activity_status(self):
        '''Search for user information in the database.

        :return: All user status information
        '''

        connect = sqlite3.connect(f'{self.db_name}.db')
        cursor = connect.cursor()
        cursor.execute(f'SELECT * FROM {self.table_name}' \
                        ' WHERE user_id=?', (self.user_id,))
        fetch = cursor.fetchall()
        connect.commit()

        return fetch
