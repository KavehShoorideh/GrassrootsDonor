# functions to run the data pipeline
import pandas as pd
import os
from pathlib import Path
import csv
from configparser import ConfigParser
from myflask.election_model import win_chance_model_race as model
from myflask.classes import Race as Race

config = ConfigParser()
config.read('config.ini')
# Config usage Examples:
# print config.get('main', 'key3') # -> "value3"
# # getfloat() raises an exception if the value is not a float
# a_float = config.getfloat('main', 'a_float')
# # getint() and getboolean() also do this for their respective types
# an_int = config.getint('main', 'an_int')

def launch_pipeline(user_inputs):

    # Clean user's input, apply defaults when appropriate.
    # convert user's favorite from a name to a dict with all the data
    # This should be ok, since the names are chosen from the same file and should never throw an error
    user_inputs['user_cand'] = next(x for x in candidate_list() if x['name'] == user_inputs['user_fav'])

    # Inputs from text boxes will be strings
    # TODO: clean candidate and zip code too
    if isinstance(user_inputs['user_budget'], str):
        if user_inputs['user_budget'].strip() == '': user_inputs['user_budget'] = 20
        try:
            user_inputs['user_budget'] = float(user_inputs['user_budget'])
        except ValueError:
            raise ValueError(f"Budget must be a number; {user_inputs['user_budget']} given instead")

    # Step 1: Get list of 2020 candidates from file.
    # This data should be updated nightly by a script somewhere else
    # The data should include candidate names, location of district (e.g. zip), party, and
    # funding to date, preferably as a time-series

    final = sorted([apply_model(user_inputs, race) for race in race_list(user_inputs)], key=lambda x: x['pref_score'])

    # return only 5 values
    return final[:5]

def candidate_list():
    # Reading from config.ini file returns extra single quotes, remove first using strip
    filename = config.get('filenames', '2020_candidate_file').strip('\'')
    filepath = Path(os.getcwd()) / filename
    with open(filepath, 'r') as f:
        for record in csv.DictReader(f):
            yield record

def race_list(user_input):
    """ Group candidates by the seat they're running for, and feed into the model"""

    # Reading from config.ini file returns extra single quotes, remove first using strip
    filename = config.get('filenames', '2020_candidate_file').strip('\'')
    filepath = Path(os.getcwd()) / filename
    df = pd.read_csv(filepath)
    grouped_df = df.groupby("office")
    output = []
    for key, item in grouped_df:
        candidates = item.to_dict('records')
        output.append(Race(user_input, candidates))
    return output

def apply_model(user_input, race):
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
              'win_chance_before': f'{(win_chance_before):.0%}',
              'win_chance_after': f'{(win_chance_after):.0%}',
              'impact': f'{(win_chance_after - win_chance_before):.0%}',
              'pref_score': race.favorite['pref_score'],
              'web_link': "https://www.google.com/"
              }
    return record
