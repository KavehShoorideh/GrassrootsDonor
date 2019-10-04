import os
from grassrootsdonor import config as cfg
import pandas as pd

""" Extracts flask data files from training data files for 2018"""

dfCand = pd.read_csv(cfg.training_candidate_file, index_col=0)
dfRace = pd.read_csv(cfg.training_race_file, index_col=0)
dfMoney = pd.read_csv(cfg.training_money_file, index_col=0)

dfCand.loc[:, 'ELECTION_DATE'] = pd.to_datetime(dfCand['ELECTION_DATE'])
dfCand = dfCand[dfCand['ELECTION_DATE'].apply(lambda x:x.year) == 2018]
try:
    dfCand.drop(['VOTE_TOTAL','OUTCOME'], axis=1, inplace=True)
except KeyError:
    pass
dfCand.to_csv(cfg.flask_2018_data)


dfRace.loc[:, 'ELECTION_DATE'] = pd.to_datetime(dfRace['ELECTION_DATE'])
dfRace = dfRace[dfRace['ELECTION_DATE'].apply(lambda x:x.year) == 2018]
dfRace.to_csv(cfg.dataDir/'flask_race_data.csv')


timecols = ['ELECTION_DATE', 'TRANSACTION_DATE']
for col in timecols:
    dfMoney[col]= pd.to_datetime(dfMoney[col], errors='coerce')
dfMoney = dfMoney.dropna(subset=['TRANSACTION_DATE'])
mask=dfMoney['ELECTION_DATE'].apply(lambda x:x.year) == 2018
dfMoney = dfMoney[mask]
try:
    dfMoney.drop(['VOTE_TOTAL','OUTCOME'], axis=1, inplace=True)
except KeyError:
    pass
dfMoney.to_csv(cfg.dataDir/'flask_money_data.csv')

