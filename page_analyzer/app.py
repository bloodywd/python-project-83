from psycopg2.pool import SimpleConnectionPool
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
    select_urls,
    select_url_id,
    select_checks,
    select_url,
    insert_check_to_db,
    insert_to_db
)
from page_analyzer.validate import Validator
from dotenv import load_dotenv
import os
import requests


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
connection_pool = SimpleConnectionPool(1, 8, dsn=os.getenv('DATABASE_URL'))


@app.route('/')
def get_main():
    return render_template(
        'index.html',
    )


@app.post('/urls')
def post_url():
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
        conn = connection_pool.getconn()
        url = validation.get_url()
        status = insert_to_db(conn, url)
        id = select_url_id(conn, url)
        connection_pool.putconn(conn)
        flash(status, 'success')
        return redirect(
            url_for('get_url', id=id)
        )


@app.post('/urls/<int:id>/checks')
def post_url_check(id):
    conn = connection_pool.getconn()
    url = select_url(conn, id)
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
    connection_pool.putconn(conn)
    return redirect(
        url_for('get_url', id=id)
    )


@app.route('/urls/<int:id>')
def get_url(id):
    conn = connection_pool.getconn()
    messages = get_flashed_messages(with_categories=True)
    url = select_url(conn, id)
    if not url:
        abort(404)
    checks = select_checks(conn, id)
    connection_pool.putconn(conn)
    return render_template(
        'url.html',
        messages=messages,
        url=url,
        checks=checks
    )


@app.route('/urls')
def get_urls():
    conn = connection_pool.getconn()
    urls = select_urls(conn)
    connection_pool.putconn(conn)
    return render_template(
        'urls.html',
        urls=urls
    )


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404
