import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas import DataFrame, Series
from sklearn import svm

from stocks import StockHelper


class SVMHelper:
    def __init__(self, symbol):
        super().__init__()
        self.__symbol = symbol
        self.__df = self.init_df()

    def init_df(self):
        sh = StockHelper(self.__symbol)
        # just cut off the df for show
        stock_df = sh.get_stock_df().tail(300)
        # Create more data
        value = pd.Series(stock_df['close'].shift(-1) -
                          stock_df['close'], index=stock_df.index)
        # Difference between high and low
        stock_df['high-low'] = stock_df['high']-stock_df['low']
        stock_df['nopen-close'] = stock_df['open'].shift(-1)-stock_df['close']
        stock_df['close-yclose'] = stock_df['close'] - \
            stock_df['close'].shift(1)  # Today is rise or fall
        stock_df['close-open'] = stock_df['close'] - \
            stock_df['open']  # today's close - open
        stock_df['high-close'] = stock_df['high'] - \
            stock_df['close']  # today's high - close
        stock_df['close-low'] = stock_df['close'] - \
            stock_df['low']  # today's close - low
        value[value >= 0] = 1  # 1 means rise
        value[value < 0] = 0  # 0 means fall
        stock_df['value'] = value
        stock_df = stock_df.dropna(how='any')
        del(stock_df['open'])
        del(stock_df['close'])
        del(stock_df['high'])
        del(stock_df['low'])
        return stock_df

    def train(self, train: int):
        L = len(self.__df)
        total_predict_data = L - train
        correct = 0
        train_original = train
        i = 0
        # loop training
        value_predicts = []
        value_reals = []
        value_corrects = []
        while train < L:
            Data_train = self.__df[train-train_original:train]
            Data_predict = self.__df[train:train+1]
            value_train = self.__df['value'][train-train_original:train]
            value_real = self.__df['value'][train:train+1]
            del(Data_train['value'])
            del(Data_predict['value'])
            # print(Data_train)
            # print(value_train)
            # poly：选择模型所使用的核函数为多项式核函数
            classifier = svm.SVC(kernel='poly')
            # 根据给定的训练数据拟合 SVM 模型
            classifier.fit(Data_train, value_train)
            value_predict = classifier.predict(Data_predict)
            value_predicts.append(int(value_predict))
            value_reals.append(int(value_real[0]))
            if(value_real[0] == int(value_predict)):
                correct = correct+1
                value_corrects.append(1)
            else:
                value_corrects.append(0)
            train = train+1
        correct = correct/total_predict_data*100
        print("Correct = ", correct, "%")
        return {'predicts': value_predicts, 'reals': value_reals, 'corrects': value_corrects, 'result': correct}


if __name__ == "__main__":
    svm_h = SVMHelper('GOOG')
    chart_data = svm_h.train(train=210)
    print(chart_data)
