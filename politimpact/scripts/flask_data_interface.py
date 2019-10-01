from datetime import datetime
import pandas as pd
from dateutil.parser import parse
from collections import defaultdict
import politimpact.config as cfg
from politimpact.scripts.pre_calc import preCalc

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
    if user_inputs['user_party'] == '':
        user_inputs['user_party'] = 'Democratic'

    # Inputs from text boxes will be strings
    # TODO: clean candidate and zip code too
    if isinstance(user_inputs['user_budget'], str):
        if user_inputs['user_budget'].strip() == '': user_inputs['user_budget'] = 20
        try:
            user_inputs['user_budget'] = float(user_inputs['user_budget'])
        except ValueError:
            raise ValueError(f"Budget must be a number; {user_inputs['user_budget']} given instead")

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
    user_today = user_inputs['user_today']
    if user_today is None:
        user_today = '2018-12-31'
    if parse(user_today) != parse('2018-12-31'):
        # User has entered a different simulated date; rerun pre-calc.
        # returns candidate table with results
        data = preCalc(**user_inputs)
    data = pd.read_csv(cfg.precalc_cand_data,  index_col=0)
    races = pd.read_csv(cfg.precalc_race_data, index_col=0)
    recommendations = filterResults(data, races, user_inputs)
    return recommendations


def filterResults(data, races, user_inputs, output_count = 5, ):
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
    user_party = user_inputs['user_party']
    print(user_party)
    mask = (races['WINNER_PARTY_NAME']!=user_party) & (races['RUNNER_UP_PARTY_NAME']!=user_party)
    temp = races[mask]
    print(temp)

if __name__ == '__main__':
    user_inputs = {
        'user_party': 'Democratic',
        'user_today': None,
        'user_budget': None
    }
    process(user_inputs)