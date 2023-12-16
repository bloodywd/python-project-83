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
    get_url_id,
    insert_to_db,
    select_url,
    insert_check_to_db,
    select_checks
)
from page_analyzer.validate import Validator
from dotenv import load_dotenv
import os
import requests


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


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
        url = validation.get_url()
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
        req = requests.get(url['name'], timeout=1)
    except Exception:
        flash('Произошла ошибка при проверке', 'danger')
    else:
        if req.status_code == 200:
            insert_check_to_db(id, req)
            flash('Страница успешно проверена', 'success')
        else:
            flash('Произошла ошибка при проверке', 'danger')
    return redirect(
        url_for('get_url', id=id)
    )


@app.route('/urls/<int:id>')
def get_url(id):
    messages = get_flashed_messages(with_categories=True)
    url = select_url(id)
    if not url:
        abort(404)
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

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html')
