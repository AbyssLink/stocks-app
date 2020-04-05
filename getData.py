import akshare as ak
from os import path


class StockHelper:
    def __init__(self, symbol: str):
        super().__init__()
        self.__symbol = symbol
        self.__stock_df = self.get_remote_data()

    def get_remote_data(self):
        try:
            stock_us_df = ak.stock_us_daily(symbol=self.__symbol)
            stock_us_df.to_csv(
                path.join('Downloads', f'{self.__symbol}_history.csv'))
            return stock_us_df
        except KeyError as e:
            return False

    def get_recent_chart_data(self):
        if self.__stock_df is not False:
            stock_data = []
            for i, j in self.__stock_df.tail(80).iterrows():
                stock_data.append({'x': i.strftime("%b %d"), 'y': [
                                  j['open'], j['high'], j['low'], j['close']]})
            return stock_data
        else:
            return {'success': False}

    def get_rencent_list_data(self):
        if self.__stock_df is not False:
            stock_data = []
            for i, j in self.__stock_df.tail(80).iterrows():
                stock_data.append({'symbol': self.__symbol,
                                   'time': i.strftime("%b %d"),
                                   'open': j['open'], 'high': j['high'], 'low': j['low'],
                                   'close': j['close'], 'volume': j['volume']
                                   })
            # return reversed list
            return stock_data[::-1]
        else:
            return {'success': False}

    def test(self):
        stock_us_df = ak.stock_us_daily(symbol='AAPL')


if __name__ == '__main__':
    sh = StockHelper()
    sh.get_recent_chart_data('AAPL')
