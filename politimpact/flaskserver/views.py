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
    user_party = request.args.get('user_party')
    user_priority = request.args.get('user_priority')
    user_today = request.args.get('user_today')
    """
         {% for record in recommendations %}
      <tr><td>{{ record['CONTEST_NAME']}}</td>
          <td>{{ record['CANDIDATE_NAME']}}</td>
          <td>{{ record['PARTY_NAME'] }}</td>
          <td>{{ '0.0f' % record['VOTE_PCT_BEFORE'] | float}}%</td>
          <td>{{ record['MIN_DONATION'] }}</td>
          <td>{{ '0.0f' % record['VOTE_PCT_AFTER']| float}}%</td>
          <td>{{ '0.0f' % (record['VOTE_PCT_AFTER'] - record['VOTE_PCT_BEFORE']) | float}}%</td>
          <td><a href={{ record['web_link'] }}>{{ record['web_link'] }}</a></td>
      </tr>
      {% endfor %}"""
    user_inputs = dict(user_party=user_party, user_priority=user_priority, user_today=user_today)
    try:
        recommendations = process(user_inputs)
        if recommendations:
            # Some recommendations have been received!
            top_rec = recommendations[0]

            return render_template("output.html", recommendations=recommendations, the_result=len(recommendations))
        else:
            print("No recommendations received!")
            return render_template("input.html")
    except FileNotFoundError:
        return render_template("input.html")
