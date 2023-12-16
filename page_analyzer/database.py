from datetime import datetime
import psycopg2
import os
from page_analyzer.parser import Parser


class DataBase():
    def close(self):
        self.cur.close()
        self.connection.close()

    def select(self, query, args=None):
        try:
            self.cur.execute(query, args)
            data = self.cur.fetchall()
        except psycopg2.OperationalError:
            print('Ошибка чтения из БД')
            self.connection.rollback()
        else:
            return data

    def insert(self, query, args=None):
        try:
            self.cur.execute(query, args)
            self.connection.commit()
        except psycopg2.OperationalError:
            print('Ошибка записи в БД')
            self.connection.rollback()


class PageAnalyzerDataBase(DataBase):
    def __init__(self, client=psycopg2):
        self.connection = client.connect(os.getenv('DATABASE_URL'))
        self.cur = self.connection.cursor()

    def select_url(self, id):
        query = "SELECT name, created_at from urls WHERE id = (%s)"
        args = (id,)
        data = self.select(query, args)
        if not data:
            return None
        (name, created_at) = data[0]
        return {
            'id': id,
            'name': name,
            'created_at': created_at
        }

    def select_urls(self):
        query = "SELECT urls.id, urls.name, urls.created_at, " \
                "MAX(url_checks.created_at), url_checks.status_code " \
                "from url_checks RIGHT JOIN urls on url_checks.url_id = " \
                "urls.id GROUP BY urls.id, url_checks.status_code " \
                "ORDER BY urls.id DESC"
        data = self.select(query)
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

    def select_url_id(self, url):
        query = "SELECT id from urls WHERE name = (%s)"
        args = (url,)
        data = self.select(query, args)
        (id,) = data[0]
        return id

    def insert_to_db(self, url):
        query = "SELECT * from urls WHERE name = (%s)"
        args = (url,)
        data = self.select(query, args)
        if data:
            return 'Страница уже существует'
        else:
            current_datetime = datetime.now()
            timestamp = current_datetime.strftime('%Y-%m-%d')
            query = "INSERT INTO urls (name, created_at) VALUES (%s, %s)"
            args = (url, timestamp)
            self.insert(query, args)
            return 'Страница успешно добавлена'

    def insert_check_to_db(self, id, req):
        parser = Parser(req.text)
        h1 = parser.get_h1()
        title = parser.get_title()
        description = parser.get_description()
        current_datetime = datetime.now()
        timestamp = current_datetime.strftime('%Y-%m-%d')
        query = "INSERT INTO url_checks (url_id, status_code, h1, title, " \
                "description, created_at) VALUES (%s, %s, %s, %s, %s, %s)"
        args = (id, req.status_code, h1, title, description, timestamp)
        self.insert(query, args)

    def select_checks(self, id):
        query = "SELECT * FROM url_checks WHERE url_id = (%s)"
        args = (id,)
        data = self.select(query, args)
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
