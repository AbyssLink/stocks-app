import datetime as dt
import json

import numpy as np
import pandas as pd

from stocks import StockHelper


class StrategyHelper:
    def __init__(self, symbol):
        super().__init__()
        self.__symbol = symbol
        self.__df = self.init_df()

    def init_df(self):
        sh = StockHelper(self.__symbol)
        return sh.get_stock_df()

    def update_range(self, range):
        self.__df = self.__df.tail(range)

    def add_signal(self,  fast: int, slow: int):
        df = self.__df
        df['ma_fast'] = df['close'].rolling(fast).mean()
        df['ma_slow'] = df['close'].rolling(slow).mean()
        df = df.dropna()
        df['shares'] = [1 if df.loc[i, 'ma_fast'] >
                        df.loc[i, 'ma_slow'] else 0 for i in df.index]
        df['close1'] = df['close'].shift(-1)
        df['profit'] = [df.loc[i, 'close1'] - df.loc[i, 'close']
                        if df.loc[i, 'shares'] == 1 else 0 for i in df.index]
        df['wealth'] = df['profit'].cumsum()
        df = df.dropna()
        self.__df = df

    def get_df(self):
        return self.__df

    def get_signal_chart_data(self):
        # use round to 2 decimal places
        chart_data = {
            'date': self.__df.index.strftime('%Y-%m-%d').to_list(),
            'fast': [round(elem, 2) for elem in self.__df['ma_fast'].to_list(
            )], 'slow': [round(elem, 2) for elem in self.__df['ma_slow'].to_list()],
            'close': [round(elem, 2) for elem in self.__df['close'].to_list()],
            'profit': [round(elem, 2) for elem in self.__df['profit'].to_list()],
            'wealth': [round(elem, 2) for elem in self.__df['wealth'].to_list()]
        }
        return chart_data


if __name__ == "__main__":
    th = StrategyHelper('FB')
    th.update_range(300)
    print(th.get_df())
    th.add_signal(10, 30)
    print(th.get_df().tail(50))
    print(th.get_wealth_chart_data())
