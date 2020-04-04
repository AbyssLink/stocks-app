from flask import Flask
from flask_cors import CORS
from getData import StockHelper
import json

app = Flask(__name__)

CORS(app)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/stocks/<stock_name>')
def show_user_profile(stock_name):
    if stock_name == 'NULL':
        return json.dumps(False)
    else:
        sh = StockHelper()
        return json.dumps(sh.get_us_recent_month(stock_name))


if __name__ == '__main__':
    app.run()
