from flask import Flask, render_template, request, url_for, redirect, flash, get_flashed_messages
from dotenv import load_dotenv
import os
import psycopg2
from validators import url as validate
from datetime import datetime


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def get_main():
    messages = get_flashed_messages()
    return render_template(
        'index.html',
        messages=messages
    )


@app.post('/')
def post_url():
    url = request.form.get('url')
    if not validate(url):
        flash('Некорректный url', 'error'),
    else:
        current_datetime = datetime.now()
        timestamp = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("INSERT INTO urls (name, created_at) VALUES (%s, %s)", (url, timestamp))
        conn.commit()
        cur.close()
        flash('Успешно добавлено', 'success')

    return redirect(
        url_for('get_main')
    )
