from myflask import render_template, request
from flaskexample import app
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import pandas as pd
import psycopg2
from flaskexample.a_Model import ModelIt

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
    fav_cand = request.args.get('fav-cand')
    fav_issues = request.args.get('fav-issue').split(',')
    print(fav_cand)
    print(fav_issues)
    candidates = []
    # query_results = pd.read_sql_query(query, con)
    for i, issue in enumerate(fav_issues):
        candidates.append(dict(index=i+1, issue=issue,
                           birth_month='aug'))
        the_result = len(candidates)
    return render_template("output.html", births=candidates, the_result=the_result)