from datetime import datetime
import psycopg2
import os

from bs4 import BeautifulSoup

from page_analyzer.parser import Parser


DATABASE_URL = os.getenv('DATABASE_URL')


class DBInterface():
    def __init__(self, client=psycopg2, url=DATABASE_URL):
        self.client = client
        self.url = url

    def connect(self):
        self.connection = self.client.connect(self.url)
        self.cur = self.connection.cursor()

    def disconnect(self):
        self.cur.close()
        self.connection.close()

    def select(self, query):
        self.cur.execute(query)
        data = self.cur.fetchall()
        return data

    def insert(self, query):
        self.cur.execute(query)
        self.connection.commit()


def select_url(id):
    client = DBInterface()
    client.connect()
    query = f"SELECT name, created_at from urls WHERE id = '{id}'"
    (name, created_at) = client.select(query)[0]
    client.disconnect()
    return {
        'id': id,
        'name': name,
        'created_at': created_at
    }


def select_urls():
    client = DBInterface()
    client.connect()
    query = ("SELECT urls.id, urls.name, urls.created_at, "
             "MAX(url_checks.created_at), url_checks.status_code "
             "from url_checks RIGHT JOIN urls on url_checks.url_id "
             "= urls.id GROUP BY urls.id, url_checks.status_code "
             "ORDER BY urls.id DESC")
    data = client.select(query)
    client.disconnect()
    return [
        {
            'id': url[0],
            'name': url[1],
            'created_at': url[2],
            'last_check': url[3],
            'status_code': url[4]
        }
        for url in data
    ]


def get_url_id(url):
    client = DBInterface()
    client.connect()
    query = f"SELECT id from urls WHERE name = '{url}'"
    (id,) = client.select(query)[0]
    client.disconnect()
    return id


def insert_to_db(url):
    client = DBInterface()
    client.connect()
    query = f"SELECT * from urls WHERE name = '{url}'"
    if client.select(query):
        client.disconnect()
        return 'Страница уже существует'
    else:
        current_datetime = datetime.now()
        timestamp = current_datetime.strftime('%Y-%m-%d')
        query = (f"INSERT INTO urls (name, created_at) "
                 f"VALUES ('{url}', '{timestamp}')")
        client.insert(query)
        client.disconnect()
        return 'Успешно добавлено'


def insert_check_to_db(id, req):
    parser = Parser(req.text)
    h1, title, description = parser.get_args()
    client = DBInterface()
    client.connect()
    current_datetime = datetime.now()
    timestamp = current_datetime.strftime('%Y-%m-%d')
    query = (f"INSERT INTO url_checks "
             f"(url_id, status_code, h1, title, description, created_at) "
             f"VALUES ('{id}', '{req.status_code}', '{h1}', "
             f"'{title}', '{description}', '{timestamp}')")
    client.insert(query)
    client.disconnect()


def select_checks(id):
    client = DBInterface()
    client.connect()
    query = (f"SELECT * FROM url_checks "
             f"WHERE url_id = '{id}'")
    data = client.select(query)
    client.disconnect()
    return [
        {
            'id': check[0],
            'url_id': check[1],
            'status_code': check[2],
            'h1': check[3],
            'title': check[4],
            'description': check[5],
            'created_at': check[6],
        }
        for check in data[::-1]
    ]
