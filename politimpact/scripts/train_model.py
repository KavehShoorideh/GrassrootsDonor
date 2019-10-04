import os
from datetime import datetime
import politimpact.config as cfg
from politimpact.scripts.engineer_features import engineerFeatures
import pandas as pd
import numpy as np
import math
from joblib import dump, load
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import KFold
from sklearn import metrics
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from politimpact.scripts.engineer_features import engineerFeatures
pd.set_option('display.max_rows', 500)
race_key = ['CONTEST_NAME', 'ELECTION_DATE']
cand_key = [*race_key, 'CANDIDATE_NAME']
#
# dfCand = pd.read_csv(cfg.training_candidate_file)
# dfRace = pd.read_csv(cfg.training_race_file)
# dfMoney = pd.read_csv(cfg.training_money_file)

def train1(dfCand):
    """ Linear Regression """

    myFeatures = ['INCUMBENT_FLAG', 'PARTY_LEAN', 'CAND_TOTAL_RAISED', 'RACE_TOTAL_RAISED', 'RACE_VOTE_TOTAL']
    myLabel = 'VOTE_TOTAL'
    dfCand = dfCand.dropna()
    X = dfCand[myFeatures]
    y = dfCand[myLabel]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    myModel = LinearRegression()
    myModel.fit(X_train, y_train)
    print(myModel.coef_)
    for idx, col_name in enumerate(X_train.columns):
        print("The coefficient for {} is {}".format(col_name, myModel.coef_[idx]))
    intercept = myModel.intercept_
    print("The intercept for our model is {}".format(intercept))
    y_pred = myModel.predict(X_test)
    mse = mean_squared_error(y_pred, y_test)
    error = math.sqrt(mse)
    print(f'mse is {mse}, its square is {error}')
    dump(myModel, cfg.linRegModel)

def train2(dfCand):
    """ Random Forest NOT FINISHED YET """
    myFeatures = ['INCUMBENT_FLAG', 'PARTY_LEAN', 'CAND_TOTAL_RAISED', 'RACE_TOTAL_RAISED', 'RACE_VOTE_TOTAL']
    myLabel = 'VOTE_TOTAL'
    dfCand = dfCand.dropna()
    X = dfCand[myFeatures]
    y = dfCand[myLabel]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
    myModel = LinearRegression()
    myModel.fit(X_train, y_train)
    print(myModel.coef_)
    for idx, col_name in enumerate(X_train.columns):
        print("The coefficient for {} is {}".format(col_name, myModel.coef_[0]))
    intercept = myModel.intercept_
    print("The intercept for our model is {}".format(intercept))
    y_pred = myModel.predict(X_test)
    mse = mean_squared_error(y_pred, y_test)
    error = math.sqrt(mse)
    print(f'mse is {mse}, its square is {error}')
    dump(myModel, linRegModel)
#
#
# def apply(dfCand, dfRace, dfMoney):
#
#     # This dfCand should not have an outcome column
#
#     LogReg = load(cfg.modelDir / 'LogRegModel.joblib')
#     myFeatures = ['Most_IND_Dollars', 'TotalFunds', 'PARTY_LEAN', 'INCUMBENT_FLAG']
#     myLabel = 'OUTCOME'
#     X = dfCand[myFeatures]
#     y_pred = LogReg.predict(X)
#     print(myConfusionMatrix)
#
# def engineer_log_reg_features(dfCand, dfRace, dfMoney):
#     sums = dfMoney.groupby(['rid', 'cid']).TransactionAmount.sum()
#     sums = sums.reset_index()
#     sums2 = sums.groupby('rid').apply(lambda x: x.sort_values('TRANSACTION_AMOUNT', ascending=False).head(2))
#     sums2['Most_IND_Dollars'] = 1
#     sums2.reset_index(drop=True, inplace=True)
#     sums2 = sums2.rename(columns={'TRANSACTION_AMOUNT': 'CAND_FUNDS_RAISED'})
#     dfCand = pd.merge(dfCand, sums2, left_on=['rid', 'cid'], right_on=['rid', 'cid'], how='left').fillna(int(0))
#     return dfCand
#
# def logRegModel1(dfCand, dfRaces=None, dfMoney=None):
#     pass


if __name__ == '__main__':
    if True:
        data, _, _= engineerFeatures(start_date = '2015-01-01')

    train1(data)
