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
    user_budget = request.args.get('user_budget')
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
    if user_budget is '':
        return render_template("input.html")

    try:
        recommendations = process(user_inputs)
        if recommendations:
            user_budget = float(user_budget)

            # Fix floats and stuff
            for record in recommendations:
                # record['IMPACT'] = record['VOTE_PCT_AFTER'] - record['VOTE_PCT_BEFORE']
                record['CANDIDATE_NAME'] = record['CANDIDATE_NAME'].title()
                record['IMPACT'] = f"{record['IMPACT'] * 1000:.3%} per 1000 dollars"
                record['VOTE_PCT_BEFORE'] = f'{record["VOTE_PCT_BEFORE"]:.0%}'
                record['VOTE_PCT_AFTER'] = f'{record["VOTE_PCT_AFTER"]:.0%}'
                record['NUM_DONATIONS'] = f"{int((float(record['MIN_DONATION']) // user_budget)):d}"
                record['MIN_DONATION'] = f"${record['MIN_DONATION']:,.0f}"

                record['TEXT'] = \
                    f"I'm donating ${user_budget:,.0f} to the campaign of {record['CANDIDATE_NAME']} for {record['CONTEST_NAME']}. With {record['NUM_DONATIONS']} donations of ${user_budget:,.0f}, we can help a {record['PARTY_NAME']} make it to the general election! Please donate and share!"

            # Some recommendations have been received!
            top_rec = recommendations[0]
            user_budget = f"${user_budget:,.0f}"
            return render_template("output.html", recommendations=recommendations, user_budget = user_budget, the_result=len(recommendations))
        else:
            print("No recommendations received!")
            return render_template("input.html")
    except FileNotFoundError:
        return render_template("input.html")
