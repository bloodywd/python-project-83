from flask import (
    Flask,
    render_template,
    request,
    url_for,
    redirect,
    flash,
    get_flashed_messages,
    abort
)
from page_analyzer.database import (
    get_checks,
    get_url_id,
    get_urls,
    get_url,
    insert_check_to_db,
    insert_url_to_db,
)
from page_analyzer.validate import Validator
from dotenv import load_dotenv
import requests
from contextlib import contextmanager
from psycopg2.pool import SimpleConnectionPool
import os


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
connection_pool = None

# @contextmanager возвращает объект с двумя магическими методами:
# __enter__() и __exit__(). Все, что до yield, относится к enter,
# остальное к exit. with() ищет метод enter и запускает его
# после выхода из with запускается exit
# global нужен для доступа и изменения переменной внутри scope функции


@contextmanager
def get_connection():
    global connection_pool
    connection = None
    DATABASE_URL = os.getenv('DATABASE_URL')
    connection_pool = SimpleConnectionPool(1, 8, dsn=DATABASE_URL)
    try:
        connection = connection_pool.getconn()
        yield connection
        connection.commit()
    except Exception as error:
        connection.rollback()
        raise error
    finally:
        connection_pool.putconn(connection)


@app.route('/')
def main_get():
    return render_template(
        'index.html',
    )


@app.post('/urls')
def url_post():
    url = request.form.get('url')
    validation = Validator(url)
    if not (validation.has_symbols().normalize().
            is_not_too_long().is_correct().is_valid()):
        flash(validation.get_error(), 'danger')
        messages = get_flashed_messages(with_categories=True)
        return render_template('index.html',
                               messages=messages,
                               value=url), 422
    else:
        url = validation.get_url()
        with get_connection() as conn:
            status = insert_url_to_db(conn, url)
            id = get_url_id(conn, url)
        flash(status, 'success')
        return redirect(
            url_for('url_get', id=id)
        )


@app.post('/urls/<int:id>/checks')
def check_post(id):
    with get_connection() as conn:
        url = get_url(conn, id)
        try:
            req = requests.get(url['name'], timeout=1)
        except Exception:
            flash('Произошла ошибка при проверке', 'danger')
        else:
            if req.status_code == 200:
                insert_check_to_db(conn, id, req)
                flash('Страница успешно проверена', 'success')
            else:
                flash('Произошла ошибка при проверке', 'danger')
    return redirect(
        url_for('url_get', id=id)
    )


@app.route('/urls/<int:id>')
def url_get(id):
    messages = get_flashed_messages(with_categories=True)
    with get_connection() as conn:
        url = get_url(conn, id)
        if not url:
            abort(404)
        checks = get_checks(conn, id)
    return render_template(
        'url.html',
        messages=messages,
        url=url,
        checks=checks
    )


@app.route('/urls')
def urls_get():
    with get_connection() as conn:
        urls = get_urls(conn)
    return render_template(
        'urls.html',
        urls=urls
    )


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404
