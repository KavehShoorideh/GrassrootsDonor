# functions to run the data pipeline
import pandas as pd
import os
from pathlib import Path
from configparser import ConfigParser
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

    user_fav_cand = read_cand_list_from_file()

    temp_output = [dict(index=1, candidate=user_fav_cand,
                               win_chance_before='10%', win_chance_after='100%', web_link="https://www.google.com/")]
    return temp_output

def read_cand_list_from_file():
    filename = config.get('filenames', '2020_candidate_file')
    home = Path(os.getcwd())
    filename = filename.strip('\'')
    print(home/filename)
    df = pd.read_csv(home / filename)
    print(df)
    # Placeholder:
    first_candidate = df['name'].loc[0]
    print(first_candidate)
    return first_candidate

