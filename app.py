from flask import Flask
from flask import request

app = Flask(__name__)


@app.route('/', methods=['POST'])
def hello_world():
    serial = request.form.get('serial_number')
    return 'Hello PineMedia!' + serial
