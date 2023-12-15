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

    def close(self):
        self.cur.close()
        self.connection.close()

    def send_query(self, query):
        self.cur.execute(query)
        if not query.startswith('INSERT'):
            data = self.cur.fetchall()
            return data


class Database():
    def __init__(self, client):
        self.client = client

    def select(self, table, target='*', key=None, value=None):
        if key:
            query = f"SELECT {target} from {table} WHERE {key} = '{value}'"
        else:
            query = f"SELECT {target} from {table}"
        data = self.client.send_query(query)
        return data

    def insert(self, table, target, values):
        query = f"INSERT INTO {table} {target} VALUES {values}"
        self.client.send_query(query)
        self.client.commit()

    def connect(self):
        self.client.connect()

    def close(self):
        self.client.close()


def select_url(id):
    client = Client()
    db = Database(client)
    db.connect()
    (name, created_at) = db.select(
        table='urls', target='name, created_at', key='id', value=id
    )[0]
    db.close()
    return {
        'id': id,
        'name': name,
        'created_at': created_at
    }


def select_urls():
    client = Client()
    db = Database(client)
    db.connect()
    (data) = db.select(table='urls')
    db.close()
    return (
        {
            'id': url[0],
            'name': url[1],
            'created_at': url[2]
        }
        for url in data[::-1]
    )


def get_url_id(url):
    client = Client()
    db = Database(client)
    db.connect()
    (id,) = db.select(table='urls', target='id', key='name', value=url)[0]
    db.close()
    return id


def insert_to_db(url):
    client = Client()
    db = Database(client)
    db.connect()
    if db.select(table='urls', key='name', value=url):
        db.close()
        return False
    else:
        current_datetime = datetime.now()
        timestamp = current_datetime.strftime('%Y-%m-%d')
        db.insert(
            table='urls', target='(name, created_at)', values=(url, timestamp)
        )
        db.close()
        return True
