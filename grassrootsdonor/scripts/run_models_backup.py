import os
from grassrootsdonor import config as cfg
from grassrootsdonor.scripts import race_model
from datetime import datetime
from joblib import load
import pandas as pd

def begin():
    modelFile = 'LogRegModel.joblib'
    model = load(cfg.linRegModel)
    run_models(model)

def run_models(model, today=None):

    dfCand = pd.read_csv(cfg.flask_candidate_file, index_col=0)
    dfRace = pd.read_csv(cfg.flask_race_file, index_col=0)
    dfMoney = pd.read_csv(cfg.flask_money_file, index_col=0)

    # Convert important columns to datetime
    dfCand.loc[:, 'ELECTION_DATE'] = pd.to_datetime(dfCand['ELECTION_DATE'])
    dfRace.loc[:, 'ELECTION_DATE'] = pd.to_datetime(dfRace['ELECTION_DATE'])
    timecols = ['ELECTION_DATE', 'TRANSACTION_DATE']
    for col in timecols:
        dfMoney[col] = pd.to_datetime(dfMoney[col], errors='coerce')
    dfMoney = dfMoney.dropna(subset=['TRANSACTION_DATE'])

    if today:
        # Drop transactions after "today"'s pretend date.
        mask = dfMoney['TRANSACTION_DATE'].apply(lambda x: x.year) < today
        dfMoney = dfMoney[mask]

    race_key = ['CONTEST_NAME', 'ELECTION_DATE']
    cand_key = ['CANDIDATE_NAME', *race_key]
    contest_names = dfCand.groupby(race_key)['VOTE_SHARE'].sum().dropna().index
    dfRace = dfRace.set_index(race_key).loc[contest_names].dropna().reset_index()
    dfCand = pd.merge(dfCand, dfRace[['CONTEST_NAME', 'ELECTION_DATE']], on=race_key, how='inner')
    groups = dfCand.groupby(race_key)
    cands = dfCand.set_index(race_key)
    results = pd.DataFrame()
    for name, group in groups:
        # we are iterating through the groups here
        myCands = cands.loc[name]
        myCands.to_csv(cfg.dataDir / 'test.csv')
        output = race_model.applyRaceModel(myCands, model)
        print(output)
        break
        myResults = race_model(myCands)
        results = pd.concat(myResults)

#
# def raceList(featuresDf, electionDate, today=datetime.today()):
#     """ Group candidates by the seat they're running for, and feed into the model. Simulate today's date if needed"""
#     mask = (featuresDf['ELECTION_DATE'] == electionDate) & (today > featuresDf['TRANSACTION_DATE'])
#     grouped_df = moneyDf[mask].groupby(['ELECTION_DATE', 'CONTEST_NAME'])
#     output = []
#     for key, item in grouped_df:
#         candidates = item.to_dict('records')
#         output.append(Race(candidates))
#     return output

def apply_model(race):
    dfCand = pd.read_csv(featuresFile)
    dfRace = pd.read_csv(racesFile)
    dfMoney = pd.read_csv(moneyFile)

    # Calculate these using the model
    win_chance_before = model(race)
    name = race.favorite['name']
    budget = user_input['user_budget']
    race.donate(name, budget)
    win_chance_after = model(race)
    # Undo donation
    race.donate(name, -budget)
    # add data to record
    record = {'name': name,
                    'office': race.favorite['office'],
                    'win_chance_before': f'{(win_chance_before):.0%}',
                    'win_chance_after': f'{(win_chance_after):.0%}',
                    'impact': f'{(win_chance_after - win_chance_before):.0%}',
                    'party': race.favorite['pref_score'],
                    'web_link': "https://www.google.com/"
                    }

    fieldnames = [key for key in record.keys()]

    return record

def calculateResults(featuresDf, model = apply_model, today=datetime.today()):

    # record = {'name': name,
    #                 'office': race.favorite['office'],
    #                 'win_chance_before': f'{(win_chance_before):.0%}',
    #                 'win_chance_after': f'{(win_chance_after):.0%}',
    #                 'impact': f'{(win_chance_after - win_chance_before):.0%}',
    #                 'party': race.favorite['pref_score'],
    #                 'web_link': "https://www.google.com/"
    #                 }
    featuresDf = pd.read_csv(cfg.featuresDataFile)
    previous_results = pd.read_csv(cfg.resultsFile)
    electionDate = dateutil.parser.parse('June 5, 2018')
    races = raceList(featuresDf, electionDate, today)
    results = [model(race) for race in races]

    with open(cfg.resultsFile, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=df.columns)
        writer.writeheader()
        [writer.writerow(record) for record in results]

if __name__ == '__main__':
    begin()