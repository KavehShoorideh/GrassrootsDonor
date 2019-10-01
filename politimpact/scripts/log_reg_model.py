import politimpact.config as cfg
import pandas as pd
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold
from sklearn import metrics
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from joblib import dump, load

dfCand = pd.read_csv(cfg.featuresFile)
dfRace = pd.read_csv(cfg.racesFile)
dfMoney = pd.read_csv(cfg.moneyFile)

def apply_model(dfCand, dfRace, dfMoney):


def train():
    dfCand = engineer_log_reg_features(dfCand, dfRace, dfMoney)

    # select out only 2016:
    dfCand = dfCand[dfCand['ELECTION_DATE'].year == 2016]
    dfRace = dfRace[dfRace['ELECTION_DATE'].year == 2016]
    dfMoney = dfMoney[dfMoney['ELECTION_DATE'].year == 2016]

    myFeatures = ['Most_IND_Dollars', 'TotalFunds', 'PARTY_LEAN', 'INCUMBENT_FLAG']
    myLabel = 'OUTCOME'
    X = dfCand[myFeatures]
    y = dfCand[myLabel]

    # Split
    kf = KFold(n_splits=5)
    kf.get_n_splits(X)
    for train_index, test_index in kf.split(X):
        print("TRAIN:", train_index, "TEST:", test_index)
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
    LogReg = LogisticRegression()
    LogReg.fit(X_train, y_train)
    y_prob = LogReg.predict_proba(X_test)
    y_pred = LogReg.predict(X_test)
    myConfusionMatrix = confusion_matrix(y_test, y_pred)

    dump(LogReg, cfg.modelDir / 'LogRegModel.joblib')


def apply(dfCand, dfRace, dfMoney):

    # This dfCand should not have an outcome column

    LogReg = load(cfg.modelDir / 'LogRegModel.joblib')
    myFeatures = ['Most_IND_Dollars', 'TotalFunds', 'PARTY_LEAN', 'INCUMBENT_FLAG']
    myLabel = 'OUTCOME'
    X = dfCand[myFeatures]
    y_pred = LogReg.predict(X)
    print(myConfusionMatrix)

def engineer_log_reg_features(dfCand, dfRace, dfMoney):
    sums = dfMoney.groupby(['rid', 'cid']).TransactionAmount.sum()
    sums = sums.reset_index()
    sums2 = sums.groupby('rid').apply(lambda x: x.sort_values('TransactionAmount', ascending=False).head(2))
    sums2['Most_IND_Dollars'] = 1
    sums2.reset_index(drop=True, inplace=True)
    sums2 = sums2.rename(columns={'TransactionAmount': 'TotalFunds'})
    dfCand = pd.merge(dfCand, sums2, left_on=['rid', 'cid'], right_on=['rid', 'cid'], how='left').fillna(int(0))
    return dfCand

def logRegModel1(dfCand, dfRaces=None, dfMoney=None):




if __name__ == '__main__':
    train()
