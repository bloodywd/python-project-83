from datetime import datetime
import psycopg2
import os
from page_analyzer.parser import get_args


def get_connection():
    return psycopg2.connect(os.getenv('DATABASE_URL'))


def select_url(id):
    connection = get_connection()
    cur = connection.cursor()
    cur.execute("SELECT name, created_at from urls WHERE id = (%s)",
                (str(id), ))
    data = cur.fetchall()
    if data == []:
        return None
    (name, created_at) = data[0]
    cur.close()
    connection.close()
    return {
        'id': id,
        'name': name,
        'created_at': created_at
    }


def select_urls():
    connection = get_connection()
    cur = connection.cursor()
    cur.execute("SELECT urls.id, urls.name, urls.created_at, "
                "MAX(url_checks.created_at), url_checks.status_code "
                "from url_checks RIGHT JOIN urls on url_checks.url_id = "
                "urls.id GROUP BY urls.id, url_checks.status_code "
                "ORDER BY urls.id DESC")
    data = cur.fetchall()
    cur.close()
    connection.close()
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
    connection = get_connection()
    cur = connection.cursor()
    cur.execute("SELECT id from urls WHERE name = (%s)", (url, ))
    (id, ) = cur.fetchall()[0]
    cur.close()
    connection.close()
    return id


def insert_to_db(url):
    connection = get_connection()
    cur = connection.cursor()
    cur.execute("SELECT * from urls WHERE name = (%s)", (url,))
    data = cur.fetchall()
    if data:
        cur.close()
        connection.close()
        return 'Страница уже существует'
    else:
        current_datetime = datetime.now()
        timestamp = current_datetime.strftime('%Y-%m-%d')
        cur.execute("INSERT INTO urls (name, created_at) VALUES (%s, %s)",
                    (url, timestamp))
        connection.commit()
        cur.close()
        connection.close()
        return 'Страница успешно добавлена'


def insert_check_to_db(id, req):
    h1, title, description = get_args(req.text)
    connection = get_connection()
    cur = connection.cursor()
    current_datetime = datetime.now()
    timestamp = current_datetime.strftime('%Y-%m-%d')
    cur.execute('INSERT INTO url_checks (url_id, status_code, h1, title, '
                'description, created_at) VALUES (%s, %s, %s, %s, %s, %s)',
                (id, req.status_code, h1, title, description, timestamp))
    connection.commit()
    cur.close()
    connection.close()


def select_checks(id):
    connection = get_connection()
    cur = connection.cursor()
    cur.execute("SELECT * FROM url_checks WHERE url_id = (%s)", (id, ))
    data = cur.fetchall()
    cur.close()
    connection.close()
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
