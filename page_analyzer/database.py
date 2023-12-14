from datetime import datetime
import psycopg2
import os

DATABASE_URL = os.getenv('DATABASE_URL')


class Connection():
    def __init__(self, client=psycopg2, url=DATABASE_URL):
        self._client = client
        self._url = url

    def connect(self):
        self.connection = self._client.connect(self._url)
        self.cur = self.connection.cursor()

    def commit(self):
        self.connection.commit()

    def close(self):
        self.cur.close()
        self.connection.close()

    def send_query(self, query):
        self.cur.execute(query)
        if not query.startswith('INSERT'):
            data = self.cur.fetchall()
            return data


class Database():
    def __init__(self, connection):
        self.connection = connection

    def select(self, table, target='*', key=None, value=None):
        self.connection.connect()
        if key:
            query = f"SELECT {target} from {table} WHERE {key} = '{value}'"
        else:
            query = f"SELECT {target} from {table}"
        data = self.connection.send_query(query)
        self.connection.close()
        return data

    def insert(self, table, target, values):
        self.connection.connect()
        query = f"INSERT INTO {table} {target} VALUES {values}"
        self.connection.send_query(query)
        self.connection.commit()
        self.connection.close()


def select_url(id):
    connect = Connection()
    db = Database(connect)
    (name, created_at) = db.select('urls', 'name, created_at', 'id', id)[0]
    return {
        'id': id,
        'name': name,
        'created_at': created_at
    }


def select_urls():
    connect = Connection()
    db = Database(connect)
    (data) = db.select('urls')
    return ({'id': url[0], 'name': url[1], 'created_at': url[2]}
            for url in data[::-1]
    )


def get_url_id(url):
    connect = Connection()
    db = Database(connect)
    (id,) = db.select('urls', 'id', 'name', url)[0]
    return id


def insert_to_db(url):
    connect = Connection()
    db = Database(connect)
    if db.select('urls', 'name', 'name', url):
        return False
    else:
        current_datetime = datetime.now()
        timestamp = current_datetime.strftime('%Y-%m-%d')
        db.insert('urls', '(name, created_at)', (url, timestamp))
        return True
