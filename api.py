from flask import Flask
from flask_cors import CORS
from flask_restful import Api, Resource, abort, reqparse

from getData import StockHelper
from strategy import StrategyHelper

app = Flask(__name__)
CORS(app)
api = Api(app)

STOCKS = {
    'stock1': {'symbol': 'AAPL'}
}


def abort_if_not_exist(symbol_id):
    if symbol_id not in STOCKS:
        abort(404, message="Stock {} doesn't exist".format(symbol_id))


parser = reqparse.RequestParser()
parser.add_argument('symbol')


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
            th.update_range(150)
            th.add_signal(10, 30)
            return th.get_signal_chart_data()
        else:
            return {'success': False}


#
# Actually setup the Api resource routing here
#
api.add_resource(StockList, '/stocks')
api.add_resource(Stock, '/stocks/<stock_id>')
api.add_resource(StockHistory, '/stocks-history/<symbol>')
api.add_resource(StockHistoryList, '/stocks-history-list/<symbol>')
api.add_resource(StockInfo, '/stocks-info/<symbol>')
api.add_resource(PloySignalChart, '/ploy-signal/<symbol>')

if __name__ == '__main__':
    app.run(debug=True)
