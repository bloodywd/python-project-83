from flask import (
    Flask,
    render_template,
    request,
    url_for,
    redirect,
    flash,
    get_flashed_messages
)
from page_analyzer.database import (
    select_urls,
    get_url_id,
    insert_to_db,
    select_url,
    insert_check_to_db,
    select_checks
)
from page_analyzer.validate import validate_url
from dotenv import load_dotenv
import os
import requests


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def get_main():
    messages = get_flashed_messages(with_categories=True)
    return render_template(
        'index.html',
        messages=messages,
    )


@app.post('/')
def post_url():
    url = request.form.get('url')
    error = validate_url(url)
    if error:
        flash(error, 'danger'),
        return redirect(
            url_for('get_main')
        )
    else:
        status = insert_to_db(url)
        id = get_url_id(url)
        flash(status, 'success')
        return redirect(
            url_for('get_url', id=id)
        )


@app.post('/urls/<int:id>/checks')
def post_url_check(id):
    url = select_url(id)
    try:
        req = requests.get(url['name'], timeout=2)
    except requests.exceptions.ConnectionError:
        req = None
    if not req or req.status_code != 200:
        flash('Произошла ошибка при проверке', 'danger')
    else:
        insert_check_to_db(id, req)
        flash('Страница успешно проверена', 'success')
    return redirect(
        url_for('get_url', id=id)
    )


@app.route('/urls/<int:id>')
def get_url(id):
    messages = get_flashed_messages(with_categories=True)
    url = select_url(id)
    checks = select_checks(id)
    return render_template(
        'url.html',
        messages=messages,
        url=url,
        checks=checks
    )


@app.route('/urls')
def get_urls():
    urls = select_urls()
    return render_template(
        'urls.html',
        urls=urls
    )
