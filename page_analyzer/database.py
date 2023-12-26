from datetime import datetime
from psycopg2.errorcodes import UNIQUE_VIOLATION
from psycopg2 import errors


class UniqueURL(Exception):
    pass


def get_url_by_id(cursor, id):
    query = "SELECT * from urls WHERE id = (%s)"
    args = (id,)
    cursor.execute(query, args)
    data = cursor.fetchone()
    return data


def get_urls(cursor):
    query = "SELECT * from urls"
    cursor.execute(query)
    data = cursor.fetchall()
    return data


def get_last_checks(cursor):
    query = ("SELECT DISTINCT ON (url_id) * from url_checks "
             "ORDER BY url_id, created_at DESC")
    cursor.execute(query)
    data = cursor.fetchall()
    return data


def get_url_by_name(cursor, url):
    query = "SELECT id from urls WHERE name = (%s)"
    args = (url,)
    cursor.execute(query, args)
    data = cursor.fetchone()
    if data:
        return data


def insert_url_to_db(cursor, url):
    current_datetime = datetime.now()
    timestamp = current_datetime.strftime('%Y-%m-%d')
    query = "INSERT INTO urls (name, created_at) VALUES (%s, %s) RETURNING *"
    args = (url, timestamp)
    try:
        cursor.execute(query, args)
        data = cursor.fetchone()
        return data
    except errors.lookup(UNIQUE_VIOLATION):
        raise UniqueURL('URL already exists')


def insert_check_to_db(cursor, *args):
    current_datetime = datetime.now()
    timestamp = current_datetime.strftime('%Y-%m-%d')
    query = "INSERT INTO url_checks (url_id, status_code, h1, title, " \
            "description, created_at) VALUES (%s, %s, %s, %s, %s, %s)"
    cursor.execute(query, (*args, timestamp))


def get_checks(cursor, id):
    query = "SELECT * FROM url_checks WHERE url_id = (%s) ORDER BY id DESC"
    args = (id,)
    cursor.execute(query, args)
    data = cursor.fetchall()
    return data
