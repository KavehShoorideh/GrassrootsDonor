def win_chance_model(record, budget):
    if budget == 0:
        return 0.1
    if budget > 0:
        return 0.8

def win_chance_model_race(race):
    return 0.5