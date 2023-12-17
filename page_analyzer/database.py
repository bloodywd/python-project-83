from datetime import datetime
from page_analyzer.parser import Parser


def get_url(conn, id):
    with conn.cursor() as cur:
        query = "SELECT name, created_at from urls WHERE id = (%s)"
        args = (id,)
        cur.execute(query, args)
        data = cur.fetchone()
    if not data:
        return None
    name, created_at = data
    return {
        'id': id,
        'name': name,
        'created_at': created_at
    }


def get_urls(conn):
    data = []
    query = "SELECT urls.id, urls.name, urls.created_at, " \
            "MAX(url_checks.created_at), url_checks.status_code " \
            "from url_checks RIGHT JOIN urls on url_checks.url_id = " \
            "urls.id GROUP BY urls.id, url_checks.status_code " \
            "ORDER BY urls.id DESC"
    with conn.cursor() as cur:
        cur.execute(query)
        while True:
            row = cur.fetchone()
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


def get_url_id(conn, url):
    query = "SELECT id from urls WHERE name = (%s)"
    args = (url,)
    with conn.cursor() as cur:
        cur.execute(query, args)
        data = cur.fetchone()
    (id,) = data
    return id


def insert_url_to_db(conn, url):
    query = "SELECT * from urls WHERE name = (%s)"
    args = (url,)
    with conn.cursor() as cur:
        cur.execute(query, args)
        data = cur.fetchone()
    if data:
        return 'Страница уже существует'
    else:
        current_datetime = datetime.now()
        timestamp = current_datetime.strftime('%Y-%m-%d')
        query = "INSERT INTO urls (name, created_at) VALUES (%s, %s)"
        args = (url, timestamp)
        with conn.cursor() as cur:
            cur.execute(query, args)
        return 'Страница успешно добавлена'


def insert_check_to_db(conn, id, req):
    parser = Parser(req.text)
    h1 = parser.get_h1()
    title = parser.get_title()
    description = parser.get_description()
    current_datetime = datetime.now()
    timestamp = current_datetime.strftime('%Y-%m-%d')
    query = "INSERT INTO url_checks (url_id, status_code, h1, title, " \
            "description, created_at) VALUES (%s, %s, %s, %s, %s, %s)"
    args = (id, req.status_code, h1, title, description, timestamp)
    with conn.cursor() as cur:
        cur.execute(query, args)


def get_checks(conn, id):
    data = []
    query = "SELECT * FROM url_checks WHERE url_id = (%s) ORDER BY id DESC"
    args = (id,)
    with conn.cursor() as cur:
        cur.execute(query, args)
        while True:
            row = cur.fetchone()
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
