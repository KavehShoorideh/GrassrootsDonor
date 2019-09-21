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


    x = read_cand_list_from_file()
    temp_output = []
    for i, cand in enumerate(x):
        temp_output.append(
            dict(index=i, candidate=cand['name'],
                      win_chance_before='10%', win_chance_after='100%', web_link="https://www.google.com/")
                 )
    return temp_output

def read_cand_list_from_file():
    filename = config.get('filenames', '2020_candidate_file')
    home = Path(os.getcwd())

    # Reading from config.ini file returns extra single quotes, remove first:
    filename = home / filename.strip('\'')

    with open(filename, 'r') as f:
        for record in csv.DictReader(f):
            yield record