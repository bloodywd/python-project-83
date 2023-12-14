from flask import Flask, render_template, request, url_for, redirect, flash, get_flashed_messages
from dotenv import load_dotenv
import os
from validators import url as validate
from page_analyzer.database import select_urls, get_url_id, insert_to_db, select_url


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
    if not validate(url) and len(url) < 256:
        flash('Некорректный url', 'danger'),
        return redirect(
            url_for('get_main')
        )

    else:
        is_inserted = insert_to_db(url)
        id = get_url_id(url)
        if is_inserted:
            flash('Успешно добавлено', 'success')
        else:
            flash('Страница уже существует', 'success')
        return redirect(
            url_for('get_url', id=id)
        )


@app.route('/urls/<int:id>')
def get_url(id):
    messages = get_flashed_messages(with_categories=True)
    url = select_url(id)
    return render_template(
        'url.html',
        messages=messages,
        url=url
    )


@app.route('/urls')
def get_urls():
    urls = select_urls()
    print(urls)
    return render_template(
        'urls.html',
        urls=urls
    )
