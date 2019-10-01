import os
os.chdir(r"C:\Users\kaveh\OneDrive\Code Repos\Data Science\Insight\PolitImpact\politimpact")
from pathlib import Path
from configparser import ConfigParser
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import math
from datetime import datetime
from collections import defaultdict
import pandas as pd

myConfig = ConfigParser()
myConfig.read('config.ini')
print(f'Running in {os.getcwd()}')
print(f"Reading from configuration file 'config.ini'")
# Reading from config.ini file returns extra single quotes, remove first using strip
dataDir = Path(myConfig.get('paths', 'dataDir').strip('\''))
modelDir = Path(myConfig.get('paths', 'modelDir').strip('\''))

# model output file
candidate_prediction_file = dataDir / myConfig.get('paths', 'resultsFile').strip('\'')

# raw files
money_2018_file = dataDir / myConfig.get('paths', 'raw2018MoneyFile').strip('\'')
votes_2018_file = dataDir / myConfig.get('paths', 'raw2018VoteFile').strip('\'')
money_2016_file = dataDir / myConfig.get('paths', 'raw2016MoneyFile').strip('\'')
votes_2016_file = dataDir / myConfig.get('paths', 'raw2016VoteFile').strip('\'')
money_files = [money_2016_file, money_2018_file]
votes_files = [votes_2016_file, votes_2018_file]

# files for flask; user choice list
flask_money_file = dataDir / 'flask_money_data.csv'
flask_candidate_file = dataDir / 'flask_cand_data.csv'
flask_race_file = dataDir / 'flask_race_data.csv'

# files for training models
training_race_file = dataDir / myConfig.get('paths', 'racesFile').strip('\'')
training_candidate_file = dataDir / myConfig.get('paths', 'candidateFile').strip('\'')
training_money_file = dataDir / myConfig.get('paths', 'moneyFile').strip('\'')

# files for training models
cleaned_race_file = dataDir / myConfig.get('paths', 'cleanRacesFile').strip('\'')
cleaned_candidate_file = dataDir / myConfig.get('paths', 'cleanCandidateFile').strip('\'')
cleaned_money_file = dataDir / myConfig.get('paths', 'cleanMoneyFile').strip('\'')

logRegModel = modelDir / myConfig.get('paths', 'LogRegModel').strip('\'')
randForestModel = modelDir / myConfig.get('paths', 'RandForestModel').strip('\'')
linRegModel = modelDir / myConfig.get('paths', 'LinRegModel').strip('\'')

