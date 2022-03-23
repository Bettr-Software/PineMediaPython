from flask import Flask
from flask import request
from alex import adtran

app = Flask(__name__)


@app.route('/', methods=['POST'])
def hello_world():
    serial = request.form.get('serial_number')
    ont_desc = request.form.get('ont_desc')
    response = adtran.run_from_app(serial,ont_desc)

    return 'Serial:' + serial + ' Description:' + ont_desc + response
