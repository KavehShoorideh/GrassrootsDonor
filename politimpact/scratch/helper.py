import  re
import pandas as pd
from datetime import datetime
from collections import defaultdict
import dateutil.parser
import politimpact.config as cfg

# Create a mapping of transaction date to election date
def nextElection(thisDate, electionDates):
    thisDate = fixDates(thisDate)
    result = None
    for key, value in sorted(electionDates.items()):
        if thisDate < key:
            result = key
            break
    return result

def prevElection(thisDate, electionDates):
    thisDate = fixDates(thisDate)
    result = None
    for key, value in sorted(electionDates.items(), reverse=True):
        if thisDate > key:
            result = key
            break
    return result

def fixName(name):
    """ Change lastname, firstname to firstname lastname"""
    result = re.sub(r'(.*), (.*)', r'\2 \1', name)
    return result

import dateutil.parser

def fixDates(dateString):
    """Function to fix dates from stribng into datetime objects"""
    if isinstance(dateString, str):
        try:
            return dateutil.parser.parse(dateString)
        except ValueError:
            return None
    elif isinstance(dateString, datetime):
        return dateString
    return None

electionDates={
    fixDates('Mar 3, 2020'):'2020 Primary',
    fixDates('November 3, 2020'): '2020 General',
    fixDates('June 5, 2018'):'2018 Primary',
    fixDates('November 6, 2018'): '2018 General',
    fixDates('June 7, 2016'):'2016 Primary',
    fixDates('November 8, 2016'): '2016 General',
    fixDates('June 3, 2014'):'2014 Primary',
    fixDates('November 4, 2014'): '2014 General'}

electionDateList = [key for key, value in electionDates.items()]


def fixElectionDates(mydate):
    for date, name in sorted(electionDates.items()):
        if mydate < date:
            output = date
            break
    return output



def moneyToDate(df, name, date, election):
    """ find money raised to date for named candidate in named election from df."""
    df = df[df['CANDIDATE_NAME'] == name]
    startDate = prevElection(election, electionDates)
    endDate = fixDates(date)
    mask = (startDate < df['TransactionDate']) & (df['TransactionDate'] <= endDate)
    result = df[mask]['TransactionAmount'].sum()
    return result

def gennaPlot(df, date, election):
    g = df.groupby(['Election', 'CONTEST_NAME'])
    top_fundraiser_winners = 0
    top_fundraiser_losers = 0 
    
    for name, group in g:
        candidates = group['CANDIDATE_NAME'].unique()
        moneys = [
            {'name': name,
             'money': moneyToDate(df, name, date, election),
            'outcome': df[df['CANDIDATE_NAME'] == name]['OUTCOME'].unique()[0]} 
            for name in candidates]
        if len(candidates) > 2:
            top_two_funded = sorted(moneys, key=lambda x: x['money'])[-2:]
            for cand in top_two_funded:
                if cand['outcome'] == 0:
                    top_fundraiser_losers += 1
                else:
                    top_fundraiser_winners += 1
    pct = 100 * top_fundraiser_winners/ (top_fundraiser_losers + top_fundraiser_winners)
    return pct

def findThresholds(dfCand, dfRace, dfMoney):
    pass


def findPrimaryOutcome(df_votes):
    # Calculate outcome
    df_outcome = df_votes[df_votes['COUNTY_NAME'] == 'State Totals']
    df_outcome.loc[:, 'OUTCOME'] = 0
    grouped = df_outcome.groupby(['ELECTION_DATE', 'CONTEST_NAME'])
    for name, group in grouped:
        winners = group.sort_values('VOTE_TOTAL', ascending=False).head(2)['CANDIDATE_NAME']
        index_location = winners.index.values
        df_outcome.loc[index_location, 'OUTCOME'] = 1
    return df_outcome
