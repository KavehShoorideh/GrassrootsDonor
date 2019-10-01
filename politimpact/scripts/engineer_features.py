from datetime import datetime
import pandas as pd
from dateutil.parser import parse
from collections import defaultdict
import politimpact.config as cfg


def engineerFeatures(start_date=None, end_date=None):
    """ Engineers features, based on given dates"""

    if start_date is None:
        start_date = parse('2015-01-01')
    elif isinstance(start_date, str):
        start_date = parse(start_date)
    if end_date is None:
        end_date = datetime.today()
    elif isinstance(end_date, str):
        end_date = parse(end_date)

    print('Engineering features.')

    # Set primary keys for races and candidates
    race_key = ['CONTEST_NAME', 'ELECTION_DATE']
    cand_key = ['CANDIDATE_NAME', 'CONTEST_NAME', 'ELECTION_DATE']

    # Read files
    dfMoney = pd.read_csv(cfg.cleaned_money_file, index_col=0, low_memory=False)
    dfRace = pd.read_csv(cfg.cleaned_race_file, index_col=0)
    dfCand = pd.read_csv(cfg.cleaned_candidate_file, index_col=0)

    # Convert election dates to datetime format
    dfCand['ELECTION_DATE'] = pd.to_datetime(dfCand['ELECTION_DATE'])
    dfRace['ELECTION_DATE'] = pd.to_datetime(dfRace['ELECTION_DATE'])
    dfMoney['ELECTION_DATE'] = pd.to_datetime(dfMoney['ELECTION_DATE'])

    dfMoney['TRANSACTION_DATE'] = pd.to_datetime(dfMoney['TRANSACTION_DATE'])

    # Only include rows in the tables that match given dates
    moneyMask = (dfMoney['TRANSACTION_DATE'] > start_date) & (dfMoney['TRANSACTION_DATE'] < end_date)
    dfMoney = dfMoney[moneyMask]
    candMask = (dfCand['ELECTION_DATE'] > start_date) & (dfCand['ELECTION_DATE'] < end_date)
    raceMask = (dfRace['ELECTION_DATE'] > start_date) & (dfRace['ELECTION_DATE'] < end_date)
    dfCand = dfCand[candMask]
    dfRace = dfRace[raceMask]

    # map party names to values
    # TODO: include establishment vs. non establishment.
    partyMap = defaultdict(lambda: 0)
    partyMap['Democratic'] = -1
    partyMap['Green'] = -1
    partyMap['American Independent'] = 1
    partyMap['Republican'] = 1
    dfCand['PARTY_LEAN'] = dfCand['PARTY_NAME'].map(partyMap)

    # Keep only state senate and assembly races
    dfRace['LEGISLATURE'] = dfRace.CONTEST_NAME.str.contains(r'(State Assembly)|(State Senate)', na=True)
    dfRace = dfRace[(dfRace.LEGISLATURE == 1)]

    # Remerge to get rid of no_contest races or non legislature races
    dfCand = pd.merge(dfCand,
                      dfRace,
                      left_on=race_key,
                      right_on=race_key, how='inner')

    # encode incumbent flag and write_in flag
    dfCand['INCUMBENT_FLAG'] = dfCand.INCUMBENT_FLAG.replace({'Y': 1, 'N': 0})
    dfCand['WRITE_IN_FLAG'] = dfCand.WRITE_IN_FLAG.replace({'Y': 1, 'N': 0})

    # remove extra candidate columns
    columns = [*cand_key, 'PARTY_NAME', 'INCUMBENT_FLAG', 'PARTY_LEAN', 'WRITE_IN_FLAG', 'VOTE_TOTAL']
    dfCand = dfCand[columns]

    # Find number of candidates running
    candCount = dfCand.groupby(race_key).agg(CANDIDATE_COUNT=('CANDIDATE_NAME', 'count'))
    dfRace = pd.merge(dfRace, candCount, left_on=race_key, right_on=race_key, how='left')
    dfRace = dfRace[dfRace['CANDIDATE_COUNT'] > 2]

    # Find total money raised in race and re-merge back into main race frame
    totalRace = dfMoney.groupby(race_key).agg(RACE_TOTAL_RAISED=('TRANSACTION_AMOUNT', 'sum')).reset_index()
    # totalRace['ELECTION_DATE'] = pd.to_datetime(totalRace['ELECTION_DATE'])
    dfRace = pd.merge(dfRace, totalRace, left_on=race_key, right_on=race_key, how='left')

    # Find total money raised by candidate and merge into candidates table
    totalCand = dfMoney.groupby(cand_key).agg(CAND_TOTAL_RAISED=('TRANSACTION_AMOUNT', 'sum')).reset_index()
    dfCand = pd.merge(dfCand, totalCand, on=cand_key, how='left')

    # topTwoThreshold= totalCand.reset_index().sort_values(by='CAND_TOTAL_RAISED', ascending=False).groupby(race_key).head(2)
    # dfRace = pd.merge(dfRace, topTwoThreshold, left_on=race_key, right_on=race_key, how='left')

    dfRace_r = dfRace.set_index(race_key)
    dfRace_r['RACE_VOTE_TOTAL'] = dfCand.groupby(race_key)['VOTE_TOTAL'].sum()
    dfRace = dfRace_r.reset_index()
    dfCand = pd.merge(dfCand, dfRace, on=race_key, how='left')
    dfCand['VOTE_SHARE'] = dfCand['VOTE_TOTAL'] / dfCand['RACE_VOTE_TOTAL']
    #
    #
    # dfnew = dfCand.groupby(race_key).filter(lambda x: x.notna().all().all())
    # dfCand = dfnew.reset_index(drop=True)  # reset index
    #
    # groups = dfCand.groupby(race_key)
    # cands = dfCand.set_index(race_key)
    # for name, group in groups:
    #     # we are iterating through the groups here
    #     myCands = cands.loc[name]
    #     myCands.to_csv(cfg.dataDir / 'test.csv')
    #     break

    return (dfCand, dfRace, dfMoney)

if __name__ == '__main__':
    dfCand, dfRace, dfMoney = engineerFeatures(end_date = '2016-12-31')

    # Save
    # dfMoney.to_csv(cfg.training_money_file)
    # dfRace.to_csv(cfg.training_race_file)
    dfCand.to_csv(cfg.training_candidate_file)
