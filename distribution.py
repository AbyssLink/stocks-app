from scipy.stats import norm
import pandas as pd
from stocks import StockHelper
import numpy as np
import matplotlib.pyplot as plt


class Distribution:
    def __init__(self, symbol):
        super().__init__()
        self.__symbol = symbol
        self.__df = self.init_df()

    def init_df(self):
        sh = StockHelper(self.__symbol)
        # just cut off the df for show
        return sh.get_stock_df().head(50)

    def get_chart_data(self):
        # let play around with self.__df data by calculating the log daily return
        self.__df['log_return'] = np.log(
            self.__df['close']).shift(-1) - np.log(self.__df['close'])

        # very close to a normal distribution
        mu = self.__df['log_return'].mean()
        sigma = self.__df['log_return'].std(ddof=1)

        density = pd.DataFrame()
        density['x'] = np.arange(self.__df['log_return'].min()-0.01,
                                 self.__df['log_return'].max()+0.01, 0.0027)
        density['pdf'] = norm.pdf(density['x'], mu, sigma)
        chart_data = {
            'x': [str(round(elem, 2)) for elem in density['x'].to_list()],
            'pdf': [round(elem, 2) for elem in density['pdf'].to_list()]
        }
        return chart_data

    def get_probility(self, ratio, days):
        self.__df['log_return'] = np.log(
            self.__df['close']).shift(-1) - np.log(self.__df['close'])
        # drop over x% in x days
        mu = self.__df['log_return'].mean()
        sigma = self.__df['log_return'].std(ddof=1)
        mu_days = days*mu
        sigma_days = (days**0.5) * sigma
        drop = norm.cdf(ratio, mu_days, sigma_days)
        print(
            f'The probability of dropping over {ratio} in {days} days is ', drop)
        return {'prob': drop}


if __name__ == "__main__":
    dt = Distribution('FB')
    print(dt.get_chart_data())
    print(dt.get_probility(-0.4, 50))
