from flask import Flask, render_template, request, url_for, redirect, flash, get_flashed_messages
from dotenv import load_dotenv
import os
from validators import url as validate
from page_analyzer.database import select_urls, get_url_id, insert_to_db, select_url, insert_check_to_db, select_checks
from urllib.parse import urlparse

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


def normalize_url(url):
    normalized = urlparse(url)
    return f'{normalized.scheme}://{normalized.hostname}'


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
    normalized_url = normalize_url(url)
    if not validate(normalized_url) or len(normalized_url) > 256:
        flash('Некорректный url', 'danger'),
        return redirect(
            url_for('get_main')
        )
    else:
        message = insert_to_db(normalized_url)
        id = get_url_id(normalized_url)
        flash(message, 'success')
        return redirect(
            url_for('get_url', id=id)
        )


@app.post('/urls/<int:id>/checks')
def post_url_check(id):
    insert_check_to_db(id)
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
