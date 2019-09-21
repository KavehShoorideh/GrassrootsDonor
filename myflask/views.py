from flask import render_template, request
from myflask import app
from sqlalchemy import create_engine
import pandas as pd
import psycopg2
from myflask.a_Model import ModelIt
from myflask import pipeline

# Python code to connect to Postgres
# You may need to modify this based on your OS,
# as detailed in the postgres dev setup materials.
user = 'postgres'  # add your Postgres username here
password = 'password'
host = 'localhost'
dbname = 'birth_db'
db = create_engine('postgres://%s%s/%s' % (user, host, dbname))
con = None
con = psycopg2.connect(database=dbname, user=user, host=host, password=password)  # add your Postgres password here


@app.route('/')
@app.route('/index')
@app.route('/input')
def user_input():
    return render_template("input.html")

@app.route('/output')
def make_recommendation():
    # pull fields from input field and store it
    user_fav_cand = request.args.get('user-fav-cand')
    user_budget = request.args.get('user-budget')
    user_zip_code = request.args.get('user_zip_code')

    recommendations = pipeline.launch_pipeline(user_fav_cand, user_budget, user_zip_code)
    if recommendations:
        # Some recommendations have been received!
        return render_template("output.html", recommendations=recommendations, the_result=len(recommendations))
    else:
        print("No recommendations received!")