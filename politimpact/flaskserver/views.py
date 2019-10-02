from flask import render_template, request
from politimpact.flaskserver import app
from politimpact.scripts.flask_data_interface import process

@app.route('/')
@app.route('/index')
@app.route('/input')
def user_input():
    return render_template("input.html")

@app.route('/output')
def make_recommendation():
    # pull fields from request
    user_party = request.args.get('user-party')
    user_priority = request.args.get('user_priority')
    user_today = request.args.get('user_today')
    user_inputs = dict(user_party=user_party, user_priority=user_priority, user_today=user_today)
    try:
        recommendations = process(user_inputs)
        if recommendations:
            # Some recommendations have been received!
            return render_template("output.html", recommendations=recommendations, the_result=len(recommendations))
        else:
            print("No recommendations received!")
            return render_template("input.html")
    except FileNotFoundError:
        return render_template("input.html")
