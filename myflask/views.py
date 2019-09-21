from flask import render_template, request
from myflask import app
from sqlalchemy import create_engine
import pandas as pd
import psycopg2
from myflask.a_Model import ModelIt

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
def cesareans_input():
    return render_template("input.html")

@app.route('/output')
def cesareans_output():
    # pull 'birth_month' from input field and store it
    user_fav_cand = request.args.get('user-fav-cand')
    user_budget = request.args.get('user-budget')
    user_zip_code = request.args.get('user_zip_code')
    print(user_fav_cand)
    print(user_budget)
    print(user_zip_code)
    candidates = []
    # query_results = pd.read_sql_query(query, con)
    candidates.append(dict(index=1, candidate=user_fav_cand,
                           win_chance_before='10%', win_chance_after='100%', web_link="https://www.google.com/"))
    the_result = len(candidates)
    return render_template("output.html", recommendations=candidates, the_result=the_result)