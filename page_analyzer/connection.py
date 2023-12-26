from os import getenv
from contextlib import contextmanager
from psycopg2.pool import SimpleConnectionPool
from psycopg2 import Error
from psycopg2.extras import DictCursor

connection_pool = None


@contextmanager
def get_connection():
    global connection_pool
    connection = None
    DATABASE_URL = getenv('DATABASE_URL')
    if not connection_pool:
        connection_pool = SimpleConnectionPool(
            1, 8, dsn=DATABASE_URL, cursor_factory=DictCursor
        )
    try:
        connection = connection_pool.getconn()
        cursor = connection.cursor()
        yield cursor
        connection.commit()
    except (Exception, Error) as e:
        connection.rollback()
        raise e
    finally:
        cursor.close()
        connection_pool.putconn(connection)
