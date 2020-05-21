from flask import Flask
from flask_cors import CORS
from flask_restful import Api, Resource, abort, reqparse

from config import config
from models import News, User, db
from routes import *

app = Flask(__name__)
# CORS request enable
CORS(app, supports_credentials=True)
# init app use restful resource
api = Api(app)
# read config from file
app.config.from_object(config['development'])
# init app use database setup
db.init_app(app)


# Actually setup the Api resource routing here
api.add_resource(Auth, '/auth')
api.add_resource(UserList, '/users')
api.add_resource(UserOne, '/users/<user_id>')
api.add_resource(StockList, '/stocks')
api.add_resource(Stock, '/stocks/<stock_id>')
api.add_resource(StockHistory, '/stocks-history/<symbol>')
api.add_resource(StockHistoryList, '/stocks-history-list/<symbol>')
api.add_resource(StockInfo, '/stocks-info/<symbol>')
api.add_resource(PloySignalChart, '/ploy-signal/<symbol>')
api.add_resource(DistributionChart, '/distrib-chart/<symbol>')
api.add_resource(DistributionProbility, '/distrib-prob/<symbol>')
api.add_resource(LinearRegression,  '/linear-regression/<symbol>')
api.add_resource(SVMPredict, '/svm/<symbol>')
api.add_resource(NewsAPI, '/news/test')
api.add_resource(RecommendNews, '/news-recommend/<title>')


if __name__ == '__main__':
    app.run(host='0.0.0.0')
