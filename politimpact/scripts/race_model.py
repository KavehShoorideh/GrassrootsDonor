
def applyRaceModel(race, model):
    # predict baseline
    myFeatures = ['INCUMBENT_FLAG', 'PARTY_LEAN', 'CAND_TOTAL_RAISED', 'RACE_TOTAL_RAISED', 'RACE_VOTE_TOTAL']
    X = race[myFeatures]
    race['VOTE_ESTIMATE_baseline'] = model.predict(X)
    race.to_csv('test_results.csv')

    # predict with money
    budget = 100,000
    new_race = pd.DataFrame()

    for i in range(len(race)):
        race.iloc[i, 9] = race.iloc[i ,9] + budget
        race[f'VOTE_ESTIMATE_{i}'] = predict(race, model)

def predict(race, model):
    # predict baseline
    myFeatures = ['INCUMBENT_FLAG', 'PARTY_LEAN', 'CAND_TOTAL_RAISED', 'RACE_TOTAL_RAISED', 'RACE_VOTE_TOTAL']
    X = race[myFeatures]
    y = model.predict(X)
    return y



