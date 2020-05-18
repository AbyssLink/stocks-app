import matplotlib
import numpy as np
import pandas as pd
from scipy.stats import norm

from utils.stocks import StockHelper

matplotlib.use('Agg')


class Distribution:
    def __init__(self, symbol):
        super().__init__()
        self.__symbol = symbol
        self.__df = self.init_df()

    def init_df(self):
        sh = StockHelper(self.__symbol)
        # just cut off the df for show
        return sh.get_stock_df().tail(300)

    def get_chart_data(self, days):
        # let play around with self.__df data by calculating the log daily return
        self.__df['log_return'] = np.log(
            self.__df['close']).shift(-1) - np.log(self.__df['close'])
        self.__df['log_return'].dropna(inplace=True)
        log_return_series = self.__df['log_return'].tail(days)

        # very close to a normal distribution
        mu = log_return_series.mean()
        sigma = log_return_series.std(ddof=1)

        density = pd.DataFrame()
        density['x'] = np.arange(log_return_series.min()-0.01,
                                 log_return_series.max()+0.01, 0.0027)
        density['pdf'] = norm.pdf(density['x'], mu, sigma)
        density['x'].dropna(inplace=True)
        density['pdf'].dropna(inplace=True)
        frequency_each, _, _ = matplotlib.pyplot.hist(
            log_return_series, bins=density['x'].size)
        chart_data = {
            'x': [str(round(elem, 2)) for elem in density['x'].to_list()],
            'pdf': [round(elem, 2) for elem in density['pdf'].to_list()],
            'freq': frequency_each.tolist()}
        return chart_data

    def get_probility(self, ratio, days):
        self.__df['log_return'] = np.log(
            self.__df['close']).shift(-1) - np.log(self.__df['close'])
        self.__df['log_return'].dropna(inplace=True)

        # drop over x% in x days
        mu = self.__df['log_return'].mean()
        sigma = self.__df['log_return'].std(ddof=1)
        mu_days = days*mu
        sigma_days = (days**0.5) * sigma
        drop = norm.cdf(ratio, mu_days, sigma_days)
        print(
            f'The probability of dropping over {ratio} in {days} days is ', drop)
        return {'prob': round(drop, 5)}


if __name__ == "__main__":
    dt = Distribution('FB')
    print(dt.get_chart_data())
    print(dt.get_probility(-0.4, 50))
