import akshare as ak
from os import path


class StockHelper:
    def get_us_recent_month(self, stock_name):
        try:
            stock_us_df = ak.stock_us_daily(symbol=stock_name)
            stock_us_df.to_csv(path.join('Downloads', f'{stock_name}_history.csv'))
            stock_data = []
            for i, j in stock_us_df.tail(80).iterrows():
                stock_data.append({'x': i.strftime("%b %d"), 'y': [j['open'], j['high'], j['low'], j['close']]})
            return stock_data
        except KeyError as e:
            return {'success': False}

    def test(self):
        stock_us_df = ak.stock_us_daily(symbol='AAPL')


if __name__ == '__main__':
    sh = StockHelper()
    sh.get_us_recent_month('AAPL')
