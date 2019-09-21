# functions to run the data pipeline
import pandas as pd
import os
from pathlib import Path
from configparser import ConfigParser
import csv
config = ConfigParser()
config.read('config.ini')
# Config usage Examples:

# print config.get('main', 'key3') # -> "value3"
# # getfloat() raises an exception if the value is not a float
# a_float = config.getfloat('main', 'a_float')
# # getint() and getboolean() also do this for their respective types
# an_int = config.getint('main', 'an_int')

def launch_pipeline(user_fav_cand, user_budget, user_zip_code):
    # Step 1: Get list of 2020 candidates from file.
    # This data should be updated nightly by a script somewhere else
    # The data should include candidate names, location of district (e.g. zip), party, and
    # funding to date, preferably as a time-series


    records = apply_model(
        engineer_features(
            read_cand_list_from_file()
        ), user_budget = user_budget
    )

    output = []
    for i, record in enumerate(records):
        output.append(
            dict(index=i, **record,
                 web_link="https://www.google.com/")
                 )
        # Only return 5 recommendations
        if i == 4: break
    return output

def read_cand_list_from_file():
    # Reading from config.ini file returns extra single quotes, remove first using strip
    filename = config.get('filenames', '2020_candidate_file').strip('\'')
    filepath = Path(os.getcwd()) / filename
    with open(filepath, 'r') as f:
        for record in csv.DictReader(f):
            yield record

def engineer_features(records):
    for record in records:
        # Some manipulation here
        # also fix preference score

        # assume user is dem for now:
        myParty = 'Democratic'
        print(record)
        if record['party'] == myParty:
            preference_score = 1
        else:
            preference_score = 0
        # Later: preference score should include proximity also ideology
        record['pref_score'] = preference_score
        yield record

def apply_model(records, user_budget):
    for record in records:
        # Calculate these using the model
        win_chance_before = win_chance_model(record, budget=0)
        win_chance_after = win_chance_model(record, budget=user_budget)
        record['win_chance_before'] = f'{(win_chance_before):.0%}'
        record['win_chance_after'] = f'{(win_chance_after):.0%}'
        record['impact'] = f'{(win_chance_after - win_chance_before):.0%}'
        yield record

def win_chance_model(record, budget=0):
    budget = float(budget)
    if budget == 0:
        return 0.1
    if budget > 0:
        return 0.8
