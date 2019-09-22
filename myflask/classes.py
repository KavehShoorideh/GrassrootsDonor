from math import *
import zipcodes
import datetime

class Race(object):

    def __init__(self, user_input, candidate_list):
        self.candidate_list = candidate_list
        self.calculate_scores(user_input)
        self.favorite = sorted(self.candidate_list, key = lambda x: x['pref_score'])[0]

    def donate(self, name, amount):
        today = datetime.date.today()  # Today's date
        year = today.year
        quarter = (today.month - 1) // 3  # What quarter of the year are we in?
        column = 'funding' + str(year) + 'Q' + str(quarter)
        for candidate in self.candidate_list:
            if candidate['name'] == name:
                candidate[column] =+ amount

    def calculate_scores(self, user_input):
        user_party = user_input['user_cand']['party']
        user_zip = zipcodes.matching(user_input['user_cand']['zip'])
        lat_user = user_zip[0]['lat']
        long_user = user_zip[0]['long']
        for candidate in self.candidate_list:
            cand_zip = zipcodes.matching(str(candidate['zip']))
            lat_cand = cand_zip[0]['lat']
            long_cand = cand_zip[0]['long']
            distance = calcDist(lat_user, long_user, lat_cand, long_cand)
            candidate['ideology_score'] = 1 if (candidate['party'] == user_party) else 0
            candidate['proximity_score'] = 1 #exp(-distance)
            candidate['pref_score'] = candidate['proximity_score'] * candidate['ideology_score']


def calcDist(lat_A, long_A, lat_B, long_B):
    """ Calculate distance between two coordinates"""
    distance = (sin(radians(lat_A)) *
                sin(radians(lat_B)) +
                cos(radians(lat_A)) *
                cos(radians(lat_B)) *
                cos(radians(long_A - long_B)))

    distance = (degrees(acos(distance))) * 69.09
    return distance