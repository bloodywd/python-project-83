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
from page_analyzer.database import PageAnalyzerDataBase
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
        db = PageAnalyzerDataBase()
        url = validation.get_url()
        status = db.insert_to_db(url)
        id = db.select_url_id(url)
        db.close()
        flash(status, 'success')
        return redirect(
            url_for('get_url', id=id)
        )


@app.post('/urls/<int:id>/checks')
def post_url_check(id):
    db = PageAnalyzerDataBase()
    url = db.select_url(id)
    try:
        req = requests.get(url['name'], timeout=1)
    except Exception:
        flash('Произошла ошибка при проверке', 'danger')
    else:
        if req.status_code == 200:
            db.insert_check_to_db(id, req)
            flash('Страница успешно проверена', 'success')
        else:
            flash('Произошла ошибка при проверке', 'danger')
    db.close()
    return redirect(
        url_for('get_url', id=id)
    )


@app.route('/urls/<int:id>')
def get_url(id):
    db = PageAnalyzerDataBase()
    messages = get_flashed_messages(with_categories=True)
    url = db.select_url(id)
    if not url:
        abort(404)
    checks = db.select_checks(id)
    db.close()
    return render_template(
        'url.html',
        messages=messages,
        url=url,
        checks=checks
    )


@app.route('/urls')
def get_urls():
    db = PageAnalyzerDataBase()
    urls = db.select_urls()
    db.close()
    return render_template(
        'urls.html',
        urls=urls
    )


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404
