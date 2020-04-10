import ast
import json
from os import path
from urllib.request import url2pathname

from flask import Flask
from flask_cors import CORS
from flask_restful import Api, Resource, abort, reqparse

from news import fetch_news
from stocks import StockHelper
from strategy import StrategyHelper

app = Flask(__name__)
CORS(app, supports_credentials=True)
api = Api(app)

STOCKS = {
    'stock1': {'symbol': 'AAPL'}
}

business_url = "https://news.google.com/news/rss/headlines/section/topic/BUSINESS.en_in/Business?ned=in&hl=en-IN&gl=IN"

# USERS = {
#     '1': {'id': 1, 'username': 'Admin', 'password': 'admin'},
#     '2': {'id': 2, 'username': 'Nick', 'password': 'admin'},
#     '3': {'id': 3, 'username': 'Chino', 'password': 'admin'},
#     '4': {'id': 4, 'username': 'Chii', 'password': 'admin'},
# }


# * very useful method *
# https://stackoverflow.com/questions/72899/how-do-i-sort-a-list-of-dictionaries-by-a-value-of-the-dictionary
def sort_list_by_key(unsorts: list, sort_key: str):
    return sorted(unsorts, key=lambda k: k[sort_key])


def get_local_users():
    if(path.exists(path.join('private', 'users.json'))):
        with open(path.join('private', 'users.json'), 'r') as f:
            users = json.loads(f.read())
            print('Read local users.json file')
            return users
    else:
        print('No users local file!')


def write_local_users(users: dict):
    with open(path.join('private', 'users.json'), 'w') as f:
        # overwrite
        f.write(json.dumps(users))
        # json.dump(users, f)
        print('Write local users.json file')


def abort_if_not_exist(symbol_id):
    if symbol_id not in STOCKS:
        abort(404, message=f"Stock {symbol_id} doesn't exist")


def abort_if_user_not_exist(user_id, USERS):
    if user_id not in USERS:
        abort(404, message=f"User {user_id} doesn't exist")


parser = reqparse.RequestParser()
parser.add_argument('symbol')
parser.add_argument('user_id')
parser.add_argument('username')
parser.add_argument('password')
parser.add_argument('range')
parser.add_argument('sort')


class User(Resource):
    def __init__(self):
        super().__init__()
        self.__users = get_local_users()

    def get(self, user_id):
        abort_if_user_not_exist(user_id, self.__users)
        return self.__users[user_id]

    # need to be synchronize
    def delete(self, user_id):
        abort_if_user_not_exist(user_id, self.__users)
        del self.__users[user_id]
        write_local_users(self.__users)
        return f'delete {user_id} success'

    def put(self, user_id):
        args = parser.parse_args()
        user = {'id': int(user_id), 'username': args['username'],
                'password': args['password']}
        self.__users[user_id] = user
        write_local_users(self.__users)
        return user


class UserList(Resource):
    def __init__(self):
        super().__init__()
        self.__users = get_local_users()

    def get(self):
        args = parser.parse_args()
        users = []
        for k, v in self.__users.items():
            users.append(v)
        if args['range'] == None:
            return users
        range_str = url2pathname(args['range'])
        range_param = ast.literal_eval(range_str)
        start = range_param[0]
        if range_param[1] <= len(users):
            end = range_param[1]
        else:
            end = len(users)
        sort_str = url2pathname(args['sort'])
        sort_param = ast.literal_eval(sort_str)
        sort_key = sort_param[0]
        sort_order = sort_param[1]
        users = sort_list_by_key(users, sort_key)
        if sort_order == 'DESC':
            users.reverse()
        return users[start: end+1], 200, {'Access-Control-Expose-Headers': 'Content-Range',
                                          'Content-Range': f'posts {start}-{end}/{len(users)}'}

    def post(self):
        args = parser.parse_args()
        user_id = str(int(max(self.__users.keys(), key=int)) + 1)
        self.__users[user_id] = {'id': int(user_id), 'username': args['username'],
                                 'password': args['password']}
        write_local_users(self.__users)
        return self.__users[user_id]


# Stock
# shows a single Stock item and lets you delete a stock item
class Stock(Resource):
    def get(self, stock_id):
        abort_if_not_exist(stock_id)
        return STOCKS[stock_id]

    def delete(self, stock_id):
        abort_if_not_exist(stock_id)
        del STOCKS[stock_id]
        return '', 204

    def put(self, stock_id):
        args = parser.parse_args()
        symbol = {'symbol': args['symbol']}
        STOCKS[stock_id] = symbol
        return symbol, 201


# StockList
# shows a list of all STOCKS, and lets you POST to add new symbols
class StockList(Resource):
    def get(self):
        return STOCKS

    def post(self):
        args = parser.parse_args()
        stock_id = int(max(STOCKS.keys()).lstrip('stock')) + 1
        stock_id = 'stock%i' % stock_id
        STOCKS[stock_id] = {'symbol': args['symbol']}
        return STOCKS[stock_id], 201


# StockHistroy
# get stock history data from AKShare
class StockHistory(Resource):
    def get(self, symbol):
        sh = StockHelper(symbol=symbol)
        return sh.get_recent_chart_data()


class StockHistoryList(Resource):
    def get(self, symbol):
        sh = StockHelper(symbol=symbol)
        return sh.get_rencent_list_data()


class StockInfo(Resource):
    def get(self, symbol):
        sh = StockHelper(symbol=symbol)
        return sh.get_stock_info()


class PloySignalChart(Resource):
    def get(self, symbol):
        th = StrategyHelper(symbol=symbol)
        if th.get_df() is not None:
            th.update_range(100)
            th.add_signal(5, 20)
            return th.get_signal_chart_data()
        else:
            return {'success': False}


class GoogleNews(Resource):
    def get(self):
        news_list = fetch_news(business_url)
        return news_list[0:20]


#
# Actually setup the Api resource routing here
#
api.add_resource(UserList, '/users')
api.add_resource(User, '/users/<user_id>')
api.add_resource(StockList, '/stocks')
api.add_resource(Stock, '/stocks/<stock_id>')
api.add_resource(StockHistory, '/stocks-history/<symbol>')
api.add_resource(StockHistoryList, '/stocks-history-list/<symbol>')
api.add_resource(StockInfo, '/stocks-info/<symbol>')
api.add_resource(PloySignalChart, '/ploy-signal/<symbol>')
api.add_resource(GoogleNews, '/google-news/test')

if __name__ == '__main__':
    app.run(debug=True)
