from flask import Flask, render_template
from dotenv import load_dotenv
import os
import psycopg2


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
try:
    conn = psycopg2.connect(DATABASE_URL)
    print('Fine')
except:
    print('Can`t establish connection to database')

app = Flask(__name__)
@app.route('/')
def get_main():
    return render_template(
        'index.html'
    )
