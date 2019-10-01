import os
os.chdir(r"C:\Users\kaveh\OneDrive\Code Repos\Data Science\Insight\PolitImpact\politimpact")
from datetime import datetime
import pandas as pd
import politimpact.config as cfg
from joblib import load, dump
import numpy as np
from politimpact.scripts.engineer_features import engineerFeatures
pd.set_option('display.max_rows', 500)
race_key = ['CONTEST_NAME', 'ELECTION_DATE']
cand_key = [*race_key, 'CANDIDATE_NAME']

def preCalc(user_party=None, today=None):
    """
    :param user_party: user's selected party.
    :param today: Simulated date in 2018
    :return: Dataframe indexed by race, candidate, and users potential donations, with columns including
    winning chance, rank, and minimum donation required to win.
    """

    if today is None:
        end_date = parse('2018-12-31')
    elif isinstance(end_date, str):
        end_date = parse(end_date)

    print("REMEMBER TO FIX LOG SCALE!!!")
    model = load(cfg.linRegModel)

    # Engineer features
    data, _, _= engineerFeatures(start_date = '2017-01-01', end_date = end_date)

    # create candidate table
    races = createBaselineRaceTable(data, model)
    dollarlist = [1, 10, 100, 1000, 10000, 100000, 1e6]
    candTables = createCandidateTables(data, model, races, dollarlist)
    candTables.to_csv(cfg.precalc_cand_data)

def createBaselineRaceTable(data, model=None):
    """
     Loop over races
        Feed each race to model
        Find #1 #2, and their parties
        Store in table
    """

    race_key = ['CONTEST_NAME', 'ELECTION_DATE']
    cand_key = [*race_key, 'CANDIDATE_NAME']

    # Group candidates by race and apply general model to all
    groups = data.groupby(race_key)
    race_columns = [*race_key, 'WINNER', 'WINNER_PARTY_NAME',
                    'WINNER_PARTY_LEAN', 'RUNNER_UP', 'RUNNER_UP_PARTY_NAME', 'RUNNER_UP_PARTY_LEAN']
    races = pd.DataFrame(columns=race_columns)
    for key, group in groups:

        # Call model for each group
        output = raceModel(group, model)

        top = output.nlargest(2, 'PRED_VOTE_PCT')[[*cand_key, 'PARTY_NAME', 'PARTY_LEAN', 'PRED_VOTE_PCT']]

        this_race = top.iloc[0].loc[[*race_key]]

        # Following line selects races with 3 or more candidates, since in CA primaries top two advance
        if len(group.index) > 2:
            winner = top.iloc[0, :].loc[['CANDIDATE_NAME', 'PARTY_NAME', 'PARTY_LEAN']]
            runner_up = top.iloc[1, :].loc[['CANDIDATE_NAME', 'PARTY_NAME', 'PARTY_LEAN']]
            row = pd.Series([*this_race, *winner, *runner_up], index=race_columns)
            races = races.append(row, ignore_index=True).copy()
    #     races.to_csv(cfg.flask_race_file)
    return races


def createCandidateTables(data, model, races, dollarlist=[1000, 10000, 100000]):
    """
    Group races in table and loop over them
            Loop over candidates
            Create 5 new RACE dataframes, with extra amounts of money
            Plug RACE with new cand info back into model
            Tabulate results and save
            Identify needed amount by each candidate
            Create new candidate table: Cand, Seat, Party, Present_Rank, Money required to break top 2
    """
    race_key = ['CONTEST_NAME', 'ELECTION_DATE']
    cand_key = [*race_key, 'CANDIDATE_NAME']
    # from all the races, select only those who have more than 2 ppl running;
    # i.e. select those with the same index as  the races table we created (races doesn't have cand data)
    myRaces = races.reset_index().set_index(race_key).index
    myRaces = data.reset_index().set_index(race_key).loc[myRaces]

    grouping = myRaces.groupby(race_key)
    resultsList0 = []
    for name, group in grouping:
        # Looping through races
        these_cands = group.reset_index().set_index(cand_key)
        resultsList1 = []
        for row in these_cands.itertuples():
            # Loop through ALL candidates in each race
            oldResults = raceModel(these_cands, model)['PRED_VOTE_PCT'].reset_index()
            resultsList2 = []
            for donation in dollarlist:
                newFacts = addMoney(these_cands, row.Index, donation)
                modelResults = raceModel(newFacts, model)
                modelResults = findRanking(modelResults)
                newResults = modelResults.copy()[['PRED_VOTE_PCT', 'RANK', 'WINS']].reset_index()
                resultsList2.append(newResults.copy())
            allResults = pd.concat(resultsList2, keys=dollarlist, names=['DONATION', 'ROW'])
            allResults = allResults.droplevel(level='ROW')
            allResults = allResults.reset_index().set_index([*cand_key, 'DONATION']).sort_index()
            allResults = findMinWinDonation(allResults)
            resultsList1.append(allResults.copy())
        allResults = pd.concat(resultsList1)
        resultsList0.append(allResults.copy())
    allResults = pd.concat(resultsList0)
    return allResults

def addMoney(candGroup, cand_index, amount):
    """Function to add and transform money to a candidate's race info, and return new candidate group dataframe"""
    # REMEMBER TO FIX LOG SCALE IF APPLYING LOG FOR MONEY
    candGroup = candGroup.copy()
    candGroup.loc[cand_index, 'CAND_TOTAL_RAISED'] = amount + candGroup.loc[cand_index, 'CAND_TOTAL_RAISED']
    return candGroup

def findRanking(candGroup):
    """Take in candidate group with results (with PRED_VOTE_PCT column) and return with ranking appended"""
    temp = candGroup.copy().sort_values('PRED_VOTE_PCT', ascending=False)
    temp['RANK'] = range(1, len(temp)+1)
    temp['WINS'] = temp['RANK'] <=2
    return temp

def findImpact(candGroup):
    """Take in candidate group with results (with PRED_VOTE_PCT column) and return impact (Delta %win / $) appended"""
    pass

def findMinWinDonation(candGroup):
    """Take in candidate group with results (with PRED_VOTE_PCT column) and return impact (Delta %win / $) appended"""
    temp = candGroup.copy()
    def myFunc(x):
        return x['WINS'].idxmax()[3]
    temp['MIN_DONATION'] = temp.groupby([*cand_key]).apply(myFunc)
    return temp

def raceModel(candGroup, model):
    """ Take in a candidate group, append a column 'PRED_VOTE_PCT' with predicted percentage of votes"""
    trial = True
    # split group, apply
    if trial:
        # shoot out a bunch of random results
        a = np.random.random(len(candGroup))
        a /= a.sum()
        candGroup = candGroup.copy()
        candGroup['PRED_VOTE_PCT'] = a
    return candGroup


preCalc()