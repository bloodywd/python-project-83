from os import getenv
from contextlib import contextmanager
from psycopg2.pool import SimpleConnectionPool
from psycopg2 import Error


connection_pool = None


@contextmanager
def get_connection():
    global connection_pool
    connection = None
    DATABASE_URL = getenv('DATABASE_URL')
    if not connection_pool:
        connection_pool = SimpleConnectionPool(1, 8, dsn=DATABASE_URL)
    try:
        connection = connection_pool.getconn()
        yield connection
        connection.commit()
    except (Exception, Error) as e:
        connection.rollback()
        raise e
    finally:
        connection_pool.putconn(connection)