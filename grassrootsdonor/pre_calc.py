import pandas as pd
from dateutil.parser import parse
import grassrootsdonor.config as cfg
from joblib import load
import numpy as np
from grassrootsdonor.engineer_features import engineerFeatures

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 1000)
pd.options.mode.chained_assignment = None  # default='warn'
race_key = ['CONTEST_NAME', 'ELECTION_DATE']
cand_key = [*race_key, 'CANDIDATE_NAME']

features = ['ELECTION_DATE', "PARTY_LEAN", 'WRITE_IN_FLAG', 'CAND_TOTAL_RAISED', 'CANDIDATE_COUNT',
                'RACE_TOTAL_RAISED',
                'RACE_VOTE_TOTAL']

target = ['VOTE_SHARE']

def preCalc(user_party=None, user_today=None, user_priority=None, live= False):
    """
    :param user_party: user's selected party; TODO: use to speed up race processing.
    :param user_today: Simulated date in 2018
    :param user_budget: user's donation budget; unused here.
    :return: Dataframe indexed by race, candidate, and users potential donations, with columns including
    winning chance, rank, and minimum donation required to win.
    """

    if user_today is None:
        end_date = parse('2018-12-31')
    elif isinstance(user_today, str):
        end_date = parse(user_today)

    print("REMEMBER TO FIX LOG SCALE!!!")
    model = load(cfg.randForestModel)

    # Engineer features
    data, _, _= engineerFeatures(start_date = '2017-01-01', end_date = end_date)
    print("Done feature engineering, calculating results:")

    # create candidate table
    # races, baselineResults = createBaselineRaceTable(data, model)
    dollarlist = [10000, 25000, 50000, 75000, 100000, 2.5e5, 5e5, 7.5e5, 1e6]

    raceTable, baselineResults = createBaselineRaceTable(data, model, features)
    candTables = createCandidateTables(data, model, features, raceTable, dollarlist)

    # Add in VOTE_PCT_BEFORE
    temp = baselineResults.filter(items = [*cand_key, 'PRED_VOTE_PCT'])\
        .rename(columns={'PRED_VOTE_PCT': 'VOTE_PCT_BEFORE'})
    candTables = candTables.reset_index()
    candTables = pd.merge(left=candTables, right=temp, left_on=[*race_key,'FAVORITE'], right_on=cand_key)
    candTables = candTables.drop('CANDIDATE_NAME_y', axis=1)
    candTables = candTables.rename(columns={'CANDIDATE_NAME_x': 'CANDIDATE_NAME'})

    candTables = candTables[candTables['FAVORITE'] == candTables['CANDIDATE_NAME']]

    if not live:
        raceTable.to_csv(cfg.precalc_race_data)
        candTables.to_csv(cfg.precalc_cand_data)
    if live:
        return candTables, raceTable

def createBaselineRaceTable(data, model, features):
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
    # baselineResults = pd.DataFrame(columns=race_columns)
    resultsList = []
    for key, group in groups:

        # Call model for each group
        output = raceModel(group, model, features)
        resultsList.append(output)
        top = output.nlargest(2, 'PRED_VOTE_PCT')[[*cand_key, 'PARTY_NAME', 'PARTY_LEAN', 'PRED_VOTE_PCT']]

        this_race = top.iloc[0].loc[[*race_key]]

        # Following line selects races with 3 or more candidates, since in CA primaries top two advance
        if len(group.index) > 2:
            winner = top.iloc[0, :].loc[['CANDIDATE_NAME', 'PARTY_NAME', 'PARTY_LEAN']]
            runner_up = top.iloc[1, :].loc[['CANDIDATE_NAME', 'PARTY_NAME', 'PARTY_LEAN']]
            row = pd.Series([*this_race, *winner, *runner_up], index=race_columns)
            races = races.append(row, ignore_index=True).copy()
    #     races.to_csv(cfg.flask_race_file)
    baselineResults = pd.concat(resultsList)
    return races, baselineResults


