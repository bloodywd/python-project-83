from datetime import datetime
import psycopg2
import os

DATABASE_URL = os.getenv('DATABASE_URL')


class Client():
    def __init__(self, client=psycopg2, url=DATABASE_URL):
        self.client = client
        self.url = url

    def connect(self):
        self.connection = self.client.connect(self.url)
        self.cur = self.connection.cursor()

    def commit(self):
        self.connection.commit()

    def disconnect(self):
        self.cur.close()
        self.connection.close()

    def send_query(self, query):
        self.cur.execute(query)
        if not query.startswith('INSERT'):
            data = self.cur.fetchall()
            return data


class DBInterface():
    def __init__(self, client):
        self.client = client

    def select(self, query):
        data = self.client.send_query(query)
        return data

    def insert(self, query):
        self.client.send_query(query)
        self.client.commit()

    def connect(self):
        self.client.connect()

    def disconnect(self):
        self.client.disconnect()


def select_url(id):
    client = Client()
    db = DBInterface(client)
    db.connect()
    query = f"SELECT name, created_at from urls WHERE id = '{id}'"
    (name, created_at) = db.select(query)[0]
    db.disconnect()
    return {
        'id': id,
        'name': name,
        'created_at': created_at
    }


def select_urls():
    client = Client()
    db = DBInterface(client)
    db.connect()
    query = ("SELECT urls.id, urls.name, urls.created_at, "
             "MAX(url_checks.created_at) from url_checks RIGHT JOIN "
             "urls on url_checks.url_id = urls.id GROUP BY urls.id")
    data = db.select(query)
    db.disconnect()
    return [
        {
            'id': url[0],
            'name': url[1],
            'created_at': url[2],
            'last_check': url[3] if url[3] else ''
        }
        for url in data
    ]


def get_url_id(url):
    client = Client()
    db = DBInterface(client)
    db.connect()
    query = f"SELECT id from urls WHERE name = '{url}'"
    (id,) = db.select(query)[0]
    db.disconnect()
    return id


def insert_to_db(url):
    client = Client()
    db = DBInterface(client)
    db.connect()
    query = f"SELECT * from urls WHERE name = '{url}'"
    if db.select(query):
        db.disconnect()
        return 'Страница уже существует'
    else:
        current_datetime = datetime.now()
        timestamp = current_datetime.strftime('%Y-%m-%d')
        query = (f"INSERT INTO urls (name, created_at) "
                 f"VALUES ('{url}', '{timestamp}')")
        db.insert(query)
        db.disconnect()
        return 'Успешно добавлено'


def insert_check_to_db(id):
    client = Client()
    db = DBInterface(client)
    db.connect()
    current_datetime = datetime.now()
    timestamp = current_datetime.strftime('%Y-%m-%d')
    query = (f"INSERT INTO url_checks (url_id, created_at) "
             f"VALUES ('{id}', '{timestamp}')")
    db.insert(query)
    db.disconnect()


def select_checks(id):
    client = Client()
    db = DBInterface(client)
    db.connect()
    query = (f"SELECT id, url_id, created_at FROM url_checks "
             f"WHERE url_id = '{id}'")
    data = db.select(query)
    db.disconnect()
    return [
        {
            'id': check[0],
            'url_id': check[1],
            'created_at': check[2]
        }
        for check in data[::-1]
    ]
