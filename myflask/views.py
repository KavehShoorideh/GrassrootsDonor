from flask import render_template, request
from myflask import app
from pathlib import Path
import os
import csv

from sqlalchemy import create_engine
import pandas as pd
import psycopg2
from myflask.a_Model import ModelIt
from myflask import pipeline
from configparser import ConfigParser
config = ConfigParser()
config.read('config.ini')

@app.route('/')
@app.route('/index')
@app.route('/input')
def user_input():

    # Read candidate list from file, to enable input search field
    def candidate_name_list():
        # Reading from config.ini file returns extra single quotes, remove first using strip
        filename = config.get('filenames', '2020_candidate_file').strip('\'')
        filepath = Path(os.getcwd()) / filename
        with open(filepath, 'r') as f:
            for record in csv.DictReader(f):
                yield record['name']

    print([str(x) for x in candidate_name_list()])
    return render_template("input.html")

@app.route('/output')
def make_recommendation():
    # pull fields from input field and store it
    user_fav = request.args.get('user-fav-cand')
    user_budget = request.args.get('user-budget')
    user_zip = request.args.get('user_zip_code')
    user_inputs = dict(user_fav=user_fav, user_budget=user_budget, user_zip=user_zip)

    recommendations = pipeline.launch_pipeline(user_inputs)
    if recommendations:
        # Some recommendations have been received!
        return render_template("output.html", recommendations=recommendations, the_result=len(recommendations))
    else:
        print("No recommendations received!")