# It is defined by the kaggle/python docker image: https://github.com/kaggle/docker-python

import os

import numpy as np  # linear algebra
import pandas as pd
from sklearn import linear_model, preprocessing
from sklearn.model_selection import train_test_split

from utils.stocks import StockHelper


def prepare_data(df, forecast_col, forecast_out, test_size):
    label = df[forecast_col].shift(-forecast_out)
    X = np.array(df[[forecast_col]])
    X = preprocessing.scale(X)
    # creating the column i want to use later in the predicting method
    X_lately = X[-forecast_out:]
    X = X[:-forecast_out]
    label.dropna(inplace=True)
    y = np.array(label)
    X_train, X_test, Y_train, Y_test = train_test_split(
        X, y, test_size=test_size)

    response = [X_train, X_test, Y_train, Y_test, X_lately]
    return response


def predict_data(symbol, forecast_col, forecast_out, test_size):
    sh = StockHelper(symbol=symbol)
    df = sh.get_stock_df()
    print(df.shape)

    # calling the method were the cross validation and data preperation is in
    X_train, X_test, Y_train, Y_test, X_lately = prepare_data(
        df, forecast_col, forecast_out, test_size)

    # initializing linear regression model
    learner = linear_model.LinearRegression()

    learner.fit(X_train, Y_train)  # training the linear regression model
    # testing the linear regression model
    score = learner.score(X_test, Y_test)

    # set that will contain the forecasted data
    forecast = learner.predict(X_lately)

    response = {}
    response['test_score'] = score
    response['forecast_set'] = forecast.tolist()

    print(response)
    return response
