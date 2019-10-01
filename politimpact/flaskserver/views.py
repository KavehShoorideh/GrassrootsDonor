from flask import render_template, request
from politimpact.flaskserver import app
from politimpact import config as cfg

import pandas as pd
from politimpact.scripts import prepare_output
from configparser import ConfigParser
config = ConfigParser()
config.read('config.ini')

@app.route('/')
@app.route('/index')
@app.route('/input')
def user_input():
    return render_template("input.html")

@app.route('/output')
def make_recommendation():
    # pull fields from input field and store it
    user_party = request.args.get('user-party')
    user_budget = request.args.get('user-budget')
    user_inputs = dict(user_party=user_party, user_budget=user_budget)
    recommendations = []
    warnings = []
    try:
        results = pd.read_csv(cfg.candidate_prediction_file)
        cleaned_inputs = prepare_output.clean(user_inputs)
        recommendations = prepare_output.process(user_inputs, results)
        if recommendations:
            # Some recommendations have been received!
            return render_template("output.html", recommendations=recommendations, the_result=len(recommendations))
        else:
            print("No recommendations received!")
    except FileNotFoundError:
        warning = 'Results File Not Found!'
        warnings.append(warning)
        print(warning)
