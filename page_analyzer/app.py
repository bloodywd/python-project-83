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
import requests
from page_analyzer.connection import get_connection
from page_analyzer.database import (
    get_checks,
    get_url_id,
    get_urls,
    get_url,
    insert_check_to_db,
    insert_url_to_db, UniqieURL,
)
from page_analyzer.parser import Parser
from page_analyzer.validate import Validator
from os import getenv
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = getenv('SECRET_KEY')


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
    url = validation.get_url()
    with get_connection() as conn:
        try:
            insert_url_to_db(conn, url)
            flash('Страница успешно добавлена', 'success')
        except (UniqieURL):
            flash('Страница уже существует', 'success')
    with get_connection() as conn:
        id = get_url_id(conn, url)
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
                parser = Parser(req.text)
                h1 = parser.get_h1()
                title = parser.get_title()
                description = parser.get_description()
                insert_check_to_db(conn, id, req.status_code, h1, title, description)
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
