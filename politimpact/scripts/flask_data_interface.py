from datetime import datetime
import pandas as pd
from dateutil.parser import parse
from collections import defaultdict
from math import copysign
import politimpact.config as cfg
from politimpact.scripts.pre_calc import preCalc
from numpy import sign

race_key = ['CONTEST_NAME', 'ELECTION_DATE']
cand_key = [*race_key, 'CANDIDATE_NAME']

## This file should interface with views.py in the flask folder
def clean(user_inputs):
    """
    Clean user's input, apply defaults when appropriate.
    convert user's favorite from a name to a dict with all the data
    This should be ok, since the names are chosen from the same file and should never throw an error
    :param user_inputs: user inputs dictionary, keys are user_budget, user_party, and user_today (simulated date)
    :return: cleaned user_inputs dictionary
    """
    #

    print(user_inputs)
    if user_inputs['user_party'] is None:
        user_inputs['user_party'] = 'Republican'
    if user_inputs['user_today'] == '':
        user_inputs['user_today'] = '2018-12-31'
    if user_inputs['user_priority'] == '' or user_inputs['user_priority'].lower() == 'ideology':
        # assume ideology first
        user_inputs['user_priority'] = True
    elif user_inputs['user_priority'].lower() == 'winning':
        user_inputs['user_priority'] = False


    # Inputs from text boxes will be strings
    # TODO: clean candidate and zip code too
    # if isinstance(user_inputs['user_budget'], str):
    #     if user_inputs['user_budget'].strip() == '': user_inputs['user_budget'] = 20
    #     try:
    #         user_inputs['user_budget'] = float(user_inputs['user_budget'])
    #     except ValueError:
    #         raise ValueError(f"Budget must be a number; {user_inputs['user_budget']} given instead")

    return user_inputs

def process(user_inputs):
    """
    :param user_inputs: user's inputs
    :param results: results file of model, including candidate names, party, (contest_name, election_date),
     calculated win probabilities vs. dollars donated (with enough $ resolution to be able to plot),
      and including campaign web-link
    :return: list of records, as given by filterResults function
    """
    user_inputs = clean(user_inputs)

    if parse(user_inputs['user_today']) != parse('2018-12-31'):
        # User has entered a different simulated date; rerun pre-calc.
        # returns candidate table with results
        data, races = preCalc(**user_inputs, live=True)
    else:
        data = pd.read_csv(cfg.precalc_cand_data,  index_col=0)
        races = pd.read_csv(cfg.precalc_race_data, index_col=0)
    recommendations = filterResults(data, races, user_inputs)
    return recommendations


def filterResults(data, races, user_inputs, output_count = 5):
    """

    :param user_inputs: user's input dictionary
    :param data: precalculated data
    :param races: precalculated race data
    :param output_count: number of rows to output
    :return: list of records of the following format:
     recordFormat = {'name': name,
                    'office': race.favorite['office'],
                    'win_chance_before': f'{(win_chance_before):.0%}',
                    'win_chance_after': f'{(win_chance_after):.0%}',
                    'impact': f'{(win_chance_after - win_chance_before):.0%}',
                    'party': race.favorite['pref_score'],
                    'web_link': "https://www.google.com/"
                    }
    """

    # Find races where nobody in the top 2 is on the same side of the ideological spectrum as the user
    user_party = user_inputs['user_party']
    temp = races.copy().apply(lambda x: not partyMatch(user_party, x), axis =1)
    myRaces = races[temp].reset_index().set_index(race_key)

    # pick candidates in those races
    data = data.reset_index().set_index(race_key)
    myCands = data[data.index.isin(myRaces.index)]


    # Make sure the candidate we're looking at is the favorite
    myCands = myCands[myCands['FAVORITE'] == myCands['CANDIDATE_NAME']]
    baseline = myCands[myCands['DONATION'] == 1].copy()

    # Extract min donation amounts and win prob
    myCands = selectMinDonation(myCands)

    # Calculate ideology matching
    myCands['IDEOLOGY_ALIGNMENT'] = myCands.copy().apply(lambda x: ideologyMatch(user_party, x), axis=1)

    # Sort
    myCands = mySort(myCands, user_inputs['user_priority'])

    # find baseline chances


    # myCands['BASELINE_VOTE_PCT'] = myCands.apply(lambda x: baseline[baseline['CANDIDATE_NAME'] == x['CANDIDATE_NAME']], axis=1)
    print(myCands)
    # Drop extra columns
    # myCands = myCands.drop(columns=['FAVORITE', 'WINS', 'DONATION'])
    myCands = myCands.reset_index()
    myCands = myCands.head(10)
    recommendations = myCands.to_dict('records')
    # Reformat percentage
    return recommendations

partyLean ={
    'establishment democratic': -0.4,
    'green': -0.8,
    'democratic': -0.7,
    'libertarian': 0.5,
    'republican': 0.7,
    'no party preference': 0,
    'independent': 0
}

def partyMatch(user_party, race):
    lean1 = partyLean.get(race['WINNER_PARTY_NAME'].lower(), 0)
    lean2 = partyLean.get(race['RUNNER_UP_PARTY_NAME'].lower(), 0)
    userLean = partyLean.get(user_party.lower(), 0)
    if (sign(lean1) == sign(userLean)) or (sign(lean2) == sign(userLean)):
        # Somebody from your party is in the top 2! No need for extra money
        # TODO: improve this.
        return True
    else:
        # Your party has no representation in the top 2! Fund fund fund!
        return False

def selectMinDonation(data):
    temp = data.copy()
    temp = temp[temp['DONATION'] == temp['MIN_DONATION']]
    return temp

def ideologyMatch(user_party, row):
    """ Calculate ideology based on simple difference. Use a score of 0 for unrecognized parties"""
    userLean = partyLean.get(user_party.lower(), 0)
    output = 1 - abs(userLean - partyLean.get(row['PARTY_NAME'].lower(), 0))
    return output

def mySort(data, ideologyFirst=False):
    temp = data.copy()
    order = ['MIN_DONATION', 'IDEOLOGY_ALIGNMENT']
    ascending = [True, False]
    if ideologyFirst:
        order = order[::-1]
        ascending = ascending[::-1]
    temp = temp[temp['IDEOLOGY_ALIGNMENT'] > 0].sort_values(order, ascending = ascending )
    return temp

if __name__ == '__main__':
    user_inputs = {
        'user_party': 'Republican',
        'user_today': None,
        'user_priority' : 'ideology'
    }
    process(user_inputs)