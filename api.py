import ast
import json
from os import path
from urllib.request import url2pathname

from flask import Flask
from flask_cors import CORS
from flask_restful import Api, Resource, abort, reqparse
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_

from app.static import STOCKS, business_url
from distribution import Distribution
from news import fetch_news
from stocks import StockHelper
from strategy import StrategyHelper
from svm_test import SVMHelper

app = Flask(__name__)
CORS(app, supports_credentials=True)
api = Api(app)

app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost:3306/stock'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


# Models
class User(db.Model):
    """Data model for user accounts."""

    # as_dict 实现对象序列化
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64))
    password = db.Column(db.String(64))

    def __repr__(self):
        return f'<User {self.username}>'


class News(db.Model):
    """Data model for News."""

    # as_dict 实现对象序列化
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    __tablename__ = 'news'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    img = db.Column(db.String(512))
    title = db.Column(db.String(512))
    description = db.Column(db.String(512))
    link = db.Column(db.String(512))
    date = db.Column(db.String(512))

    def __repr__(self):
        return f'<News {self.title}>'


db.create_all()

# * very useful method *
# https://stackoverflow.com/questions/72899/how-do-i-sort-a-list-of-dictionaries-by-a-value-of-the-dictionary


def sort_list_by_key(unsorts: list, sort_key: str):
    return sorted(unsorts, key=lambda k: k[sort_key])


def abort_if_stock_not_exist(symbol_id):
    if symbol_id not in STOCKS:
        abort(404, message=f"Stock {symbol_id} doesn't exist")


def get_user_from_db(user_id):
    if User.query.filter_by(id=user_id).first() is None:
        abort(404, message=f"User {user_id} doesn't exist")
    else:
        return User.query.filter_by(id=user_id).first()


parser = reqparse.RequestParser()
parser.add_argument('symbol')
parser.add_argument('user_id')
parser.add_argument('username')
parser.add_argument('password')
parser.add_argument('range')
parser.add_argument('sort')


class UserOne(Resource):
    def __init__(self):
        super().__init__()
        users = User.query.all()
        user_list = []
        for user in users:
            user_list.append(user.as_dict())
        self.__users = user_list

    def get(self, user_id):
        user = get_user_from_db(user_id)
        return user.as_dict()

    # need to be synchronize
    def delete(self, user_id):
        user = get_user_from_db(user_id)
        db.session.delete(user)
        db.session.commit()
        return f'delete {user_id} success'

    # update one user
    def put(self, user_id):
        args = parser.parse_args()
        username = args['username']
        password = args['password']
        # Create an instance of the User class
        user = get_user_from_db(user_id)
        user.username = username
        user.password = password
        db.session.commit()  # Commits all changes
        return user.as_dict()


class UserList(Resource):
    def __init__(self):
        super().__init__()
        users = User.query.all()
        user_list = []
        for user in users:
            user_list.append(user.as_dict())
        self.__users = user_list

    def get(self):
        args = parser.parse_args()
        users = self.__users
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
        username = args['username']
        password = args['password']
        # Create an instance of the User class
        new_user = User(username=username, password=password)
        db.session.add(new_user)  # Adds new User record to database
        db.session.commit()  # Commits all changes
        return new_user.as_dict()


# Stock
# shows a single Stock item and lets you delete a stock item
class Stock(Resource):
    def get(self, stock_id):
        abort_if_stock_not_exist(stock_id)
        return STOCKS[stock_id]

    def delete(self, stock_id):
        abort_if_stock_not_exist(stock_id)
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
        # FIXME: dirty method
        real_symbol, fast, slow, days = symbol.split('|')
        th = StrategyHelper(symbol=real_symbol)
        if th.get_df() is not None:
            th.update_range(int(days))
            th.add_signal(int(fast), int(slow))
            return th.get_signal_chart_data()
        else:
            return {'success': False}


class DistributionChart(Resource):
    def get(self, symbol):
        # FIXME: dirty method
        real_symbol = symbol.split('|')[0]
        days = symbol.split('|')[2]
        dt = Distribution(symbol=real_symbol)
        return dt.get_chart_data(int(days))


class DistributionProbility(Resource):
    def get(self, symbol):
        # FIXME: dirty method
        real_symbol, ratio, days = symbol.split('|')
        dt = Distribution(symbol=real_symbol)
        return dt.get_probility(float(ratio), int(days))


class SVMPredict(Resource):
    def get(self, symbol):
        # FIXME: dirty method
        real_symbol = symbol.split('|')[0]
        train = symbol.split('|')[1]
        vh = SVMHelper(symbol=real_symbol)
        return vh.train(train=int(train))


class Auth(Resource):
    def post(self):
        args = parser.parse_args()
        username = args['username']
        password = args['password']
        if User.query.filter_by(username=username).first() is not None:
            if User.query.filter_by(username=username).first().password == password:
                return {'success': True}, 200
        return {'success': False}, 233


class NewsAPI(Resource):
    def get(self):
        news_list = fetch_news(business_url)
        for news in news_list:
            if News.query.filter_by(title=news['title']).first() is None:
                new_news = News(img=news['img'], title=news['title'],
                                description=news['description'], link=news['link'], date=news['date'])
                db.session.add(new_news)
                db.session.commit()
        return news_list


#
# Actually setup the Api resource routing here
#
api.add_resource(UserList, '/users')
api.add_resource(UserOne, '/users/<user_id>')
api.add_resource(StockList, '/stocks')
api.add_resource(Stock, '/stocks/<stock_id>')
api.add_resource(StockHistory, '/stocks-history/<symbol>')
api.add_resource(StockHistoryList, '/stocks-history-list/<symbol>')
api.add_resource(StockInfo, '/stocks-info/<symbol>')
api.add_resource(PloySignalChart, '/ploy-signal/<symbol>')
api.add_resource(NewsAPI, '/news/test')
api.add_resource(Auth, '/auth')
api.add_resource(DistributionChart, '/distrib-chart/<symbol>')
api.add_resource(DistributionProbility, '/distrib-prob/<symbol>')
api.add_resource(SVMPredict, '/svm/<symbol>')

if __name__ == '__main__':
    app.run(debug=True)
