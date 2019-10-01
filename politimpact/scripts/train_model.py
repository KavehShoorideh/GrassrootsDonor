import os
os.chdir(r"C:\Users\kaveh\OneDrive\Code Repos\Data Science\Insight\PolitImpact\politimpact")
import politimpact.config as cfg
import pandas as pd
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import math
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import KFold
from sklearn import metrics
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from joblib import dump, load

dfCand = pd.read_csv(cfg.training_candidate_file)
dfRace = pd.read_csv(cfg.training_race_file)
dfMoney = pd.read_csv(cfg.training_money_file)

def train1(dfCand, dfRace, dfMoney):
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

def train2(dfCand, dfRace, dfMoney):
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
    train1(dfCand, dfRace, dfMoney)