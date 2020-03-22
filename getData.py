import akshare as ak


class StockHelper:
    def get_us_recent_month(self, stock_name):
        try:
            stock_us_df = ak.stock_us_daily(symbol=stock_name)
            stock_us_df.to_csv(f'stock_{stock_name}_history.csv')
            stock_data = []
            for i, j in stock_us_df.tail(25).iterrows():
                stock_data.append({'x': i.strftime("%b %d"), 'y': [j['open'], j['high'], j['low'], j['close']]})
            return stock_data
        except KeyError as e:
            print('keyError: ', e)

    def test(self):
        stock_us_df = ak.stock_us_daily(symbol='AAPL')


if __name__ == '__main__':
    sh = StockHelper()
    sh.test()
