from pathlib import Path
from configparser import ConfigParser

myConfig = ConfigParser()
myConfig.read('config.ini')
print(f"Reading from configuration file 'config.ini'")
# Reading from config.ini file returns extra single quotes, remove first using strip
dataDir = Path('data')
modelDir = Path('models')


# raw files
money_2018_file = dataDir / 'money_2018.csv'
votes_2018_file = dataDir / 'votes_2018.xls'
money_2016_file = dataDir / 'money_2016.csv'
votes_2016_file = dataDir / 'votes_2016.xls'
money_files = [money_2016_file, money_2018_file]
votes_files = [votes_2016_file, votes_2018_file]

# files for flask; user choice list
flask_money_file = dataDir / 'flask_money_data.csv'
flask_candidate_file = dataDir / 'flask_cand_data.csv'
flask_race_file = dataDir / 'flask_race_data.csv'

flask_results_file = dataDir / 'flask_results_file.csv'
flask_2018_data = dataDir / 'flask_2018_data.csv'
precalc_cand_data = dataDir / 'precalc_2018_data.csv'
precalc_race_data = dataDir / 'precalc_2018_races.csv'

engineered_cand_data = dataDir / 'engineered_cand.csv'


# files for training models
training_race_file = dataDir / 'training_race_file.csv'
training_candidate_file = dataDir / 'training_candidate_file.csv'
training_money_file = dataDir / 'training_money_file.csv'

# files for training models
cleaned_race_file = dataDir / 'clean_race_file.csv'
cleaned_candidate_file = dataDir / 'clean_candidate_file.csv'
cleaned_money_file = dataDir / 'clean_money_file.csv'

# logRegModel = modelDir / 'LinRegModel.joblib'
randForestModel = modelDir / 'RandForestModel.joblib'
linRegModel = modelDir / 'LinRegModel.joblib'

