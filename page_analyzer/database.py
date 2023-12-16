from datetime import datetime
import psycopg2
import os
from page_analyzer.parser import Parser


class DataBase():
    def __init__(self, client=psycopg2):
        self.connection = client.connect(os.getenv('DATABASE_URL'))
        self.cur = self.connection.cursor()

    def close(self):
        self.cur.close()
        self.connection.close()

    def select_url(self, id):
        try:
            self.cur.execute("SELECT name, created_at from urls "
                             "WHERE id = (%s)", (id,))
            data = self.cur.fetchall()
        except psycopg2.OperationalError:
            print('Ошибка чтения из БД')
        if not data:
            return None
        (name, created_at) = data[0]
        return {
            'id': id,
            'name': name,
            'created_at': created_at
        }

    def select_urls(self):
        try:
            self.cur.execute(
                "SELECT urls.id, urls.name, urls.created_at, MAX(url_checks."
                "created_at), url_checks.status_code from url_checks RIGHT "
                "JOIN urls on url_checks.url_id = urls.id GROUP BY urls.id, "
                "url_checks.status_code ORDER BY urls.id DESC"
            )
            data = self.cur.fetchall()
        except psycopg2.OperationalError:
            print('Ошибка чтения из БД')
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

    def get_url_id(self, url):
        try:
            self.cur.execute("SELECT id from urls WHERE name = (%s)", (url,))
            (id,) = self.cur.fetchall()[0]
        except psycopg2.OperationalError:
            print('Ошибка чтения из БД')
        return id

    def insert_to_db(self, url):
        try:
            self.cur.execute("SELECT * from urls WHERE name = (%s)", (url,))
            data = self.cur.fetchall()
        except psycopg2.OperationalError:
            print('Ошибка чтения из БД')
        if data:
            return 'Страница уже существует'
        else:
            current_datetime = datetime.now()
            timestamp = current_datetime.strftime('%Y-%m-%d')
            try:
                self.cur.execute("INSERT INTO urls (name, created_at) "
                                 "VALUES (%s, %s)", (url, timestamp))
                self.connection.commit()
            except psycopg2.OperationalError:
                print('Ошибка записи в БД')
            return 'Страница успешно добавлена'

    def insert_check_to_db(self, id, req):
        parser = Parser(req.text)
        h1 = parser.get_h1()
        title = parser.get_title()
        description = parser.get_description()
        current_datetime = datetime.now()
        timestamp = current_datetime.strftime('%Y-%m-%d')
        try:
            self.cur.execute(
                'INSERT INTO url_checks (url_id, status_code, h1, title, '
                'description, created_at) VALUES (%s, %s, %s, %s, %s, %s)',
                (id, req.status_code, h1, title, description, timestamp))
            self.connection.commit()
        except psycopg2.OperationalError:
            print('Ошибка записи в БД')

    def select_checks(self, id):
        try:
            self.cur.execute("SELECT * FROM url_checks "
                             "WHERE url_id = (%s)", (id,))
            data = self.cur.fetchall()
        except psycopg2.OperationalError:
            print('Ошибка чтения из БД')
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
