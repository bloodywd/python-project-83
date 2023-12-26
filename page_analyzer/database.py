from datetime import datetime
from psycopg2.errorcodes import UNIQUE_VIOLATION
from psycopg2 import errors


class UniqueURL(Exception):
    pass


def get_url_by_id(cursor, id):
    query = "SELECT name, created_at from urls WHERE id = (%s)"
    args = (id,)
    cursor.execute(query, args)
    data = cursor.fetchone()
    if not data:
        return None
    name, created_at = data
    return {
        'id': id,
        'name': name,
        'created_at': created_at
    }


def get_urls(connection):
    data = []
    query = "SELECT urls.id, urls.name, urls.created_at, " \
            "MAX(url_checks.created_at), url_checks.status_code " \
            "from url_checks RIGHT JOIN urls on url_checks.url_id = " \
            "urls.id GROUP BY urls.id, url_checks.status_code " \
            "ORDER BY urls.id DESC"
    connection.execute(query)
    while True:
        row = connection.fetchone()
        if not row:
            break
        data.append({
            'id': row[0],
            'name': row[1],
            'created_at': row[2],
            'last_check': row[3],
            'status_code': row[4]
        })
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
    data = []
    query = "SELECT * FROM url_checks WHERE url_id = (%s) ORDER BY id DESC"
    args = (id,)
    cursor.execute(query, args)
    while True:
        row = cursor.fetchone()
        if not row:
            break
        data.append({
            'id': row[0],
            'url_id': row[1],
            'status_code': row[2],
            'h1': row[3],
            'title': row[4],
            'description': row[5],
            'created_at': row[6],
        })
    return data
