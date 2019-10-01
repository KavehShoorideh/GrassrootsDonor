def clean(user_inputs):

    # Clean user's input, apply defaults when appropriate.
    # convert user's favorite from a name to a dict with all the data
    # This should be ok, since the names are chosen from the same file and should never throw an error
    if user_inputs['user_party'] == '':
        user_inputs['user_party'] = 'Democratic'

    # Inputs from text boxes will be strings
    # TODO: clean candidate and zip code too
    if isinstance(user_inputs['user_budget'], str):
        if user_inputs['user_budget'].strip() == '': user_inputs['user_budget'] = 20
        try:
            user_inputs['user_budget'] = float(user_inputs['user_budget'])
        except ValueError:
            raise ValueError(f"Budget must be a number; {user_inputs['user_budget']} given instead")

    return user_inputs


def process(user_inputs, results):
    """
    :param user_inputs: user's inputs
    :param results: results file of model, including candidate names, party, (contest_name, election_date),
     calculated win probabilities vs. dollars donated (with enough $ resolution to be able to plot),
      and including campaign web-link
    :return: a record with the format below:
     recordFormat = {'name': name,
                    'office': race.favorite['office'],
                    'win_chance_before': f'{(win_chance_before):.0%}',
                    'win_chance_after': f'{(win_chance_after):.0%}',
                    'impact': f'{(win_chance_after - win_chance_before):.0%}',
                    'party': race.favorite['pref_score'],
                    'web_link': "https://www.google.com/"
                    }
    """

    user_inputs = clean(user_inputs)
    # Perform sort and filter functions, then output as list of dicts. Here 'records' is a pandas keyword.
    finalResults = results.sort_values(by=['party', 'impact']).to_dict('records')
    # return first 5 results only!
    return finalResults[:5]