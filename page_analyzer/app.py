from flask import Flask, render_template
from dotenv import load_dotenv


load_dotenv()
app = Flask(__name__)


@app.route('/')
def get_main():
    return render_template(
        'index.html'
    )