def createCandidateTables(data, model, features, races, dollarlist=[1000, 10000, 100000]):
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
    myRaceIndices = races.reset_index().set_index(race_key).index
    myRaces = data.reset_index(drop=True).set_index(race_key).loc[myRaceIndices]
    grouping = myRaces.groupby(race_key, as_index=False)
    raceList = []
    for name, group in grouping:
        # Looping through races
        # these_cands = group.reset_index().set_index(cand_key).copy()
        candList = []
        for row in group.itertuples():
            # Loop through ALL candidates in each race
            # Row is a named tuple, so we can access the names, and also the Index, like below
            #Pandas(Index=('State Assembly Member District 1', Timestamp('2018-06-05 00:00:00')),
            #      CANDIDATE_NAME='JENNY O CONNELL-NOWAIN', PARTY_NAME='No Party Preference', ...
            candName = row.CANDIDATE_NAME
            dollarList = []
            for donation in dollarlist:
                # these_cands['FAVORITE'] = these_cands.loc[row.Index, 'CANDIDATE_NAME']
                newFacts = addMoney(group, row.Index, candName, donation).reset_index()
                newResults = raceModel(newFacts, model, features)
                newResults = findRanking(newResults)
                newcols = ['PARTY_NAME', 'RANK', 'WINS', 'FAVORITE','PRED_VOTE_PCT']
                newResults = newResults[list(set(cand_key + features + newcols))]
                newResults = newResults.set_index([*race_key, 'FAVORITE'])
                dollarList.append(newResults.copy())
            candResults = pd.concat(dollarList, keys=dollarlist, names=['DONATION'])
            candResults['MIN_DONATION'] = findMinWinDonation(candResults, candName)
            candList.append(candResults.copy())
        raceResults = pd.concat(candList)
        raceList.append(raceResults.copy())
    allResults = pd.concat(raceList)
    return allResults

def addMoney(candGroup, cand_index, candName, amount):
    """Function to add and transform money to a candidate's race info, and return new candidate group dataframe"""
    # REMEMBER TO FIX LOG SCALE IF APPLYING LOG FOR MONEY
    candGroup = candGroup.copy()
    candGroup.loc[candGroup['CANDIDATE_NAME'] == candName, 'CAND_TOTAL_RAISED'] = amount + candGroup.loc[candGroup['CANDIDATE_NAME'] == candName, 'CAND_TOTAL_RAISED']
    candGroup['FAVORITE'] = candName
    candGroup.loc[candGroup['CANDIDATE_NAME'] == candName, 'FAVORITE'] = candName
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

def findMinWinDonation(candGroup, candName):
    """Take in candidate group with results (with PRED_VOTE_PCT column) and return min dollars to win"""
    temp = candGroup.copy().reset_index()
    mask = (temp['CANDIDATE_NAME'] == candName) & (temp['WINS'] == True)
    temp = temp[mask]['DONATION']
    if temp.empty:
        output = np.nan
    else:
        # output = temp.min()
        output2 = temp.nsmallest(2)
        output = max(output2)
    return output


def raceModel(candGroup, model, features):
    """ Take in a candidate group, append a column 'PRED_VOTE_PCT' with predicted percentage of votes"""
    race_key = ['CONTEST_NAME', 'ELECTION_DATE']
    cand_key = [*race_key, 'CANDIDATE_NAME']
    data = candGroup.copy()
    data['RANDOM_VARIABLE'] = np.random.randint(100)
    raceFeatures = ['CANDIDATE_COUNT', 'RACE_TOTAL_RAISED', 'RACE_VOTE_TOTAL']
    moneyFeatures = ['CAND_TOTAL_RAISED', 'CAND_SHARE_OF_MONEY_RAISED', 'NUM_IND_DONORS', 'SUM_IND_DONATIONS']
    candFeatures = ['PARTY_LEAN', 'WRITE_IN_FLAG', 'PARTY_FAVORITE', 'IND_DONOR_RATIO']
    randomFeature = ['RANDOM_VARIABLE']
    features = raceFeatures + candFeatures + randomFeature + moneyFeatures
    X = data[features]
    y = model.predict(X)
    y = y / np.sum(y)
    data['PRED_VOTE_PCT'] = y
    return data

if __name__ == '__main__':
    from os import chdir
    chdir('..')

    preCalc()